# LLM InterSpace — Final Architecture

## 1. Vision

> **The models stay independent. The experience becomes collective.**

InterSpace is a local-first, model-agnostic shared memory and communication layer for independent LLM agents.

Each agent keeps its own local model and private reasoning. InterSpace provides the shared layer through which verified contracts, facts, messages, test results, experiences, and audit history become collective.

## 2. Final System Architecture

    Laptop 1                 Laptop 2                 Laptop 3
    Backend Agent             Frontend Agent            QA Agent
    Local Model A             Local Model B             Local Model C
    Private Memory            Private Memory             Private Memory
          \                       |                       /
           \                      |                      /
            +---------------------+---------------------+
                                  |
                         Shared Network / WiFi
                                  |
                         +--------v---------+
                         |  FastAPI Gateway |
                         +--------+---------+
                                  |
                  +---------------+---------------+
                  |               |               |
              SQLite       Precedence Engine  Verification
                  |
        +---------+---------+
        |                   |
   Shared InterSpace     Audit Events
        |
   Project State
   Knowledge
   Experiences
   Communication Log
   History
        |
     Dashboard

### Trust boundary

Raw agent reasoning, drafts, failed attempts, and intermediate steps remain private to the agent.

Only settled, checkable outputs cross into the shared store:

- contract versions
- verified facts
- structured messages
- test results
- experience records
- audit events

## 3. Core Components

| Component | Runs where | Purpose |
|---|---|---|
| Backend Agent | Local machine | Owns backend/API changes |
| Frontend Agent | Local machine | Owns frontend consumers |
| QA Agent | Local machine | Runs tests and verifies fixes |
| FastAPI Gateway | Central host | Network entry point |
| SQLite Store | Central host | Shared InterSpace state |
| Precedence Engine | Central host | Resolves conflicting information |
| Verification Engine | Central host | Promotes evidence-backed results |
| Dashboard | Central host / browser | Live system visibility |

## 4. Core Demo Loop

    Backend changes API
            |
    New contract version
            |
    Deterministic contract diff
            |
    Affected consumer identified
            |
    Frontend Agent notified
            |
    Relevant Experience retrieved
            |
    Frontend proposes patch
            |
    QA executes sandboxed tests
          /   \
       PASS   FAIL
        |       |
     VERIFIED  retry
        |
    New Experience
        |
    Audit updated
        |
    Future agent reuses experience

This is the primary golden path for the hackathon. Additional features must not destabilize it.

## 5. Agent Model

Agents are specialized and independent.

### Backend Agent

- modifies backend code
- owns API contracts
- publishes contract versions
- answers contract questions

### Frontend Agent

- consumes API contracts
- identifies frontend impact
- retrieves relevant experiences
- proposes/applies patches

### QA Agent

- runs tests
- validates proposed fixes
- produces evidence
- supports promotion to VERIFIED

The architecture permits additional roles later.

## 6. Private vs Shared Memory

### Private memory

Local only:

- raw reasoning
- drafts
- failed attempts
- intermediate steps
- temporary context

### Shared InterSpace

Networked:

- project state
- verified knowledge
- contract versions
- experiences
- structured communication
- test results
- audit history

An agent's private reasoning is never copied into the shared store as raw chain-of-thought.

## 7. Contract Drift

For the MVP, contract change detection is deterministic.

    Contract V1 + Contract V2
              |
        Schema / field diff
              |
      Dependency lookup
              |
       Impact identified
              |
       Agent notification

Example:

    user_id -> userId

The LLM reasons about impact and remediation; deterministic tooling establishes what actually changed.

## 8. Communication

Agent communication is structured and auditable.

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

Every important message is logged.

## 9. Memory Lifecycle

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

Contradictions:

    TESTED -> REVIEW -> REVISED
                    -> INVALIDATED

Not every agent statement becomes trusted knowledge.

## 10. Experience Model

An Experience captures:

    Problem
       +
    Context
       +
    Attempts / failures
       +
    Solution
       +
    Evidence
       +
    Verification
       +
    Provenance
       +
    Reusability

Example:

    Experience #048
    Problem: backend changed user_id -> userId
    Resolution: updated frontend consumer
    Evidence: integration tests
    Agents: Backend + Frontend + QA
    Status: VERIFIED
    Reusable: YES

## 11. Retrieval and Precedence

When an agent needs information:

    Current verified project state
              >
    Project-specific verified knowledge
              >
    Verified historical experiences
              >
    Shared agent knowledge
              >
    External reference knowledge
              >
    Foundation-model knowledge

This prevents stale historical or generic model knowledge from overriding current project truth.

## 12. Verification

Verification can use:

- unit tests
- integration tests
- schema validation
- static checks
- reproducible execution
- explicit review

For the demo, patches execute in a sandboxed/allowlisted environment.

Only evidence-backed results should become reusable VERIFIED experiences.

## 13. Audit Trail

The audit log records:

- contract changes
- notifications
- agent messages
- experience retrieval
- patches
- test requests
- test results
- verification changes
- experience creation

The dashboard exposes this timeline live.

## 14. Dashboard

Minimum dashboard panels:

1. Agent status
2. Contract version history
3. Agent-to-agent messages
4. Experience records
5. Verification states
6. Audit timeline
7. Test results

The dashboard is for proving the system visually, not for hiding system behavior.

## 15. Technology Stack

| Layer | Choice |
|---|---|
| Language | Python |
| Local inference | Ollama |
| Model strategy | Different local model per agent where useful |
| Networking/API | FastAPI |
| Shared storage | SQLite |
| Private storage | Local SQLite/JSON |
| Retrieval | Local embeddings/vector store |
| Dashboard | Streamlit initially; React/Next.js only if time permits |
| Execution | Sandboxed subprocess |
| Testing | pytest |
| Events | Structured JSON |
| History | Git-style memory/event history |

## 16. Repository Mapping

    LLM-InterSpace/
    ├── interspace/
    │   ├── core/           # contracts, versioning, precedence
    │   ├── agents/         # backend, frontend, QA
    │   ├── communication/  # messages and notifications
    │   ├── audit/          # events and memory state machine
    │   ├── retrieval/      # experience matching/retrieval
    │   └── training/       # future roadmap only
    ├── storage/            # shared/private SQLite
    ├── demo/               # deterministic demo scenario
    ├── dashboard/          # live dashboard
    ├── tests/              # pytest suite
    └── docs/               # architecture and design

## 17. Scope Rule

### Must work

- local model connection
- three specialized agents
- shared InterSpace store
- contract versioning/diff
- affected-agent notification
- structured communication
- experience creation/retrieval
- QA verification
- audit trail
- live dashboard
- complete end-to-end demo

### Only if stable

- richer semantic retrieval
- multiple model providers/runtimes
- knowledge graph
- dataset export
- additional agent roles

### Future only

- LoRA/fine-tuning
- distributed InterSpace protocol
- cross-project collective memory
- large-scale deployment

## 18. Engineering Rule

The **golden path must be deterministic wherever possible**.

Use deterministic code for:

- contract diffs
- state transitions
- persistence
- permissions
- audit events
- test execution
- verification status

Use LLMs for:

- reasoning
- impact analysis
- natural-language interpretation
- proposing fixes
- agent-specific problem solving

This keeps the system demonstrable, testable, and trustworthy.
