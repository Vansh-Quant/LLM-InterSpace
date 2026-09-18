# InterSpace Memory Model

## Goal

The memory system is the core differentiator of InterSpace.

It should preserve not only what is known, but also how that knowledge was obtained and whether it was verified.

## 1. Memory Categories

### Project State

Current truth: APIs, schemas, files, dependencies, configuration and latest test state.

### Knowledge

Stable project-specific facts and concepts.

### Experience

A complete problem-solving episode:

    Problem -> Attempt -> Failure -> Correction -> Verification -> Reuse

### Skill

A reusable procedure or workflow.

### Failure

A documented unsuccessful approach that future agents should avoid repeating.

### Verified Solution

A solution supported by evidence.

### Communication

Messages exchanged between agents.

### History

Versioned evolution of shared memory.

## 2. Experience Lifecycle

    UNVERIFIED
        |
     OBSERVED
        |
      TESTED
        |
     VERIFIED
        |
      REUSED
        |
   RECONFIRMED

Contradictions can enter:

    REVIEW -> REVISED
          -> INVALIDATED

## 3. Experience Schema

Conceptual schema:

    {
      "id": "exp-048",
      "version": 1,
      "type": "CONTRACT_DRIFT",
      "problem": "Backend renamed user_id to userId",
      "context": {
        "project": "demo-app",
        "endpoint": "/users/{id}"
      },
      "attempts": [
        {
          "description": "Changed frontend consumer",
          "result": "success",
          "evidence": ["test-run-18"]
        }
      ],
      "solution": "Updated consumer contract mapping",
      "agents": [
        "backend-agent",
        "frontend-agent",
        "qa-agent"
      ],
      "status": "VERIFIED",
      "reusable": true,
      "created_at": "...",
      "updated_at": "..."
    }

## 4. Provenance

Minimum provenance:

- creator agent
- task ID
- timestamp
- source artifact
- evidence
- verification method
- current status
- memory version

This lets an agent distinguish verified project experience from an unverified suggestion.

## 5. Confidence

Confidence should not replace evidence.

A possible future model:

    confidence =
      evidence_quality
      * verification_strength
      * project_specificity
      * freshness

The exact scoring algorithm should be implemented only after the core lifecycle works.

## 6. Memory Versioning

Memory should behave similarly to source control:

    exp-048:v1
         |
    exp-048:v2
         |
    exp-048:v3

Each version records what changed and why.

This enables rollback, historical inspection, contradiction analysis and reproducibility.

## 7. Retrieval

A retrieval query should consider:

1. semantic relevance
2. project match
3. component match
4. verification status
5. freshness
6. prior successful reuse

Example:

    "frontend broke after backend API contract change"

Potential results:

- verified contract-drift experience
- known frontend patch procedure
- current API contract
- previous test evidence

Current project state remains authoritative over stale history.

## 8. Promotion Rules

    Agent statement
          |
    Candidate memory
          |
    Evidence attached?
       /        \
     No          Yes
     |            |
 UNVERIFIED    Verification
                  |
               VERIFIED
                  |
               Reusable

The system should never silently turn arbitrary agent output into trusted project truth.

## 9. Contradictions

If an older memory says:

    API uses user_id

while current verified project state says:

    API uses userId

the two should not be presented as equal.

The current project state takes precedence. The older memory remains historically useful but can be marked stale, superseded or invalidated.

## 10. Core Principle

InterSpace memory is not merely things the model remembers.

It is:

    Knowledge
    + Experience
    + Evidence
    + Provenance
    + Verification
    + History
