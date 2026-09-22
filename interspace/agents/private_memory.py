import json
from pathlib import Path
from typing import Any

class PrivateMemory:
    """Local-only agent memory. It is never sent to the shared store automatically."""
    def __init__(self, agent_id: str, root: str = "storage/private"):
        self.path=Path(root)/f"{agent_id}.json"
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if not self.path.exists(): self.path.write_text("[]",encoding="utf-8")
    def load(self) -> list[dict[str,Any]]:
        return json.loads(self.path.read_text(encoding="utf-8"))
    def append(self, record: dict[str,Any]) -> None:
        data=self.load(); data.append(record); self.path.write_text(json.dumps(data,indent=2,sort_keys=True),encoding="utf-8")
