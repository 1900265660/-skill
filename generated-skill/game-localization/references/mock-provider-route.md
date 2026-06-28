# Mock Provider Route

Use this route when you need a deterministic provider-like execution slice for fixtures or budget-gate tests.

## Command

```bash
python scripts/run_mock_provider.py "path/to/translation-inventory.csv" --out "path/to/provider-output" --cost-json "path/to/cost-estimate.json" --validation-json "path/to/inventory-validation.json"
```

## Behavior

- Reads inventory rows and writes `target_text`.
- Preserves protected tokens and placeholders.
- Writes `translated-inventory.mock.csv`.
- Writes `provider-usage-log.jsonl`.
- Writes a short report and summary JSON.
- Does not call any remote service.

## Gate Use

- If `inventory-validation.json` has blockers, the route stops.
- If the cost gate is not `READY_FOR_LOCAL_OR_MANUAL_STEP` or `CAUTION_PENDING_WARNING_ACCEPTANCE`, the route stops.
- Warning acceptance is required when validation warnings are present.

## Expected Log Fields

Each JSONL usage line includes:

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

Use the current fixture smoke harness before and after adding real provider adapters. After running the mock provider route, feed `translated-inventory.mock.csv` into `generate_patch.py` to confirm the route satisfies the `target_text` contract.
