# Phase 2.5 Report

Date: 2026-06-24

## Scope

Implemented structural inventory validation for the local `game-localization` skill.

Purpose:

- Validate extracted inventory before any provider call.
- Catch placeholder/token mismatch risk.
- Catch empty target text, duplicate unit IDs, target mojibake, and wrapper changes.
- Leave literary/style quality for later human review.

## Files Added Or Updated

- Added `scripts/validate_inventory.py`
- Added `references/inventory-validation.md`
- Updated `SKILL.md` with Phase 2.5 usage
- Updated `references/translation-quality.md`

## Verification

Commands run:

- Python syntax compile for `validate_inventory.py`, `extract_inventory.py`, and `scan_project.py`
- `quick_validate.py` for the generated skill
- Inventory validation for:
  - Ren'Py small fixture inventory
  - Generic packaged fixture inventory
  - `Tactical Breach Wizards` inventory
  - `Order of the Sinking Star Demo` inventory

## Results

### Ren'Py small fixture

- Rows: 4
- Blockers: 0
- Warnings: 0
- Decision: `PASS`

### Generic packaged fixture

- Rows: 4
- Blockers: 0
- Warnings: 0
- Decision: `PASS`

### Tactical Breach Wizards

- Rows: 50
- Blockers: 0
- Warnings: 0
- Decision: `PASS`

Interpretation:

The shallow Unity `mission.txt` inventory is structurally clean and ready for later cost/provider dry run. It is still only a small lane, not full localization coverage.

### Order of the Sinking Star Demo

- Rows: 885
- Blockers: 0
- Warnings: 686
- Decision: `PASS_WITH_WARNINGS`

Warnings are expected because the inventory contains many entries with empty existing target text. That means the inventory is useful, but it still needs translation work, choice of source/target pairing, and human review before patching.

## What The Validator Catches

- Missing required columns.
- Duplicate `unit_id`.
- Empty source text.
- Invalid `protected_tokens` JSON.
- Missing existing target text when required.
- Mojibake in existing target text.
- Protected token mismatches.
- Unexpected extra token-like syntax in target.
- Arrow-wrapper changes.
- Linebreak changes.
- Very large length expansion.
- Conflicting targets for duplicate source groups.

## Engine Experience Captured

Phase 2.5 did not add a new engine note, but it confirmed one important migration rule:

- Validation must not treat natural-language translation as a blocker.
- Validation must focus on structure, placeholders, wrappers, and mojibake.

## Remaining Risks

- The validator still does not judge literary quality or screenshot/layout fit.
- A future patch writer must use these findings to block structural failures before file mutation.
- Provider dry runs are still Phase 3 work.

## Recommended Next Goal

Implement Phase 3 cost/provider dry run:

- Read `translation-inventory.csv`.
- Estimate cost/time from actual inventory rows.
- Gate provider calls behind budget approval.
- Keep `validate_inventory.py` as the preflight gate before translation or patching.
