# Autonomous Product Manager Framework

## Core Philosophy

Use a light process with heavy standards:

- Define the goal, output contract, acceptance criteria, and red lines.
- Let the agent plan the detailed route unless the path is fragile or regulated.
- Preserve context through documents, not through a single long conversation.
- Use one main agent by default. Add subagents only where independence or parallelism creates real value.
- Evolve rules from observed failures, not imagined edge cases.

## Reconstructed 11-Module System

### 1. product-spec-builder

Purpose: turn a vague product idea into a buildable product spec.

Inputs:
- User idea, market context, target users, constraints, existing repo or prototype.

Outputs:
- `product-spec.md`
- open questions list
- acceptance-test candidates
- raw evolution signals when the user corrects a question, assumption, or scope choice

Ask about:
- target user and primary job-to-be-done
- pain, current workaround, and success moment
- must-have flows and explicit non-goals
- data inputs/outputs and permissions
- platform, runtime, integrations, and deployment
- privacy, safety, abuse, reliability, and cost constraints
- edge cases, empty states, errors, and recovery
- how the user will judge whether the product is good

Question flow:
- Ask one question at a time during early intake unless the user explicitly asks for a questionnaire.
- Record each useful answer before asking the next question.
- If an answer remains vague, ask a narrower follow-up before planning.

Acceptance:
- A developer can start planning without guessing the core problem, user, scope, flows, or success criteria.
- Each requirement is testable or explicitly marked as exploratory.
- Non-goals and constraints are visible.

Red lines:
- Do not accept flattery, vague adjectives, or "make it better" as requirements.
- Do not hide uncertainty. Mark unknowns and ask or propose assumptions.
- Do not expand scope silently.

### 2. design-brief-builder

Purpose: translate product requirements into design decisions.

Inputs:
- `product-spec.md`
- brand material, target audience, comparable products, accessibility needs

Outputs:
- `design-brief.md`

Decide:
- information density
- navigation model
- layout structure
- visual tone
- color system
- typography
- component behavior
- states: loading, empty, error, disabled, success
- responsive behavior
- accessibility standard

Acceptance:
- The brief contains concrete choices, not only mood words.
- A designer or UI agent can produce screens without inventing the product personality.
- The brief aligns with product flows and constraints.

Red lines:
- Do not use generic "premium, clean, modern" language without concrete implications.
- Do not add decorative complexity that harms the product workflow.
- Do not ignore accessibility, mobile behavior, or data density.

### 3. design-maker

Purpose: create or supervise high-fidelity prototype direction from product and design documents.

Inputs:
- `product-spec.md`
- `design-brief.md`
- existing prototype or design code

Outputs:
- prototype files, design screenshots, or design implementation guidance
- `design-handoff.md` when the prototype is external
- `claude-design-brief.md` when Claude Design should make the prototype but is unavailable in the current environment

Acceptance:
- Key flows have visible screens and states.
- The prototype can be used as implementation input, not just inspiration.
- Deviations from product/design documents are recorded.

Red lines:
- Do not recreate a provided prototype unless explicitly asked.
- Do not skip the design brief before user-facing implementation planning.
- Do not let the prototype become the source of product truth; keep docs updated.

### 4. development-planner

Purpose: split the work into independently verifiable phases.

Inputs:
- product/design documents
- repo inspection
- prototype handoff

Outputs:
- `development-plan.md`

Plan each phase with:
- phase objective
- user-visible result
- dependencies
- implementation areas
- acceptance criteria
- verification commands
- review focus
- rollback or fallback notes

Acceptance:
- Each phase can run, compile, or demonstrate something observable.
- Dependencies and parallelizable work are clear.
- Risks are named before implementation starts.

Red lines:
- Do not create phases that only produce invisible scaffolding unless unavoidable.
- Do not treat static prototype code as production-ready without review.

### 5. implementation-builder

Purpose: implement the next phase against the current documents and goal.

Inputs:
- `development-plan.md`
- current goal
- product/design documents
- repo state

Outputs:
- code changes
- updated documents when decisions change
- test and verification results

Acceptance:
- Implementation satisfies the phase goal.
- Tests/build/checks pass or exceptions are documented.
- Product and design docs still match reality.

Red lines:
- Do not call work complete without verification.
- Do not silently rewrite scope.
- Do not overwrite user changes.

### 6. reviewer

Purpose: independently review a completed implementation phase.

Inputs:
- diff
- goal
- docs
- test output
- app behavior or screenshots when relevant

Outputs:
- `review-report.md`
- pass/fail decision
- required fixes

Review:
- correctness against acceptance criteria
- regression risk
- missing tests
- design fidelity
- accessibility and responsive behavior
- security/privacy concerns
- maintainability

Acceptance:
- Review is performed by an agent or pass that did not write the implementation where possible.
- Findings are specific and reproducible.
- Failed review sends the work back to implementation.

Red lines:
- Do not approve code because it "looks plausible".
- Do not let the builder grade its own work without an independent pass when risk is non-trivial.

### 7. release-builder

Purpose: prepare the product for packaging, deployment, or handoff.

Inputs:
- completed implementation
- review report
- product/design/development documents

Outputs:
- `release-report.md`
- changelog
- packaging/deployment notes
- privacy/security audit notes

Acceptance:
- Release state is explicit: ready, blocked, or partial.
- User-facing changes and known risks are documented.
- Secrets, PII, permissions, and external integrations have been checked.

Red lines:
- Do not release with unknown privacy posture.
- Do not omit migration or setup steps.

### 8. bugfix-builder

Purpose: handle defects through reproduction, diagnosis, fix, and regression protection.

Inputs:
- bug report
- logs/screenshots/repro steps
- current docs and code

Outputs:
- fix
- regression test or documented reason none was added
- updated `change-log.md`
- evolution signal if the bug indicates a reusable workflow failure

Acceptance:
- Bug is reproduced or a credible reason is documented.
- Root cause is named.
- Fix is verified.

Red lines:
- Do not patch symptoms without checking for adjacent failures.
- After two failed fix attempts, stop and research known issues before continuing.

### 9. goal-creator

Purpose: write an execution goal that lets an agent run a phase autonomously.

Inputs:
- development plan
- docs
- repo state
- user priority

Outputs:
- entry in `goals.md` or a standalone goal prompt

Acceptance:
- Goal is specific enough for execution without extra guessing.
- It includes objective, scope, acceptance criteria, verification, loop policy, and reporting requirements.
- It limits changes to the intended phase unless a documented dependency requires otherwise.

Red lines:
- Do not write a goal with fuzzy completion criteria.
- Do not combine unrelated goals if separate verification would be clearer.

### 10. evolution-runner

Purpose: digest feedback signals into durable rule improvements.

Inputs:
- `evolution-signals.md`
- review failures
- bugfix learnings
- user corrections

Outputs:
- proposed edits to question banks, document templates, or operating rules
- cleared signal queue after accepted changes
- rejected or deferred signals with reasons

Acceptance:
- Each new rule maps to a real failure.
- The runner decides whether to add, replace, or delete a rule.
- The rule is placed where it will affect future behavior.
- Durable rule edits require user approval before mutation.

Red lines:
- Do not accumulate rules as a dumping ground.
- Do not convert one-off taste feedback into a universal rule.

### 11. skill-builder

Purpose: create or refine reusable domain skills for the product system.

Inputs:
- repeated workflow need
- observed failures
- existing skill structure

Outputs:
- skill folder or skill update
- concise trigger description
- instructions, references, scripts, or assets as needed

Acceptance:
- The skill states when to use it, what good output means, and what red lines apply.
- It does not over-fragment general AI ability into tiny tools.
- Deterministic or fragile work is moved to scripts when useful.

Red lines:
- Do not create a new skill before the workflow has repeated or is clearly reusable.
- Do not write a procedure manual where standards and examples would work better.

## Agent Dispatch Rule

Default to one main agent. Use a subagent only for:

- independent review after implementation
- parallel research or independent alternatives
- evolution digest of feedback signals
- specialized work where context contamination would reduce quality

Avoid long handoff chains. Documents are the handoff layer.

## Rule Evolution Policy

Create a durable rule only when:

- a real failure occurred
- the failure is likely to recur
- a rule would prevent or expose the failure
- the rule has an owner location

Delete or weaken a rule when:

- it no longer prevents a live failure
- it blocks better model judgment
- it duplicates another rule
- it forces unnecessary ceremony
