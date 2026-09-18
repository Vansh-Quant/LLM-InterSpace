# InterSpace End-to-End Demo

## Objective

Demonstrate that independent local LLM agents can:

1. work on different parts of the same project
2. detect a change made by another agent
3. communicate about the impact
4. retrieve previous experience
5. repair the integration
6. verify the result
7. preserve the experience for future agents

## Scenario

The project contains a backend and frontend.

### API V1

    {
      "user_id": 42
    }

Frontend code expects:

    user.user_id

The system initially passes all integration tests.

## Step 1 — Backend Agent

The backend agent receives a task that causes the response field to change:

    user_id -> userId

The backend now returns:

    {
      "userId": 42
    }

The backend agent publishes Contract V2.

## Step 2 — InterSpace Detects Drift

The contract auditor compares V1 and V2:

    V1: user_id
    V2: userId

    CHANGE DETECTED

InterSpace checks dependencies and identifies the frontend consumer.

## Step 3 — Frontend Notification

Frontend Agent receives:

    {
      "type": "CONTRACT_CHANGED",
      "contract": "/users/{id}",
      "from": "v1",
      "to": "v2",
      "impact": "frontend consumer may break"
    }

## Step 4 — Experience Retrieval

InterSpace searches previous experiences and finds:

    Experience #031

    Problem:
    API contract changed and frontend consumer failed.

    Resolution:
    Update consumer mapping and integration tests.

    Verification:
    Previously passed integration suite.

    Status:
    VERIFIED

The frontend agent uses this as contextual guidance.

## Step 5 — Agent Coordination

The frontend agent can communicate with the backend agent when clarification is needed.

Example:

    Frontend:
    Confirm whether userId is the new stable response field.

    Backend:
    Confirmed. userId is the V2 contract.

InterSpace records both messages.

## Step 6 — Repair

The frontend agent updates the consumer and submits the patch for verification.

## Step 7 — QA

QA executes the test suite.

    Integration tests
    -----------------
    Passed: 18
    Failed: 0
    Total: 18

    STATUS: VERIFIED

## Step 8 — New Experience

InterSpace creates:

    Experience #048

    Problem:
    Backend contract changed user_id -> userId.

    Action:
    Frontend consumer updated.

    Verification:
    18/18 integration tests passed.

    Agents:
    Backend + Frontend + QA

    Status:
    VERIFIED

    Reusable:
    YES

## Step 9 — Future Task

A later agent encounters a similar contract change.

    New Task
       |
    Retrieve Experience #048
       |
    Apply known procedure
       |
    Verify

This demonstrates collective experience.

## Dashboard View

Recommended panels:

### Agent Activity

    Backend Agent      ACTIVE
    Frontend Agent     WAITING
    QA Agent           IDLE

### Contract History

    API V1
      |
    API V2
      |
    Drift detected
      |
    Frontend notified

### Memory

    Experience #031  VERIFIED
    Experience #048  VERIFIED

### Audit Timeline

    Backend changed contract
    Drift detected
    Frontend notified
    Experience retrieved
    Patch applied
    QA passed
    Experience created

## Demo Success Criteria

Judges should clearly see:

- agents are independent
- agents communicate
- agents share persistent memory
- memory contains experience rather than only documents
- verification determines trust
- history is preserved
- a future agent can reuse a previous solution
- the system remains local-first

The complete flow:

    Problem
      |
    Agent A acts
      |
    Agent B affected
      |
    InterSpace detects
      |
    Agents communicate
      |
    Experience retrieved
      |
    Repair
      |
    QA verification
      |
    New verified experience
      |
    Future agents inherit it
