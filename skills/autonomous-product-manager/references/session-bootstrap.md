# Session Bootstrap

Use this when a product-development workspace starts or resumes, especially when the user says "hello agent", "你好 agent", "continue", "resume", or asks what the current state is.

## Purpose

Rebuild enough context from durable files so a new session can continue without relying on memory from the previous chat.

## Startup Checks

1. Identify the active product workspace. If unknown, ask for the workspace path before editing.
2. Read durable state files when present:
   - `AGENTS.md`
   - `PROJECT_STATE.md`
   - `TODO.md`
   - `product-spec.md`
   - `design-brief.md`
   - `development-plan.md`
   - `goals.md`
   - `review-report.md`
   - `release-report.md`
   - `change-log.md`
   - `evolution-signals.md`
3. Summarize the current phase, next likely action, blockers, and stale documents.
4. If `evolution-signals.md` contains pending signals, run the evolution loop before new planning work unless the user explicitly asks to skip it.
5. If no pending signals exist, continue from the next documented task.

## Clean-State Rule

A bootstrap is complete only when:

- pending signals are classified as proposed, rejected, deferred, or already covered;
- approved rule changes are applied to the right skill or project document;
- rejected or deferred signals include a reason;
- processed signals are removed from the active queue or marked processed;
- the user can see the next concrete product action.

## Red Lines

- Do not invent missing project state. Mark unknowns and ask the smallest useful question.
- Do not mutate durable rules without user approval.
- Do not continue implementation when the current documents contradict each other; resolve the contradiction first.
