#!/usr/bin/env python3
"""Prepare a low-cost sample translation inventory.

This script selects a small set of inventory rows for personal-use trial
translation. It never calls remote providers. The output can be hand-edited,
fed to a later approved provider, or used in mock mode for patch/QA tests.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


TRANSLATION_COLUMNS = ("target_text", "translated_text", "new_target_text", "existing_target_text")
PLACEHOLDER_RE = re.compile(
    r"(\{[^{}\n]+\}|\[[A-Za-z_][^\]\n]*\]|<[/A-Za-z][^>\n]*>|%[0-9.]*[sdif]|"
    r"\$\{[^}\n]+\}|\\[ntr\"']|\{/?[A-Za-z][^{}\n]*\})"
)


def read_inventory(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader], list(reader.fieldnames or [])


def source_key(row: dict[str, str]) -> str:
    return row.get("group_id") or re.sub(r"\s+", " ", row.get("source_text", "").strip())


def has_target(row: dict[str, str]) -> bool:
    return any(row.get(column, "").strip() for column in TRANSLATION_COLUMNS)


def row_target(row: dict[str, str]) -> str:
    for column in TRANSLATION_COLUMNS:
        value = row.get(column, "")
        if value and value.strip():
            return value.strip()
    return ""


def parse_tokens(row: dict[str, str]) -> list[str]:
    raw = row.get("protected_tokens", "")
    if raw:
        try:
            value = json.loads(raw)
            if isinstance(value, list):
                return [str(item) for item in value]
        except json.JSONDecodeError:
            pass
    seen: list[str] = []
    for match in PLACEHOLDER_RE.finditer(row.get("source_text", "")):
        token = match.group(0)
        if token not in seen:
            seen.append(token)
    return seen


def select_rows(rows: list[dict[str, str]], sample_size: int, scope: str, formats: set[str] | None) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        if formats and row.get("format", "") not in formats:
            continue
        if not row.get("source_text", "").strip():
            continue
        if scope == "missing-target" and has_target(row):
            continue
        if scope == "existing-target-review" and not has_target(row):
            continue
        key = source_key(row)
        if key in seen:
            continue
        seen.add(key)
        selected.append(dict(row))
        if len(selected) >= sample_size:
            break
    return selected


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
    tokens = parse_tokens(row)
    suffix = " ".join(tokens)
    return f"【样例译文】{source}" + (f" {suffix}" if suffix and suffix not in source else "")


def fill_targets(rows: list[dict[str, str]], mode: str) -> list[dict[str, str]]:
    filled: list[dict[str, str]] = []
    for row in rows:
        out = dict(row)
        if mode == "manual":
            out["target_text"] = ""
        elif mode == "reuse-existing":
            out["target_text"] = row_target(row)
        elif mode == "mock-zh":
            out["target_text"] = mock_target(row)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
        filled.append(out)
    return filled


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    output_fields = list(fieldnames)
    if "target_text" not in output_fields:
        output_fields.append("target_text")
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def brief(rows: list[dict[str, str]], mode: str, source_locale: str, target_locale: str) -> str:
    by_format = Counter(row.get("format", "unknown") for row in rows)
    protected = sum(1 for row in rows if parse_tokens(row))
    lines = [
        "# Sample Translation Brief",
        "",
        f"Source locale: `{source_locale}`",
        f"Target locale: `{target_locale}`",
        f"Mode: `{mode}`",
        "",
        "## Counts",
        "",
        f"- Sample rows: {len(rows)}",
        f"- Rows with protected tokens: {protected}",
        "",
        "## Formats",
        "",
    ]
    for fmt, count in by_format.most_common():
        lines.append(f"- {fmt}: {count}")
    lines.extend(
        [
            "",
            "## Instructions",
            "",
            "- Fill `target_text` only.",
            "- Preserve placeholders, tags, variables, escapes, and line-break-sensitive syntax exactly.",
            "- Keep UI strings concise.",
            "- If unsure, leave `target_text` blank rather than guessing.",
            "- After editing, run `generate_patch.py` to create patch/copy output and static QA.",
            "",
            "## Personal-Use Next Step",
            "",
            "Review this sample before translating the full inventory. Continue only if the tone, cost, and patch output feel acceptable.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a low-cost sample translation inventory.")
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--mode", choices=["manual", "mock-zh", "reuse-existing"], default="manual")
    parser.add_argument("--scope", choices=["all", "missing-target", "existing-target-review"], default="all")
    parser.add_argument("--formats", help="Comma-separated format filter, e.g. renpy,localization")
    parser.add_argument("--source-locale", default="en")
    parser.add_argument("--target-locale", default="s-cn")
    args = parser.parse_args()

    if not args.inventory.exists() or not args.inventory.is_file():
        raise SystemExit(f"Inventory file does not exist: {args.inventory}")
    if args.sample_size < 1:
        raise SystemExit("--sample-size must be at least 1")

    rows, fieldnames = read_inventory(args.inventory)
    formats = {item.strip() for item in args.formats.split(",") if item.strip()} if args.formats else None
    selected = select_rows(rows, args.sample_size, args.scope, formats)
    filled = fill_targets(selected, args.mode)

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "sample-to-translate.csv", fill_targets(selected, "manual"), fieldnames)
    write_csv(out / "translated-inventory.sample.csv", filled, fieldnames)
    (out / "sample-translation-brief.md").write_text(
        brief(filled, args.mode, args.source_locale, args.target_locale),
        encoding="utf-8",
    )
    print(f"Wrote sample translation package to {out}")
    print(f"Sample rows: {len(filled)}")
    print(f"Mode: {args.mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
