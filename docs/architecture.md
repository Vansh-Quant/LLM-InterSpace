# InterSpace Architecture

## 1. Purpose

InterSpace is a coordination and persistent experience layer for independent local LLM agents.

The architecture separates:

1. Foundation-model inference
2. Agent specialization
3. Shared memory
4. Agent communication
5. Verification
6. Audit/history
7. Future training

This separation keeps the system model-agnostic.

## 2. High-Level Architecture

    LOCAL MODEL RUNTIME
            |
      Agent Gateway
            |
    +-------+-------+
    |       |       |
 Backend Frontend  QA
 Agent    Agent   Agent
    |       |       |
    +-------+-------+
            |
       INTERSPACE CORE
            |
    +-------+-------+
    |       |       |
 Memory  Message   Audit
 Store    Bus      Log
    |       |       |
    +-------+-------+
            |
     Retrieval + Precedence
            |
       Verification
            |
     Experience Store
            |
      Training Export

## 3. Agent Gateway

The gateway provides a consistent interface between agents and local models.

Responsibilities:

- select configured local model
- build agent context
- retrieve relevant InterSpace memories
- expose permitted tools
- enforce structured output
- record invocation metadata
- forward messages
- submit candidate knowledge for verification

Agents should not directly manipulate the database.

## 4. Agent Roles

### Backend Agent

Owns backend implementation and API contracts.

Typical operations:

- modify backend code
- update API schema
- explain contract changes
- publish contract versions
- respond to consumer questions

### Frontend Agent

Owns frontend consumers.

Typical operations:

- inspect current contracts
- identify impacted consumers
- retrieve previous solutions
- patch integration code
- report unresolved dependencies

### QA Agent

Acts as an independent verification layer.

Typical operations:

- run tests
- inspect failures
- validate proposed fixes
- produce evidence
- promote experiences to VERIFIED when criteria are met

Additional agents can be added later.

## 5. InterSpace Core

The core provides shared state without merging agent identities.

### Project State

Current files, APIs, contracts, dependencies, configuration and test state.

### Knowledge

Stable project-specific facts.

### Experiences

Historical problem-solving records.

### Skills

Reusable procedures.

### Failures

Known unsuccessful approaches.

### Verified Solutions

Solutions supported by evidence.

### Communication

Structured agent-to-agent messages.

### History

Versioned changes to shared memory.

## 6. Retrieval Flow

    Task
      |
    Identify entities / dependencies
      |
    Retrieve current project state
      |
    Retrieve verified knowledge
      |
    Retrieve relevant experiences
      |
    Rank by relevance + trust + freshness
      |
    Apply precedence
      |
    Build agent context
      |
    Agent acts

Retrieval should prefer information that is relevant, project-specific, verified, evidence-backed and appropriately fresh.

## 7. Precedence Engine

Default precedence:

    1. Current Verified Project State
    2. Project-specific Verified Knowledge
    3. Verified Historical Experiences
    4. Shared Agent Knowledge
    5. External Reference Knowledge
    6. Foundation-model Knowledge

The engine resolves conflicts without treating stale history as current truth.

## 8. Communication Protocol

Agents communicate through structured messages.

Example:

    {
      "message_id": "msg-102",
      "sender": "backend-agent",
      "recipient": "frontend-agent",
      "type": "CONTRACT_CHANGED",
      "task_id": "task-21",
      "from_version": "v1",
      "to_version": "v2",
      "changes": ["user_id -> userId"],
      "requires_action": true
    }

Message types may include:

- TASK_CREATED
- TASK_COMPLETED
- CONTRACT_CHANGED
- DEPENDENCY_IMPACT
- QUESTION
- PROPOSAL
- PATCH_PROPOSED
- TEST_REQUEST
- TEST_RESULT
- EXPERIENCE_CREATED
- VERIFICATION_RESULT
- CONFLICT_DETECTED

## 9. Contract Drift Detection

For the MVP, deterministic comparison is preferred over asking an LLM to decide whether schemas differ.

    Contract V1 + Contract V2
              |
        Deterministic diff
              |
      Changed fields/types
              |
      Dependency lookup
              |
        Potential impact
              |
        Agent notification

The LLM reasons about impact and remediation; deterministic tooling establishes the change.

## 10. Verification

Candidate knowledge should not automatically become trusted memory.

Verification may use:

- unit tests
- integration tests
- schema validation
- static checks
- reproducible execution
- explicit agent review

Evidence-backed results can be promoted to reusable knowledge.

## 11. Audit Architecture

Audit events should be structured and append-oriented.

Example:

    {
      "event_id": "evt-882",
      "timestamp": "2026-09-18T10:02:20Z",
      "type": "CONTRACT_DRIFT_DETECTED",
      "actor": "interspace-auditor",
      "task_id": "task-21",
      "payload": {
        "from": "v1",
        "to": "v2",
        "affected_agent": "frontend-agent"
      }
    }

The audit trail should make the full coordination chain reconstructable.

## 12. Safety Boundary

Agents should operate through controlled tools.

Recommended boundaries:

- allowlisted tools
- sandboxed execution
- repository-scoped file access
- command validation
- test isolation
- structured tool calls
- confirmation for destructive operations when necessary

## 13. Future Distributed Architecture

The hackathon version can run on one machine.

A later architecture can allow:

    Agent A ─┐
    Agent B ─┼── InterSpace Protocol ── Shared / Replicated Memory
    Agent C ─┘

Agents can eventually run on different machines or use different local runtimes without requiring the same foundation model.
