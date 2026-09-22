from typing import Any
from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient

class BaseAgent:
    def __init__(self, registration: AgentRegistration, gateway: str):
        self.registration = registration
        self.client = InterSpaceClient(gateway)

    def start(self) -> dict[str, Any]:
        return self.client.register(self.registration)

    def heartbeat(self, status: str = "online") -> dict[str, Any]:
        return self.client.heartbeat(self.registration.agent_id, status)

    def send(self, recipient_id: str, message_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.client.send_message(self.registration.agent_id, recipient_id, message_type, payload)

class BackendAgent(BaseAgent):
    pass

class FrontendAgent(BaseAgent):
    pass

class QAAgent(BaseAgent):
    def run_tests(self, test_path: str | None = None, timeout_seconds: int = 60) -> dict[str, Any]:
        return self.client.run_qa(self.registration.agent_id, test_path, timeout_seconds)
