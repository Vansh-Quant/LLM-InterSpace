import json
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from interspace.agents.models import AgentHeartbeat, AgentRegistration, AgentResponse, utc_now
from interspace.communication.models import EventCreate, EventResponse
from interspace.core.database import get_connection, initialize_database

app = FastAPI(title="LLM InterSpace Gateway", version="0.2.0")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


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
    return AgentResponse(
        agent_id=row["agent_id"], name=row["name"], role=row["role"],
        model=row["model"], capabilities=json.loads(row["capabilities_json"]),
        status=row["status"], last_heartbeat=row["last_heartbeat"]
    )


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
    return AgentResponse(
        agent_id=row["agent_id"], name=row["name"], role=row["role"],
        model=row["model"], capabilities=json.loads(row["capabilities_json"]),
        status=row["status"], last_heartbeat=row["last_heartbeat"]
    )


@app.get("/agents", response_model=list[AgentResponse])
def list_agents() -> list[AgentResponse]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM agents ORDER BY name").fetchall()
    return [
        AgentResponse(
            agent_id=row["agent_id"], name=row["name"], role=row["role"],
            model=row["model"], capabilities=json.loads(row["capabilities_json"]),
            status=row["status"], last_heartbeat=row["last_heartbeat"]
        )
        for row in rows
    ]


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
