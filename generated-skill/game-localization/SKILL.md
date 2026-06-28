---
name: game-localization
description: Audit packaged video game folders or modding workspaces for localization feasibility, cost, risk, and patch strategy. Use when the user wants to translate or localize a game, inspect an installed game folder, estimate Chinese localization difficulty/cost/time, find text/font/image-text assets, generate a localization plan, prepare a safe patch workflow, or decide whether a packaged game is worth translating. Prioritize read-only assessment for Godot, Ren'Py, generic data-driven games, and unknown engines; do not provide DRM or anti-cheat bypass steps.
---

# Game Localization

## Overview

Run an audit-first localization workflow for packaged games. Start read-only, decide whether the project is worth translating, then proceed only through safe lanes: text inventory, glossary/style draft, cost estimate, patch output, and QA.

This skill defaults to personal-use mode: favor the cheapest reversible next step, usually a small text sample, before any broader translation plan. Do not lead with commercial delivery pricing unless the user explicitly asks for it.

## Intake Rule

When the user's request is vague, ask one question at a time. Do not send a long questionnaire.

Read `references/intake-question-flow.md` before demand collection, especially when the user has only described an idea, does not know the engine, has not provided a game folder, or has not chosen budget/provider/output scope.

Ask the single most important missing question, wait for the answer, then ask the next one. Once the minimum information for the next safe step is available, summarize the collected answers and proceed.

## Design Gate

After requirements are collected, write a design document before implementation or workflow expansion. Read `references/design-and-prototype-flow.md` for this step.

If the work needs a user-facing prototype, prefer Claude Design for prototype design. If Claude Design is unavailable, write a `claude-design-brief.md` handoff and say that the prototype was not generated yet.

## Evolution Rule

When a session starts with pending learning signals, or when the user corrects the skill's workflow, read `references/evolution-loop.md` and `references/signal-capture-rules.md`.

Self-evolution must produce proposals before edits. Do not silently mutate rules. Apply durable skill changes only after user approval, then archive or mark signals as processed.

## Default Workflow

1. Confirm the game folder, target language, and permission scope. If any of these are missing, collect them one at a time using `references/intake-question-flow.md`.
2. For new workflows, provider integrations, UI/report prototypes, or reusable skill behavior changes, write a design document first using `references/design-and-prototype-flow.md`.
3. Run a read-only audit before editing anything:

   ```bash
   python scripts/scan_project.py "path/to/game" --out "path/to/audit-output" --target-language zh-Hans
   ```

4. Read `localization-audit.md` and classify the outcome:
   - `PROCEED`: safe enough for extraction planning.
   - `CAUTION`: feasible, but needs user approval and tool setup.
   - `HIGH_LEVEL_ONLY`: permission, DRM, anti-cheat, or protected-package concern; do not provide modification steps.
   - `DO_NOT_TRANSLATE`: effort/risk is not worth it from available evidence.
5. If the user approves, create a translation inventory and glossary/style draft. For extraction rules, read `references/engine-patterns.md`.
   ```bash
   python scripts/extract_inventory.py "path/to/game" --out "path/to/inventory-output" --source-locale en --target-locale s-cn
   ```
6. Validate the inventory before any provider call:
   ```bash
   python scripts/validate_inventory.py "path/to/translation-inventory.csv" --out "path/to/validation-output" --target-locale s-cn --require-target
   ```
7. Estimate character/token/money/time cost before any provider calls. Read `references/cost-control.md`.
   ```bash
   python scripts/estimate_cost.py "path/to/translation-inventory.csv" --out "path/to/cost-output" --route manual_csv --provider manual_csv --model manual_csv
   ```
8. In personal-use mode, prepare a small sample translation before full-batch work:
   ```bash
   python scripts/prepare_sample_translation.py "path/to/translation-inventory.csv" --out "path/to/sample-output" --sample-size 100 --mode manual
   ```
9. Generate patches by default. Read `references/patch-safety.md`.
   ```bash
   python scripts/generate_patch.py "path/to/game" "path/to/translated-inventory.sample.csv" --out "path/to/patch-output" --target-locale s-cn --require-target
   ```
10. Run static QA first. If image text or untranslated runtime UI is a concern, read `references/ocr-qa-strategy.md` and plan a capped screenshot/OCR QA sample:
   ```bash
   python scripts/plan_ocr_qa.py "path/to/localization-audit.json" --out "path/to/ocr-plan" --screenshots-dir "path/to/screenshots" --sample-size 30
   ```
   Do not run full-asset OCR or paid vision calls before the OCR plan and budget gate.

11. Before adding or changing provider, OCR, screenshot, paid vision, or engine-package adapters, run the fixture smoke harness. Read `references/verification-smoke-harness.md`.
   ```bash
   python scripts/run_fixture_smoke.py
   ```

12. For deterministic provider-like fixture tests, use the mock provider route. Read `references/mock-provider-route.md`.
   ```bash
   python scripts/run_mock_provider.py "path/to/translation-inventory.csv" --out "path/to/provider-output" --cost-json "path/to/cost-estimate.json" --validation-json "path/to/inventory-validation.json"
   ```

## Hard Rules

- Do not mutate the installed game folder during audit.
- Do not unpack or repack binary archives unless a supported tool path is explicitly chosen and the user approves.
- Do not provide DRM bypass, anti-cheat bypass, license circumvention, or executable tampering instructions.
- Do not call a remote model or translation MCP before a dry-run estimate and user budget approval.
- Do not claim localization is complete when image text, fonts, runtime screens, or package formats are unverified.
- Do not remove placeholders, variables, tags, control codes, or line-break-sensitive syntax during translation.
- If the same extraction, patch, or QA failure persists after two attempts, stop and research known engine/tool issues before continuing.

## Lane Model

Use lanes so high-risk work does not block safe work:

- **Audit lane**: engine/package detection, text candidates, fonts, image assets, run/build/test hints, difficulty, cost-effectiveness.
- **Text lane**: safe structured files, scripts, tables, subtitles, dialogue, translation catalogs.
- **Glossary/style lane**: names, terms, tone, do-not-translate list, style profile.
- **Design/prototype lane**: design document after intake; Claude Design first for UI or workflow prototypes.
- **Evolution lane**: capture session signals, digest them into proposals, apply approved rule changes, and archive processed signals.
- **Cost lane**: character counts, token estimates, provider pricing config, time estimate, budget stop.
- **Patch lane**: patch directory or tool-specific patch package; original game stays untouched.
- **Font lane**: CJK glyph coverage, bitmap font/font atlas risk, replacement/subsetting tasks.
- **Image/OCR lane**: plan capped screenshot/image-text checks, choose local OCR tools first, detect likely text-bearing assets, and hand off art edits.
- **QA lane**: static validation, placeholder parity, format validity, launch/screenshot/OCR evidence.

## Resource Guide

- Read `references/engine-patterns.md` when choosing extraction strategy for Godot, Ren'Py, Unity, Unreal, RPG Maker, or unknown engines.
- Read `references/intake-question-flow.md` before asking the user for missing requirements or approvals.
- Read `references/design-and-prototype-flow.md` after requirements are collected and before implementation or prototype work.
- Read `references/evolution-loop.md` when a new session has pending signals, when the user asks for self-evolution, or before applying rule changes from session learnings.
- Read `references/signal-capture-rules.md` when deciding whether a user correction, friction point, or workflow change should become an evolution signal.
- Read `references/personal-use-mode.md` when the user is localizing for themselves, friends, a fan patch, or a small modding group.
- Read `references/engine-field-notes.md` when migrating lessons from previous audits to new engines or games.
- Read `references/localization-risk-rubric.md` when assigning proceed/caution/high-level-only/do-not-translate recommendations.
- Read `references/cost-control.md` before model, MCP, OCR, or vision calls.
- Read `references/provider-interface.md` before adding or wiring any translation provider route.
- Read `references/translation-quality.md` before translating strings or drafting glossary/style guides.
- Read `references/inventory-validation.md` before accepting an inventory for translation/provider calls.
- Read `references/patch-safety.md` before generating patches or rollback plans.
- Read `references/ocr-qa-strategy.md` before screenshot OCR, image text checks, cloud OCR, or vision-model QA.
- Read `references/verification-smoke-harness.md` before adapter implementation or regression checks.
- Read `references/mock-provider-route.md` before deterministic provider-like fixture tests.
- Use `scripts/scan_project.py` for read-only packaged-game audits.
- Use `scripts/extract_inventory.py` for Phase 2 inventory extraction from supported text lanes. It does not translate, patch, or call providers.
- Use `scripts/validate_inventory.py` for Phase 2.5 structural QA. It does not translate, patch, or call providers.
- Use `scripts/estimate_cost.py` for Phase 3 character/token/money/time estimates and provider dry-run plans. It does not call providers. Paid routes require pricing, budget, and approval gates before later translation work.
- Use `scripts/prepare_sample_translation.py` to create a personal-use sample CSV and optional mock translated inventory. It does not call providers.
- Use `scripts/generate_patch.py` to create patch/copy output and static QA reports from a translated inventory. It does not modify the source game folder.
- Use `scripts/plan_ocr_qa.py` to rank screenshots/image candidates and choose a low-cost OCR QA route. It does not run OCR, call providers, or modify the source game folder.
- Use `scripts/run_fixture_smoke.py` to verify the offline fixture chain before and after adding adapters. It does not call providers, run OCR, launch games, or modify the fixture source folder.
- Use `scripts/run_mock_provider.py` to generate deterministic `target_text` outputs and usage logs for fixtures. It does not call providers or OCR services.

## Minimum Demo Target

For the first end-to-end demo, prefer a small Ren'Py fixture or toy project:

1. Audit the folder.
2. Extract `.rpy` dialogue and strings.
3. Estimate cost.
4. Translate through mock/manual provider.
5. Generate a patch.
6. Validate placeholder parity.

Use Godot packaged games as the first real audit priority, but keep Godot patching behind explicit tool selection because `.pck` extraction/repacking can be blocked by custom formats or permissions.

## Personal-Use Default

When the user is a solo hobbyist, mod author, or small friend group, prefer:

1. Sample translation first.
2. Text lane only.
3. Patch-only output.
4. Static QA.
5. Capped screenshot/manual OCR planning only after the sample patch works.
6. Keep full image OCR, deep package tooling, and runtime automation out of the first pass.

When the user later wants to share the workflow, the same defaults remain safe to reuse because they minimize spend and rollback risk.
