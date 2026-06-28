#!/usr/bin/env python3
"""Extract translation inventory from safe, text-based localization lanes.

This script reads a game folder and writes inventory artifacts to an output
directory. It does not modify the input folder and does not call translation
providers.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


SUPPORTED_EXTENSIONS = {".localization", ".subtitles", ".rpy", ".json", ".csv", ".tsv", ".txt"}
SKIP_DIRS = {".git", ".svn", "__pycache__", "node_modules", "logs"}
SUPPORT_FILE_RE = re.compile(r"(license|licenses|notice|readme|credits|changelog|steamworks\.net)", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"(\{[^{}\n]+\}|\[[A-Za-z_][^\]\n]*\]|<[/A-Za-z][^>\n]*>|%[0-9.]*[sdif]|"
    r"\$\{[^}\n]+\}|\\[ntr\"']|\{/?[A-Za-z][^{}\n]*\})"
)
RENPLY_DIALOGUE_RE = re.compile(r'^\s*(?:(?P<speaker>[A-Za-z_][\w.]*)\s+)?["“](?P<text>.+?)["”]\s*$')
RENPLY_MENU_RE = re.compile(r'^\s*["“](?P<text>.+?)["”]\s*:\s*$')
WORD_RE = re.compile(r"\b[A-Z][A-Za-z][A-Za-z'_-]{2,}\b")
TECHNICAL_JSON_RE = re.compile(r"(unityservicesprojectconfiguration|package-lock|manifest|app\.info)", re.IGNORECASE)
TECHNICAL_STRING_RE = re.compile(
    r"(^\d+(\.\d+)+$|^[a-f0-9]{16,}$|^[a-z0-9_.-]+\.[a-z0-9_.-]+|Version=|PublicKeyToken=)",
    re.IGNORECASE,
)


@dataclass
class Unit:
    unit_id: str
    group_id: str
    format: str
    file_path: str
    key: str
    context: str
    speaker: str
    source_text: str
    existing_target_text: str = ""
    protected_tokens: list[str] = field(default_factory=list)
    char_count: int = 0
    confidence: str = "medium"
    notes: str = ""


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def iter_files(root: Path, max_files: int) -> Iterable[Path]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            if count >= max_files:
                return
            count += 1
            yield Path(dirpath) / filename


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def is_support_file(path: Path) -> bool:
    lowered = str(path).replace("\\", "/").lower()
    return "/logs/" in lowered or SUPPORT_FILE_RE.search(path.name) is not None


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def group_id(text: str) -> str:
    return hashlib.sha1(normalize_text(text).encode("utf-8")).hexdigest()[:12]


def protected_tokens(text: str) -> list[str]:
    seen: list[str] = []
    for match in PLACEHOLDER_RE.finditer(text):
        token = match.group(0)
        if token not in seen:
            seen.append(token)
    return seen


def looks_mojibake(text: str) -> bool:
    if "�" in text:
        return True
    signals = ("鍗", "璺", "鎴", "绔", "閫", "鏃", "锛", "涓", "涔")
    return sum(text.count(s) for s in signals) >= 2


def arrow_wrapped(text: str) -> bool:
    stripped = text.strip()
    return stripped.startswith("<-") and stripped.endswith("->")


def make_unit(
    root: Path,
    path: Path,
    fmt: str,
    key: str,
    source_text: str,
    context: str = "",
    speaker: str = "",
    existing_target_text: str = "",
    confidence: str = "medium",
    notes: str = "",
) -> Unit | None:
    source_text = source_text.strip()
    if not source_text:
        return None
    rel_path = rel(path, root)
    unit_key = f"{rel_path}:{key}"
    gid = group_id(source_text)
    unit_id = hashlib.sha1(unit_key.encode("utf-8")).hexdigest()[:16]
    target_note = ""
    if existing_target_text and looks_mojibake(existing_target_text):
        target_note = "existing target text may be mojibake"
    joined_notes = "; ".join(n for n in (notes, target_note) if n)
    return Unit(
        unit_id=unit_id,
        group_id=gid,
        format=fmt,
        file_path=rel_path,
        key=key,
        context=context,
        speaker=speaker,
        source_text=source_text,
        existing_target_text=existing_target_text.strip(),
        protected_tokens=protected_tokens(source_text),
        char_count=len(source_text),
        confidence=confidence,
        notes="; ".join(n for n in (joined_notes, "arrow_wrapped" if arrow_wrapped(source_text) else "") if n),
    )


def parse_backtick_pairs(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("#"):
            continue
        if line.startswith("`"):
            if current_key is not None:
                entries[current_key] = "\n".join(current_lines).strip()
            current_key = line[1:].strip()
            current_lines = []
            continue
        if current_key is not None:
            current_lines.append(line)
    if current_key is not None:
        entries[current_key] = "\n".join(current_lines).strip()
    return entries


def parse_subtitles(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    block = ""
    speaker = ""
    index = 0
    lines: list[str] = []

    def flush() -> None:
        nonlocal index, lines
        body = "\n".join(lines).strip()
        if block and body:
            key = f"{block}#{index:03d}"
            entries[key] = {"text": body, "speaker": speaker, "block": block}
            index += 1
        lines = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("::"):
            flush()
            block = line[2:].strip()
            speaker = ""
            index = 0
            continue
        if line.startswith("="):
            flush()
            parts = line[1:].strip().split()
            speaker = parts[0] if parts else ""
            continue
        if block and line and not line.startswith("["):
            lines.append(line)
    flush()
    return entries


def locale_stem(path: Path) -> str:
    return path.stem.lower()


def target_peer(path: Path, source_locale: str, target_locale: str) -> Path | None:
    stem = locale_stem(path)
    if stem != source_locale.lower():
        return None
    peer = path.with_name(f"{target_locale}{path.suffix}")
    return peer if peer.exists() else None


def extract_localization(root: Path, path: Path, source_locale: str, target_locale: str) -> list[Unit]:
    text = read_text(path)
    if text is None:
        return []
    source_entries = parse_backtick_pairs(text)
    target_entries: dict[str, str] = {}
    peer = target_peer(path, source_locale, target_locale)
    if peer:
        peer_text = read_text(peer)
        if peer_text is not None:
            target_entries = parse_backtick_pairs(peer_text)
    units: list[Unit] = []
    for key, value in source_entries.items():
        unit = make_unit(
            root,
            path,
            "localization",
            key,
            value,
            context=f"locale={source_locale}",
            existing_target_text=target_entries.get(key, ""),
            confidence="high",
        )
        if unit:
            units.append(unit)
    return units


def extract_subtitles(root: Path, path: Path, source_locale: str, target_locale: str) -> list[Unit]:
    text = read_text(path)
    if text is None:
        return []
    source_entries = parse_subtitles(text)
    target_entries: dict[str, dict[str, str]] = {}
    peer = target_peer(path, source_locale, target_locale)
    if peer:
        peer_text = read_text(peer)
        if peer_text is not None:
            target_entries = parse_subtitles(peer_text)
    units: list[Unit] = []
    for key, data in source_entries.items():
        target = target_entries.get(key, {})
        unit = make_unit(
            root,
            path,
            "subtitles",
            key,
            data["text"],
            context=data.get("block", ""),
            speaker=data.get("speaker", ""),
            existing_target_text=target.get("text", ""),
            confidence="high",
        )
        if unit:
            units.append(unit)
    return units


def extract_renpy(root: Path, path: Path) -> list[Unit]:
    text = read_text(path)
    if text is None:
        return []
    units: list[Unit] = []
    current_label = ""
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("label "):
            current_label = stripped.removeprefix("label ").split(":", 1)[0].strip()
        match = RENPLY_DIALOGUE_RE.match(line) or RENPLY_MENU_RE.match(line)
        if not match:
            continue
        value = match.group("text")
        speaker = match.groupdict().get("speaker") or ""
        unit = make_unit(
            root,
            path,
            "renpy",
            f"L{line_no}",
            value,
            context=current_label,
            speaker=speaker,
            confidence="medium",
        )
        if unit:
            units.append(unit)
    return units


def walk_json(value: Any, prefix: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from walk_json(child, next_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            next_prefix = f"{prefix}[{index}]"
            yield from walk_json(child, next_prefix)
    elif isinstance(value, str):
        yield prefix, value


def extract_json(root: Path, path: Path) -> list[Unit]:
    if TECHNICAL_JSON_RE.search(path.name):
        return []
    text = read_text(path)
    if text is None:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    units: list[Unit] = []
    for key, value in walk_json(data):
        if TECHNICAL_STRING_RE.search(value):
            continue
        unit = make_unit(root, path, "json", key, value, confidence="medium")
        if unit:
            units.append(unit)
    return units


def extract_mission_txt(root: Path, path: Path) -> list[Unit]:
    if path.name.lower() != "mission.txt":
        return []
    text = read_text(path)
    if text is None:
        return []
    units: list[Unit] = []
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = [part.strip() for part in stripped.split("=", 1)]
        if key.lower() not in {"title", "description", "subtitle", "displayname", "display_name"}:
            continue
        unit = make_unit(
            root,
            path,
            "mission-txt",
            f"{key}@L{line_no}",
            value,
            context="Unity StreamingAssets mission.txt",
            confidence="medium",
            notes="custom key/value mission text",
        )
        if unit:
            units.append(unit)
    return units


def extract_csv_like(root: Path, path: Path, source_locale: str, target_locale: str) -> list[Unit]:
    text = read_text(path)
    if text is None:
        return []
    dialect = csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel
    rows = list(csv.reader(text.splitlines(), dialect=dialect))
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]
    source_index = None
    target_index = None
    key_index = 0
    for candidate in (source_locale.lower(), "en", "source", "text", "value"):
        if candidate in header:
            source_index = header.index(candidate)
            break
    if target_locale.lower() in header:
        target_index = header.index(target_locale.lower())
    if "key" in header:
        key_index = header.index("key")
    if source_index is None:
        source_index = 1 if len(rows[0]) > 1 else 0
    units: list[Unit] = []
    for row_no, row in enumerate(rows[1:], start=2):
        if source_index >= len(row):
            continue
        key = row[key_index] if key_index < len(row) and row[key_index] else f"row_{row_no}"
        target = row[target_index] if target_index is not None and target_index < len(row) else ""
        unit = make_unit(root, path, "csv", key, row[source_index], existing_target_text=target, confidence="medium")
        if unit:
            units.append(unit)
    return units


def should_extract(path: Path, source_locale: str) -> bool:
    if is_support_file(path):
        return False
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False
    if ext == ".txt" and path.name.lower() != "mission.txt":
        return False
    if ext in {".localization", ".subtitles"}:
        return locale_stem(path) == source_locale.lower()
    return True


def extract_units(root: Path, files: Iterable[Path], source_locale: str, target_locale: str) -> tuple[list[Unit], list[dict[str, str]]]:
    units: list[Unit] = []
    skipped: list[dict[str, str]] = []
    for path in files:
        ext = path.suffix.lower()
        if not should_extract(path, source_locale):
            continue
        before = len(units)
        if ext == ".localization":
            units.extend(extract_localization(root, path, source_locale, target_locale))
        elif ext == ".subtitles":
            units.extend(extract_subtitles(root, path, source_locale, target_locale))
        elif ext == ".rpy":
            units.extend(extract_renpy(root, path))
        elif ext == ".json":
            units.extend(extract_json(root, path))
        elif ext in {".csv", ".tsv"}:
            units.extend(extract_csv_like(root, path, source_locale, target_locale))
        elif ext == ".txt":
            units.extend(extract_mission_txt(root, path))
        if before == len(units):
            skipped.append({"path": rel(path, root), "reason": "no supported translatable units found"})
    return units, skipped


def glossary_markdown(units: list[Unit], source_locale: str, target_locale: str) -> str:
    words: Counter[str] = Counter()
    for unit in units:
        for match in WORD_RE.finditer(unit.source_text):
            word = match.group(0)
            if len(word) > 3 and word.lower() not in {"this", "that", "with", "from", "when", "what", "your"}:
                words[word] += 1
    lines = [
        "# Glossary Draft",
        "",
        f"Source locale: `{source_locale}`",
        f"Target locale: `{target_locale}`",
        "",
        "## Style Profile",
        "",
        "- Default: natural Simplified Chinese for game UI/dialogue.",
        "- Preserve placeholders, variables, tags, line-break-sensitive syntax, and speaker identity.",
        "- Keep UI labels concise.",
        "- Mark jokes, lore terms, and character voice for human review.",
        "",
        "## Candidate Terms",
        "",
        "| Term | Count | Proposed Translation | Notes |",
        "| --- | ---: | --- | --- |",
    ]
    for term, count in words.most_common(40):
        lines.append(f"| {term} | {count} |  |  |")
    if not words:
        lines.append("|  | 0 |  | No candidate terms found. |")
    lines.extend(
        [
            "",
            "## Do Not Translate",
            "",
            "- File paths",
            "- Placeholder tokens such as `{name}`, `%s`, `[player_name]`, and `<color=...>`",
            "- Engine labels, script labels, and command names",
            "",
        ]
    )
    return "\n".join(lines)


def inventory_markdown(units: list[Unit], skipped: list[dict[str, str]], source_locale: str, target_locale: str) -> str:
    by_format = Counter(unit.format for unit in units)
    duplicate_groups = sum(1 for count in Counter(unit.group_id for unit in units).values() if count > 1)
    target_risks = sum(1 for unit in units if "mojibake" in unit.notes)
    total_chars = sum(unit.char_count for unit in units)
    protected_count = sum(1 for unit in units if unit.protected_tokens)
    lines = [
        "# Translation Inventory Summary",
        "",
        f"Source locale: `{source_locale}`",
        f"Target locale: `{target_locale}`",
        "",
        "## Counts",
        "",
        f"- Units: {len(units)}",
        f"- Source characters: {total_chars}",
        f"- Units with protected tokens: {protected_count}",
        f"- Duplicate source-text groups: {duplicate_groups}",
        f"- Existing target mojibake risks: {target_risks}",
        f"- Skipped supported files with no units: {len(skipped)}",
        "",
        "## Formats",
        "",
    ]
    for fmt, count in by_format.most_common():
        lines.append(f"- {fmt}: {count}")
    lines.extend(["", "## Next Step", ""])
    if units:
        lines.append("Review `translation-inventory.csv` and `glossary.md`; do not call a translation provider until budget and placeholder validation are approved.")
    else:
        lines.append("No extractable units found. Return to audit and choose another lane or tool.")
    return "\n".join(lines)


def write_outputs(out: Path, units: list[Unit], skipped: list[dict[str, str]], source_locale: str, target_locale: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rows = [asdict(unit) for unit in units]
    for row in rows:
        row["protected_tokens"] = json.dumps(row["protected_tokens"], ensure_ascii=False)
    fieldnames = [
        "unit_id",
        "group_id",
        "format",
        "file_path",
        "key",
        "context",
        "speaker",
        "source_text",
        "existing_target_text",
        "protected_tokens",
        "char_count",
        "confidence",
        "notes",
    ]
    with (out / "translation-inventory.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    (out / "translation-inventory.json").write_text(
        json.dumps([asdict(unit) for unit in units], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out / "inventory-summary.md").write_text(inventory_markdown(units, skipped, source_locale, target_locale), encoding="utf-8")
    (out / "glossary.md").write_text(glossary_markdown(units, source_locale, target_locale), encoding="utf-8")
    (out / "skipped-files.json").write_text(json.dumps(skipped, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract localization inventory from supported text lanes.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-locale", default="en")
    parser.add_argument("--target-locale", default="s-cn")
    parser.add_argument("--max-files", type=int, default=50000)
    args = parser.parse_args()

    root = args.project.resolve()
    out = args.out.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project folder does not exist or is not a directory: {root}")
    try:
        out.relative_to(root)
    except ValueError:
        pass
    else:
        raise SystemExit("Output directory must not be inside the audited project folder.")

    files = list(iter_files(root, args.max_files))
    units, skipped = extract_units(root, files, args.source_locale, args.target_locale)
    write_outputs(out, units, skipped, args.source_locale, args.target_locale)
    print(f"Wrote inventory to {out}")
    print(f"Units: {len(units)}")
    print(f"Skipped supported files with no units: {len(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
