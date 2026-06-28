# Signal Capture Rules

Use this reference when deciding whether a session event should become an evolution signal.

## What Counts As A Signal

Capture a signal when the user:

- Corrects the agent's workflow.
- Says the output missed the point.
- Identifies friction caused by the skill's behavior.
- Adds a durable constraint.
- Changes the operating boundary of the thread.
- Confirms a new process rule.
- Rejects a plan because the skill skipped a required step.

Examples from this project:

- The user said the skill should ask one question at a time instead of sending many intake questions.
- The user said requirements should become a design document before planning implementation.
- The user said prototypes should prefer Claude Design.
- The user said this thread should focus on skill adjustment and pause translation tool implementation.

## What Not To Capture

Do not capture:

- Temporary preferences that only affect the current answer.
- Secrets, API keys, private credentials, or paid provider responses.
- Large transcripts.
- User frustration without a clear actionable behavior.
- Implementation TODOs that belong in `TODO.md`, not the evolution queue.
- Bugs that need immediate fixing rather than durable rule changes.

## Severity

Use:

- `low`: polish or wording improvement.
- `medium`: repeated friction or useful workflow refinement.
- `high`: user correction, safety boundary, spend/privacy issue, or behavior that caused premature/wrong work.

## Scope

Use:

- `thread`: applies only to the current thread.
- `project`: applies to this project/test environment.
- `skill`: should become part of `game-localization`.
- `global-candidate`: may apply to other skills, but needs stronger review before promotion.

Default to the narrowest scope that solves the problem.

## Signal Format

```json
{
  "id": "sig-YYYYMMDD-001",
  "created_at": "YYYY-MM-DD",
  "source": "user_correction",
  "quote": "short evidence quote or paraphrase",
  "observed_problem": "what failed or changed",
  "area": "intake|design|cost|privacy|handoff|qa|provider|ocr|general",
  "severity": "low|medium|high",
  "scope": "thread|project|skill|global-candidate",
  "suggested_target": "references/intake-question-flow.md",
  "status": "pending"
}
```

## Capture Decision

Ask:

1. Would this prevent a repeated mistake?
2. Is it more durable than a one-off preference?
3. Does it belong in a skill reference, project decision, handoff file, or TODO?
4. Is there enough evidence to propose a rule?
5. Can the evidence be stored without exposing private data?

If the answer is unclear, write a short note in the phase report instead of adding a pending signal.

## Privacy Rule

Store the shortest useful evidence.

Prefer paraphrase unless a short direct quote is needed to preserve the exact user constraint.

Never store credentials, keys, private provider output, or unnecessary personal data.

## From Signal To Proposal

Signals should not edit rules directly.

Route them through `references/evolution-loop.md`:

```text
signal -> digest -> proposal -> user approval -> apply -> archive
```
