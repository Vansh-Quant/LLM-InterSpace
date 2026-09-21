from fastapi.testclient import TestClient

from interspace.core.app import app


def _register(client: TestClient, agent_id: str = "contract-agent") -> None:
    response = client.post(
        "/agents/register",
        json={
            "agent_id": agent_id,
            "name": "Contract Agent",
            "role": "backend",
            "model": "test-model",
        },
    )
    assert response.status_code == 200


def test_contract_publish_versions_and_diff():
    with TestClient(app) as client:
        _register(client)

        v1 = client.post(
            "/contracts/publish",
            json={
                "contract_id": "user-api",
                "name": "User API",
                "created_by": "contract-agent",
                "definition": {
                    "endpoint": "/users",
                    "request": {"user_id": "string"},
                    "response": {"name": "string"},
                },
            },
        )
        assert v1.status_code == 200
        assert v1.json()["version"] == 1

        v2 = client.post(
            "/contracts/publish",
            json={
                "contract_id": "user-api",
                "name": "User API",
                "created_by": "contract-agent",
                "definition": {
                    "endpoint": "/users",
                    "request": {"userId": "string"},
                    "response": {"name": "string"},
                },
            },
        )
        assert v2.status_code == 200
        assert v2.json()["version"] == 2

        latest = client.get("/contracts/user-api")
        assert latest.status_code == 200
        assert latest.json()["version"] == 2

        diff = client.get("/contracts/user-api/diff?from_version=1&to_version=2")
        assert diff.status_code == 200
        assert diff.json()["removed"] == ["request.user_id"]
        assert diff.json()["added"] == ["request.userId"]
        assert diff.json()["changed"] == []


def test_contract_publish_requires_registered_agent():
    with TestClient(app) as client:
        response = client.post(
            "/contracts/publish",
            json={
                "contract_id": "unowned-api",
                "name": "Unowned API",
                "created_by": "missing-agent",
                "definition": {"endpoint": "/test"},
            },
        )
        assert response.status_code == 404


def test_contract_diff_rejects_same_version():
    with TestClient(app) as client:
        _register(client, "same-version-agent")
        response = client.post(
            "/contracts/publish",
            json={
                "contract_id": "same-version-api",
                "name": "Same Version API",
                "created_by": "same-version-agent",
                "definition": {"endpoint": "/test"},
            },
        )
        assert response.status_code == 200

        response = client.get(
            "/contracts/same-version-api/diff?from_version=1&to_version=1"
        )
        assert response.status_code == 400
