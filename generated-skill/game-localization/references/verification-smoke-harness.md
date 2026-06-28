# Verification Smoke Harness

Use this before and after adding provider, OCR, screenshot, paid vision, or engine-package adapters.

## Purpose

The fixture smoke harness proves that the current offline safe chain still works:

```bash
python scripts/run_fixture_smoke.py
```

It runs:

1. Python syntax compile.
2. Read-only audit.
3. Inventory extraction.
4. Inventory validation.
5. Manual cost dry-run.
6. Mock sample translation.
7. Patch generation and static QA.
8. OCR QA planning.

## Safety

- No remote provider call.
- No OCR engine call.
- No cloud OCR or vision model call.
- No game launch.
- No fixture source modification.
- Output is written outside the fixture folder.

## Expected Result

The harness writes:

- `fixture-smoke-report.md`
- `fixture-smoke-report.json`

The expected decision is `PASS`.

## When It Fails

Treat failures as blockers for adapter work when:

- Any stage exits nonzero.
- Inventory has no rows.
- Validation has blockers.
- Manual cost gate is not ready.
- Sample target text is empty.
- Patch QA has blockers.
- OCR planning is unexpectedly blocked.
- Fixture source hashes changed.

Fix the failing safe-chain behavior before continuing to provider, OCR, screenshot, paid vision, or Godot package work.
