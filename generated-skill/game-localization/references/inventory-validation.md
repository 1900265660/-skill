# Inventory Validation

Run this after `extract_inventory.py` and before cost/provider/patch work.

```bash
python scripts/validate_inventory.py "path/to/translation-inventory.csv" --out "path/to/validation-output" --target-locale s-cn --require-target
```

## What It Checks

- Required inventory columns exist.
- Each unit has a unique `unit_id`.
- Source text is non-empty.
- `protected_tokens` is valid JSON or can be recalculated.
- Existing target text is present when `--require-target` is set.
- Existing target text does not look like mojibake.
- Protected source tokens are preserved in existing target text.
- Existing target does not introduce unexpected token-like syntax.
- Duplicate source groups do not have conflicting target translations without review.
- Target length expansion is flagged as layout risk.

## Severity

- `blocker`: Do not translate, patch, or call providers until fixed.
- `warning`: Review before proceeding; user may accept residual risk.
- `info`: Useful for QA planning but not a hard stop.

## Interpretation

- `PASS`: Inventory is structurally ready for the next phase.
- `PASS_WITH_WARNINGS`: Inventory is usable, but review warnings before translation or patching.
- `BLOCKED`: Fix blockers before any provider call or patch generation.

## Limits

This is structural QA, not literary QA. It cannot judge tone, jokes, character voice, cultural adaptation, or screenshot layout quality.
