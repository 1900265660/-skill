#!/usr/bin/env python3
"""Read-only packaged-game localization audit.

The script scans a game folder, writes audit files to an output directory, and
never modifies the input folder. It is intentionally conservative: packed and
binary files are classified as risk evidence, not unpacked.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
    ".xml",
    ".po",
    ".pot",
    ".localization",
    ".subtitles",
    ".ini",
    ".cfg",
    ".rpy",
    ".gd",
    ".translation",
    ".strings",
    ".lang",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".svg", ".tga", ".dds"}
FONT_EXTENSIONS = {".ttf", ".otf", ".fnt", ".font", ".woff", ".woff2"}
ARCHIVE_EXTENSIONS = {".pck", ".pak", ".rpa", ".unity3d", ".assets", ".bundle", ".bank", ".asar", ".package"}
EXECUTABLE_EXTENSIONS = {".exe", ".app", ".x86_64", ".x86", ".sh"}
SKIP_DIRS = {".git", ".svn", "__pycache__", "node_modules"}

TEXT_RE = re.compile(r"[A-Za-z][A-Za-z0-9 ,.!?'\";:\-(){}\[\]<>%/$\\]{3,}")
HARD_PROTECTED_RE = re.compile(
    r"(easyanticheat|easy anti cheat|battleye|denuvo|anti[-_ ]?cheat|\bvac\b|\bdrm\b)",
    re.IGNORECASE,
)
PLATFORM_RE = re.compile(r"(steam_api|steamworks|gog|epicgames|eos_sdk)", re.IGNORECASE)


@dataclass
class FileHit:
    path: str
    size: int
    ext: str
    reason: str


@dataclass
class TextStats:
    files_sampled: int = 0
    readable_files: int = 0
    candidate_files: int = 0
    source_characters: int = 0
    unique_strings: int = 0
    sample_strings: list[str] = field(default_factory=list)
    candidate_paths: list[str] = field(default_factory=list)
    support_text_files: int = 0


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


def read_text_sample(path: Path, max_bytes: int) -> str | None:
    try:
        data = path.read_bytes()[:max_bytes]
    except OSError:
        return None
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def is_support_text(path_rel: str) -> bool:
    lowered = path_rel.lower().replace("\\", "/")
    name = Path(lowered).name
    if lowered.startswith("logs/") or "/logs/" in lowered:
        return True
    support_names = ("license", "licenses", "notice", "readme", "credits", "changelog", "steamworks.net")
    return any(part in name for part in support_names)


def detect_engines(root: Path, files: list[Path]) -> list[dict[str, object]]:
    names = [rel(p, root).lower() for p in files]
    base_names = [p.name.lower() for p in files]
    hits: list[dict[str, object]] = []

    def add(name: str, evidence: list[str], confidence: str) -> None:
        if evidence:
            hits.append({"engine": name, "confidence": confidence, "evidence": evidence[:10]})

    add(
        "Godot",
        [n for n in names if n.endswith(".pck") or n.endswith("project.godot") or ".godot/" in n or ".import/" in n],
        "high" if any(n.endswith(".pck") for n in names) else "medium",
    )
    add(
        "Ren'Py",
        [n for n in names if n.startswith("renpy/") or "/renpy/" in n or n.endswith(".rpy") or n.endswith(".rpa")],
        "high",
    )
    add(
        "Unity",
        [n for n in names if "_data/" in n or n.endswith("globalgamemanagers") or "assembly-csharp.dll" in n],
        "high",
    )
    add(
        "Unreal",
        [n for n in names if "/content/paks/" in n or n.endswith(".pak") or "/binaries/win64/" in n],
        "high",
    )
    add(
        "RPG Maker-like",
        [n for n in names if n.startswith("www/data/") or "/www/data/" in n or "rpg_core.js" in n or "rpg_managers.js" in n],
        "medium",
    )
    add(
        "Custom/localization files",
        [n for n in names if "/strings/" in n and (n.endswith(".localization") or n.endswith(".subtitles"))],
        "medium",
    )
    if not hits:
        executable_names = [n for n in base_names if Path(n).suffix.lower() in EXECUTABLE_EXTENSIONS]
        if executable_names:
            add("Unknown packaged game", executable_names, "low")
    return hits


def estimate_tokens(characters: int, target_language: str) -> dict[str, int]:
    input_tokens = math.ceil(characters / 4) if characters else 0
    if target_language.lower().startswith(("zh", "cn", "chinese")):
        output_tokens = math.ceil(characters / 2.2) if characters else 0
    else:
        output_tokens = math.ceil(characters / 3.5) if characters else 0
    return {"estimated_input_tokens": input_tokens, "estimated_output_tokens": output_tokens}


def estimate_cost(tokens: dict[str, int], in_price: float | None, out_price: float | None) -> dict[str, object]:
    if in_price is None or out_price is None:
        return {
            "priced": False,
            "note": "No provider prices supplied. Pass --usd-per-million-input and --usd-per-million-output for money estimate.",
        }
    cost = (tokens["estimated_input_tokens"] / 1_000_000 * in_price) + (
        tokens["estimated_output_tokens"] / 1_000_000 * out_price
    )
    return {
        "priced": True,
        "usd_per_million_input": in_price,
        "usd_per_million_output": out_price,
        "estimated_usd": round(cost, 4),
    }


def estimate_time(strings: int, characters: int) -> dict[str, str]:
    review_minutes = max(5, math.ceil(strings / 35))
    audit_minutes = "5-20 min"
    extraction_minutes = "10-60 min" if characters else "blocked until text is extractable"
    return {
        "audit_time": audit_minutes,
        "translation_provider_time": "minutes once inventory is approved",
        "human_review_time": f"{review_minutes}-{review_minutes * 3} min rough review range",
        "extraction_time": extraction_minutes,
    }


def recommendation(
    engine_hits: list[dict[str, object]], archives: list[FileHit], text: TextStats, protected_hits: list[FileHit]
) -> str:
    if protected_hits:
        return "HIGH_LEVEL_ONLY"
    archive_exts = {hit.ext for hit in archives}
    has_godot = any(hit["engine"] == "Godot" for hit in engine_hits)
    has_renpy = any(hit["engine"] == "Ren'Py" for hit in engine_hits)
    if text.source_characters > 500 and (has_renpy or not archive_exts):
        return "PROCEED"
    if has_godot and ".pck" in archive_exts:
        return "CAUTION"
    if text.source_characters > 0:
        return "CAUTION"
    if archive_exts:
        return "DO_NOT_TRANSLATE"
    return "CAUTION"


def risk_summary(rec: str) -> str:
    return {
        "PROCEED": "Readable text paths exist and no major protected-game indicator was found.",
        "CAUTION": "Feasible signals exist, but package/tool/font/OCR/manual QA risk remains.",
        "HIGH_LEVEL_ONLY": "Protected-game indicators were found. Keep assessment high-level and do not provide modification steps.",
        "DO_NOT_TRANSLATE": "No practical low-risk text path was found from read-only evidence.",
    }[rec]


def markdown_report(result: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# Localization Audit")
    lines.append("")
    lines.append(f"Project path: `{result['project_path']}`")
    lines.append(f"Target language: `{result['target_language']}`")
    lines.append(f"Recommendation: **{result['recommendation']}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(str(result["risk_summary"]))
    lines.append("")
    lines.append("## Engine Signals")
    lines.append("")
    engines = result["engine_signals"]
    if engines:
        for engine in engines:  # type: ignore[assignment]
            lines.append(f"- {engine['engine']} ({engine['confidence']}): {', '.join(engine['evidence'][:5])}")
    else:
        lines.append("- No confident engine marker found.")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    counts = result["counts"]  # type: ignore[assignment]
    for key, value in counts.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Text Estimate")
    lines.append("")
    text = result["text_estimate"]  # type: ignore[assignment]
    for key, value in text.items():
        if key != "sample_strings":
            lines.append(f"- {key}: {value}")
    samples = text.get("sample_strings", [])
    if samples:
        lines.append("")
        lines.append("Sample strings:")
        for sample in samples[:10]:
            safe = sample.replace("\n", "\\n")
            lines.append(f"- `{safe[:160]}`")
    lines.append("")
    lines.append("## Cost And Time")
    lines.append("")
    cost = result["cost_estimate"]  # type: ignore[assignment]
    for key, value in cost.items():
        lines.append(f"- {key}: {value}")
    time_est = result["time_estimate"]  # type: ignore[assignment]
    for key, value in time_est.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Risk Evidence")
    lines.append("")
    for section in ("archives", "image_assets", "font_assets", "executables", "platform_indicators", "protected_indicators"):
        hits = result[section]  # type: ignore[index]
        lines.append(f"### {section.replace('_', ' ').title()}")
        lines.append("")
        if hits:
            for hit in hits[:25]:
                lines.append(f"- `{hit['path']}` ({hit['size']} bytes)")
            if len(hits) > 25:
                lines.append(f"- ... {len(hits) - 25} more")
        else:
            lines.append("- None found in scan limit.")
        lines.append("")
    lines.append("## Next Step")
    lines.append("")
    rec = result["recommendation"]
    if rec == "PROCEED":
        lines.append("Prepare translation inventory and glossary/style draft.")
    elif rec == "CAUTION":
        lines.append("Ask the user whether to continue, and identify required extraction/patch tools before translation.")
    elif rec == "HIGH_LEVEL_ONLY":
        lines.append("Stop at high-level assessment. Do not provide modification steps.")
    else:
        lines.append("Do not translate from current evidence. Ask for source/modding files or a safer target.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only packaged-game localization audit.")
    parser.add_argument("project", type=Path, help="Game folder or modding workspace to audit.")
    parser.add_argument("--out", type=Path, required=True, help="Output directory for audit files.")
    parser.add_argument("--target-language", default="zh-Hans")
    parser.add_argument("--max-files", type=int, default=20000)
    parser.add_argument("--max-text-file-bytes", type=int, default=2_000_000)
    parser.add_argument("--usd-per-million-input", type=float, default=None)
    parser.add_argument("--usd-per-million-output", type=float, default=None)
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
    archives: list[FileHit] = []
    images: list[FileHit] = []
    fonts: list[FileHit] = []
    executables: list[FileHit] = []
    protected_hits: list[FileHit] = []
    platform_hits: list[FileHit] = []
    text_stats = TextStats()
    unique_strings: set[str] = set()

    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        ext = path.suffix.lower()
        path_rel = rel(path, root)
        if ext in ARCHIVE_EXTENSIONS:
            archives.append(FileHit(path_rel, size, ext, "packed/archive resource"))
        if ext in IMAGE_EXTENSIONS:
            images.append(FileHit(path_rel, size, ext, "possible image text or UI art"))
        if ext in FONT_EXTENSIONS:
            fonts.append(FileHit(path_rel, size, ext, "font/glyph support candidate"))
        if ext in EXECUTABLE_EXTENSIONS:
            executables.append(FileHit(path_rel, size, ext, "launch/build candidate"))
        if HARD_PROTECTED_RE.search(path_rel):
            protected_hits.append(FileHit(path_rel, size, ext, "protected-game indicator"))
        elif PLATFORM_RE.search(path_rel):
            platform_hits.append(FileHit(path_rel, size, ext, "platform/launcher indicator"))
        if ext in TEXT_EXTENSIONS and size <= args.max_text_file_bytes:
            text_stats.files_sampled += 1
            sample = read_text_sample(path, args.max_text_file_bytes)
            if sample is None:
                continue
            text_stats.readable_files += 1
            if is_support_text(path_rel):
                text_stats.support_text_files += 1
                continue
            matches = [m.group(0).strip() for m in TEXT_RE.finditer(sample)]
            matches = [m for m in matches if len(m) >= 4]
            if matches:
                text_stats.candidate_files += 1
                if len(text_stats.candidate_paths) < 100:
                    text_stats.candidate_paths.append(path_rel)
            for match in matches:
                unique_strings.add(match)
                text_stats.source_characters += len(match)
                if len(text_stats.sample_strings) < 20:
                    text_stats.sample_strings.append(match)

    text_stats.unique_strings = len(unique_strings)
    engine_hits = detect_engines(root, files)
    tokens = estimate_tokens(text_stats.source_characters, args.target_language)
    cost = estimate_cost(tokens, args.usd_per_million_input, args.usd_per_million_output)
    rec = recommendation(engine_hits, archives, text_stats, protected_hits)

    result: dict[str, object] = {
        "project_path": str(root),
        "target_language": args.target_language,
        "recommendation": rec,
        "risk_summary": risk_summary(rec),
        "engine_signals": engine_hits,
        "counts": {
            "files_scanned": len(files),
            "archives": len(archives),
            "image_assets": len(images),
            "font_assets": len(fonts),
            "executables": len(executables),
            "protected_indicators": len(protected_hits),
            "platform_indicators": len(platform_hits),
        },
        "text_estimate": {
            "files_sampled": text_stats.files_sampled,
            "readable_files": text_stats.readable_files,
            "candidate_files": text_stats.candidate_files,
            "support_text_files_excluded": text_stats.support_text_files,
            "source_characters": text_stats.source_characters,
            "unique_strings": text_stats.unique_strings,
            **tokens,
            "sample_strings": text_stats.sample_strings,
            "candidate_paths": text_stats.candidate_paths,
        },
        "cost_estimate": cost,
        "time_estimate": estimate_time(text_stats.unique_strings, text_stats.source_characters),
        "archives": [hit.__dict__ for hit in archives],
        "image_assets": [hit.__dict__ for hit in images],
        "font_assets": [hit.__dict__ for hit in fonts],
        "executables": [hit.__dict__ for hit in executables],
        "protected_indicators": [hit.__dict__ for hit in protected_hits],
        "platform_indicators": [hit.__dict__ for hit in platform_hits],
    }

    out.mkdir(parents=True, exist_ok=True)
    (out / "localization-audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "localization-audit.md").write_text(markdown_report(result), encoding="utf-8")
    with (out / "text-samples.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["sample"])
        for sample in text_stats.sample_strings:
            writer.writerow([sample])
    print(f"Wrote audit to {out}")
    print(f"Recommendation: {rec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
