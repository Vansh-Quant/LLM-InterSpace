# LLM InterSpace

> **The models stay independent. The experience becomes collective.**

## Phase 0 — Infrastructure

This phase establishes the deterministic foundation for multi-agent coordination.

### Current implementation

- FastAPI gateway
- SQLite shared store
- Agent registration and discovery
- Agent heartbeat/status
- Structured event ingestion
- Automated API tests
- Health endpoint

### Repository layout

```
LLM-InterSpace/
├── interspace/
│   ├── core/
│   ├── agents/
│   ├── communication/
│   ├── audit/
│   └── retrieval/
├── storage/
├── demo/
├── dashboard/
├── tests/
├── main.py
└── requirements.txt
```

## Run locally

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Run tests:

```bash
pytest -q
```

Gateway endpoints:

- `GET /health`
- `POST /agents/register`
- `GET /agents`
- `POST /agents/{agent_id}/heartbeat`
- `POST /events`
- `GET /events`

## Design rule

The LLMs will provide reasoning and proposals. Deterministic InterSpace code will control persistence, validation, state transitions, verification, and audit history.

## Next Phase

After Phase 0 passes its test suite, we will implement contract storage, versioning, and deterministic contract diffing.
