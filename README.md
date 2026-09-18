# LLM InterSpace

> **The models stay independent. The experience becomes collective.**

LLM InterSpace is a local-first, model-agnostic shared interspace for independent LLM agents.

Instead of forcing every agent to rediscover the same project knowledge, InterSpace gives agents a persistent layer where they can share verified knowledge and experiences, communicate across specialized roles, inherit solutions discovered by other agents, detect changes made by other agents, and preserve provenance, verification status, and history.

The foundation models remain independent. InterSpace becomes the layer that makes their project-specific experience collective.

## Why InterSpace?

Most LLM agents operate as isolated sessions. When several agents work on the same software system, an important discovery made by one agent can remain trapped inside that agent's context.

A typical failure looks like this:

1. A backend agent changes an API.
2. A frontend agent still follows the previous contract.
3. Integration breaks.
4. The frontend agent has to rediscover the solution.
5. The useful experience disappears when the task ends.

InterSpace creates a persistent, auditable coordination and experience layer between agents.

## Core Idea

Traditional RAG:

    Task -> Retrieve documents -> LLM -> Answer

InterSpace:

    Local foundation models
             |
        Agent Gateway
             |
      Backend / Frontend / QA Agents
             |
         InterSpace
             |
      Project State
      Knowledge
      Experiences
      Skills
      Failures
      Verified Solutions
      Communication
      Complete History
             |
        Verification
             |
      Reusable Experience
             |
        Future Agents

The important object is not only a document. It is a traceable experience:

    What happened
        -> what was attempted
        -> what failed
        -> what changed
        -> what worked
        -> how it was verified
        -> whether it is reusable

## Design Principles

### Local-first

The MVP is designed around locally runnable models and local project data.

Possible runtimes/models include Ollama, Qwen, Llama, Mistral, Gemma, DeepSeek, Phi, and other compatible local models.

### Model-agnostic

InterSpace should not depend on one foundation model. Different agents can use different local models according to role, latency, or hardware.

### Independent agents

Agents remain specialized and independently executable. A backend agent does not become a frontend agent; verified experiences become available to the wider system.

### Verified memory

Not everything an agent says becomes truth.

    UNVERIFIED
        -> OBSERVED
        -> TESTED
        -> VERIFIED
        -> REUSED
        -> RECONFIRMED

Contradictions can enter REVIEW and become REVISED or INVALIDATED.

### Complete provenance

Important memory should answer:

- Which agent created it?
- What task produced it?
- What evidence supports it?
- What was attempted?
- What failed?
- What verification was performed?
- When was it created?
- Which version is current?
- Was it reused or reconfirmed?

### Project truth has precedence

Recommended precedence:

    1. Current Verified Project State
    2. Project-specific Verified Knowledge
    3. Verified Historical Experiences
    4. Shared Agent Knowledge
    5. External / Reference Knowledge
    6. Foundation-model Knowledge

Project-specific truth therefore wins over stale generic knowledge.

## MVP Demo

Initial backend response:

    {
      "user_id": 42
    }

Frontend expects:

    user.user_id

The backend agent changes the response to:

    {
      "userId": 42
    }

InterSpace then:

1. Detects the contract change.
2. Records Contract V1 -> V2.
3. Identifies the affected frontend consumer.
4. Notifies the frontend agent.
5. Retrieves relevant previous experiences.
6. Lets the agents coordinate.
7. Applies or proposes a repair.
8. Runs QA tests.
9. Records the result.
10. Creates a new verified experience.

Example:

    Experience #048

    Problem:
    Backend renamed user_id -> userId.

    Impact:
    Frontend consumer expected user_id.

    Resolution:
    Updated frontend contract mapping and integration test.

    Verification:
    18/18 tests passed.

    Reusable:
    Yes.

The next similar task can retrieve this experience instead of rediscovering the solution.

## Architecture

    Local Foundation Models
              |
        Agent Gateway
              |
    +---------+---------+
    |         |         |
 Backend  Frontend     QA
 Agent      Agent     Agent
    |         |         |
    +---------+---------+
              |
        +-----+------+
        | InterSpace |
        +------------+
        | Project State
        | Knowledge
        | Experiences
        | Skills
        | Failures
        | Solutions
        | Communication
        | Audit History
        +-----+------+
              |
       Precedence Engine
              |
         Verification
              |
      Reusable Experience
              |
        Training Pipeline

## Memory Architecture

| Layer | Purpose |
|---|---|
| Project State | Current code, contracts, configuration and test state |
| Knowledge | Stable project facts and concepts |
| Experiences | Problem -> action -> result -> verification |
| Skills | Reusable procedures and workflows |
| Failures | Known unsuccessful approaches |
| Verified Solutions | Proven fixes and patterns |
| Communication | Agent-to-agent messages |
| Relationships | Dependencies between agents, components and memories |
| History | Evolution of shared memory |

See docs/memory-model.md.

## Learning Loop

InterSpace distinguishes memory from model training.

Storing an experience does not modify model weights.

Long-term pipeline:

    Verified Experiences
            |
      Experience Filter
            |
     Quality Evaluation
            |
     Training Dataset
            |
    LoRA / Fine-tuning /
       Distillation
            |
      Improved Model
            |
        New Agent
            |
     New Experiences
            |
            +---->

For the hackathon MVP, persistent experience retrieval is the primary learning mechanism.

See docs/learning-loop.md.

## Audit Trail

Every meaningful coordination event should be observable.

Example:

    Backend Agent started task
    API contract modified
    InterSpace detected contract drift
    Frontend dependency identified
    Frontend Agent notified
    Previous experience retrieved
    Patch proposed
    QA started
    18/18 tests passed
    New experience created
    Experience marked VERIFIED

History is part of the product, not merely debug logging.

## Repository Structure

    LLM-InterSpace/
    ├── README.md
    ├── LICENSE
    ├── .gitignore
    ├── requirements.txt
    ├── docs/
    │   ├── architecture.md
    │   ├── memory-model.md
    │   ├── learning-loop.md
    │   └── demo-scenario.md
    ├── interspace/
    │   ├── core/
    │   ├── agents/
    │   ├── communication/
    │   ├── audit/
    │   ├── retrieval/
    │   └── training/
    ├── storage/
    ├── demo/
    ├── dashboard/
    └── tests/

## Proposed Technology Stack

| Layer | MVP Choice |
|---|---|
| Language | Python |
| Local inference | Ollama or compatible runtime |
| API | FastAPI |
| Storage | SQLite |
| Semantic retrieval | Local vector store / embeddings |
| Dashboard | React / Next.js |
| Execution | Sandboxed subprocess / container |
| Testing | pytest |
| Events | Structured JSON |
| Versioning | Git-style memory/event history |

The architecture should remain replaceable and model-agnostic.

## Hackathon Scope

### MUST HAVE

- Local LLM integration
- Backend Agent
- Frontend Agent
- QA Agent
- Unified memory
- Experience records
- Retrieval
- Precedence engine
- Agent communication
- Contract-change detection
- Assisted or automatic patching
- Test execution
- Complete audit trail
- Basic dashboard
- One strong end-to-end demo

### NICE TO HAVE

- Knowledge graph
- Multiple local models
- Memory visualization
- Training dataset export
- LoRA/fine-tuning demonstration

### OUT OF SCOPE FOR MVP

- Training a foundation model from scratch
- Distributed GPU infrastructure
- Large production-scale codebases
- Dozens of autonomous agents
- Unrestricted operating-system control
- Continuous model retraining during every interaction

## Security & Trust

Agents should treat generated information as untrusted until verified.

Core safeguards:

- sandboxed code execution
- allowlisted tools
- structured agent messages
- append-oriented audit events
- verification before promotion to reusable knowledge
- contradiction detection
- memory versioning
- no unrestricted system access

## Roadmap

### Phase 1 — Hackathon MVP

Local agents + shared memory + experiences + audit + contract-drift demo.

### Phase 2 — InterSpace Platform

More agent roles, dependency graphs, stronger retrieval, memory visualization, and project integrations.

### Phase 3 — Collective Learning

Experience filtering, trajectory datasets, evaluation pipelines, LoRA/fine-tuning, and model-specific improvement.

### Phase 4 — InterSpace Ecosystem

Independent local agents and models connect through a common protocol and exchange verified experience while preserving provenance and permissions.

## Vision

The goal is not to create one giant agent.

It is to create an environment where many specialized agents remain independent while continuously benefiting from what the collective has already learned.

**The models stay independent.  
The experience becomes collective.**

## Status

Early-stage / Hackathon build.

The architecture is being implemented incrementally. Features are considered complete only after automated testing and an end-to-end demonstration.

## License

To be decided.
