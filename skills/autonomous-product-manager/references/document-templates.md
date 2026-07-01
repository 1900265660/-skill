# Document Templates

## research-notes.md

```markdown
# Research Notes

Research date:

## Existing Solutions

## Official Docs And Technical Constraints

## Known Issues

## Product Implications

## Open Research Questions
```

Quality bar:
- Research must happen before implementation planning when external APIs, libraries, competitors, or known issue risk matter.
- Prefer official docs and active open-source references over generic blog posts.
- Translate research into product implications, not just links.

## product-spec.md

```markdown
# Product Spec

## Summary

## Target Users

## Problem

## Current Workaround

## Desired Outcome

## Core Flows

## Requirements

## Non-Goals

## Data And Permissions

## Integrations

## Edge Cases

## Acceptance Tests

## Open Questions

## Change Log
```

Quality bar:
- A requirement must be testable, observable, or explicitly exploratory.
- Non-goals must be as visible as goals.
- Open questions must not hide blocking ambiguity.

## design-brief.md

```markdown
# Design Brief

## Product Personality

## Audience And Usage Context

## Information Architecture

## Layout Decisions

## Interaction Model

## Visual System

## Components

## States

## Responsive Behavior

## Accessibility

## Design Red Lines

## Change Log
```

Quality bar:
- Replace vague adjectives with concrete design implications.
- Include loading, empty, error, disabled, and success states.
- Specify density and scanning priorities for operational tools.

## development-plan.md

```markdown
# Development Plan

## Current Inputs

## Technical Direction

## Phase Map

### Phase 1: [Name]

Objective:

User-visible result:

Scope:

Dependencies:

Acceptance criteria:

Verification:

Risks:

Review focus:

## Parallel Work

## Risks And Mitigations

## Change Log
```

Quality bar:
- Every phase must have an observable outcome.
- Verification must include exact commands or manual checks where possible.
- Prototype reuse expectations must be explicit.

## claude-design-brief.md

```markdown
# Claude Design Brief

## Product Context

## Target Users

## Key Flow To Prototype

## Required Screens And States

## Interaction Requirements

## Visual Direction

## Accessibility Requirements

## Source Documents

## Non-Goals

## Questions For The Designer
```

Quality bar:
- Use only when a visual or interactive prototype is needed.
- It must be grounded in `product-spec.md` and `design-brief.md`.
- It must state whether Claude Design is expected to create a prototype or whether another agent should use the brief.

## goals.md

```markdown
# Goals

## Goal: [Phase Or Outcome]

Objective:

Inputs:

Scope:

Non-scope:

Acceptance criteria:

Verification:

Loop policy:

Report:
```

Quality bar:
- A goal should be executable without another planning conversation.
- Completion criteria must be falsifiable.

## review-report.md

```markdown
# Review Report

## Scope Reviewed

## Inputs

## Checks Run

## Findings

## Required Fixes

## Residual Risks

## Decision

Pass or fail:
```

Quality bar:
- Findings must point to concrete behavior, files, commands, screenshots, or criteria.
- A failed review must produce actionable fixes.

## release-report.md

```markdown
# Release Report

## Release Scope

## User-Facing Changes

## Verification Summary

## Privacy And Security

## Setup Or Migration

## Known Issues

## Changelog

## Decision
```

Quality bar:
- Privacy and security cannot be left as "not checked".
- Known issues must be explicit.

## evolution-signals.md

```markdown
# Evolution Signals

## Signal: [Short Name]

Source:

What failed:

Why it may recur:

Candidate rule:

Target location:

Decision:
```

Quality bar:
- Keep raw signals until digested.
- Do not add a rule until the failure and target location are clear.
- Mark processed, rejected, or deferred signals so a new session does not digest the same signal repeatedly.
