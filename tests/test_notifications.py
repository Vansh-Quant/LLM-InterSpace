from fastapi.testclient import TestClient

from interspace.core.app import app


def register(client: TestClient, agent_id: str) -> None:
    response = client.post("/agents/register", json={
        "agent_id": agent_id, "name": agent_id, "role": "test", "model": "test-model"
    })
    assert response.status_code == 200


def publish(client: TestClient, agent_id: str, definition: dict) -> dict:
    response = client.post("/contracts/publish", json={
        "contract_id": "notify-api",
        "name": "Notify API",
        "created_by": agent_id,
        "definition": definition,
    })
    assert response.status_code == 200
    return response.json()


def test_contract_change_notifies_subscriber():
    with TestClient(app) as client:
        register(client, "backend-agent")
        register(client, "frontend-agent")

        publish(client, "backend-agent", {"request": {"user_id": "string"}})

        subscribed = client.post("/contracts/subscribe", json={
            "contract_id": "notify-api",
            "agent_id": "frontend-agent",
        })
        assert subscribed.status_code == 200

        publish(client, "backend-agent", {"request": {"userId": "string"}})

        notifications = client.get("/agents/frontend-agent/notifications?unread_only=true")
        assert notifications.status_code == 200
        data = notifications.json()
        assert len(data) == 1
        assert data[0]["notification_type"] == "contract_changed"
        assert data[0]["from_version"] == 1
        assert data[0]["to_version"] == 2
        assert data[0]["payload"]["changes"]["removed"] == ["request.user_id"]
        assert data[0]["payload"]["changes"]["added"] == ["request.userId"]


def test_notification_can_be_acknowledged():
    with TestClient(app) as client:
        register(client, "backend-ack")
        register(client, "frontend-ack")

        publish(client, "backend-ack", {"request": {"id": "string"}})
        client.post("/contracts/subscribe", json={
            "contract_id": "notify-api",
            "agent_id": "frontend-ack",
        })
        publish(client, "backend-ack", {"request": {"id": "integer"}})

        notification = client.get("/agents/frontend-ack/notifications").json()[0]
        ack = client.post(
            f"/agents/frontend-ack/notifications/{notification['notification_id']}/ack"
        )
        assert ack.status_code == 200

        unread = client.get("/agents/frontend-ack/notifications?unread_only=true")
        assert unread.status_code == 200
        assert unread.json() == []
