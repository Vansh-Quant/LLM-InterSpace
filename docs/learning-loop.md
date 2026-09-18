# InterSpace Learning Loop

## 1. Learning vs Memory

InterSpace uses learning in two distinct senses.

### Runtime learning

An agent retrieves an experience created by another agent and uses it to solve a new task.

This does not modify model weights.

### Model learning

Verified experiences are eventually converted into training examples for LoRA, fine-tuning, distillation or evaluation-driven model improvement.

This can modify a model.

The MVP focuses on runtime learning.

## 2. Runtime Learning

    Agent receives task
          |
    Retrieve relevant experiences
          |
    Apply verified knowledge
          |
       Solve task
          |
     Run verification
          |
    Create / update experience
          |
    Store reusable result
          |
    Future agent retrieves it

The collective capability improves because the experience base improves.

## 3. Training Pipeline

Long-term:

    Verified Experiences
            |
      Experience Filter
            |
      Quality Evaluation
            |
      Trajectory Extraction
            |
      Training Dataset
            |
      Model preprocessing
            |
    LoRA / Fine-tuning / Distillation
            |
         Evaluation
            |
     Approved Model Version
            |
       InterSpace Agent
            |
      New Experiences
            |
            +---->

## 4. Experience Filtering

Not every experience should become training data.

Candidate criteria:

- verified result
- reproducible evidence
- clear problem statement
- clear solution
- no unresolved contradiction
- future usefulness
- acceptable provenance
- no sensitive information leakage

## 5. Training Example

A future training item could contain:

    {
      "instruction": "Resolve a frontend failure caused by an API contract change.",
      "context": {
        "old_contract": "...",
        "new_contract": "...",
        "error": "..."
      },
      "trajectory": [
        "identify contract diff",
        "find affected consumer",
        "update consumer",
        "run integration tests"
      ],
      "result": "18/18 tests passed",
      "verification": "integration-test-run-18"
    }

Training data should retain provenance back to the original experience.

## 6. Model Promotion

A fine-tuned model should not automatically replace the current model.

Recommended process:

    Train candidate
         |
      Evaluate
         |
    Compare baseline
         |
      Approval
         |
    Register model version
         |
    Deploy to selected agent

This prevents low-quality experiences from silently degrading the system.

## 7. Hackathon Scope

The 24-hour implementation should demonstrate:

1. verified experience creation
2. experience retrieval
3. reuse by another agent
4. audit trail
5. optional dataset export

Actual fine-tuning is an extension point, not a requirement for the core demo.
