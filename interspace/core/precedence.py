from typing import Any

PRECEDENCE = (
    "project_state",
    "project_knowledge",
    "historical_experience",
    "shared_agent_knowledge",
    "foundation_model",
)

def resolve_precedence(
    project_state: list[dict[str, Any]],
    project_knowledge: list[dict[str, Any]],
    historical_experience: list[dict[str, Any]],
    shared_agent_knowledge: list[dict[str, Any]],
    foundation_model: Any = None,
) -> dict[str, Any]:
    sources = {
        "project_state": project_state,
        "project_knowledge": project_knowledge,
        "historical_experience": historical_experience,
        "shared_agent_knowledge": shared_agent_knowledge,
    }
    for source in PRECEDENCE[:-1]:
        if sources[source]:
            return {"source": source, "value": sources[source][0]}
    return {"source": "foundation_model", "value": foundation_model}
