from typing import Any
import json
import httpx

class OllamaError(RuntimeError): pass

class OllamaModel:
    def __init__(self,model:str,host:str="http://127.0.0.1:11434",timeout:float=120.0):
        self.model=model; self.host=host.rstrip("/"); self.timeout=timeout
    def chat(self,messages:list[dict[str,str]],format_schema:dict[str,Any]|None=None)->dict[str,Any]:
        payload={"model":self.model,"messages":messages,"stream":False}
        if format_schema: payload["format"]=format_schema
        try:
            r=httpx.post(f"{self.host}/api/chat",json=payload,timeout=self.timeout); r.raise_for_status(); return r.json()
        except (httpx.HTTPError,ValueError) as exc: raise OllamaError(f"Ollama request failed for model {self.model}") from exc
    def chat_json(self,messages:list[dict[str,str]],schema:dict[str,Any]|None=None)->dict[str,Any]:
        response=self.chat(messages,schema)
        content=response.get("message",{}).get("content","")
        try: return json.loads(content)
        except (TypeError,ValueError) as exc: raise OllamaError("Ollama returned non-JSON model output") from exc
