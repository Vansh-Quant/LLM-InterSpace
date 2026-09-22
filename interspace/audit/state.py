from typing import Literal

VerificationState = Literal[
    "UNVERIFIED", "OBSERVED", "TESTED", "VERIFIED",
    "REUSED", "RECONFIRMED", "REVIEW", "REVISED", "INVALIDATED"
]

ALLOWED_TRANSITIONS = {
    "UNVERIFIED": {"OBSERVED"},
    "OBSERVED": {"TESTED", "REVIEW"},
    "TESTED": {"VERIFIED", "REVIEW"},
    "VERIFIED": {"REUSED", "REVIEW"},
    "REUSED": {"RECONFIRMED", "REVIEW"},
    "RECONFIRMED": set(),
    "REVIEW": {"REVISED", "INVALIDATED"},
    "REVISED": {"TESTED"},
    "INVALIDATED": set(),
}

def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
