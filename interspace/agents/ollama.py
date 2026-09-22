from typing import Any
import httpx

class OllamaError(RuntimeError):
    pass

class OllamaModel:
    def __init__(self, model: str, host: str = "http://127.0.0.1:11434", timeout: float = 120.0):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def chat(self, messages: list[dict[str, str]], format_schema: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": self.model, "messages": messages, "stream": False}
        if format_schema:
            payload["format"] = format_schema
        try:
            response = httpx.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaError(f"Ollama request failed for model {self.model}") from exc
