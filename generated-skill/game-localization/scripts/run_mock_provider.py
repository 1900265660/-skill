#!/usr/bin/env python3
"""Run a deterministic mock provider route for fixtures and gate tests.

This script consumes the existing inventory/validation/cost planning outputs,
writes a translated inventory with `target_text`, and records usage logs without
calling any remote provider or OCR service.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


OWNER_MARKER = ".mock-provider-owned.json"
TRANSLATION_COLUMNS = ("target_text", "translated_text", "new_target_text", "existing_target_text")
PLACEHOLDER_RE = re.compile(
    r"(\{[^{}\n]+\}|\[[A-Za-z_][^\]\n]*\]|<[/A-Za-z][^>\n]*>|%[0-9.]*[sdif]|"
    r"\$\{[^}\n]+\}|\\[ntr\"']|\{/?[A-Za-z][^{}\n]*\})"
)
ALLOWED_COST_GATES = {"READY_FOR_LOCAL_OR_MANUAL_STEP", "CAUTION_PENDING_WARNING_ACCEPTANCE"}


@dataclass
class BatchPlan:
    batch_id: str
    unit_ids: list[str]
    row_count: int
    source_characters: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_cost_usd: float


@dataclass
class UsageRecord:
    timestamp: str
    provider: str
    model: str
    route: str
    batch_id: str
    unit_ids: list[str]
    row_count: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_cost_usd: float
    actual_input_tokens: int
    actual_output_tokens: int
    actual_total_cost_usd: float
    status: str
    output_path: str


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def generated_root() -> Path:
    return skill_root().parent


def default_inventory() -> Path:
    return generated_root() / "inventory-output" / "renpy-small" / "translation-inventory.csv"


def default_output() -> Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return generated_root() / "provider-output" / "mock-provider" / timestamp


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def prepare_output(out: Path, input_root: Path, overwrite: bool) -> None:
    out = out.resolve()
    input_root = input_root.resolve()
    if is_relative_to(out, input_root):
        raise SystemExit("Output directory must not be inside the inventory source folder.")
    if out.exists():
        if not overwrite:
            raise SystemExit(f"Output directory already exists; pass --overwrite for harness-owned paths: {out}")
        marker = out / OWNER_MARKER
        if not marker.exists():
            raise SystemExit(f"Refusing to overwrite an unmarked directory: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / OWNER_MARKER).write_text(
        json.dumps({"owned_by": "game-localization mock provider"}, indent=2),
        encoding="utf-8",
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def row_target(row: dict[str, str]) -> str:
    for column in TRANSLATION_COLUMNS:
        value = row.get(column, "")
        if value and value.strip():
            return value.strip()
    return ""


def source_key(row: dict[str, str]) -> str:
    return row.get("group_id") or re.sub(r"\s+", " ", row.get("source_text", "").strip())


def select_rows(rows: list[dict[str, str]], scope: str) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        source_text = row.get("source_text", "").strip()
        if not source_text:
            continue
        target = row_target(row)
        if scope == "missing-target" and target:
            continue
        if scope == "existing-target-review" and not target:
            continue
        key = source_key(row)
        if key in seen:
            continue
        seen.add(key)
        selected.append(dict(row))
    return selected


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


def batch_rows(rows: list[dict[str, str]], batch_size: int) -> list[BatchPlan]:
    batches: list[BatchPlan] = []
    for index in range(0, len(rows), batch_size):
        chunk = rows[index : index + batch_size]
        unit_ids = [row.get("unit_id", "") for row in chunk]
        source_chars = sum(len(row.get("source_text", "")) for row in chunk)
        input_tokens = chars_to_tokens(source_chars, 4.0) + sum(estimate_context_tokens(row) for row in chunk) + 100
        output_chars = sum(len(mock_target(row)) for row in chunk)
        output_tokens = chars_to_tokens(output_chars, 1.5)
        batches.append(
            BatchPlan(
                batch_id=f"batch_{len(batches) + 1:04d}",
                unit_ids=unit_ids,
                row_count=len(chunk),
                source_characters=source_chars,
                estimated_input_tokens=input_tokens,
                estimated_output_tokens=output_tokens,
                estimated_total_cost_usd=0.0,
            )
        )
    return batches


def validate_gate(cost_json: Path | None, validation_json: Path | None, accept_warnings: bool) -> list[str]:
    reasons: list[str] = []
    if validation_json is not None:
        findings = read_json(validation_json)
        blockers = sum(1 for item in findings if item.get("severity") == "blocker")
        warnings = sum(1 for item in findings if item.get("severity") == "warning")
        if blockers:
            raise SystemExit(f"Validation has {blockers} blocker(s); mock provider will not run.")
        if warnings and not accept_warnings:
            raise SystemExit(f"Validation has {warnings} warning(s); pass --accept-validation-warnings to continue.")
        reasons.append(f"Validation blockers={blockers}, warnings={warnings}.")
    if cost_json is not None:
        cost = read_json(cost_json)
        gate = cost.get("gate_decision", "")
        if gate not in ALLOWED_COST_GATES:
            raise SystemExit(f"Cost gate `{gate}` does not allow mock provider execution.")
        reasons.append(f"Cost gate={gate}.")
    return reasons


def mock_target(row: dict[str, str]) -> str:
    known = {
        "Welcome to the sinking star.": "欢迎来到沉星。",
        "Use {b}caution{/b}, [player_name].": "请保持{b}谨慎{/b}，[player_name]。",
        "Open the door": "打开门",
        "Stay outside": "留在外面",
    }
    source = row.get("source_text", "")
    if source in known:
        return known[source]
    tokens = []
    for match in PLACEHOLDER_RE.finditer(source):
        token = match.group(0)
        if token not in tokens:
            tokens.append(token)
    suffix = " ".join(tokens)
    return f"【模拟译文】{source}" + (f" {suffix}" if suffix and suffix not in source else "")


def fill_targets(rows: list[dict[str, str]], mode: str) -> list[dict[str, str]]:
    filled: list[dict[str, str]] = []
    for row in rows:
        out = dict(row)
        if mode == "reuse-existing":
            out["target_text"] = row_target(row)
        else:
            out["target_text"] = mock_target(row)
        filled.append(out)
    return filled


def log_records(out: Path, provider: str, model: str, route: str, batches: list[BatchPlan]) -> Path:
    log_path = out / "provider-usage-log.jsonl"
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    with log_path.open("w", encoding="utf-8", newline="\n") as fh:
        for batch in batches:
            record = UsageRecord(
                timestamp=timestamp,
                provider=provider,
                model=model,
                route=route,
                batch_id=batch.batch_id,
                unit_ids=batch.unit_ids,
                row_count=batch.row_count,
                estimated_input_tokens=batch.estimated_input_tokens,
                estimated_output_tokens=batch.estimated_output_tokens,
                estimated_total_cost_usd=batch.estimated_total_cost_usd,
                actual_input_tokens=batch.estimated_input_tokens,
                actual_output_tokens=batch.estimated_output_tokens,
                actual_total_cost_usd=0.0,
                status="mocked",
                output_path=str(out),
            )
            fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    return log_path


def markdown_report(args: argparse.Namespace, rows: list[dict[str, str]], batches: list[BatchPlan], reasons: list[str], output: Path) -> str:
    lines = [
        "# Mock Provider Report",
        "",
        f"Inventory: `{args.inventory}`",
        f"Output: `{output}`",
        f"Route: `{args.route}`",
        f"Provider/model: `{args.provider}` / `{args.model}`",
        "",
        "## Gate",
        "",
    ]
    if reasons:
        for reason in reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- No gate inputs supplied; mock route ran without external gate checks.")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Rows selected: {len(rows)}",
            f"- Batches: {len(batches)}",
            f"- Output inventory rows: {len(rows)}",
            "",
            "## Outputs",
            "",
            f"- `translated-inventory.mock.csv`",
            f"- `provider-usage-log.jsonl`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic mock provider route for fixtures and gate tests.")
    parser.add_argument("inventory", type=Path, nargs="?", default=default_inventory())
    parser.add_argument("--out", type=Path, default=default_output())
    parser.add_argument("--scope", choices=["all", "missing-target", "existing-target-review"], default="missing-target")
    parser.add_argument("--mode", choices=["mock-zh", "reuse-existing"], default="mock-zh")
    parser.add_argument("--provider", default="mock_model")
    parser.add_argument("--model", default="mock_model")
    parser.add_argument("--route", default="mock_model")
    parser.add_argument("--batch-size", type=int, default=80)
    parser.add_argument("--cost-json", type=Path)
    parser.add_argument("--validation-json", type=Path)
    parser.add_argument("--accept-validation-warnings", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--source-locale", default="en")
    parser.add_argument("--target-locale", default="s-cn")
    args = parser.parse_args()

    if not args.inventory.exists() or not args.inventory.is_file():
        raise SystemExit(f"Inventory file does not exist: {args.inventory}")
    if args.batch_size < 1:
        raise SystemExit("--batch-size must be at least 1")

    inventory_root = args.inventory.parent
    out = args.out.resolve()
    if is_relative_to(out, inventory_root):
        raise SystemExit("Output directory must not be inside the inventory source folder.")
    if out.exists():
        if not args.overwrite:
            raise SystemExit(f"Output directory already exists; pass --overwrite for harness-owned paths: {out}")
        marker = out / OWNER_MARKER
        if not marker.exists():
            raise SystemExit(f"Refusing to overwrite an unmarked directory: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / OWNER_MARKER).write_text(
        json.dumps({"owned_by": "game-localization mock provider"}, indent=2),
        encoding="utf-8",
    )

    rows = read_csv(args.inventory)
    selected = select_rows(rows, args.scope)
    gate_reasons = validate_gate(args.cost_json, args.validation_json, args.accept_validation_warnings)
    batches = batch_rows(selected, args.batch_size)
    translated = fill_targets(selected, args.mode)
    fieldnames = list(rows[0].keys()) if rows else ["target_text"]
    if "target_text" not in fieldnames:
        fieldnames.append("target_text")
    write_csv(out / "translated-inventory.mock.csv", translated, fieldnames)
    log_path = log_records(out, args.provider, args.model, args.route, batches)
    (out / "mock-provider-report.md").write_text(markdown_report(args, translated, batches, gate_reasons, out), encoding="utf-8")
    summary = {
        "inventory": str(args.inventory.resolve()),
        "output": str(out),
        "provider": args.provider,
        "model": args.model,
        "route": args.route,
        "scope": args.scope,
        "mode": args.mode,
        "selected_rows": len(translated),
        "batches": [asdict(batch) for batch in batches],
        "usage_log": str(log_path),
        "gate_reasons": gate_reasons,
    }
    (out / "mock-provider-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote mock provider output to {out}")
    print(f"Rows translated: {len(translated)}")
    print(f"Batches: {len(batches)}")
    print(f"Usage log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
