import re
from typing import Any

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")

def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text) if len(t) > 1}

def score_experience(problem: str, action: str, result: str, query: str) -> float:
    q = _tokens(query)
    if not q:
        return 0.0
    candidate = _tokens(" ".join([problem, action, result]))
    return len(q & candidate) / len(q)

def rank_experiences(rows: list[dict[str, Any]], query: str, limit: int = 5) -> list[dict[str, Any]]:
    ranked = []
    for row in rows:
        score = score_experience(row.get("problem", ""), row.get("action", ""), row.get("result", ""), query)
        if score > 0:
            item = dict(row)
            item["score"] = round(score, 4)
            ranked.append(item)
    ranked.sort(key=lambda x: (-x["score"], x.get("created_at", "")))
    return ranked[:max(1, min(limit, 20))]
