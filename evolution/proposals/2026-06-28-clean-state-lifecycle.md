# Evolution Proposal: Clean-State Lifecycle

Date: 2026-06-28

## Signals Reviewed

- New-session self-evolution should inspect project docs and queued signals, digest them into proposals, ask for confirmation, apply approved rules, clear processed signals, and return to a clean state.

## Proposed Rule

Clarify that the evolution loop is complete only when processed or rejected signals are archived, the active queue no longer contains already-handled items, and the session can continue from a clean state.

## Change Type

`supplement`

## Target Files

- `generated-skill/game-localization/references/evolution-loop.md`

## Why

The current evolution loop already says to archive processed signals and avoid reprocessing them. The forward-test found the behavior mostly covered, but the video-inspired signal emphasizes a useful product detail: after digestion and approval/rejection, the system should explicitly return to a clean operating state.

This keeps new sessions from repeatedly re-reading the same signals and makes the self-evolution loop feel complete rather than leaving a lingering queue.

## Suggested Patch Concept

Add a short "Clean State" section to `references/evolution-loop.md`:

```markdown
## Clean State

The evolution loop is complete only when:

- Approved proposals have been applied.
- Rejected proposals have a recorded reason.
- Processed signals have moved out of the active queue.
- The active queue contains only unresolved signals.
- `PROJECT_STATE.md` and `TODO.md` reflect any new follow-up work.

After that, continue the session normally.
```

## Risk

Low.

This is a clarification of existing archive behavior, not a new implementation requirement.

## Approval Needed

Yes.

This proposal changes durable skill behavior by making clean-state closure explicit.

## Confirmation Question

Apply this supplement to `references/evolution-loop.md`?
