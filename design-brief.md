# Design Brief

## Product Personality

This should feel like a careful localization engineer, not a fast generic translator. The experience should emphasize audit, safety, cost visibility, and reversible changes. The tone should be direct: "I found these text sources, these are safe, these are risky, this will cost roughly X, and these checks passed/failed."

Concrete implications:

- Reports should be structured, scannable, and evidence-backed.
- Risk must be visible before translation starts.
- Cost and time estimates must appear before provider calls.
- Translation changes should be shown as patches/inventories, not hidden behind a single "done" message.
- If the project is not worth translating, the skill should say so plainly and stop at assessment.

## Audience And Usage Context

Users are likely independent fan translation groups, ordinary players, mod authors, or AI-assisted builders. Many will not know the game engine or project structure. They may be working with an installed Steam game folder rather than source code. The skill should work as a document/CLI/report workflow inside Codex or Claude Code before becoming a standalone product.

Primary context:

- A user points the agent at an installed game folder.
- The agent reads files and writes markdown/CSV/patch artifacts.
- The user reviews risk and chooses whether to translate.
- The user expects a reliable rollback path.

## Information Architecture

Recommended generated artifact structure:

- `localization-audit.md`
  - engine detection
  - text source map
  - package/archive risk
  - asset/image text map
  - font/glyph risk
  - launch/build/test commands
  - legal/modding notes
  - cost and time estimate
  - required tools
  - recommendation

- `translation-inventory.csv` or `.json`
  - id
  - source text
  - file path
  - key/context
  - protected tokens
  - confidence
  - translation status

- `glossary.md`
  - names
  - terms
  - tone rules
  - do-not-translate list

- `translation-plan.md`
  - lanes
  - batches
  - provider selection
  - budget
  - estimated time
  - QA checks

- `translation-qa-report.md`
  - validation checks
  - build/test/launch results
  - screenshot/OCR/vision findings
  - screenshot/manual checks
  - unresolved risks

Inside the product-manager test package, these map to `product-spec.md`, `development-plan.md`, `goals.md`, `review-report.md`, `release-report.md`, and `evolution-signals.md`.

## Layout Decisions

For a future UI:

- Use a left-side lane list: Game Audit, Inventory, Translate, Patch, QA, Image Text, Fonts, Cost.
- Use a central table for translatable units with filters: untranslated, high risk, placeholder mismatch, needs context, image text, expensive batch.
- Use a right inspector for selected string context, file location, protected tokens, glossary matches, and translation candidates.
- Use a persistent budget/time bar showing estimated characters, tokens, cost, elapsed time, approved budget, spent cost, and remaining budget.

For a terminal/agent-only skill:

- Use markdown sections with stable headings.
- Use tables for inventories and risk summaries.
- Use explicit PASS/WARN/BLOCKED states.
- Use file paths and commands as monospace literals.

## Interaction Model

- Step 1: Audit only.
  - The skill must not modify files.
  - It asks for target language, permission scope, budget, and whether read-only inspection of the game folder is allowed if missing.
  - It should stop after assessment when risk/cost is not worth continuing.

- Step 2: User approves lane.
  - Safe lanes can proceed.
  - Risky lanes require explicit confirmation.
  - Unsupported lanes become tasks, not hidden omissions.

- Step 3: Dry-run estimate.
  - The skill counts candidate strings and approximate tokens.
  - It deduplicates strings and estimates provider costs and time.

- Step 4: Translate batch.
  - The skill sends only needed text and context.
  - It protects tokens.
  - It records provider/model/MCP used.

- Step 5: Apply and QA.
  - The skill writes a patch by default.
  - It validates syntax, placeholders, encodings, and tests/builds.
  - If possible, it launches the game, captures screenshots, and uses OCR/vision checks for untranslated text.

- Step 6: Revise.
  - Failures return to targeted correction.
  - Safe structural issues may be auto-fixed; unsafe changes should roll back.
  - Real repeated failures become evolution signals.

## Visual System

If implemented as a UI, use a workbench-style system:

- Neutral document background.
- Dense tables.
- Risk colors:
  - Green: safe/proven adapter.
  - Amber: needs review.
  - Red: blocked or likely to break.
  - Blue: informational/cost.
- Monospace for paths, keys, commands, placeholders, and patches.
- No decorative game art unless it is a real screenshot or asset under review.

## Components

- Engine detector summary.
- Text source map.
- Risk matrix.
- Translation inventory table.
- Protected token viewer.
- Glossary editor.
- Provider selector.
- Budget estimator.
- Time estimator.
- Batch progress list.
- Patch preview.
- Rollback status.
- QA checklist.
- Image text task list.
- Screenshot/OCR review summary.
- Evolution signal recorder.

## States

- Loading:
  - Show current scan stage: file tree, engine detection, text candidates, asset candidates, cost estimate.

- Empty:
  - No project path: request path and target language.
  - No text found: show searched patterns and next manual options.

- Error:
  - Parse failure: show file, parser, line/offset if available.
  - Provider failure: preserve untranslated batch and actual cost spent.
  - Build failure: show command and failure summary.

- Disabled:
  - Translate action disabled until audit exists and budget is approved.
  - Apply action disabled when validation fails.

- Success:
  - Show translated units count, skipped units count, patch output path, QA pass count, screenshot/OCR result, and unresolved risks.

- Blocked:
  - Unsupported binary archive, missing permission, missing provider credentials, missing required extraction tool, or anti-cheat/DRM concern.

## Responsive Behavior

For a UI version:

- Desktop-first.
- Tables must support column resizing and horizontal scrolling.
- Mobile is not a core authoring surface; it can show summaries only.

For a skill-only version:

- Markdown files must remain readable in terminals, GitHub, Obsidian, and IDE preview.
- CSV/JSON inventories should be machine-readable and reviewable in spreadsheet tools.

## Accessibility

- Risk states must include text labels, not color only.
- Reports must use semantic headings.
- Tables should avoid relying on emoji or icons alone.
- Long inventories should include summary counts before detail tables.
- Image text tasks should include alt descriptions or OCR excerpts where available.

## Design Red Lines

- Do not present "translation complete" if images, fonts, or runtime screens are unverified.
- Do not hide risky lanes in footnotes.
- Do not make provider calls before budget approval.
- Do not mutate the installed game folder; generate patches by default.
- Do not remove placeholders, tags, or control codes during translation.
- Do not provide modification steps for games with DRM/anti-cheat or unclear permission; keep those outputs high-level.

## Change Log

- 2026-06-21: Initial design brief generated. Defines the skill as an audit-first, risk-visible, budget-aware localization workbench.
- 2026-06-24: Revised after discovery answers. Design now targets a skill-first packaged-game audit/report flow with patch output, cost/time gates, screenshot/OCR QA, and explicit do-not-translate recommendations.
