#!/usr/bin/env python3
"""Validate extracted localization inventory before translation or patching.

The validator checks structural risks in inventory rows. It does not judge
translation literary quality and does not modify source game files.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = {
    "unit_id",
    "group_id",
    "format",
    "file_path",
    "key",
    "source_text",
    "existing_target_text",
    "protected_tokens",
}
PLACEHOLDER_RE = re.compile(
    r"(\{[^{}\n]+\}|\[[A-Za-z_][^\]\n]*\]|<[/A-Za-z][^>\n]*>|%[0-9.]*[sdif]|"
    r"\$\{[^}\n]+\}|\\[ntr\"']|\{/?[A-Za-z][^{}\n]*\})"
)
HAN_RE = re.compile(r"[\u4e00-\u9fff]")
MOJIBAKE_SIGNALS = (
    "\ufffd",
    "\u953f",
    "\u9357",
    "\u7481",
    "\u93c3",
    "\u7ec1",
    "\u95ab",
    "\u6d93",
)


@dataclass
class Finding:
    severity: str
    code: str
    unit_id: str
    file_path: str
    key: str
    message: str
    source_text: str = ""
    target_text: str = ""


def read_inventory(path: Path) -> tuple[list[dict[str, str]], list[Finding]]:
    findings: list[Finding] = []
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            findings.append(
                Finding(
                    "blocker",
                    "missing_columns",
                    "",
                    str(path),
                    "",
                    f"Inventory is missing required columns: {', '.join(sorted(missing))}",
                )
            )
            return [], findings
        return [dict(row) for row in reader], findings


def tokens_in_text(text: str) -> list[str]:
    seen: list[str] = []
    for match in PLACEHOLDER_RE.finditer(text or ""):
        token = match.group(0)
        if token not in seen:
            seen.append(token)
    return seen


def parse_tokens(raw: str, source_text: str) -> tuple[list[str], bool]:
    if raw:
        try:
            value = json.loads(raw)
            if isinstance(value, list):
                return [str(item) for item in value], True
        except json.JSONDecodeError:
            pass
    return tokens_in_text(source_text), False if raw else True


def looks_mojibake(text: str) -> bool:
    if not text:
        return False
    return sum(text.count(signal) for signal in MOJIBAKE_SIGNALS) >= 2


def arrow_wrapped(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("<-") and stripped.endswith("->")


def target_language_present(text: str, target_locale: str) -> bool:
    if not text:
        return False
    if target_locale.lower().startswith(("s-cn", "t-cn", "zh", "cn")):
        return HAN_RE.search(text) is not None
    return True


def add_finding(findings: list[Finding], row: dict[str, str], severity: str, code: str, message: str) -> None:
    findings.append(
        Finding(
            severity=severity,
            code=code,
            unit_id=row.get("unit_id", ""),
            file_path=row.get("file_path", ""),
            key=row.get("key", ""),
            message=message,
            source_text=row.get("source_text", "")[:240],
            target_text=row.get("existing_target_text", "")[:240],
        )
    )


def validate_rows(rows: list[dict[str, str]], target_locale: str, require_target: bool) -> list[Finding]:
    findings: list[Finding] = []
    seen_ids: set[str] = set()
    by_group: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        unit_id = row.get("unit_id", "")
        source = row.get("source_text", "")
        target = row.get("existing_target_text", "")
        source_tokens, token_json_ok = parse_tokens(row.get("protected_tokens", ""), source)
        target_tokens = tokens_in_text(target)
        if not unit_id:
            add_finding(findings, row, "blocker", "missing_unit_id", "Row has no unit_id.")
        elif unit_id in seen_ids:
            add_finding(findings, row, "blocker", "duplicate_unit_id", f"Duplicate unit_id `{unit_id}`.")
        seen_ids.add(unit_id)
        if not source.strip():
            add_finding(findings, row, "blocker", "empty_source", "Source text is empty.")
        if not token_json_ok:
            add_finding(
                findings,
                row,
                "warning",
                "malformed_token_json",
                "protected_tokens was not valid JSON; recalculated from source text.",
            )
        if require_target and not target.strip():
            add_finding(findings, row, "warning", "missing_target", "Existing target text is empty.")
        if target and looks_mojibake(target):
            add_finding(findings, row, "warning", "target_mojibake", "Existing target text looks like mojibake.")
        if target and not target_language_present(target, target_locale):
            add_finding(findings, row, "info", "target_language_not_detected", f"No target-language characters detected for `{target_locale}`.")
        if target:
            missing_tokens = [token for token in source_tokens if token not in target]
            extra_tokens = [token for token in target_tokens if token not in source_tokens]
            if missing_tokens:
                add_finding(
                    findings,
                    row,
                    "blocker",
                    "missing_protected_tokens",
                    f"Target is missing protected tokens: {', '.join(missing_tokens)}",
                )
            if extra_tokens:
                add_finding(
                    findings,
                    row,
                    "warning",
                    "extra_target_tokens",
                    f"Target has tokens not present in source: {', '.join(extra_tokens)}",
                )
            if arrow_wrapped(source) and not arrow_wrapped(target):
                add_finding(findings, row, "warning", "arrow_wrapper_changed", "Arrow-wrapped source text lost its wrapper in target.")
            if "\n" in source and "\n" not in target:
                add_finding(findings, row, "info", "linebreak_changed", "Source has line breaks but target does not.")
            if target_locale.lower().startswith(("s-cn", "t-cn", "zh", "cn")) and len(target) > max(24, len(source) * 1.8):
                add_finding(findings, row, "info", "target_length_expansion", "Target text is much longer than source.")
        by_group[row.get("group_id", "")].append(row)
    for group_id, group_rows in by_group.items():
        if not group_id or len(group_rows) < 2:
            continue
        targets = {row.get("existing_target_text", "").strip() for row in group_rows if row.get("existing_target_text", "").strip()}
        if len(targets) > 1:
            representative = group_rows[0]
            add_finding(
                findings,
                representative,
                "info",
                "duplicate_source_multiple_targets",
                f"Duplicate source group `{group_id}` has {len(targets)} different existing targets.",
            )
    return findings


def counts_by(items: Iterable[Finding], attr: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in items:
        counter[getattr(item, attr)] += 1
    return counter


def markdown_report(rows: list[dict[str, str]], findings: list[Finding], target_locale: str, require_target: bool) -> str:
    severity_counts = counts_by(findings, "severity")
    code_counts = counts_by(findings, "code")
    blocker_count = severity_counts.get("blocker", 0)
    warning_count = severity_counts.get("warning", 0)
    info_count = severity_counts.get("info", 0)
    decision = "BLOCKED" if blocker_count else "PASS_WITH_WARNINGS" if warning_count else "PASS"
    lines = [
        "# Inventory Validation Report",
        "",
        f"Target locale: `{target_locale}`",
        f"Require target text: `{require_target}`",
        f"Decision: **{decision}**",
        "",
        "## Counts",
        "",
        f"- Inventory rows: {len(rows)}",
        f"- Blockers: {blocker_count}",
        f"- Warnings: {warning_count}",
        f"- Info: {info_count}",
        "",
        "## Finding Types",
        "",
    ]
    if code_counts:
        for code, count in code_counts.most_common():
            lines.append(f"- {code}: {count}")
    else:
        lines.append("- None")
    lines.extend(["", "## Blockers And Warnings", ""])
    serious = [finding for finding in findings if finding.severity in {"blocker", "warning"}]
    if not serious:
        lines.append("- None")
    else:
        for finding in serious[:100]:
            lines.append(
                f"- **{finding.severity.upper()} {finding.code}** `{finding.file_path}` `{finding.key}`: {finding.message}"
            )
        if len(serious) > 100:
            lines.append(f"- ... {len(serious) - 100} more")
    lines.extend(["", "## Next Step", ""])
    if blocker_count:
        lines.append("Fix blockers before translation, patch generation, or provider calls.")
    elif warning_count:
        lines.append("Review warnings before translation. Provider calls may proceed only after budget approval and user acceptance of residual risk.")
    else:
        lines.append("Inventory is structurally ready for cost/provider dry run.")
    lines.append("")
    return "\n".join(lines)


def write_outputs(out: Path, rows: list[dict[str, str]], findings: list[Finding], target_locale: str, require_target: bool) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "inventory-validation.json").write_text(
        json.dumps([asdict(finding) for finding in findings], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out / "inventory-validation.md").write_text(markdown_report(rows, findings, target_locale, require_target), encoding="utf-8")
    with (out / "inventory-validation.csv").open("w", newline="", encoding="utf-8") as fh:
        fieldnames = ["severity", "code", "unit_id", "file_path", "key", "message", "source_text", "target_text"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            writer.writerow(asdict(finding))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate translation inventory before translation or patching.")
    parser.add_argument("inventory", type=Path, help="translation-inventory.csv from extract_inventory.py")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--target-locale", default="s-cn")
    parser.add_argument("--require-target", action="store_true", help="Warn when existing target text is empty.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when blockers are found.")
    args = parser.parse_args()

    if not args.inventory.exists() or not args.inventory.is_file():
        raise SystemExit(f"Inventory file does not exist: {args.inventory}")
    rows, initial_findings = read_inventory(args.inventory)
    findings = initial_findings + validate_rows(rows, args.target_locale, args.require_target)
    write_outputs(args.out.resolve(), rows, findings, args.target_locale, args.require_target)
    blockers = sum(1 for finding in findings if finding.severity == "blocker")
    warnings = sum(1 for finding in findings if finding.severity == "warning")
    print(f"Wrote validation to {args.out.resolve()}")
    print(f"Rows: {len(rows)}")
    print(f"Blockers: {blockers}")
    print(f"Warnings: {warnings}")
    if args.strict and blockers:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
