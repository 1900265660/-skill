# Phase 2 Report

Date: 2026-06-24

## Scope

Implemented Phase 2 inventory extraction for the local `game-localization` skill.

Location:

`E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\game-localization`

## Files Added Or Updated

- Added `scripts/extract_inventory.py`
- Added `references/engine-field-notes.md`
- Updated `SKILL.md` with Phase 2 usage
- Updated `references/translation-quality.md`
- Updated `references/engine-field-notes.md` with real audit lessons

## Extractor Capabilities

Supported formats in this phase:

- `.localization`
  - Backtick-prefixed key plus following text block.
  - Supports source/target locale pairing, such as `en.localization` with `s-cn.localization`.
- `.subtitles`
  - `:: block_id` sections.
  - `= speaker time` entries.
  - Supports source/target locale pairing.
- Ren'Py `.rpy`
  - Basic dialogue lines.
  - Basic menu choices.
  - Captures current label as context.
- JSON
  - Recursively extracts string values.
  - Skips obvious technical Unity/package config strings.
- CSV/TSV
  - Uses locale/source/text-style columns when present.
- Unity `mission.txt`
  - Extracts conservative key/value mission fields such as `title` and `description`.

The extractor writes:

- `translation-inventory.csv`
- `translation-inventory.json`
- `inventory-summary.md`
- `glossary.md`
- `skipped-files.json`

## Verification

Commands run:

- Python syntax compile for `scan_project.py` and `extract_inventory.py`.
- `quick_validate.py` for the generated skill.
- Fixture extraction for:
  - Ren'Py small fixture
  - Generic JSON packaged fixture
- Real-game extraction for:
  - `Tactical Breach Wizards`
  - `Order of the Sinking Star Demo`

Results:

- Skill validation: pass.
- Ren'Py fixture: 4 units.
- Generic fixture: 4 units.
- `Tactical Breach Wizards`: 50 units.
- `Order of the Sinking Star Demo`: 885 units.

## Real-Game Findings

### Tactical Breach Wizards

Inventory:

- 50 units.
- Format: `mission-txt`.
- Source characters: 468.
- Duplicate source-text groups: 3.

Interpretation:

The skill found a shallow Unity `StreamingAssets/Levels/*/mission.txt` lane, mostly mission titles. This is useful but does not represent full game localization. Unity `.assets` and other packaged content remain out of scope for Phase 2.

### Order of the Sinking Star Demo

Inventory:

- 885 units.
- Formats:
  - `localization`: 204 units.
  - `subtitles`: 681 units.
- Source characters: 44,480.
- Units with protected tokens: 14.
- Duplicate source-text groups: 11.

Interpretation:

This is the best Phase 3 candidate. It has clear source and target locale files, including existing Simplified Chinese translations. The next useful workflow is quality improvement or retranslation with side-by-side source/target review, not blind first-pass localization.

## Engine Experience Captured

Added `references/engine-field-notes.md` to preserve migration lessons:

- Godot: split PCK detection, extraction tool choice, patch strategy, and runtime QA.
- Ren'Py: good first end-to-end demo target, preserve labels/tags/interpolation.
- Unity: separate shallow `StreamingAssets` text lanes from full `.assets` package work.
- Unreal: keep `.pak` work high-complexity unless modding workflow exists.
- RPG Maker-like: JSON can be favorable but escape codes must be preserved.
- Custom engines: existing locale files are strong green flags; logs/licenses must not drive recommendations.

## Remaining Risks

- Placeholder detection exists but placeholder parity validation is not yet implemented as a separate QA script.
- The glossary draft is heuristic and needs human cleanup.
- JSON extraction is intentionally conservative and may miss custom schemas.
- `Tactical Breach Wizards` full localization remains blocked behind Unity asset tooling.
- No model/MCP calls, patch writer, or OCR/vision QA exists yet.

## Recommended Next Goal

Implement Phase 3 cost/time estimation and provider-interface dry run, or split out a smaller Phase 2.5:

- `validate_inventory.py` for placeholder parity and target-locale mojibake checks.
- Inventory filters for "existing target needs review".
- Cost estimate from actual inventory rather than audit rough count.
