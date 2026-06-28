# Development Plan

## Current Inputs

- Raw idea: `raw-idea.md`
- Research: `research-notes.md`
- Product spec: `product-spec.md`
- Design brief: `design-brief.md`
- Skill under test: `E:\Projects\chanpin\autonomous-product-manager`

## Technical Direction

Recommended first implementation:

- Build a Codex/Claude Code skill folder named `game-localization`.
- Make the default user path personal-use: cheap sample translation, safe text lane, patch/copy output, and go/no-go before broader work.
- Make v1 an audit-first packaged-game localization workflow.
- Prioritize Godot packaged game detection, while using a small Ren'Py fixture for the first end-to-end translation demo.
- Prefer deterministic scripts for scanning, extraction inventory, placeholder validation, cost estimation, and QA.
- Keep model translation behind interfaces: default prompt/style profile, translation MCP, configured model, local model, or manual CSV handoff.
- Generate patches by default.
- Do not implement DRM bypass, anti-cheat bypass, or unsupported binary patching.

Suggested skill structure:

- `SKILL.md`
- `references/engine-patterns.md`
- `references/localization-risk-rubric.md`
- `references/translation-quality.md`
- `references/cost-control.md`
- `references/patch-safety.md`
- `scripts/scan_project.py`
- `scripts/extract_inventory.py`
- `scripts/estimate_cost.py`
- `scripts/validate_translation.py`

## Phase Map

### Phase 1: Packaged-Game Audit Skill Skeleton

Objective:

Create the skill skeleton and a read-only audit workflow that identifies packaged game type, likely engine, text locations, asset/image candidates, font risk, launch/build/test possibilities, required tools, cost/time factors, and unsupported areas.

User-visible result:

Given an installed game folder path, the skill produces `localization-audit.md` with qualitative difficulty, cost-effectiveness, risk, tool requirements, and recommendation before making changes.

Scope:

- Skill trigger description and operating rules.
- Engine/project pattern reference.
- Read-only scanner script.
- Audit report template.
- Difficulty and cost-effectiveness rubric.
- Safety rules: no mutation, no DRM/anti-cheat bypass.

Dependencies:

- Python or Node runtime for scanner script.
- Sample fixture projects or synthetic test folders.

Acceptance criteria:

- Audit runs without modifying the input project.
- Audit identifies at least generic structured files and common engine markers, with Godot priority.
- Audit reports text lanes, image/asset candidates, font indicators, unknowns, launch/build/test command candidates, and required external tools.
- Audit includes proceed/caution/high-level-only/do-not-translate recommendation.
- Audit estimates rough text volume where readable text exists and reports whether cost estimation is blocked by packaging.

Verification:

- Run scanner against synthetic Godot-like, Ren'Py-like, and generic packaged-game fixtures.
- Confirm file hashes or modification timestamps do not change.
- Inspect generated `localization-audit.md`.

Risks:

- Engine detection may be overconfident.
- Too many false-positive text candidates.

Review focus:

- Read-only safety.
- Clear uncertainty labels.
- Useful risk classification.

### Phase 2: Translation Inventory, Glossary Draft, And Token Protection

Objective:

Extract translatable units from safe structured lanes, draft glossary/style-guide assets, and protect placeholders, markup, escape sequences, and control codes.

User-visible result:

The user receives `translation-inventory.csv/json` plus draft `glossary.md`/style configuration with deduped strings, contexts, protected tokens, and confidence levels.

Scope:

- JSON/YAML/TOML/CSV/plain text/Ren'Py-style extraction where safe.
- Placeholder detector.
- Deduplication.
- Context capture.
- Do-not-translate and glossary support.
- Initial style profile and glossary draft generation.

Dependencies:

- Phase 1 scanner.
- Parser libraries for supported formats.

Acceptance criteria:

- Inventory preserves file path, key/context, source text, protected tokens, and status.
- Duplicate text is translated once but maps back to all locations.
- Placeholder detector catches common patterns such as `{name}`, `%s`, `${var}`, `<tag>`, `\n`, and engine markup.
- Unsupported files are skipped with reasons.
- Draft glossary/style guide is produced and editable by the user.

Verification:

- Unit tests for placeholder detection.
- Fixture extraction tests for JSON, CSV, Ren'Py-like files, and mixed markup strings.
- Manual review of generated inventory.

Risks:

- Extracting prose from code literals may catch non-user-facing strings.
- Placeholder patterns vary by engine.

Review focus:

- False positives/negatives.
- Reversibility.
- Context quality.

### Phase 3: Cost/Time Estimation And Provider Interface

Objective:

Estimate translation cost and time before provider calls and support multiple translation routes through simple interfaces.

User-visible result:

The user sees estimated characters, tokens, money cost, image/OCR/batch cost, and time. They can choose provider/MCP/local/manual mode before translation.

Scope:

- Token estimate by source text, context, glossary, and expected output ratio.
- Character count estimate.
- Time estimate by batch/provider/manual review assumptions.
- Provider pricing config file.
- Budget gate.
- Adapter interface for model, translation MCP, local model, and manual CSV.
- Actual usage logging when provider reports usage.

Dependencies:

- Phase 2 inventory.
- Current provider pricing configured by user or fetched/entered manually.

Acceptance criteria:

- Dry run produces cost estimate without provider calls.
- Translation cannot start when estimate exceeds budget unless user approves.
- Provider calls record model/provider, batch id, estimated cost, actual usage if available.
- Manual CSV flow works without API credentials.
- Estimate reports characters, tokens, money cost, and time.

Verification:

- Unit tests for budget gate.
- Mock provider tests.
- Manual dry run with a small inventory and a deliberately tiny budget.

Risks:

- Provider pricing changes frequently.
- Token estimates are approximate.

Review focus:

- Stop-before-spend behavior.
- Cost transparency.
- No API key leakage.

### Phase 4: Patch Generation And Static QA

Objective:

Generate a patch safely and validate structural correctness.

User-visible result:

The user receives a translated patch plus `translation-qa-report.md`.

Scope:

- Write translated structured files.
- Generate patch output by default.
- Preserve encoding and newline style where practical.
- Validate syntax for supported formats.
- Validate placeholder parity.
- Report missing translations and risky length changes.
- Produce patch/diff summary.
- Support rollback by leaving original game folder untouched.

Dependencies:

- Phase 3 translated inventory.
- Supported format writers.

Acceptance criteria:

- Original project is not modified unless explicitly requested.
- Translated output validates for supported structured formats.
- Placeholder mismatches block release.
- QA report lists passed checks, failed checks, skipped files, and residual risks.
- Auto-fix is limited to safe structural corrections; otherwise the skill reports and rolls back.

Verification:

- Fixture round-trip tests.
- Placeholder mismatch tests.
- Manual diff inspection.

Risks:

- Formatting preservation may vary by parser.
- Code literal patching can be dangerous.

Review focus:

- Source safety.
- Validation completeness.
- Clear failure messages.

### Phase 5: Runtime/Screenshot QA And Image Text Lane

Objective:

Run available launch/build/tests, use screenshots/OCR/vision checks where possible, and create a separate workflow for image/art text localization.

User-visible result:

The user sees which runtime checks passed, which failed, whether screenshots still contain untranslated text, and which image assets need OCR/editing handoff.

Scope:

- Build/test command detection and execution with user approval.
- Launch command detection and screenshot capture where safe.
- OCR/vision-model checks for remaining untranslated UI text.
- Screenshot/manual checklist template.
- OCR candidate list for images.
- Handoff format for image-editing/OCR plugin.
- Evolution signal capture from recurring QA failures.

Dependencies:

- Phase 4 patch/copy.
- Optional OCR/image plugin.
- Runnable project or fixture.

Acceptance criteria:

- If build/test commands exist, the skill can run or list them for approval.
- If launch/screenshot checks are possible, the skill captures evidence and OCR/vision summary.
- If no runnable build exists, runtime verification is marked blocked.
- Image text tasks are listed separately with confidence and proposed handoff.
- QA failures can create evolution signals.

Verification:

- Run against a fixture with fake build/test commands.
- Run image candidate detector on sample assets.
- Inspect QA and release reports.

Risks:

- Running game builds can be slow or environment-specific.
- OCR false positives are likely.

Review focus:

- Honest verification status.
- No false "complete" claims.
- Useful handoff for image text.

## Parallel Work

- Research engine-specific extractors can run alongside Phase 1.
- Translation quality/style guide can be drafted alongside Phase 2.
- Cost provider configs can be maintained separately from core scanner.
- Image/OCR plugin selection can be explored after text-lane MVP is stable.

## Risks And Mitigations

- Risk: Skill damages a project.
  - Mitigation: read-only audit first, patch output by default, require explicit write approval for any direct modification.
- Risk: Translation breaks placeholders or syntax.
  - Mitigation: protected-token extraction, placeholder parity validation, parser round-trip tests.
- Risk: Font/CJK support breaks UI.
  - Mitigation: audit font assets, collect used glyph set, flag font replacement/subsetting task.
- Risk: Cost surprises user.
  - Mitigation: dry-run estimate of characters/tokens/money/time, budget gate, dedupe, batching, actual usage logs.
- Risk: Image text expands scope.
  - Mitigation: separate image lane and require configured OCR/image agent.
- Risk: Legal/modding misuse.
  - Mitigation: permission prompt, no DRM/anti-cheat bypass, source/modding-permitted framing.

## Change Log

- 2026-06-21: Initial development plan generated. Defines a five-phase build from audit-only skill to translation, QA, and image-text handoff.
- 2026-06-24: Revised from discovery answers. Plan now targets packaged games, Godot priority, patch output, cost/time gate, runtime screenshot/OCR QA, and Ren'Py as first end-to-end demo.
- 2026-06-24: Phase 3 implementation now exists: cost/time estimator, provider dry-run plan, external pricing config, and budget gates.
- 2026-06-24: Reframed default posture to low-cost personal-use mode for solo users, friends, and hobby communities.
