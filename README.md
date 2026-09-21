# LLM InterSpace

> **The models stay independent. The experience becomes collective.**

## Current build — Gateway + cross-device connectivity

The current `develop` branch is focused on making the InterSpace backend reachable by independent devices before building the dashboard.

### Implemented

- FastAPI gateway
- Central SQLite shared store
- Agent registration and discovery
- Agent heartbeat/status
- Structured event ingestion
- Network ping endpoint
- Python InterSpace HTTP client
- Cross-device network probe
- Automated tests
- Health endpoint

### How the connection works

```text
Device A — InterSpace Gateway
        |
        | HTTP over LAN/Wi-Fi
        |
        +-------------------- Device B — Agent
        |
        +-------------------- Device C — Agent
```

Only the gateway machine owns the SQLite database. Other devices communicate with it through HTTP; they do **not** open the SQLite file directly.

### Run the gateway

On the machine that will host InterSpace:

```bash
python -m venv .venv

# Windows / Git Bash
source .venv/Scripts/activate

python -m pip install -r requirements.txt

# Listen on the local network
uvicorn main:app --host 0.0.0.0 --port 8000
```

Find the gateway machine's LAN IPv4 address:

```powershell
ipconfig
```

Look for the active adapter's `IPv4 Address`, for example:

```text
192.168.1.10
```

From another device on the same Wi-Fi/hotspot, first test:

```text
http://192.168.1.10:8000/network/ping
```

Then, from a second device with the repository and dependencies installed:

```bash
python demo/network_probe.py http://192.168.1.10:8000
```

The probe performs:

1. gateway ping
2. agent registration
3. heartbeat
4. test event

A successful run ends with:

```text
CONNECTION TEST PASSED
```

### Windows firewall

If the second device cannot reach port `8000`, Windows Firewall may be blocking the Python process/port. Allow Python/Uvicorn on the **Private network** when Windows asks, or create an appropriate inbound TCP rule for port `8000`.

Keep the devices on the same trusted LAN/hotspot while testing.

### Gateway endpoints

- `GET /health`
- `GET /network/ping`
- `POST /agents/register`
- `GET /agents`
- `POST /agents/{agent_id}/heartbeat`
- `POST /events`
- `GET /events`

### Tests

```bash
pytest -q
```

## Repository layout

```text
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

## Design rule

The LLMs will provide reasoning and proposals. Deterministic InterSpace code will control persistence, validation, state transitions, verification, and audit history.

## Next backend milestone

With cross-device connectivity proven, implement:

1. Contract storage
2. Contract versioning
3. Deterministic contract diffing
4. Affected-agent detection
5. Structured notifications

The dashboard comes later as a visualization layer over these working backend capabilities.