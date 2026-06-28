# Self-Evolution Session Bootstrap Design

Date: 2026-06-28

## User Goal

Make the skill learn from real session failures without relying on long-lived chat context.

When a new session starts, the agent should quickly reattach to the project, inspect queued learning signals, propose rule updates, and apply approved improvements to the right skill references.

## Target Users

- The skill author refining `game-localization`.
- Future agents opening a fresh session on this skill.
- Personal-use localization users who benefit from better questions, safer defaults, and fewer repeated mistakes.

## Current Context

The project already has:

- `PROJECT_STATE.md` for current status.
- `TODO.md` for next work.
- `decisions.md` for durable decisions.
- Phase reports for completed work.
- `translation-tool-handoff.md` for paused implementation work.
- `references/intake-question-flow.md` for one-question-at-a-time intake.
- `references/design-and-prototype-flow.md` for design/prototype gates.

Current gap:

- Session learning is manual.
- User corrections are handled directly by the active agent.
- There is no queue of unprocessed signals.
- There is no proposal step before editing rules.
- There is no processed-signal archive.

## Non-Goals

- Do not implement background automation in this phase.
- Do not modify provider/OCR/translation implementation work in this thread.
- Do not auto-apply rule changes without user approval.
- Do not create global rules from project-specific signals without classification.
- Do not preserve private user data beyond the minimum signal evidence needed for rule improvement.

## Proposed Workflow

### 1. Capture Signals

During a session, capture signals when the user:

- Corrects the agent's behavior.
- Rejects an output because the workflow was wrong.
- Adds a new durable constraint.
- Identifies a repeated friction point.
- Confirms a new product decision.

Signals should be appended to a pending queue, not immediately treated as rules.

### 2. Bootstrap New Session

At the beginning of a new session, the agent should:

1. Read `AGENTS.md`.
2. Read `PROJECT_STATE.md`.
3. Read `TODO.md`.
4. Read `decisions.md` if decisions affect the current request.
5. Check whether an evolution queue exists.
6. If the queue is empty, continue normally.
7. If pending signals exist, summarize them and offer or run a lightweight evolution digest depending on user intent.

### 3. Digest Signals

The digest step should classify each signal:

- `ignore`: too local, unclear, or already handled.
- `question-bank`: improves future intake questions.
- `rule-supplement`: adds a narrow rule.
- `rule-replacement`: replaces an existing weak/conflicting rule.
- `workflow-gate`: adds or changes a step boundary.
- `safety-policy`: protects spend, privacy, files, or user data.
- `handoff`: belongs in a handoff file, not the skill.

The digest should detect conflicts with existing references before proposing edits.

### 4. Create Proposals

The evolution runner should write proposals before editing skill docs.

Each proposal should include:

- Signals reviewed.
- Proposed rule.
- Change type: add, supplement, replace, split, ignore.
- Target file(s).
- Why this belongs there.
- Risk and tradeoff.
- User confirmation question.

### 5. Apply Approved Changes

Only after user approval:

1. Update the target skill references or project docs.
2. Add a decision when the rule is durable.
3. Archive processed signals.
4. Update `PROJECT_STATE.md` and `TODO.md`.

### 6. Archive Signals

Processed signals should move out of the active queue so future sessions do not reprocess them.

Rejected proposals should also be archived with the rejection reason.

## Suggested File Structure

Inside the skill folder:

```text
game-localization/
  references/
    evolution-loop.md
    signal-capture-rules.md
  evolution/
    signals.jsonl
    proposals/
    processed/
```

For the current phase, references are enough. The `evolution/` queue can be created when the first real signal needs to be stored.

## Signal Schema

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

## Proposal Schema

```markdown
# Evolution Proposal

## Signals Reviewed

- sig-YYYYMMDD-001

## Proposed Rule

...

## Change Type

add | supplement | replace | split | ignore

## Target Files

- references/...

## Why

...

## Risk

...

## Confirmation

Apply this proposal?
```

## Safety And Privacy

- Store the shortest useful evidence.
- Prefer paraphrase over long direct transcript.
- Do not store secrets, API keys, private paths beyond what is needed, or paid provider outputs.
- Do not auto-promote project-specific preferences to global rules.
- Do not apply proposals without user approval.

## Cost Controls

The first version should be file-based and manual:

- No background process.
- No remote model calls.
- No automatic subagent unless the user approves or the current environment clearly supports it safely.
- No heavy scans on every session start.

## QA And Verification Plan

Test with three known signals from this project:

1. Vague requirements should be clarified one question at a time.
2. Requirements collection should lead to a design document before new implementation.
3. Translation tool implementation should be split into a separate thread when the current thread is skill-only.

Expected result:

- Each signal maps to a target reference or project doc.
- No duplicate rule is proposed if the rule already exists.
- The proposal identifies whether to add, supplement, replace, or ignore.
- Processed signals are not reprocessed.

## Open Questions

- Should the queue live inside the skill folder or at project root?
- Should each signal require explicit user confirmation before being written to the queue?
- Should future implementation use a script or remain document-driven?
- Should subagent evolution digest be optional, required, or only used for larger batches?

## Decision Needed Before Implementation

Approve Phase 5.3 as a document-first self-evolution loop:

- Add evolution references now.
- Keep queue creation lazy until first real queued signal.
- Keep proposal application user-approved.
- Defer scripts until the workflow has been tested manually.
