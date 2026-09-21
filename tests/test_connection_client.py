from unittest.mock import Mock, patch

import pytest

from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient, InterSpaceConnectionError


def test_client_ping():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"status": "ok"}

    with patch("interspace.communication.client.httpx.request", return_value=response) as request:
        result = InterSpaceClient("http://192.168.1.10:8000").ping()

    assert result["status"] == "ok"
    request.assert_called_once_with(
        "GET",
        "http://192.168.1.10:8000/network/ping",
        timeout=5.0,
    )


def test_client_register():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"agent_id": "frontend-1"}

    agent = AgentRegistration(
        agent_id="frontend-1",
        name="Frontend Agent",
        role="frontend",
        model="test-model",
    )

    with patch("interspace.communication.client.httpx.request", return_value=response) as request:
        result = InterSpaceClient("http://gateway:8000").register(agent)

    assert result["agent_id"] == "frontend-1"
    request.assert_called_once()


def test_client_wraps_connection_errors():
    with patch(
        "interspace.communication.client.httpx.request",
        side_effect=__import__("httpx").ConnectError("offline"),
    ):
        with pytest.raises(InterSpaceConnectionError):
            InterSpaceClient("http://offline-host:8000").ping()
