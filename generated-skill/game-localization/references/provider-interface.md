# Provider Interface

Phase 3 keeps translation routes behind a simple planning contract. The skill does not call any remote provider during dry run.

## Route Types

- `manual_csv`: export the inventory for human review or a separate offline workflow.
- `mock_model`: deterministic test route for fixtures and budget-gate tests.
- `local_model`: local inference route with user-owned compute.
- `external_model`: paid remote model route.
- `translation_mcp`: translation service or MCP-backed route.
- `openai`: provider namespace used in the pricing config.
- `anthropic`: provider namespace used in the pricing config.

## Required Planning Fields

Any translation adapter should be able to derive or receive:

- `provider`
- `model`
- `route`
- `batch_id`
- `unit_ids`
- `source_text`
- `context`
- `speaker`
- `protected_tokens`
- `style_profile`
- `glossary`
- `budget_usd`
- `estimated_input_tokens`
- `estimated_output_tokens`
- `estimated_total_cost_usd`

## Minimum Adapter Contract

An adapter must expose these behaviors:

1. `plan_batches(...)` to group rows before translation.
2. `estimate_usage(...)` to compute an in-memory dry run.
3. `can_proceed(...)` to enforce the validation/budget gate.
4. `translate_batch(...)` only after gate approval.
5. `record_usage(...)` when actual token usage is returned.
6. `write_manual_export(...)` for the zero-API fallback.

## Gate Order

1. Inventory validation.
2. Budget estimate.
3. User budget approval.
4. Provider route selection.
5. Translation execution.
6. Usage logging.

If a route is paid, the adapter must not call the provider until the dry run and budget approval are complete.
