# Goal Patterns

## Single-Phase Implementation Goal

```text
Goal: Implement Phase [N]: [name].

Inputs:
- Read product-spec.md, design-brief.md, development-plan.md, and the current repo state.
- Treat any provided prototype as [source of truth / reference only], as stated in development-plan.md.

Scope:
- Implement only the Phase [N] deliverables.
- Update product-spec.md, design-brief.md, development-plan.md, and change-log.md if implementation decisions change the documented product.

Acceptance:
- [User-visible behavior]
- [Technical behavior]
- [Design fidelity]
- [Error/empty/loading states]

Verification:
- Run [commands].
- Inspect [screens/pages/flows].
- Add or update tests for [critical behavior].

Loop policy:
- Continue implementing, testing, and fixing until acceptance passes.
- If the same failure persists after two attempts, stop and research known issues before continuing.
- Stop only for a named blocker that cannot be resolved from local context or research.

Review:
- After implementation, perform an independent review pass and write review-report.md.
- Do not mark the goal complete until review passes or the remaining risk is explicitly accepted.

Report:
- Summarize files changed, tests run, review result, and remaining risks.
```

## Whole-Plan Goal

Use this only when the plan is mature and phases are small enough to verify within one autonomous run.

```text
Goal: Execute the full development plan from development-plan.md.

Inputs:
- product-spec.md
- design-brief.md
- development-plan.md
- existing repo and prototype assets

Execution:
- Work phase by phase in the order specified by development-plan.md.
- For each phase, implement, verify, review, fix, and update documents before moving on.
- Keep phase boundaries visible in change-log.md.

Acceptance:
- Every phase acceptance criterion passes.
- Build/test/lint commands pass or documented exceptions are accepted.
- User-facing flows from product-spec.md are demonstrable.
- Design decisions from design-brief.md are represented in the product.

Verification:
- Run all commands listed in development-plan.md.
- Perform visual or manual checks for the primary flows.
- Produce review-report.md and release-report.md.

Loop policy:
- Iterate until all acceptance criteria pass.
- After two failed attempts on the same issue, stop and research known issues.
- Stop if external credentials, missing assets, or user decisions block progress.

Report:
- Final status by phase.
- Tests and checks run.
- Release readiness.
- Open risks and recommended next goal.
```

## Goal Quality Checklist

- The objective names one concrete outcome.
- Inputs are explicit.
- Scope and non-scope are both present.
- Acceptance criteria can fail.
- Verification is concrete.
- The loop policy tells the agent when to continue and when to stop.
- Reporting requirements keep the user informed without requiring constant supervision.

## Weak Goal Smells

- "Make it better."
- "Finish the app" without a plan.
- "Use best practices" without acceptance criteria.
- No verification commands.
- No limit on scope expansion.
- No policy for repeated failure.
