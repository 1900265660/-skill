# Mock Provider Report

Date: 2026-06-28

## Scope

Implemented a deterministic mock provider route for the `game-localization` skill.

This is a local provider-like execution slice for fixtures and gate tests. It writes `target_text` and provider usage logs without calling any remote service.

## Files Added Or Updated

- Added `mock-provider-design.md`
- Added `generated-skill/game-localization/scripts/run_mock_provider.py`
- Added `generated-skill/game-localization/references/mock-provider-route.md`
- Updated `generated-skill/game-localization/SKILL.md`
- Updated `translation-tool-handoff.md`
- Updated project tracking files: `PROJECT_STATE.md`, `TODO.md`, and `decisions.md`

## What The Script Does

`run_mock_provider.py`:

- Reads `translation-inventory.csv`.
- Optionally reads `inventory-validation.json` and `cost-estimate.json`.
- Stops on validation blockers.
- Stops when validation warnings exist unless `--accept-validation-warnings` is supplied.
- Stops when the cost gate is not ready for local/manual-style execution.
- Generates deterministic mock Chinese `target_text`.
- Preserves protected tokens in mock output.
- Writes `translated-inventory.mock.csv`.
- Writes `provider-usage-log.jsonl`.
- Writes `mock-provider-report.md` and `mock-provider-summary.json`.

## Usage Log Contract

Each JSONL record includes:

- `timestamp`
- `provider`
- `model`
- `route`
- `batch_id`
- `unit_ids`
- `row_count`
- `estimated_input_tokens`
- `estimated_output_tokens`
- `estimated_total_cost_usd`
- `actual_input_tokens`
- `actual_output_tokens`
- `actual_total_cost_usd`
- `status`
- `output_path`

## Verification

Commands run:

```powershell
python -m py_compile <all generated-skill/game-localization/scripts/*.py>

python generated-skill\game-localization\scripts\run_mock_provider.py `
  generated-skill\inventory-output\renpy-small\translation-inventory.csv `
  --out generated-skill\provider-output\mock-provider\validation-run `
  --cost-json generated-skill\smoke-output\renpy-small\validation-run\cost\cost-estimate.json `
  --validation-json generated-skill\smoke-output\renpy-small\validation-run\validation\inventory-validation.json

python generated-skill\game-localization\scripts\generate_patch.py `
  generated-skill\game-localization\assets\fixtures\renpy-small `
  generated-skill\provider-output\mock-provider\validation-run\translated-inventory.mock.csv `
  --out generated-skill\provider-output\mock-provider\validation-run\patch `
  --source-locale en `
  --target-locale s-cn `
  --require-target

python generated-skill\game-localization\scripts\run_fixture_smoke.py `
  --out generated-skill\smoke-output\renpy-small\validation-run `
  --overwrite
```

Result:

- Mock provider rows translated: 4
- Batches: 1
- Usage log lines: 1
- Patch files from mock output: 1
- Patch blockers: 0
- Fixture smoke harness decision: `PASS`
- Fixture smoke assertions: 21 passed, 0 failed

Output:

- `E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\provider-output\mock-provider\validation-run\translated-inventory.mock.csv`
- `E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\provider-output\mock-provider\validation-run\provider-usage-log.jsonl`
- `E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\provider-output\mock-provider\validation-run\mock-provider-report.md`

## Remaining Risks

- This is not real translation quality.
- It does not call OpenAI, Anthropic, translation MCPs, local LLMs, OCR engines, cloud OCR, or vision models.
- The usage token counts are deterministic estimates for test plumbing, not provider-reported billing data.
- Real provider adapters still need current pricing config, budget approval, retries, error handling, and provider-specific usage parsing.

## Recommended Next Goal

Design the real provider adapter behind the existing budget gate. Keep it disabled until pricing, budget, provider credentials, and explicit approval are supplied.
