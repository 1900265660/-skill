# Phase 3 Report

Date: 2026-06-24

## Scope

Implemented cost/time estimation and provider dry-run planning for the local `game-localization` skill.

Purpose:

- Estimate characters, tokens, money, batches, and review time from actual `translation-inventory.csv` rows.
- Support manual, mock/local, and remote provider planning without calling providers.
- Enforce a budget gate before any future paid translation route.
- Keep price configuration external because provider pricing changes over time.

## Files Added Or Updated

- Added `scripts/estimate_cost.py`
- Added `assets/provider-pricing.example.json`
- Added `references/provider-interface.md`
- Updated `SKILL.md`
- Updated `references/cost-control.md`

## Implementation Notes

`estimate_cost.py` reads a Phase 2 inventory and writes:

- `cost-estimate.md`
- `cost-estimate.json`
- `provider-dry-run.json`
- `provider-batches.csv`
- `provider-usage-log.jsonl`

The script supports:

- Scope selection: all rows, missing-target rows, or existing-target review rows.
- Deduplication by `group_id` or normalized source text.
- Batch planning with source character totals and format mix.
- Approximate input/output token estimation.
- Provider pricing from JSON config.
- Manual CSV and mock zero-cost routes.
- Paid-route gates for validation, warnings, known pricing, budget, and explicit budget approval.

It does not:

- Translate text.
- Call OpenAI, Anthropic, MCP servers, local models, OCR, or vision services.
- Write patches.
- Modify game folders.

## Verification

Commands run:

- Python syntax compile for `estimate_cost.py`
- Manual CSV dry run for `Order of the Sinking Star Demo`
- Manual CSV dry run for `Tactical Breach Wizards`
- OpenAI-style route with unknown pricing to verify `BLOCKED_UNKNOWN_PRICE`
- Anthropic Haiku-style route with known pricing, budget, approval, and accepted warnings to verify `READY_FOR_USER_APPROVED_PROVIDER_STEP`
- Deliberately tiny budget run to verify `BLOCKED_BUDGET_EXCEEDED`

## Real-Game Results

### Order of the Sinking Star Demo

Inventory:

- Rows: 885
- Unique translation units after dedupe: 871
- Source characters in scope: 44,480
- Deduped source characters: 44,361
- Batches: 11

Token/time estimate:

- Estimated input tokens: 37,548
- Estimated output tokens: 22,181
- Estimated total tokens: 59,729
- Provider/runtime time: 3.3-13.2 minutes
- Human review time: 17.74-36.97 hours

Budget-gate checks:

- Manual CSV without accepted validation warnings: `CAUTION_PENDING_WARNING_ACCEPTANCE`
- Manual CSV with accepted validation warnings: `READY_FOR_LOCAL_OR_MANUAL_STEP`
- OpenAI-style route with missing current price: `BLOCKED_UNKNOWN_PRICE`
- Anthropic Haiku-style route with $0.20 budget and explicit approval: `READY_FOR_USER_APPROVED_PROVIDER_STEP`
- Tiny $0.01 budget route: `BLOCKED_BUDGET_EXCEEDED`

Anthropic Haiku-style money estimate using the bundled example config:

- Estimated total cost: `$0.1485`

This is only a planning estimate. It still needs current official pricing verification before any paid run.

### Tactical Breach Wizards

Inventory:

- Rows: 50
- Unique translation units after dedupe: 41
- Source characters in scope: 468
- Deduped source characters: 396
- Batches: 1

Token/time estimate:

- Estimated input tokens: 2,307
- Estimated output tokens: 198
- Estimated total tokens: 2,505
- Human review time: 0.16-0.33 hours

Gate:

- Manual CSV route: `READY_FOR_LOCAL_OR_MANUAL_STEP`

Interpretation remains unchanged from Phase 2.5: this is only a shallow Unity `mission.txt` lane, not full localization coverage.

## Research Notes

Before implementation, provider-pricing and token-counting guidance was checked. Anthropic's official pricing and token-counting docs confirm that pricing is per million tokens and token counts can vary by model/tokenizer. OpenAI pricing could not be reliably verified through the available search results in this run, so the OpenAI entry in the example config intentionally uses null prices and blocks paid calls until the user fills current official pricing.

Relevant references used:

- Anthropic pricing docs: `https://docs.anthropic.com/en/docs/about-claude/pricing`
- Anthropic token counting docs: `https://docs.anthropic.com/en/docs/build-with-claude/token-counting`
- OpenAI pricing page to verify manually before use: `https://openai.com/pricing`

## Remaining Risks

- Token estimates are approximate until a real provider tokenizer or usage report is used.
- Translation quality and style are still human-review responsibilities.
- Remote provider adapters are not implemented yet.
- Usage logging exists as an empty output file but no actual usage is recorded because no provider call is made.
- OCR/image/vision costs are only represented as a configurable image-count estimate.
- Existing validation warnings for `Order of the Sinking Star Demo` still require explicit acceptance before translation.

## Recommended Next Goal

Implement Phase 4 patch generation and static QA:

- Consume translated inventory from manual/mock route.
- Generate patch output instead of mutating the game folder.
- Block patch generation on validation blockers or placeholder mismatches.
- Produce a patch manifest and translation QA report.
