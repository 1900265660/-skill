# Phase 5.3 Self-Evolution Report

Date: 2026-06-28

## Scope

Designed and documented a self-evolution/session-bootstrap loop for the `game-localization` skill.

This phase is document-first. It does not add background automation, provider calls, OCR calls, or implementation work.

## Problem

The skill was learning from user corrections manually. When a session ended or context became overloaded, useful learning signals could be lost or handled inconsistently.

The desired behavior is:

```text
session friction -> captured signal -> queued learning item -> digest -> proposal -> user approval -> rule update -> archive
```

## Product Decision

Self-evolution must be proposal-based.

The system may capture and digest signals, but durable rule changes require user approval before editing skill references.

## Files Added Or Updated

- Added `self-evolution-design.md`
- Added `references/evolution-loop.md`
- Added `references/signal-capture-rules.md`
- Updated `SKILL.md`

## Designed Workflow

1. Capture meaningful user corrections, workflow friction, durable constraints, and thread boundary changes as signals.
2. On a fresh session, read project state and check whether pending signals exist.
3. If pending signals exist, digest them before unrelated work.
4. Classify each signal as ignore, add, supplement, replace, split, safety-policy, question-bank, workflow-gate, or handoff.
5. Write an evolution proposal before editing.
6. Ask for user approval.
7. Apply approved changes to the right target file.
8. Archive processed or rejected signals.

## Why Not Fully Automate Yet

The hard part is not file writing. The hard part is deciding:

- Whether a signal is durable.
- Whether it is project-specific or skill-level.
- Whether it conflicts with an existing rule.
- Which file should own it.
- Whether the user approves the behavior change.

Therefore the first version remains document-driven.

## Verification

Docs were inspected after the change.

No runtime validation was needed because this phase only changed markdown instructions.

## Remaining Work

- Decide whether to create the `evolution/` queue immediately or lazily on the first pending signal.
- Forward-test the loop with the known signals:
  - one-question-at-a-time intake
  - design document before new implementation
  - Claude Design first for prototypes
  - current thread is skill-adjustment-only
- Later, optionally add scripts:
  - `capture_signal.py`
  - `prepare_evolution_digest.py`
  - `archive_evolution_signals.py`

## Current Boundary

This thread remains focused on skill adjustment. Translation tool implementation remains paused and should continue through `translation-tool-handoff.md` in a separate conversation.
