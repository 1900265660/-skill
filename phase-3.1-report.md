# Phase 3.1 Report

Date: 2026-06-24

## Why This Revision Happened

The first Phase 3 estimate correctly measured extracted text translation cost, but it was too easy to misread as full localization cost. The user pointed out that real cost also includes file modification, image/art work, code/package/tooling work, QA, and time cost.

## Change

`scripts/estimate_cost.py` now separates:

- API text translation cost.
- Project delivery cost.

The project delivery estimate can consume Phase 1 `localization-audit.json` and account for:

- Files to modify.
- Code-like rows.
- Archive/package count.
- Image asset count.
- Font asset count.
- Executable/runtime QA count.
- Human review time.
- Text patching time.
- Image/OCR lane time.
- Font lane time.
- Tooling/code/package lane time.
- QA time.
- Labor cost at a configurable hourly rate.

## Updated Real-Game Results

### Order of the Sinking Star Demo

Text/API estimate:

- Estimated total tokens: 59,729
- Estimated API cost using the Anthropic Haiku example config: `$0.1485`

Project delivery estimate:

- Audited archives: 4
- Audited image assets: 1,232
- Audited font assets: 20
- Text files to modify: 2
- Total delivery time: 37.61-117.95 hours
- Estimated labor cost at `$25/hour`: `$940.25-$2948.75`
- Estimated project total cost: `$940.40-$2948.90`
- Risk level: `MODERATE`

Interpretation:

The extracted text is cheap to send to a model, but image/OCR checking, font verification, package/tooling uncertainty, and QA dominate project cost.

### Tactical Breach Wizards

Text/API estimate:

- Estimated total tokens for the discovered `mission.txt` lane: 2,505
- API cost on manual route: `$0`

Project delivery estimate:

- Audited archives: 178
- Text files to modify: 50
- Code-like rows: 50
- Total delivery time: 45.51-308.83 hours
- Estimated labor cost at `$25/hour`: `$1137.75-$7720.75`
- Risk level: `MODERATE`

Interpretation:

The discovered shallow lane is cheap, but complete Unity localization remains expensive and risky because most content is still behind Unity asset/package tooling.

## Decision

Cost reporting must not collapse full localization into token pricing. Future reports should always show at least two numbers:

- `API/text translation cost`
- `Project delivery cost`
