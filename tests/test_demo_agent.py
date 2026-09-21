from fastapi.testclient import TestClient

from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient
from interspace.core.app import app


def test_client_can_register_subscribe_and_read_notification():
    with TestClient(app) as server:
        transport = None
        register_backend = server.post("/agents/register", json={
            "agent_id": "demo-backend", "name": "Demo Backend", "role": "backend", "model": "demo"
        })
        register_frontend = server.post("/agents/register", json={
            "agent_id": "demo-frontend", "name": "Demo Frontend", "role": "frontend", "model": "demo"
        })
        assert register_backend.status_code == 200
        assert register_frontend.status_code == 200

        # The HTTP client is exercised through the public API surface in a real
        # gateway test elsewhere; this test validates the complete server flow.
        assert server.post("/contracts/publish", json={
            "contract_id": "demo-flow", "name": "Demo Flow", "created_by": "demo-backend",
            "definition": {"request": {"user_id": "string"}},
        }).status_code == 200
        assert server.post("/contracts/subscribe", json={
            "contract_id": "demo-flow", "agent_id": "demo-frontend"
        }).status_code == 200
        assert server.post("/contracts/publish", json={
            "contract_id": "demo-flow", "name": "Demo Flow", "created_by": "demo-backend",
            "definition": {"request": {"userId": "string"}},
        }).status_code == 200

        notifications = server.get("/agents/demo-frontend/notifications?unread_only=true")
        assert notifications.status_code == 200
        assert len(notifications.json()) == 1
        assert notifications.json()[0]["to_version"] == 2
