---
name: autonomous-product-manager
description: "Use when turning a vague product idea into a shippable software product through an AI-assisted product-management loop: requirements discovery, product spec, design brief, prototype handoff, development planning, goal creation, implementation guidance, independent review, release audit, bug iteration, and rule evolution. Trigger for requests such as 'help me build this product', 'write product requirements', 'create a design brief', 'plan development phases', 'write a Go/goal for implementation', 'review this AI-built feature', 'prepare release', 'evolve the workflow from feedback', 'session bootstrap', or '你好 agent' in a product-development workspace."
---

# Autonomous Product Manager

## Overview

Run a lightweight, document-driven product-development loop. Define goals, standards, and acceptance criteria; let the agent choose the exact execution path; keep context stable by updating the core project documents after each phase.

This is an original reconstruction inspired by public descriptions of an autonomous product-manager workflow. Do not copy proprietary skill text; use the framework, document contracts, and acceptance standards below to build your own implementation.

## Core Loop

Follow this default order unless the user's request clearly starts later in the loop:

0. When starting or resuming a product workspace, run the session bootstrap in `references/session-bootstrap.md`.
1. Research existing solutions, official docs, known issues, and technical constraints when the idea involves implementation, APIs, libraries, or non-trivial product risk.
2. Discover requirements one question at a time and write or update `product-spec.md`.
3. Translate product intent into `design-brief.md`.
4. Create or refine visual/prototype direction when needed; prefer Claude Design for prototypes when available.
5. Convert the documents into `development-plan.md` with independently verifiable phases.
6. Write a goal command for the next phase or the whole plan.
7. Implement or guide implementation against the goal.
8. Run independent review and verification before calling work complete.
9. Prepare release notes, privacy/security audit, and handoff.
10. Capture failure signals and evolve rules only from real failures.

## Operating Rules

- Ask questions until vague intent becomes buildable requirements. During intake, ask one question at a time unless the user explicitly asks for a questionnaire. Reject agreeable-but-unclear answers.
- After requirements are collected, write or update the design document before implementation planning. Do not jump from vague idea directly to engineering phases.
- Write standards thickly and procedures lightly. Specify what counts as good, done, unsafe, or unacceptable; leave implementation tactics to the agent.
- Treat documents as the source of continuity. Update them when product, design, plan, or implementation behavior changes.
- Prefer one main agent from start to finish. Use subagents only for independent review, rule evolution, or genuinely parallel work.
- Never mark a phase complete without objective verification: tests, build, visual check, user acceptance criteria, or an explicit documented exception.
- Convert feedback into a rule only when it corresponds to a real failure that would recur if the rule were absent.
- Delete or revise stale rules that no longer protect against actual failure.

Read `references/intake-question-flow.md` for vague ideas or early discovery. Read `references/design-and-prototype-flow.md` before prototype or UI implementation work. Read `references/evolution-loop.md` when there are pending signals or user corrections about the workflow.

## Module Map

Use these reconstructed modules as roles inside one skill or split them into separate skills:

- `product-spec-builder`: interrogate the idea and produce buildable requirements.
- `design-brief-builder`: turn product intent into concrete visual and interaction decisions.
- `design-maker`: create or supervise high-fidelity prototype direction.
- `development-planner`: split work into independently verifiable phases.
- `implementation-builder`: implement the plan while preserving document contracts.
- `reviewer`: independently audit code, tests, UX, and acceptance criteria.
- `release-builder`: audit privacy/security, package, changelog, and release readiness.
- `bugfix-builder`: reproduce, diagnose, fix, and backfill tests for defects.
- `goal-creator`: write a precise execution goal with done criteria and verification.
- `evolution-runner`: digest feedback signals into rule updates.
- `skill-builder`: create or refine reusable domain skills without over-fragmenting tools.

For detailed responsibilities, inputs, outputs, acceptance checks, and red lines, read `references/framework.md`.

## Document Contracts

Create or maintain these files in the project when relevant:

- `research-notes.md`: existing solutions, official docs, known issues, technical constraints, and product implications.
- `product-spec.md`: users, problem, scope, requirements, edge cases, non-goals, acceptance tests.
- `design-brief.md`: product personality, layout density, color/typography decisions, component behavior, accessibility requirements.
- `development-plan.md`: phases, dependencies, technical plan, verification strategy, risks.
- `goals.md`: executable goal prompts for phase work.
- `review-report.md`: independent review findings, tests run, failures, pass/fail decision.
- `release-report.md`: privacy/security checks, packaging state, changelog, deployment notes.
- `change-log.md`: chronological record of product/design/implementation decisions.
- `evolution-signals.md`: raw feedback or failure signals awaiting digestion.
- `claude-design-brief.md`: prototype handoff for Claude Design or another visual design agent when a prototype is needed but cannot be created in the current environment.

Read `references/document-templates.md` before creating a new product workspace or rewriting these files.

When asked to test this skill, create an isolated `skill-test-env/<idea-name>/` workspace, copy or reference the skill under test, write a raw idea file, then generate the core document set and review report before claiming the skill works.

## Goal Shape

When asked to "go", "build", "run the plan", or "write a goal", produce a goal with:

- Objective: one concrete outcome.
- Inputs: documents, prototype, repo state, constraints.
- Scope: what to change and what not to change.
- Acceptance: user-visible behavior and technical requirements.
- Verification: commands, tests, screenshots, review checks, manual checks.
- Loop policy: continue until acceptance passes or a named blocker is reached.
- Reporting: files changed, tests run, unresolved risks.

Use `references/goal-patterns.md` for examples and review heuristics.

## Completion Standard

The work is not done when an artifact merely exists. It is done when the relevant document contract is updated, objective verification has passed, and an independent review or explicit user acceptance says the phase is shippable.
