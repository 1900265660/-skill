# Mock Provider Design

Date: 2026-06-28

## User Goal

Add a deterministic provider-like execution route for fixtures and budget-gate tests that writes `target_text` and records usage logs without calling any remote service.

## Current Context

The skill already has:

- inventory extraction
- inventory validation
- cost estimation and budget gates
- sample translation packaging
- patch generation
- fixture smoke harness

What is missing is a small execution slice that behaves like a provider adapter, consumes the existing gate/planning contract, and writes a translated inventory plus usage records.

## Non-Goals

- Do not call OpenAI, Anthropic, translation MCPs, local LLMs, OCR engines, cloud OCR, or vision models.
- Do not require network access.
- Do not change the existing budget gate rules.
- Do not implement literary-quality translation.
- Do not modify source game folders.

## Proposed Workflow

Create a new script, `scripts/run_mock_provider.py`, that:

1. Reads `translation-inventory.csv`.
2. Optionally reads `cost-estimate.json` and `inventory-validation.json`.
3. Builds batches using the same planning spirit as `estimate_cost.py`.
4. Generates deterministic mock translations into `target_text`.
5. Writes `translated-inventory.mock.csv`.
6. Writes `provider-usage-log.jsonl`.
7. Writes a brief report describing what was translated and what gate was observed.

## Mock Translation Behavior

The route should be deterministic and conservative:

- Preserve placeholders and protected tokens exactly.
- Preserve empty strings as empty if the row is blank.
- For simple strings, produce a visible Chinese mock translation.
- For rows with existing Chinese target text, reuse it if the caller asks for a reuse mode.
- Keep the route predictable so fixture tests can assert against it.

## Usage Log Schema

Each JSONL entry should record at least:

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

The mock route may set estimated and actual usage to the same deterministic numbers, but it must still keep the fields explicit.

## Safety And Rollback

- Output directory must not live inside the source project or fixture folder.
- Existing output directories require explicit overwrite and a harness-owned marker if we reuse them.
- The script should fail fast if the input inventory is missing required columns.

## Verification Plan

Run the mock provider on the `renpy-small` inventory and confirm:

- `target_text` is written.
- `provider-usage-log.jsonl` contains one line per batch.
- Fixture smoke harness still passes before and after the new script is added.

## Decision

Implement the mock provider as a standalone script first. Keep it narrow and deterministic so it can be used as a test double for later real provider adapters.
