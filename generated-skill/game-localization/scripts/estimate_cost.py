#!/usr/bin/env python3
"""Estimate localization cost/time and produce a provider dry-run plan.

This script reads a Phase 2 translation inventory and writes Phase 3 dry-run
artifacts. It never calls a remote model, translation MCP, OCR service, or game
tool. Paid provider routes remain blocked until validation and budget gates are
explicitly satisfied.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REMOTE_ROUTES = {"openai", "anthropic", "translation_mcp", "external_model"}
LOCAL_ROUTES = {"manual_csv", "mock_model", "local_model"}
PAID_ROUTES = REMOTE_ROUTES | {"local_model"}
DEFAULT_BATCH_SIZE = 80
CODE_LIKE_FORMATS = {"json", "renpy", "mission-txt"}


@dataclass
class Pricing:
    provider: str
    model: str
    input_usd_per_mtok: float | None = None
    output_usd_per_mtok: float | None = None
    request_usd: float = 0.0
    vision_image_usd: float = 0.0
    notes: str = ""


@dataclass
class Estimate:
    scope: str
    route: str
    provider: str
    model: str
    rows_in_inventory: int
    rows_in_scope: int
    unique_translation_units: int
    duplicate_rows_saved: int
    source_characters: int
    deduped_source_characters: int
    estimated_target_characters: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    batches: int
    estimated_text_cost_usd: float | None
    estimated_vision_cost_usd: float | None
    estimated_total_cost_usd: float | None
    budget_usd: float | None
    budget_status: str
    gate_decision: str
    gate_reasons: list[str]
    provider_calls_enabled: bool
    estimated_provider_minutes: tuple[float, float]
    estimated_human_review_hours: tuple[float, float]
    validation_blockers: int
    validation_warnings: int
    audit_supplied: bool
    audited_archives: int
    audited_image_assets: int
    audited_font_assets: int
    audited_executables: int
    text_files_to_modify: int
    code_like_rows: int
    estimated_text_file_hours: tuple[float, float]
    estimated_image_lane_hours: tuple[float, float]
    estimated_font_lane_hours: tuple[float, float]
    estimated_tooling_or_code_hours: tuple[float, float]
    estimated_qa_hours: tuple[float, float]
    estimated_total_delivery_hours: tuple[float, float]
    estimated_labor_cost_usd: tuple[float, float]
    estimated_project_total_cost_usd: tuple[float, float]
    project_risk_level: str


def read_inventory(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def row_in_scope(row: dict[str, str], scope: str) -> bool:
    target = row.get("existing_target_text", "").strip()
    if scope == "all":
        return bool(row.get("source_text", "").strip())
    if scope == "missing-target":
        return bool(row.get("source_text", "").strip()) and not target
    if scope == "existing-target-review":
        return bool(row.get("source_text", "").strip()) and bool(target)
    raise ValueError(f"Unsupported scope: {scope}")


def dedupe_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        key = row.get("group_id") or normalize_text(row.get("source_text", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def chars_to_tokens(chars: int, chars_per_token: float) -> int:
    if chars <= 0:
        return 0
    return max(1, math.ceil(chars / max(chars_per_token, 0.1)))


def estimate_context_tokens(row: dict[str, str]) -> int:
    context = "\n".join(
        [
            row.get("unit_id", ""),
            row.get("file_path", ""),
            row.get("key", ""),
            row.get("context", ""),
            row.get("speaker", ""),
            row.get("protected_tokens", ""),
            row.get("notes", ""),
        ]
    )
    return chars_to_tokens(len(context), 6.0)


def read_validation_counts(path: Path | None) -> tuple[int, int]:
    if path is None:
        return 0, 0
    if not path.exists():
        raise SystemExit(f"Validation JSON does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    blockers = sum(1 for item in data if item.get("severity") == "blocker")
    warnings = sum(1 for item in data if item.get("severity") == "warning")
    return blockers, warnings


def load_audit_summary(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise SystemExit(f"Audit JSON does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_pricing(path: Path | None, provider: str, model: str) -> Pricing:
    if provider in {"manual_csv", "mock_model"}:
        return Pricing(provider=provider, model=model or provider, input_usd_per_mtok=0.0, output_usd_per_mtok=0.0)
    if path is None:
        return Pricing(provider=provider, model=model, notes="No provider pricing config supplied.")
    data = json.loads(path.read_text(encoding="utf-8"))
    providers = data.get("providers", {})
    provider_data = providers.get(provider)
    if not provider_data:
        return Pricing(provider=provider, model=model, notes=f"Provider `{provider}` not found in pricing config.")
    models = provider_data.get("models", {})
    model_data = models.get(model)
    if not model_data:
        return Pricing(provider=provider, model=model, notes=f"Model `{model}` not found in pricing config.")
    return Pricing(
        provider=provider,
        model=model,
        input_usd_per_mtok=as_float_or_none(model_data.get("input_usd_per_mtok")),
        output_usd_per_mtok=as_float_or_none(model_data.get("output_usd_per_mtok")),
        request_usd=float(model_data.get("request_usd", 0.0)),
        vision_image_usd=float(model_data.get("vision_image_usd", 0.0)),
        notes=str(model_data.get("notes", "")),
    )


def as_float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def money(input_tokens: int, output_tokens: int, batches: int, vision_images: int, pricing: Pricing) -> tuple[float | None, float | None, float | None]:
    if pricing.input_usd_per_mtok is None or pricing.output_usd_per_mtok is None:
        return None, None, None
    text_cost = (
        input_tokens / 1_000_000 * pricing.input_usd_per_mtok
        + output_tokens / 1_000_000 * pricing.output_usd_per_mtok
        + batches * pricing.request_usd
    )
    vision_cost = vision_images * pricing.vision_image_usd
    return text_cost, vision_cost, text_cost + vision_cost


def budget_status(total_cost: float | None, budget: float | None) -> str:
    if total_cost is None:
        return "UNKNOWN_PRICE"
    if budget is None:
        return "NO_BUDGET"
    if total_cost > budget:
        return "OVER_BUDGET"
    return "WITHIN_BUDGET"


def gate(
    route: str,
    pricing: Pricing,
    total_cost: float | None,
    budget: float | None,
    approve_budget: bool,
    blockers: int,
    warnings: int,
    accept_warnings: bool,
) -> tuple[str, list[str], bool]:
    reasons: list[str] = []
    if blockers:
        reasons.append(f"Validation has {blockers} blocker(s).")
    if warnings and not accept_warnings:
        reasons.append(f"Validation has {warnings} warning(s) that have not been accepted.")
    if route in REMOTE_ROUTES:
        reasons.append("Remote provider route selected; this script is dry-run only and will not call it.")
    if route in PAID_ROUTES and route not in {"manual_csv", "mock_model"}:
        if total_cost is None:
            reasons.append("Provider pricing is unknown; supply a pricing config before paid calls.")
        if budget is None:
            reasons.append("No budget was supplied.")
        elif total_cost is not None and total_cost > budget:
            reasons.append(f"Estimated total cost ${total_cost:.4f} exceeds budget ${budget:.4f}.")
        if not approve_budget:
            reasons.append("Budget approval flag was not supplied.")
    if blockers:
        return "BLOCKED_VALIDATION", reasons, False
    if route in PAID_ROUTES and route not in {"manual_csv", "mock_model"}:
        if total_cost is None:
            return "BLOCKED_UNKNOWN_PRICE", reasons, False
        if budget is None:
            return "BLOCKED_NO_BUDGET", reasons, False
        if total_cost > budget:
            return "BLOCKED_BUDGET_EXCEEDED", reasons, False
        if not approve_budget:
            return "BLOCKED_PENDING_BUDGET_APPROVAL", reasons, False
    if warnings and not accept_warnings:
        return "CAUTION_PENDING_WARNING_ACCEPTANCE", reasons, False
    if route in REMOTE_ROUTES:
        return "READY_FOR_USER_APPROVED_PROVIDER_STEP", reasons, False
    return "READY_FOR_LOCAL_OR_MANUAL_STEP", reasons, False


def provider_minutes(batches: int, route: str) -> tuple[float, float]:
    if route == "manual_csv":
        return 0.0, 0.0
    if route == "local_model":
        return max(2.0, batches * 1.5), max(5.0, batches * 5.0)
    return max(1.0, batches * 0.3), max(3.0, batches * 1.2)


def human_review_hours(chars: int, chars_per_hour_low: int, chars_per_hour_high: int) -> tuple[float, float]:
    if chars <= 0:
        return 0.0, 0.0
    fast = chars / max(chars_per_hour_high, 1)
    slow = chars / max(chars_per_hour_low, 1)
    return round(fast, 2), round(slow, 2)


def lane_hours(count: int, per_item_low: float, per_item_high: float, minimum_low: float = 0.0) -> tuple[float, float]:
    if count <= 0:
        return 0.0, 0.0
    low = max(minimum_low, count * per_item_low)
    high = max(low, count * per_item_high)
    return round(low, 2), round(high, 2)


def sum_hours(*ranges: tuple[float, float]) -> tuple[float, float]:
    return round(sum(item[0] for item in ranges), 2), round(sum(item[1] for item in ranges), 2)


def multiply_hours(hours: tuple[float, float], rate: float) -> tuple[float, float]:
    return round(hours[0] * rate, 2), round(hours[1] * rate, 2)


def money_range(labor: tuple[float, float], api_cost: float | None) -> tuple[float, float]:
    api = api_cost or 0.0
    return round(labor[0] + api, 2), round(labor[1] + api, 2)


def classify_project_risk(audit_supplied: bool, archives: int, images: int, fonts: int, code_like_rows: int) -> str:
    if not audit_supplied:
        return "UNKNOWN"
    score = 0
    score += 3 if archives >= 20 else 2 if archives >= 5 else 1 if archives else 0
    score += 3 if images >= 500 else 2 if images >= 100 else 1 if images else 0
    score += 2 if fonts >= 8 else 1 if fonts else 0
    score += 3 if code_like_rows >= 50 else 2 if code_like_rows >= 10 else 1 if code_like_rows else 0
    if score >= 7:
        return "HIGH"
    if score >= 3:
        return "MODERATE"
    return "LOW"


def build_batches(rows: list[dict[str, str]], batch_size: int) -> list[dict[str, Any]]:
    batches: list[dict[str, Any]] = []
    for index in range(0, len(rows), batch_size):
        chunk = rows[index : index + batch_size]
        source_chars = sum(len(row.get("source_text", "")) for row in chunk)
        batches.append(
            {
                "batch_id": f"batch_{len(batches) + 1:04d}",
                "row_count": len(chunk),
                "source_characters": source_chars,
                "formats": dict(Counter(row.get("format", "unknown") for row in chunk)),
                "first_unit_id": chunk[0].get("unit_id", "") if chunk else "",
                "last_unit_id": chunk[-1].get("unit_id", "") if chunk else "",
            }
        )
    return batches


def markdown_report(estimate: Estimate, batches: list[dict[str, Any]], pricing: Pricing, args: argparse.Namespace) -> str:
    cost_text = "unknown"
    if estimate.estimated_total_cost_usd is not None:
        cost_text = f"${estimate.estimated_total_cost_usd:.4f}"
    lines = [
        "# Cost And Provider Dry Run",
        "",
        f"Inventory: `{args.inventory}`",
        f"Scope: `{estimate.scope}`",
        f"Route: `{estimate.route}`",
        f"Provider/model: `{estimate.provider}` / `{estimate.model}`",
        f"Provider calls enabled by this script: `{estimate.provider_calls_enabled}`",
        "",
        "## Counts",
        "",
        f"- Inventory rows: {estimate.rows_in_inventory}",
        f"- Rows in scope: {estimate.rows_in_scope}",
        f"- Unique translation units after dedupe: {estimate.unique_translation_units}",
        f"- Duplicate rows saved by dedupe: {estimate.duplicate_rows_saved}",
        f"- Source characters in scope: {estimate.source_characters}",
        f"- Deduped source characters: {estimate.deduped_source_characters}",
        f"- Estimated target characters: {estimate.estimated_target_characters}",
        f"- Batches: {estimate.batches}",
        f"- Text files to modify: {estimate.text_files_to_modify}",
        f"- Code-like rows: {estimate.code_like_rows}",
        f"- Audit supplied: {estimate.audit_supplied}",
        f"- Audited archives: {estimate.audited_archives}",
        f"- Audited image assets: {estimate.audited_image_assets}",
        f"- Audited font assets: {estimate.audited_font_assets}",
        f"- Audited executables: {estimate.audited_executables}",
        "",
        "## Token Estimate",
        "",
        f"- Estimated input tokens: {estimate.estimated_input_tokens}",
        f"- Estimated output tokens: {estimate.estimated_output_tokens}",
        f"- Estimated total tokens: {estimate.estimated_total_tokens}",
        "",
        "## API Money Estimate",
        "",
        f"- Pricing status: `{estimate.budget_status}`",
        f"- Text cost: `{format_money(estimate.estimated_text_cost_usd)}`",
        f"- Vision/OCR image cost: `{format_money(estimate.estimated_vision_cost_usd)}`",
        f"- Total estimated API cost: `{cost_text}`",
        f"- Budget: `{format_money(estimate.budget_usd)}`",
        f"- Pricing notes: {pricing.notes or 'None'}",
        "",
        "## Project Delivery Estimate",
        "",
        f"- Provider/runtime time: {estimate.estimated_provider_minutes[0]:.1f}-{estimate.estimated_provider_minutes[1]:.1f} minutes",
        f"- Human review time: {estimate.estimated_human_review_hours[0]:.2f}-{estimate.estimated_human_review_hours[1]:.2f} hours",
        f"- Text file edit/patch time: {estimate.estimated_text_file_hours[0]:.2f}-{estimate.estimated_text_file_hours[1]:.2f} hours",
        f"- Image/OCR lane time: {estimate.estimated_image_lane_hours[0]:.2f}-{estimate.estimated_image_lane_hours[1]:.2f} hours",
        f"- Font lane time: {estimate.estimated_font_lane_hours[0]:.2f}-{estimate.estimated_font_lane_hours[1]:.2f} hours",
        f"- Tooling/code/package lane time: {estimate.estimated_tooling_or_code_hours[0]:.2f}-{estimate.estimated_tooling_or_code_hours[1]:.2f} hours",
        f"- QA time: {estimate.estimated_qa_hours[0]:.2f}-{estimate.estimated_qa_hours[1]:.2f} hours",
        f"- Total delivery time: {estimate.estimated_total_delivery_hours[0]:.2f}-{estimate.estimated_total_delivery_hours[1]:.2f} hours",
        f"- Estimated labor cost: `{format_money_range(estimate.estimated_labor_cost_usd)}`",
        f"- Estimated project total cost: `{format_money_range(estimate.estimated_project_total_cost_usd)}`",
        f"- Project risk level: `{estimate.project_risk_level}`",
        "",
        "Interpretation: token cost only covers text sent to a translation provider. Delivery cost also includes file editing, patching, image/OCR checks, font work, package/tool risk, QA, and human review.",
        "",
        "## Gate",
        "",
        f"Decision: **{estimate.gate_decision}**",
        "",
    ]
    if estimate.gate_reasons:
        for reason in estimate.gate_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- No blocking reasons for the selected dry-run route.")
    lines.extend(
        [
            "",
            "## Batch Preview",
            "",
            "| Batch | Rows | Source Chars | Formats |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for batch in batches[:20]:
        formats = ", ".join(f"{name}:{count}" for name, count in batch["formats"].items())
        lines.append(f"| {batch['batch_id']} | {batch['row_count']} | {batch['source_characters']} | {formats} |")
    if len(batches) > 20:
        lines.append(f"| ... | ... | ... | {len(batches) - 20} more batches |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Use this report to decide whether the translation route is worth running. Keep remote calls disabled until validation warnings, provider pricing, and budget approval are all resolved.",
            "",
        ]
    )
    return "\n".join(lines)


def format_money(value: float | None) -> str:
    if value is None:
        return "unknown"
    return f"${value:.4f}"


def format_money_range(value: tuple[float, float]) -> str:
    return f"${value[0]:.2f}-${value[1]:.2f}"


def write_outputs(out: Path, estimate: Estimate, batches: list[dict[str, Any]], pricing: Pricing, args: argparse.Namespace) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "cost-estimate.json").write_text(json.dumps(asdict(estimate), indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "provider-dry-run.json").write_text(json.dumps({"pricing": asdict(pricing), "batches": batches}, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "cost-estimate.md").write_text(markdown_report(estimate, batches, pricing, args), encoding="utf-8")
    with (out / "provider-batches.csv").open("w", newline="", encoding="utf-8") as fh:
        fieldnames = ["batch_id", "row_count", "source_characters", "formats", "first_unit_id", "last_unit_id"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for batch in batches:
            row = dict(batch)
            row["formats"] = json.dumps(row["formats"], ensure_ascii=False)
            writer.writerow(row)
    usage_log = out / "provider-usage-log.jsonl"
    if not usage_log.exists():
        usage_log.write_text("", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate localization translation cost and provider dry-run plan.")
    parser.add_argument("inventory", type=Path, help="translation-inventory.csv from extract_inventory.py")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scope", choices=["all", "missing-target", "existing-target-review"], default="all")
    parser.add_argument("--route", choices=sorted(REMOTE_ROUTES | LOCAL_ROUTES), default="manual_csv")
    parser.add_argument("--provider", default="manual_csv")
    parser.add_argument("--model", default="manual_csv")
    parser.add_argument("--pricing-config", type=Path)
    parser.add_argument("--audit-json", type=Path, help="localization-audit.json from scan_project.py")
    parser.add_argument("--budget-usd", type=float)
    parser.add_argument("--approve-budget", action="store_true", help="Mark that the user approved this dry-run budget.")
    parser.add_argument("--validation-json", type=Path, help="inventory-validation.json from validate_inventory.py")
    parser.add_argument("--accept-validation-warnings", action="store_true")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--source-chars-per-token", type=float, default=4.0)
    parser.add_argument("--target-chars-per-token", type=float, default=1.5)
    parser.add_argument("--target-char-ratio", type=float, default=0.75)
    parser.add_argument("--prompt-overhead-tokens", type=int, default=700)
    parser.add_argument("--glossary-tokens", type=int, default=300)
    parser.add_argument("--vision-images", type=int, default=0)
    parser.add_argument("--review-chars-per-hour-low", type=int, default=1200)
    parser.add_argument("--review-chars-per-hour-high", type=int, default=2500)
    parser.add_argument("--labor-usd-per-hour", type=float, default=25.0)
    parser.add_argument("--image-check-ratio", type=float, default=0.1)
    parser.add_argument("--image-edit-ratio", type=float, default=0.02)
    args = parser.parse_args()

    if not args.inventory.exists() or not args.inventory.is_file():
        raise SystemExit(f"Inventory file does not exist: {args.inventory}")
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be at least 1")

    rows = read_inventory(args.inventory)
    scoped_rows = [row for row in rows if row_in_scope(row, args.scope)]
    unique_rows = dedupe_rows(scoped_rows)
    batches = build_batches(unique_rows, args.batch_size)
    audit = load_audit_summary(args.audit_json)
    counts = audit.get("counts", {}) if audit else {}
    archives = int(counts.get("archives", 0))
    images = int(counts.get("image_assets", 0))
    fonts = int(counts.get("font_assets", 0))
    executables = int(counts.get("executables", 0))

    source_chars = sum(len(row.get("source_text", "")) for row in scoped_rows)
    deduped_chars = sum(len(row.get("source_text", "")) for row in unique_rows)
    target_chars = math.ceil(deduped_chars * args.target_char_ratio)
    source_tokens = chars_to_tokens(deduped_chars, args.source_chars_per_token)
    target_tokens = chars_to_tokens(target_chars, args.target_chars_per_token)
    context_tokens = sum(estimate_context_tokens(row) for row in unique_rows)
    overhead_tokens = len(batches) * (args.prompt_overhead_tokens + args.glossary_tokens)
    input_tokens = source_tokens + context_tokens + overhead_tokens
    output_tokens = target_tokens

    pricing = load_pricing(args.pricing_config, args.provider, args.model)
    text_cost, vision_cost, total_cost = money(input_tokens, output_tokens, len(batches), args.vision_images, pricing)
    blockers, warnings = read_validation_counts(args.validation_json)
    text_files_to_modify = len({row.get("file_path", "") for row in scoped_rows if row.get("file_path")})
    code_like_rows = sum(1 for row in scoped_rows if row.get("format", "") in CODE_LIKE_FORMATS)
    review_hours = human_review_hours(deduped_chars, args.review_chars_per_hour_low, args.review_chars_per_hour_high)
    text_file_hours = lane_hours(text_files_to_modify, 0.08, 0.35, 0.5)
    images_to_check = math.ceil(images * args.image_check_ratio)
    images_to_edit = math.ceil(images * args.image_edit_ratio)
    image_hours = sum_hours(lane_hours(images_to_check, 0.03, 0.12), lane_hours(images_to_edit, 0.5, 2.0))
    font_hours = lane_hours(fonts, 0.05, 0.25, 0.5 if fonts else 0.0)
    tooling_hours = sum_hours(lane_hours(archives, 0.2, 1.5), lane_hours(code_like_rows, 0.02, 0.12))
    qa_hours = sum_hours((1.0, 3.0), lane_hours(text_files_to_modify, 0.05, 0.2), lane_hours(executables, 0.25, 1.0))
    total_delivery_hours = sum_hours(review_hours, text_file_hours, image_hours, font_hours, tooling_hours, qa_hours)
    labor_cost = multiply_hours(total_delivery_hours, args.labor_usd_per_hour)
    project_total_cost = money_range(labor_cost, total_cost)
    project_risk = classify_project_risk(bool(audit), archives, images, fonts, code_like_rows)
    gate_decision, reasons, calls_enabled = gate(
        args.route,
        pricing,
        total_cost,
        args.budget_usd,
        args.approve_budget,
        blockers,
        warnings,
        args.accept_validation_warnings,
    )

    estimate = Estimate(
        scope=args.scope,
        route=args.route,
        provider=args.provider,
        model=args.model,
        rows_in_inventory=len(rows),
        rows_in_scope=len(scoped_rows),
        unique_translation_units=len(unique_rows),
        duplicate_rows_saved=len(scoped_rows) - len(unique_rows),
        source_characters=source_chars,
        deduped_source_characters=deduped_chars,
        estimated_target_characters=target_chars,
        estimated_input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        estimated_total_tokens=input_tokens + output_tokens,
        batches=len(batches),
        estimated_text_cost_usd=text_cost,
        estimated_vision_cost_usd=vision_cost,
        estimated_total_cost_usd=total_cost,
        budget_usd=args.budget_usd,
        budget_status=budget_status(total_cost, args.budget_usd),
        gate_decision=gate_decision,
        gate_reasons=reasons,
        provider_calls_enabled=calls_enabled,
        estimated_provider_minutes=provider_minutes(len(batches), args.route),
        estimated_human_review_hours=review_hours,
        validation_blockers=blockers,
        validation_warnings=warnings,
        audit_supplied=bool(audit),
        audited_archives=archives,
        audited_image_assets=images,
        audited_font_assets=fonts,
        audited_executables=executables,
        text_files_to_modify=text_files_to_modify,
        code_like_rows=code_like_rows,
        estimated_text_file_hours=text_file_hours,
        estimated_image_lane_hours=image_hours,
        estimated_font_lane_hours=font_hours,
        estimated_tooling_or_code_hours=tooling_hours,
        estimated_qa_hours=qa_hours,
        estimated_total_delivery_hours=total_delivery_hours,
        estimated_labor_cost_usd=labor_cost,
        estimated_project_total_cost_usd=project_total_cost,
        project_risk_level=project_risk,
    )

    write_outputs(args.out.resolve(), estimate, batches, pricing, args)
    print(f"Wrote cost estimate to {args.out.resolve()}")
    print(f"Rows in scope: {estimate.rows_in_scope}")
    print(f"Unique translation units: {estimate.unique_translation_units}")
    print(f"Estimated total tokens: {estimate.estimated_total_tokens}")
    print(f"Estimated total cost: {format_money(estimate.estimated_total_cost_usd)}")
    print(f"Gate decision: {estimate.gate_decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
