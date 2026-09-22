from typing import Any
import httpx

class OllamaEmbeddingError(RuntimeError): pass

class OllamaEmbedder:
    def __init__(self, model="nomic-embed-text", host="http://127.0.0.1:11434", timeout=60.0):
        self.model=model; self.host=host.rstrip("/"); self.timeout=timeout
    def embed(self, text: str) -> list[float]:
        try:
            r=httpx.post(f"{self.host}/api/embed",json={"model":self.model,"input":text},timeout=self.timeout)
            r.raise_for_status(); data=r.json()
            if "embeddings" in data: return data["embeddings"][0]
            if "embedding" in data: return data["embedding"]
            raise OllamaEmbeddingError("Ollama returned no embedding")
        except (httpx.HTTPError,ValueError,KeyError,IndexError) as exc:
            raise OllamaEmbeddingError("Embedding request failed") from exc
