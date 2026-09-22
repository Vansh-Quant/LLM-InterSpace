from typing import Any
from interspace.agents.models import AgentRegistration
from interspace.communication.client import InterSpaceClient
from interspace.agents.ollama import OllamaModel
from interspace.agents.private_memory import PrivateMemory

class BaseAgent:
    def __init__(self,registration:AgentRegistration,gateway:str,ollama_host:str="http://127.0.0.1:11434"):
        self.registration=registration
        self.client=InterSpaceClient(gateway)
        self.model=OllamaModel(registration.model,ollama_host)
        self.private_memory=PrivateMemory(registration.agent_id)
    def start(self)->dict[str,Any]: return self.client.register(self.registration)
    def heartbeat(self,status="online")->dict[str,Any]: return self.client.heartbeat(self.registration.agent_id,status)
    def send(self,recipient_id,message_type,payload): return self.client.send_message(self.registration.agent_id,recipient_id,message_type,payload)
    def ask(self,messages,schema=None)->dict[str,Any]:
        result=self.model.chat_json(messages,schema); self.private_memory.append({"type":"model_output","payload":result}); return result

class BackendAgent(BaseAgent):
    def publish_contract(self,contract): return self.client.publish_contract(contract)

class FrontendAgent(BaseAgent):
    def subscribe(self,contract_id): return self.client.subscribe(contract_id,self.registration.agent_id)
    def pending_notifications(self): return self.client.notifications(self.registration.agent_id,unread_only=True)

class QAAgent(BaseAgent):
    def run_tests(self,test_path=None,timeout_seconds=60): return self.client.run_qa(self.registration.agent_id,test_path,timeout_seconds)
