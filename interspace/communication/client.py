from typing import Any

import httpx

from interspace.agents.models import AgentHeartbeat, AgentRegistration
from interspace.communication.notifications import ContractSubscriptionCreate
from interspace.core.contracts import ContractPublish


class InterSpaceConnectionError(RuntimeError):
    """Raised when an agent cannot reach the InterSpace gateway."""


class InterSpaceClient:
    """HTTP client used by agents to connect to the shared InterSpace gateway."""

    def __init__(self, gateway_url: str, timeout: float = 5.0) -> None:
        self.gateway_url = gateway_url.rstrip("/")
        self.timeout = timeout

    def ping(self) -> dict[str, Any]:
        return self._request("GET", "/network/ping")

    def register(self, agent: AgentRegistration) -> dict[str, Any]:
        return self._request("POST", "/agents/register", json=agent.model_dump())

    def heartbeat(self, agent_id: str, status: str = "online") -> dict[str, Any]:
        heartbeat = AgentHeartbeat(status=status)
        return self._request(
            "POST",
            f"/agents/{agent_id}/heartbeat",
            json=heartbeat.model_dump(),
        )

    def send_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/events",
            json={
                "event_type": event_type,
                "agent_id": agent_id,
                "payload": payload,
            },
        )

    def publish_contract(self, contract: ContractPublish) -> dict[str, Any]:
        return self._request(
            "POST",
            "/contracts/publish",
            json=contract.model_dump(),
        )

    def get_contract(self, contract_id: str, version: int | None = None) -> dict[str, Any]:
        path = (
            f"/contracts/{contract_id}"
            if version is None
            else f"/contracts/{contract_id}/versions/{version}"
        )
        return self._request("GET", path)

    def diff_contract(
        self,
        contract_id: str,
        from_version: int,
        to_version: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/contracts/{contract_id}/diff",
            params={"from_version": from_version, "to_version": to_version},
        )

    def subscribe(self, contract_id: str, agent_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/contracts/subscribe",
            json=ContractSubscriptionCreate(
                contract_id=contract_id,
                agent_id=agent_id,
            ).model_dump(),
        )

    def notifications(
        self,
        agent_id: str,
        unread_only: bool = False,
    ) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            f"/agents/{agent_id}/notifications",
            params={"unread_only": unread_only},
        )

    def acknowledge_notification(
        self,
        agent_id: str,
        notification_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/agents/{agent_id}/notifications/{notification_id}/ack",
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = httpx.request(
                method,
                f"{self.gateway_url}{path}",
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise InterSpaceConnectionError(
                f"InterSpace gateway request failed: {method} {path}"
            ) from exc
