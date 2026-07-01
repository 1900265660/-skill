# Design And Prototype Flow

Use this after requirements are collected and before implementation planning for user-facing products, workflows, dashboards, tools, websites, or apps.

## Design Document First

Write or update `design-brief.md` before implementation planning. The design brief should make concrete decisions about:

- information architecture;
- layout density;
- navigation model;
- interaction model;
- visual system;
- components;
- loading, empty, error, disabled, and success states;
- responsive behavior;
- accessibility;
- design red lines.

## Prototype Preference

When a prototype is useful:

1. Prefer Claude Design if it is available in the user's environment.
2. If Claude Design is unavailable, write `claude-design-brief.md` as a handoff.
3. If a code prototype already exists, treat it as reference or source of truth according to `development-plan.md`.
4. After prototype review, update `design-brief.md` with accepted changes before implementation.

## Prototype Acceptance

A prototype is useful only if it shows the key flow and important states. It should not replace the product spec or design brief as the source of truth.

## Red Lines

- Do not skip from vague requirements to engineering tasks.
- Do not call a prototype complete if it only shows a landing page but the product is an operational tool.
- Do not let visual polish hide missing product behavior.
