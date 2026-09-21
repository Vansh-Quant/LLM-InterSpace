from fastapi.testclient import TestClient

from interspace.core.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_list_and_heartbeat():
    payload = {
        "agent_id": "backend-test",
        "name": "Backend Test Agent",
        "role": "backend",
        "model": "test-model",
        "capabilities": ["contract_analysis"],
    }
    response = client.post("/agents/register", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "online"

    response = client.get("/agents")
    assert response.status_code == 200
    assert any(agent["agent_id"] == "backend-test" for agent in response.json())

    response = client.post(
        "/agents/backend-test/heartbeat",
        json={"status": "busy"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "busy"

def test_unknown_agent_heartbeat():
    response = client.post(
        "/agents/missing/heartbeat",
        json={"status": "online"},
    )
    assert response.status_code == 404

def test_event_creation_and_listing():
    client.post(
        "/agents/register",
        json={
            "agent_id": "event-test",
            "name": "Event Test Agent",
            "role": "test",
            "model": "test-model",
        },
    )
    response = client.post(
        "/events",
        json={
            "event_type": "agent.test",
            "agent_id": "event-test",
            "payload": {"ok": True},
        },
    )
    assert response.status_code == 200
    event_id = response.json()["event_id"]

    response = client.get("/events")
    assert response.status_code == 200
    assert any(event["event_id"] == event_id for event in response.json())

def test_event_rejects_unknown_agent():
    response = client.post(
        "/events",
        json={
            "event_type": "agent.test",
            "agent_id": "does-not-exist",
            "payload": {},
        },
    )
    assert response.status_code == 404
