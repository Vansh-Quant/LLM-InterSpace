from typing import Any
import httpx
from interspace.agents.models import AgentHeartbeat, AgentRegistration
from interspace.communication.notifications import ContractSubscriptionCreate
from interspace.communication.messages import MessageCreate
from interspace.core.contracts import ContractPublish
from interspace.core.experiences import ExperienceCreate, ExperienceSearch
from interspace.core.knowledge import KnowledgeCreate, ProjectStateUpsert
from interspace.core.qa_models import QARunCreate
from interspace.core.verification import VerificationCreate, VerificationTransition

class InterSpaceConnectionError(RuntimeError):
    """Raised when an agent cannot reach the InterSpace gateway."""

class InterSpaceClient:
    def __init__(self, gateway_url: str, timeout: float = 5.0) -> None:
        self.gateway_url = gateway_url.rstrip("/")
        self.timeout = timeout
    def ping(self): return self._request("GET", "/network/ping")
    def register(self, agent): return self._request("POST", "/agents/register", json=agent.model_dump())
    def heartbeat(self, agent_id, status="online"):
        return self._request("POST", f"/agents/{agent_id}/heartbeat", json=AgentHeartbeat(status=status).model_dump())
    def send_event(self, event_type, payload, agent_id=None):
        return self._request("POST", "/events", json={"event_type":event_type,"agent_id":agent_id,"payload":payload})
    def publish_contract(self, contract): return self._request("POST", "/contracts/publish", json=contract.model_dump())
    def get_contract(self, contract_id, version=None):
        path=f"/contracts/{contract_id}" if version is None else f"/contracts/{contract_id}/versions/{version}"
        return self._request("GET", path)
    def diff_contract(self, contract_id, from_version, to_version):
        return self._request("GET", f"/contracts/{contract_id}/diff", params={"from_version":from_version,"to_version":to_version})
    def subscribe(self, contract_id, agent_id):
        return self._request("POST","/contracts/subscribe",json=ContractSubscriptionCreate(contract_id=contract_id,agent_id=agent_id).model_dump())
    def notifications(self, agent_id, unread_only=False):
        return self._request("GET",f"/agents/{agent_id}/notifications",params={"unread_only":unread_only})
    def acknowledge_notification(self, agent_id, notification_id):
        return self._request("POST",f"/agents/{agent_id}/notifications/{notification_id}/ack")
    def send_message(self, sender_id, recipient_id, message_type, payload):
        return self._request("POST","/messages",json=MessageCreate(sender_id=sender_id,recipient_id=recipient_id,message_type=message_type,payload=payload).model_dump())
    def messages(self, agent_id=None, limit=100):
        return self._request("GET","/messages",params={"agent_id":agent_id,"limit":limit})
    def create_experience(self, experience):
        return self._request("POST","/experiences",json=experience.model_dump())
    def search_experiences(self, query, limit=5):
        return self._request("POST","/experiences/search",json=ExperienceSearch(query=query,limit=limit).model_dump())
    def transition_experience(self, experience_id, transition):
        return self._request("POST",f"/experiences/{experience_id}/transition",json=transition.model_dump())
    def create_verification(self, verification):
        return self._request("POST","/verifications",json=verification.model_dump())
    def transition_verification(self, verification_id, transition):
        return self._request("POST",f"/verifications/{verification_id}/transition",json=transition.model_dump())
    def run_qa(self, requested_by, test_path=None, timeout_seconds=60):
        return self._request("POST","/qa/run",json=QARunCreate(requested_by=requested_by,test_path=test_path,timeout_seconds=timeout_seconds).model_dump())
    def upsert_state(self, state):
        return self._request("POST","/project-state",json=state.model_dump())
    def get_state(self): return self._request("GET","/project-state")
    def create_knowledge(self, knowledge):
        return self._request("POST","/knowledge",json=knowledge.model_dump())
    def get_audit(self, limit=100): return self._request("GET","/audit",params={"limit":limit})
    def _request(self, method, path, **kwargs):
        try:
            response=httpx.request(method,f"{self.gateway_url}{path}",timeout=self.timeout,**kwargs)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError,ValueError) as exc:
            raise InterSpaceConnectionError(f"InterSpace gateway request failed: {method} {path}") from exc
