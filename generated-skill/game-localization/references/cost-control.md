# Cost Control

Estimate cost before provider calls. If pricing is unknown, report character/token counts and ask the user to provide pricing or provider choice.

For personal-use mode, always lead with the smallest reversible next step. Avoid surfacing commercial delivery pricing unless the user asks for a service-style estimate.

## Estimate Inputs

- Source characters.
- Estimated input tokens.
- Estimated output tokens.
- Context overhead per batch.
- Glossary/style prompt size.
- Number of unique strings after dedupe.
- Number of OCR/vision images or screenshots.
- OCR route: manual review, local OCR, cloud OCR, or vision model.
- Number of files that may need patch output.
- Number of image assets that need OCR sampling or art edits.
- Font asset count and CJK glyph risk.
- Archive/package/tooling risk.
- Static QA and runtime QA effort.
- Provider prices.
- Expected manual review speed.
- Human labor rate or local equivalent.

## Phase 3 Command

Run a dry-run estimate from a Phase 2 inventory:

```bash
python scripts/estimate_cost.py "path/to/translation-inventory.csv" --out "path/to/cost-output" --route manual_csv --provider manual_csv --model manual_csv
```

For paid routes, supply a pricing config and budget:

```bash
python scripts/estimate_cost.py "path/to/translation-inventory.csv" --out "path/to/cost-output" --route external_model --provider example_paid_provider --model example_model --pricing-config assets/provider-pricing.example.json --budget-usd 5 --approve-budget
```

The bundled `assets/provider-pricing.example.json` is a test fixture, not authoritative pricing. Replace it with current official provider pricing before paid work.

When Phase 1 audit output exists, include it:

```bash
python scripts/estimate_cost.py "path/to/translation-inventory.csv" --out "path/to/cost-output" --audit-json "path/to/localization-audit.json" --route manual_csv --provider manual_csv --model manual_csv
```

## Controls

- Dedupe identical source strings.
- Batch small strings with IDs and protected tokens.
- Send only necessary context.
- Cache translations and glossary decisions.
- Stop before budget is exceeded.
- Log estimated and actual usage.
- Keep manual CSV export as a zero-API fallback.
- Keep manual screenshot review and local OCR as zero-API visual QA fallbacks.
- Cap OCR/vision samples before any full image sweep.
- Prefer screenshots over raw asset OCR when checking player-visible untranslated text.
- Separate translation API cost from total localization delivery cost.
- Treat package files, code-like files, image/OCR lanes, fonts, and QA as project labor/risk costs even when API cost is low.

## Budget Gate

Paid provider calls remain blocked unless all of these are true:

- Inventory validation has no blockers.
- Validation warnings are reviewed or explicitly accepted.
- Provider pricing is known.
- A budget is supplied.
- The estimate is within budget.
- The user explicitly approves the budget.

`estimate_cost.py` only produces dry-run artifacts. A future translation adapter must read the gate decision before making any provider call.

## Personal-Use Quote Rule

When the user is translating for themselves or a small group, quote in this order:

1. Sample cost.
2. Text-lane cost.
3. Optional font/basic QA additions.
4. Optional screenshot/OCR sample cost.
5. Only then, if asked, a full project delivery estimate.

The default user-facing message should emphasize that the first pass is meant to be cheap and reversible.

## OCR Cost Rule

OCR cost is controlled separately from text translation cost.

Default order:

1. Manual screenshot review: zero API spend.
2. Local OCR sample: zero API spend after setup.
3. Cloud OCR sample: paid per image/page/transaction; verify current official pricing first.
4. Vision model sample: paid by provider-specific image/token rules; use only for hard cases.

Never assume OCR is cheap because text token cost is cheap. For games, the expensive part is often sorting useful screenshots from noisy assets and fixing art-text manually.

## Time Estimate

Report ranges:

- Audit time.
- Extraction time.
- Translation provider time.
- Human review time.
- Text file edit/patch time.
- Tooling/code/package time.
- QA time.
- Image/font lane time if needed.

For first-pass rough estimates, use character count and string count. Mark estimates as approximate until real provider usage is known.

## Interpretation Rule

Do not present token/API cost as the full localization cost. Token cost answers "what would the model call roughly cost for extracted text?" Full project cost must also include:

- Modifying or generating files/patches.
- Code-like string risk and parser/writer work.
- Package extraction/repacking research.
- Image OCR and possible art edits.
- Font support work.
- Static QA, runtime QA, screenshot/OCR QA, and rollback checks.
- Human review for terms, style, jokes, UI length, and bug reports.

## Outputs

The dry run writes:

- `cost-estimate.md`
- `cost-estimate.json`
- `provider-dry-run.json`
- `provider-batches.csv`
- `provider-usage-log.jsonl`
