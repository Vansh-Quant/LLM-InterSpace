import json
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query

from interspace.agents.models import AgentHeartbeat, AgentRegistration, AgentResponse, utc_now
from interspace.communication.models import EventCreate, EventResponse
from interspace.core.contract_diff import diff_contracts
from interspace.core.contracts import (
    ContractDiffResponse,
    ContractPublish,
    ContractSummary,
    ContractVersionResponse,
)
from interspace.core.database import get_connection, initialize_database

app = FastAPI(title="LLM InterSpace Gateway", version="0.3.0")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


def _agent_response(row) -> AgentResponse:
    return AgentResponse(
        agent_id=row["agent_id"],
        name=row["name"],
        role=row["role"],
        model=row["model"],
        capabilities=json.loads(row["capabilities_json"]),
        status=row["status"],
        last_heartbeat=row["last_heartbeat"],
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "interspace-gateway"}


@app.get("/network/ping")
def network_ping() -> dict:
    return {
        "status": "ok",
        "service": "interspace-gateway",
        "gateway_version": app.version,
        "timestamp": utc_now(),
    }


@app.post("/agents/register", response_model=AgentResponse)
def register_agent(agent: AgentRegistration) -> AgentResponse:
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO agents(agent_id, name, role, model, status, capabilities_json, last_heartbeat, created_at)
            VALUES (?, ?, ?, ?, 'online', ?, ?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                name=excluded.name,
                role=excluded.role,
                model=excluded.model,
                status='online',
                capabilities_json=excluded.capabilities_json,
                last_heartbeat=excluded.last_heartbeat
            """,
            (
                agent.agent_id, agent.name, agent.role, agent.model,
                json.dumps(agent.capabilities), now.isoformat(), now.isoformat()
            ),
        )
        row = conn.execute("SELECT * FROM agents WHERE agent_id = ?", (agent.agent_id,)).fetchone()
    return _agent_response(row)


@app.post("/agents/{agent_id}/heartbeat", response_model=AgentResponse)
def heartbeat(agent_id: str, heartbeat_data: AgentHeartbeat) -> AgentResponse:
    now = utc_now()
    with get_connection() as conn:
        result = conn.execute(
            "UPDATE agents SET status = ?, last_heartbeat = ? WHERE agent_id = ?",
            (heartbeat_data.status, now.isoformat(), agent_id),
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Agent not registered")
        row = conn.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
    return _agent_response(row)


@app.get("/agents", response_model=list[AgentResponse])
def list_agents() -> list[AgentResponse]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM agents ORDER BY name").fetchall()
    return [_agent_response(row) for row in rows]


@app.post("/events", response_model=EventResponse)
def create_event(event: EventCreate) -> EventResponse:
    if event.agent_id:
        with get_connection() as conn:
            exists = conn.execute(
                "SELECT 1 FROM agents WHERE agent_id = ?", (event.agent_id,)
            ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Agent not registered")

    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO events(event_id, event_type, agent_id, payload_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (event_id, event.event_type, event.agent_id, json.dumps(event.payload), now.isoformat()),
        )
    return EventResponse(
        event_id=event_id, event_type=event.event_type,
        agent_id=event.agent_id, payload=event.payload, created_at=now
    )


@app.get("/events", response_model=list[EventResponse])
def list_events(limit: int = 100) -> list[EventResponse]:
    limit = max(1, min(limit, 500))
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [
        EventResponse(
            event_id=row["event_id"], event_type=row["event_type"],
            agent_id=row["agent_id"], payload=json.loads(row["payload_json"]),
            created_at=datetime.fromisoformat(row["created_at"])
        )
        for row in rows
    ]


@app.post("/contracts/publish", response_model=ContractVersionResponse)
def publish_contract(contract: ContractPublish) -> ContractVersionResponse:
    now = utc_now()
    with get_connection() as conn:
        agent = conn.execute(
            "SELECT 1 FROM agents WHERE agent_id = ?", (contract.created_by,)
        ).fetchone()
        if not agent:
            raise HTTPException(status_code=404, detail="Publishing agent not registered")

        current = conn.execute(
            "SELECT latest_version FROM contracts WHERE contract_id = ?",
            (contract.contract_id,),
        ).fetchone()

        version = 1 if current is None else current["latest_version"] + 1
        definition_json = json.dumps(contract.definition, sort_keys=True, separators=(",", ":"))

        conn.execute(
            """
            INSERT INTO contracts(contract_id, name, latest_version, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(contract_id) DO UPDATE SET
                name=excluded.name,
                latest_version=excluded.latest_version,
                updated_at=excluded.updated_at
            """,
            (contract.contract_id, contract.name, version, now.isoformat()),
        )
        conn.execute(
            """
            INSERT INTO contract_versions(contract_id, version, definition_json, created_by, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (contract.contract_id, version, definition_json, contract.created_by, now.isoformat()),
        )

    return ContractVersionResponse(
        contract_id=contract.contract_id,
        name=contract.name,
        version=version,
        definition=contract.definition,
        created_by=contract.created_by,
        created_at=now,
    )


@app.get("/contracts", response_model=list[ContractSummary])
def list_contracts() -> list[ContractSummary]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT contract_id, name, latest_version, updated_at FROM contracts ORDER BY contract_id"
        ).fetchall()
    return [
        ContractSummary(
            contract_id=row["contract_id"],
            name=row["name"],
            latest_version=row["latest_version"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]


@app.get("/contracts/{contract_id}", response_model=ContractVersionResponse)
def get_latest_contract(contract_id: str) -> ContractVersionResponse:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT c.contract_id, c.name, v.version, v.definition_json, v.created_by, v.created_at
            FROM contracts c
            JOIN contract_versions v
              ON v.contract_id = c.contract_id AND v.version = c.latest_version
            WHERE c.contract_id = ?
            """,
            (contract_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ContractVersionResponse(
        contract_id=row["contract_id"],
        name=row["name"],
        version=row["version"],
        definition=json.loads(row["definition_json"]),
        created_by=row["created_by"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


@app.get("/contracts/{contract_id}/versions/{version}", response_model=ContractVersionResponse)
def get_contract_version(contract_id: str, version: int) -> ContractVersionResponse:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT c.contract_id, c.name, v.version, v.definition_json, v.created_by, v.created_at
            FROM contracts c
            JOIN contract_versions v ON v.contract_id = c.contract_id
            WHERE c.contract_id = ? AND v.version = ?
            """,
            (contract_id, version),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Contract version not found")
    return ContractVersionResponse(
        contract_id=row["contract_id"],
        name=row["name"],
        version=row["version"],
        definition=json.loads(row["definition_json"]),
        created_by=row["created_by"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


@app.get("/contracts/{contract_id}/diff", response_model=ContractDiffResponse)
def contract_diff(
    contract_id: str,
    from_version: int = Query(ge=1),
    to_version: int = Query(ge=1),
) -> ContractDiffResponse:
    if from_version == to_version:
        raise HTTPException(status_code=400, detail="Versions must be different")

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT version, definition_json
            FROM contract_versions
            WHERE contract_id = ? AND version IN (?, ?)
            ORDER BY version
            """,
            (contract_id, from_version, to_version),
        ).fetchall()

    if len(rows) != 2:
        raise HTTPException(status_code=404, detail="One or both contract versions not found")

    definitions = {row["version"]: json.loads(row["definition_json"]) for row in rows}
    changes = diff_contracts(definitions[from_version], definitions[to_version])

    return ContractDiffResponse(
        contract_id=contract_id,
        from_version=from_version,
        to_version=to_version,
        **changes,
    )
