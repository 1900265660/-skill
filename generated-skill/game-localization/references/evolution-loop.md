# Evolution Loop

Use this reference when a session starts with pending learning signals, when the user asks the skill to self-improve, or when a session reveals repeated friction that should become a durable rule.

## Principle

Self-evolution is a proposal loop, not an auto-edit loop.

Capture signals, digest them, propose rule changes, ask for approval, then apply approved changes to the right documents.

## Session Bootstrap

At the start of a fresh session on this skill:

1. Read the project rules and state files required by the workspace.
2. Read `PROJECT_STATE.md` and `TODO.md`.
3. Check whether the current thread is skill-adjustment-only or implementation-focused.
4. Check whether an evolution queue exists.
5. If there are no pending signals, continue normally.
6. If pending signals exist, summarize them and run a lightweight digest before unrelated work.

Do not run expensive scans, provider calls, OCR, or broad implementation work during bootstrap.

## Queue Location

Preferred future queue structure:

```text
evolution/
  signals.jsonl
  proposals/
  processed/
```

Create the queue lazily when the first real pending signal needs to be stored.

## Digest Workflow

For each pending signal:

1. Identify the concrete behavior that failed or improved.
2. Decide whether the signal is project-only, skill-level, or global-candidate.
3. Check whether the rule already exists.
4. Classify the change:
   - `ignore`
   - `add`
   - `supplement`
   - `replace`
   - `split`
   - `handoff`
5. Pick the target file.
6. Write a proposal before editing.

## Proposal Requirements

Each proposal should include:

- Signals reviewed.
- Proposed rule.
- Change type.
- Target files.
- Why this belongs there.
- Conflicts or overlap with existing rules.
- Risk and tradeoff.
- One clear confirmation question.

Apply only after user approval.

## Target Selection

Use these targets by default:

- Intake behavior: `references/intake-question-flow.md`
- Design/prototype behavior: `references/design-and-prototype-flow.md`
- Personal-use defaults: `references/personal-use-mode.md`
- Cost/budget behavior: `references/cost-control.md`
- Provider behavior: `references/provider-interface.md`
- OCR behavior: `references/ocr-qa-strategy.md`
- Patch safety: `references/patch-safety.md`
- Cross-cutting durable decisions: project `decisions.md`
- Paused implementation or thread split: handoff files such as `translation-tool-handoff.md`

Update `SKILL.md` only when the rule affects top-level routing or must be discoverable before reading references.

## Approval Rule

Do not silently mutate rules.

User approval is required before:

- Replacing an existing rule.
- Adding a new hard rule.
- Promoting a project-specific preference into a reusable skill rule.
- Changing cost, privacy, file-mutation, provider, OCR, or thread-scope behavior.

Small clarifications to an already-approved rule may be applied with a concise explanation.

## Archive Rule

After applying or rejecting a proposal:

- Mark the signal processed or rejected.
- Record the target file change.
- Keep the reason.
- Do not reprocess the same signal in the next session.

## Clean State

The evolution loop is complete only when:

- Approved proposals have been applied.
- Rejected proposals have a recorded reason.
- Processed signals have moved out of the active queue.
- The active queue contains only unresolved signals.
- `PROJECT_STATE.md` and `TODO.md` reflect any new follow-up work.

After that, continue the session normally.

## Anti-Patterns

Avoid:

- Appending every user comment as a new rule.
- Creating duplicate rules across many files.
- Promoting one project's preference into a global behavior.
- Storing long transcripts when a short paraphrase is enough.
- Running evolution before reading current project state.
- Applying evolution changes during a thread reserved for implementation unless the user asks for skill adjustment.
