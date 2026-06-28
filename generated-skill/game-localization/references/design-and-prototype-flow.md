# Design And Prototype Flow

Use this reference after intake is complete and before implementation, provider wiring, new workflow design, or user-facing prototype work.

## Principle

Requirements collection is not the same as design.

After the intake loop has collected enough information, write a design document before building or planning implementation details. If a prototype is needed, prefer Claude Design for prototype design.

## When This Applies

Use this flow when the task involves:

- Designing a new localization workflow.
- Adding a new lane such as provider translation, OCR QA, screenshot capture, or patch application.
- Creating a user-facing tool, dashboard, wizard, report format, or prototype.
- Turning a vague localization idea into a reusable skill behavior.
- Changing product behavior rather than only fixing a small bug or updating a narrow script.

Skip this flow for:

- Pure read-only audits.
- Running an existing script with already-known inputs.
- Small documentation corrections.
- Focused bug fixes where the intended behavior is already clear.

## Required Design Document

Create or update a design document before implementation.

Recommended filename:

- `design-doc.md` for a standalone product/workflow design.
- `localization-design.md` for a specific game localization run.
- `feature-design.md` for a new skill feature.

The design document should include:

- User goal.
- Target users.
- Current context and known constraints.
- Non-goals.
- Proposed workflow.
- Inputs and outputs.
- Safety and rollback model.
- Cost controls.
- QA/verification plan.
- Open questions.
- Decision needed from the user before implementation.

Keep it practical. Do not turn the design document into a large product spec unless the user asks for one.

## Prototype Rule

If the work needs a prototype, use Claude Design first when available.

Prototype candidates include:

- User-facing app screens.
- Wizard flows.
- Report layouts.
- Review dashboards.
- Translation sample review UI.
- OCR hit review UI.
- Patch apply/rollback UI.

The prototype step should produce one of:

- A Claude Design prototype.
- A `claude-design-brief.md` handoff brief.
- A fallback prototype brief if Claude Design is unavailable.

Do not claim that Claude Design was used unless it actually was.

## Claude Design Brief

When preparing a Claude Design handoff, include:

- Product/workflow name.
- Primary user.
- Main job-to-be-done.
- Screens or states needed.
- Data shown on each screen.
- Actions available to the user.
- Empty/error/loading states.
- Visual tone.
- Constraints from the skill, such as local-first, patch-only output, low-cost mode, no in-place game edits, and budget gates.

## Order Of Operations

1. Finish one-question-at-a-time intake.
2. Summarize collected requirements.
3. Write the design document.
4. Ask for confirmation only if the design changes scope, spend, risk, or user-facing behavior.
5. If a prototype is needed, use Claude Design or write a Claude Design brief.
6. Only then implement scripts, provider adapters, UI, or patch workflows.

## User Confirmation

Ask one question at a time here as well.

Good confirmation:

> I have enough to write the design doc. Should the first prototype be a review dashboard or a command-line report flow?

Avoid:

> Please answer these twelve prototype and implementation questions before I continue.

## Fallback

If Claude Design is unavailable:

- Say so plainly.
- Write `claude-design-brief.md` so the prototype can be generated later.
- Continue with text-based design only when the user approves or the task does not require a visual prototype.
