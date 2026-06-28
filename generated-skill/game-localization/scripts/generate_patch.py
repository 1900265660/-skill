#!/usr/bin/env python3
"""Generate safe localization patch output from a translated inventory.

The script writes patch/copy files into an output directory and never modifies
the source game folder. It is intentionally conservative: unsupported formats
are reported, not edited in place.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


PLACEHOLDER_RE = re.compile(
    r"(\{[^{}\n]+\}|\[[A-Za-z_][^\]\n]*\]|<[/A-Za-z][^>\n]*>|%[0-9.]*[sdif]|"
    r"\$\{[^}\n]+\}|\\[ntr\"']|\{/?[A-Za-z][^{}\n]*\})"
)
SUPPORTED_FORMATS = {"renpy", "localization", "subtitles", "mission-txt"}
TRANSLATION_COLUMNS = ("target_text", "translated_text", "new_target_text", "existing_target_text")


@dataclass
class Finding:
    severity: str
    code: str
    unit_id: str
    file_path: str
    key: str
    message: str


@dataclass
class PatchFile:
    source_file: str
    patch_file: str
    format: str
    units: int
    source_sha256: str
    patch_sha256: str
    status: str


def read_inventory(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"Could not decode text file: {path}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens_in_text(text: str) -> list[str]:
    seen: list[str] = []
    for match in PLACEHOLDER_RE.finditer(text or ""):
        token = match.group(0)
        if token not in seen:
            seen.append(token)
    return seen


def target_text(row: dict[str, str]) -> str:
    for column in TRANSLATION_COLUMNS:
        value = row.get(column, "")
        if value and value.strip():
            return value.strip()
    return ""


def patch_rel(path: Path, out_root: Path) -> str:
    return str(path.relative_to(out_root)).replace("\\", "/")


def safe_join(root: Path, rel_path: str) -> Path:
    path = (root / rel_path).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise SystemExit(f"Inventory path escapes project root: {rel_path}")
    return path


def target_locale_path(source_rel: str, source_locale: str, target_locale: str) -> str:
    path = Path(source_rel)
    name = path.name
    source_stem = source_locale.lower()
    if name.lower().startswith(source_stem + "."):
        return str(path.with_name(target_locale + path.suffix)).replace("\\", "/")
    parts = list(path.parts)
    return str(Path(*parts[:-1], target_locale, name)).replace("\\", "/") if len(parts) > 1 else f"{target_locale}/{name}"


def renpy_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def parse_token_json(row: dict[str, str]) -> list[str]:
    raw = row.get("protected_tokens", "")
    if raw:
        try:
            value = json.loads(raw)
            if isinstance(value, list):
                return [str(item) for item in value]
        except json.JSONDecodeError:
            pass
    return tokens_in_text(row.get("source_text", ""))


def validate_row(row: dict[str, str], findings: list[Finding], require_target: bool) -> bool:
    fmt = row.get("format", "")
    target = target_text(row)
    if fmt not in SUPPORTED_FORMATS:
        findings.append(Finding("warning", "unsupported_format", row.get("unit_id", ""), row.get("file_path", ""), row.get("key", ""), f"Unsupported patch format `{fmt}`."))
        return False
    if require_target and not target:
        findings.append(Finding("blocker", "missing_target", row.get("unit_id", ""), row.get("file_path", ""), row.get("key", ""), "No translated target text found."))
        return False
    if not target:
        return False
    missing = [token for token in parse_token_json(row) if token not in target]
    if missing:
        findings.append(Finding("blocker", "missing_protected_tokens", row.get("unit_id", ""), row.get("file_path", ""), row.get("key", ""), f"Target is missing protected tokens: {', '.join(missing)}."))
        return False
    return True


def group_rows(rows: Iterable[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get("file_path", "")].append(row)
    return grouped


def write_renpy_patch(rows: list[dict[str, str]], out_root: Path, target_locale: str) -> PatchFile:
    rel_path = f"game/tl/{target_locale}/generated_strings.rpy"
    patch_path = out_root / "patch-files" / rel_path
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"translate {target_locale} strings:",
        "",
    ]
    for row in rows:
        lines.append(f"    old {renpy_quote(row.get('source_text', ''))}")
        lines.append(f"    new {renpy_quote(target_text(row))}")
        lines.append("")
    patch_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return PatchFile(
        source_file=";".join(sorted({row.get("file_path", "") for row in rows})),
        patch_file=patch_rel(patch_path, out_root),
        format="renpy",
        units=len(rows),
        source_sha256="generated",
        patch_sha256=sha256(patch_path),
        status="generated",
    )


def patch_localization(source_text: str, rows: list[dict[str, str]]) -> str:
    targets = {row.get("key", ""): target_text(row) for row in rows if target_text(row)}
    out_lines: list[str] = []
    current_key: str | None = None
    current_value: list[str] = []

    def flush() -> None:
        nonlocal current_key, current_value
        if current_key is None:
            return
        if current_key in targets:
            out_lines.extend(targets[current_key].splitlines() or [""])
        else:
            out_lines.extend(current_value)
        current_key = None
        current_value = []

    for line in source_text.splitlines():
        if line.startswith("`"):
            flush()
            current_key = line[1:].strip()
            out_lines.append(line)
            current_value = []
        elif current_key is not None:
            current_value.append(line)
        else:
            out_lines.append(line)
    flush()
    return "\n".join(out_lines) + "\n"


def patch_subtitles(source_text: str, rows: list[dict[str, str]]) -> str:
    targets = {row.get("key", ""): target_text(row) for row in rows if target_text(row)}
    out_lines: list[str] = []
    block = ""
    index = 0
    body: list[str] = []

    def flush_body() -> None:
        nonlocal body, index
        if block and body:
            key = f"{block}#{index:03d}"
            replacement = targets.get(key)
            out_lines.extend((replacement.splitlines() if replacement else body) or [""])
            index += 1
        body = []

    for raw_line in source_text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("::"):
            flush_body()
            block = line[2:].strip()
            index = 0
            out_lines.append(line)
        elif line.startswith("="):
            flush_body()
            out_lines.append(line)
        elif block and line and not line.startswith("["):
            body.append(line)
        else:
            flush_body()
            out_lines.append(line)
    flush_body()
    return "\n".join(out_lines) + "\n"


def patch_mission_txt(source_text: str, rows: list[dict[str, str]]) -> str:
    by_line: dict[int, str] = {}
    for row in rows:
        match = re.search(r"@L(\d+)$", row.get("key", ""))
        if match and target_text(row):
            by_line[int(match.group(1))] = target_text(row)
    out_lines: list[str] = []
    for line_no, line in enumerate(source_text.splitlines(), start=1):
        if line_no in by_line and "=" in line:
            key, _old = line.split("=", 1)
            out_lines.append(f"{key.rstrip()} = {by_line[line_no]}")
        else:
            out_lines.append(line)
    return "\n".join(out_lines) + "\n"


def write_file_patch(project: Path, out_root: Path, source_rel: str, rows: list[dict[str, str]], source_locale: str, target_locale: str) -> PatchFile:
    fmt = rows[0].get("format", "")
    source_path = safe_join(project, source_rel)
    source_text = read_text(source_path)
    if fmt == "localization":
        target_rel = target_locale_path(source_rel, source_locale, target_locale)
        patched = patch_localization(source_text, rows)
    elif fmt == "subtitles":
        target_rel = target_locale_path(source_rel, source_locale, target_locale)
        patched = patch_subtitles(source_text, rows)
    elif fmt == "mission-txt":
        target_rel = source_rel
        patched = patch_mission_txt(source_text, rows)
    else:
        raise SystemExit(f"Unsupported file patch format: {fmt}")
    patch_path = out_root / "patch-files" / target_rel
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    patch_path.write_text(patched, encoding="utf-8", newline="\n")
    return PatchFile(
        source_file=source_rel,
        patch_file=patch_rel(patch_path, out_root),
        format=fmt,
        units=len(rows),
        source_sha256=sha256(source_path),
        patch_sha256=sha256(patch_path),
        status="generated",
    )


def markdown_report(patches: list[PatchFile], findings: list[Finding], rows: list[dict[str, str]], args: argparse.Namespace) -> str:
    severity_counts = Counter(finding.severity for finding in findings)
    blockers = severity_counts.get("blocker", 0)
    warnings = severity_counts.get("warning", 0)
    decision = "BLOCKED" if blockers else "PASS_WITH_WARNINGS" if warnings else "PASS"
    lines = [
        "# Patch QA Report",
        "",
        f"Project: `{args.project}`",
        f"Inventory: `{args.inventory}`",
        f"Target locale: `{args.target_locale}`",
        f"Decision: **{decision}**",
        "",
        "## Counts",
        "",
        f"- Inventory rows read: {len(rows)}",
        f"- Patch files generated: {len(patches)}",
        f"- Blockers: {blockers}",
        f"- Warnings: {warnings}",
        "",
        "## Generated Patch Files",
        "",
    ]
    if patches:
        for patch in patches:
            lines.append(f"- `{patch.patch_file}` from `{patch.source_file}` ({patch.format}, {patch.units} units)")
    else:
        lines.append("- None")
    lines.extend(["", "## Findings", ""])
    if findings:
        for finding in findings[:100]:
            lines.append(f"- **{finding.severity.upper()} {finding.code}** `{finding.file_path}` `{finding.key}`: {finding.message}")
        if len(findings) > 100:
            lines.append(f"- ... {len(findings) - 100} more")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- Source project was not modified.",
            "- Patch output can be removed by deleting the output directory.",
            "- Runtime/screenshot/OCR QA is not covered by this static Phase 4 report.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(out: Path, patches: list[PatchFile], findings: list[Finding], rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "patch-manifest.json").write_text(json.dumps([asdict(patch) for patch in patches], indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "translation-qa-report.json").write_text(json.dumps([asdict(finding) for finding in findings], indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "translation-qa-report.md").write_text(markdown_report(patches, findings, rows, args), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate safe localization patch output from a translated inventory.")
    parser.add_argument("project", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-locale", default="en")
    parser.add_argument("--target-locale", default="s-cn")
    parser.add_argument("--sample-size", type=int, default=0, help="Limit patch generation to the first N valid translated rows.")
    parser.add_argument("--require-target", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    out = args.out.resolve()
    if not project.exists() or not project.is_dir():
        raise SystemExit(f"Project folder does not exist or is not a directory: {project}")
    if not args.inventory.exists() or not args.inventory.is_file():
        raise SystemExit(f"Inventory file does not exist: {args.inventory}")
    try:
        out.relative_to(project)
    except ValueError:
        pass
    else:
        raise SystemExit("Output directory must not be inside the source project folder.")

    rows = read_inventory(args.inventory)
    findings: list[Finding] = []
    valid_rows = [row for row in rows if validate_row(row, findings, args.require_target)]
    if args.sample_size > 0:
        findings.append(
            Finding(
                "warning",
                "sample_patch",
                "",
                "",
                "",
                f"Sample mode enabled; only the first {args.sample_size} valid translated rows are included.",
            )
        )
        valid_rows = valid_rows[: args.sample_size]

    patches: list[PatchFile] = []
    renpy_rows = [row for row in valid_rows if row.get("format") == "renpy"]
    if renpy_rows:
        patches.append(write_renpy_patch(renpy_rows, out, args.target_locale))

    for source_rel, file_rows in group_rows(row for row in valid_rows if row.get("format") != "renpy").items():
        if not source_rel:
            continue
        patches.append(write_file_patch(project, out, source_rel, file_rows, args.source_locale, args.target_locale))

    write_outputs(out, patches, findings, rows, args)
    blockers = sum(1 for finding in findings if finding.severity == "blocker")
    warnings = sum(1 for finding in findings if finding.severity == "warning")
    print(f"Wrote patch output to {out}")
    print(f"Patch files: {len(patches)}")
    print(f"Blockers: {blockers}")
    print(f"Warnings: {warnings}")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
