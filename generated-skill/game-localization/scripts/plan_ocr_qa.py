#!/usr/bin/env python3
"""Plan low-cost OCR/screenshot QA without running OCR.

This script reads Phase 1 audit output and optionally a screenshot folder, then
selects a small candidate set for visual text checks. It intentionally does not
call OCR engines, cloud APIs, vision models, or modify game files.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tga", ".dds"}

TEXT_HINTS = (
    "text",
    "font",
    "fonts",
    "title",
    "logo",
    "menu",
    "menus",
    "ui",
    "hud",
    "button",
    "buttons",
    "label",
    "labels",
    "dialog",
    "dialogue",
    "subtitle",
    "subtitles",
    "caption",
    "credits",
    "tutorial",
    "chapter",
    "quest",
    "mission",
    "story",
    "ending",
    "intro",
    "outro",
    "settings",
    "options",
    "pause",
    "loading",
)

LOW_VALUE_HINTS = (
    "icon",
    "icons",
    "portrait",
    "avatar",
    "background",
    "bg",
    "backs",
    "effect",
    "effects",
    "particle",
    "particles",
    "normal",
    "roughness",
    "metallic",
    "albedo",
    "diffuse",
    "specular",
    "shadow",
    "lightmap",
    "mask",
    "noise",
    "probe",
)


@dataclass
class Candidate:
    source: str
    path: str
    size: int
    ext: str
    score: int
    reasons: list[str]


@dataclass
class OcrPlan:
    audit_json: str
    screenshots_dir: str | None
    total_audited_images: int
    total_screenshots: int
    candidate_images: int
    selected_for_first_pass: int
    recommendation: str
    recommended_default_tool: str
    fallback_tools: list[str]
    estimated_local_ocr_minutes: tuple[float, float]
    estimated_manual_review_minutes: tuple[float, float]
    cloud_ocr_cost_usd: float | None
    vision_model_cost_usd: float | None
    gate_decision: str
    gate_reasons: list[str]
    notes: list[str]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        raise SystemExit(f"Audit JSON does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def iter_screenshots(root: Path) -> list[Candidate]:
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Screenshot folder does not exist: {root}")
    hits: list[Candidate] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in {".git", "__pycache__"}]
        for filename in filenames:
            path = Path(dirpath) / filename
            ext = path.suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            candidate = score_image("screenshot", rel(path, root), size, ext)
            candidate.score += 4
            candidate.reasons.append("runtime screenshot")
            hits.append(candidate)
    return hits


def score_image(source: str, path: str, size: int, ext: str) -> Candidate:
    lowered = path.lower().replace("\\", "/")
    parts = [part for part in lowered.replace(".", "/").replace("_", "/").replace("-", "/").split("/") if part]
    path_obj = Path(lowered)
    basename = path_obj.stem.replace("_", " ").replace("-", " ")
    parent = path_obj.parent.name.replace("_", " ").replace("-", " ")
    score = 0
    reasons: list[str] = []

    matched_text = [hint for hint in TEXT_HINTS if hint in parts or hint in lowered]
    if matched_text:
        filename_hits = [hint for hint in TEXT_HINTS if hint in basename.split() or hint in basename]
        parent_hits = [hint for hint in TEXT_HINTS if hint in parent.split() or hint in parent]
        path_only_hits = [hint for hint in matched_text if hint not in filename_hits and hint not in parent_hits]
        score += min(10, len(filename_hits) * 4 + len(parent_hits) * 2 + len(path_only_hits))
        reasons.append("text-like path: " + ", ".join(matched_text[:4]))

    matched_low = [hint for hint in LOW_VALUE_HINTS if hint in parts or hint in lowered]
    if matched_low:
        filename_hits = [hint for hint in LOW_VALUE_HINTS if hint in basename.split() or hint in basename]
        parent_hits = [hint for hint in LOW_VALUE_HINTS if hint in parent.split() or hint in parent]
        path_only_hits = [hint for hint in matched_low if hint not in filename_hits and hint not in parent_hits]
        score -= min(8, len(filename_hits) * 4 + len(parent_hits) * 2 + len(path_only_hits))
        reasons.append("low-value path: " + ", ".join(matched_low[:4]))

    if ext == ".svg":
        score += 4
        reasons.append("svg may contain readable text")
    elif ext in {".png", ".webp"}:
        score += 1
        reasons.append("common UI image format")
    elif ext in {".dds", ".tga"}:
        score -= 1
        reasons.append("may require texture conversion before OCR")

    if size >= 500_000:
        score += 2
        reasons.append("large image")
    elif size < 4_000:
        score -= 2
        reasons.append("tiny image likely icon/marker")

    if not reasons:
        reasons.append("no strong signal")
    return Candidate(source=source, path=path, size=size, ext=ext, score=score, reasons=reasons)


def candidates_from_audit(audit: dict[str, Any]) -> list[Candidate]:
    items = audit.get("image_assets", [])
    candidates: list[Candidate] = []
    for item in items:
        path = str(item.get("path", ""))
        ext = str(item.get("ext", Path(path).suffix.lower()))
        size = int(item.get("size", 0) or 0)
        candidates.append(score_image("asset", path, size, ext))
    return candidates


def choose_recommendation(total_images: int, screenshots: int, selected: int, high_score: int) -> tuple[str, str, list[str], list[str]]:
    notes: list[str] = []
    if selected == 0 and total_images >= 100:
        return "MANUAL_SCREENSHOTS_FIRST", "manual screenshot review", ["RapidOCR", "PaddleOCR", "cloud OCR for small samples"], [
            "Many image assets exist, but path/size signals did not find a reliable OCR sample.",
            "Capture representative runtime screenshots before asset OCR.",
        ]
    if selected == 0:
        return "SKIP_OCR_FOR_NOW", "manual screenshot review", ["RapidOCR", "PaddleOCR", "Tesseract"], [
            "No good image candidates were found from path/size signals.",
            "Continue with text lane and runtime manual review.",
        ]
    if screenshots:
        notes.append("Screenshots are better than raw assets for finding untranslated UI because they show what players actually see.")
        return "SCREENSHOT_OCR_SAMPLE", "RapidOCR", ["PaddleOCR", "EasyOCR", "Tesseract", "cloud OCR"], notes
    if total_images >= 500 and high_score < 20:
        notes.append("The project has many images but few strong text hints; avoid full-asset OCR until screenshots prove it is useful.")
        return "MANUAL_SCREENSHOTS_FIRST", "manual screenshot review", ["RapidOCR", "PaddleOCR", "cloud OCR for small samples"], notes
    if total_images >= 200:
        notes.append("Image volume is high, so keep OCR to a capped candidate sample before expanding.")
        return "LOCAL_PREFILTER_THEN_SAMPLE", "RapidOCR", ["PaddleOCR", "EasyOCR", "Tesseract"], notes
    return "LOCAL_OCR_SAMPLE", "RapidOCR", ["PaddleOCR", "EasyOCR", "Tesseract"], notes


def estimate_minutes(count: int, per_item_low: float, per_item_high: float) -> tuple[float, float]:
    if count <= 0:
        return 0.0, 0.0
    return round(max(1.0, count * per_item_low), 1), round(max(1.0, count * per_item_high), 1)


def estimate_cost_per_1000(count: int, usd_per_1000: float | None) -> float | None:
    if usd_per_1000 is None:
        return None
    return round(count / 1000 * usd_per_1000, 4)


def gate(
    selected: int,
    recommendation: str,
    cloud_cost: float | None,
    vision_cost: float | None,
    budget: float | None,
    approve_budget: bool,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    paid_costs = [value for value in (cloud_cost, vision_cost) if value is not None]
    total_paid = sum(paid_costs) if paid_costs else None
    if selected <= 0 and recommendation == "MANUAL_SCREENSHOTS_FIRST":
        return "READY_FOR_MANUAL_SCREENSHOT_REVIEW", ["Capture representative screenshots before deciding whether OCR is useful."]
    if selected <= 0:
        return "READY_WITHOUT_OCR", ["No selected image sample needs OCR."]
    if total_paid is None:
        return "READY_FOR_LOCAL_OR_MANUAL_OCR", [
            "No paid OCR price was supplied; use local/manual tools or provide current pricing for cloud/vision routes."
        ]
    if budget is None:
        return "BLOCKED_NO_BUDGET_FOR_PAID_OCR", ["Paid OCR/vision cost is known, but no budget was supplied."]
    if total_paid > budget:
        return "BLOCKED_OCR_BUDGET_EXCEEDED", [f"Estimated paid OCR/vision cost ${total_paid:.4f} exceeds budget ${budget:.4f}."]
    if not approve_budget:
        return "BLOCKED_PENDING_OCR_BUDGET_APPROVAL", ["Budget was supplied but not explicitly approved."]
    reasons.append(f"Estimated paid OCR/vision cost ${total_paid:.4f} is within approved budget ${budget:.4f}.")
    return "READY_FOR_USER_APPROVED_PAID_OCR_STEP", reasons


def markdown_report(plan: OcrPlan, selected: list[Candidate], all_candidates: list[Candidate], args: argparse.Namespace) -> str:
    lines = [
        "# OCR QA Plan",
        "",
        f"Audit JSON: `{args.audit_json}`",
        f"Screenshots dir: `{args.screenshots_dir or ''}`",
        "",
        "## Decision",
        "",
        f"- Recommendation: **{plan.recommendation}**",
        f"- Default tool: `{plan.recommended_default_tool}`",
        f"- Fallback tools: {', '.join(plan.fallback_tools)}",
        f"- Gate: **{plan.gate_decision}**",
    ]
    for reason in plan.gate_reasons:
        lines.append(f"- {reason}")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Total audited image assets: {plan.total_audited_images}",
            f"- Total screenshots supplied: {plan.total_screenshots}",
            f"- Candidate images after scoring: {plan.candidate_images}",
            f"- Selected for first pass: {plan.selected_for_first_pass}",
            "",
            "## Cost And Time",
            "",
            f"- Local OCR time: {plan.estimated_local_ocr_minutes[0]:.1f}-{plan.estimated_local_ocr_minutes[1]:.1f} minutes",
            f"- Manual review time: {plan.estimated_manual_review_minutes[0]:.1f}-{plan.estimated_manual_review_minutes[1]:.1f} minutes",
            f"- Cloud OCR cost: `{format_cost(plan.cloud_ocr_cost_usd)}`",
            f"- Vision model cost: `{format_cost(plan.vision_model_cost_usd)}`",
            "",
            "## Notes",
            "",
        ]
    )
    for note in plan.notes:
        lines.append(f"- {note}")
    lines.extend(
        [
            "- This script does not run OCR. It only chooses a small first-pass sample and reports gates.",
            "- Use screenshots before full asset OCR whenever possible.",
            "- Treat positive OCR hits as QA evidence, not final translation output.",
            "",
            "## First-Pass Candidates",
            "",
            "| Rank | Source | Score | Size | Path | Reasons |",
            "| ---: | --- | ---: | ---: | --- | --- |",
        ]
    )
    for index, candidate in enumerate(selected, start=1):
        reasons = "; ".join(candidate.reasons)
        safe_path = candidate.path.replace("|", "\\|")
        safe_reasons = reasons.replace("|", "\\|")
        lines.append(f"| {index} | {candidate.source} | {candidate.score} | {candidate.size} | `{safe_path}` | {safe_reasons} |")
    if not selected:
        lines.append("|  |  |  |  |  | No selected candidates. |")
    if len(all_candidates) > len(selected):
        lines.extend(
            [
                "",
                f"{len(all_candidates) - len(selected)} additional candidates were omitted from the first-pass table.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def format_cost(value: float | None) -> str:
    if value is None:
        return "unknown"
    return f"${value:.4f}"


def write_outputs(out: Path, plan: OcrPlan, selected: list[Candidate], all_candidates: list[Candidate], args: argparse.Namespace) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "ocr-qa-plan.json").write_text(
        json.dumps(
            {
                "plan": asdict(plan),
                "selected_candidates": [asdict(item) for item in selected],
                "all_candidates": [asdict(item) for item in all_candidates],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (out / "ocr-qa-plan.md").write_text(markdown_report(plan, selected, all_candidates, args), encoding="utf-8")
    with (out / "ocr-candidates.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["source", "path", "size", "ext", "score", "reasons", "selected"])
        writer.writeheader()
        selected_paths = {(item.source, item.path) for item in selected}
        for item in all_candidates:
            writer.writerow(
                {
                    "source": item.source,
                    "path": item.path,
                    "size": item.size,
                    "ext": item.ext,
                    "score": item.score,
                    "reasons": json.dumps(item.reasons, ensure_ascii=False),
                    "selected": (item.source, item.path) in selected_paths,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan low-cost OCR/screenshot QA without running OCR.")
    parser.add_argument("audit_json", type=Path, help="localization-audit.json from scan_project.py")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--screenshots-dir", type=Path)
    parser.add_argument("--sample-size", type=int, default=30)
    parser.add_argument("--min-score", type=int, default=2)
    parser.add_argument("--cloud-ocr-usd-per-1000", type=float)
    parser.add_argument("--vision-model-usd-per-image", type=float)
    parser.add_argument("--budget-usd", type=float)
    parser.add_argument("--approve-budget", action="store_true")
    args = parser.parse_args()

    if args.sample_size < 1:
        raise SystemExit("--sample-size must be at least 1")

    audit = read_json(args.audit_json)
    asset_candidates = candidates_from_audit(audit)
    screenshot_candidates = iter_screenshots(args.screenshots_dir) if args.screenshots_dir else []
    all_candidates = asset_candidates + screenshot_candidates
    viable = [item for item in all_candidates if item.score >= args.min_score]
    viable.sort(key=lambda item: (item.score, item.size), reverse=True)
    selected = viable[: args.sample_size]
    high_score = sum(1 for item in viable if item.score >= 5)
    recommendation, default_tool, fallback_tools, notes = choose_recommendation(
        total_images=len(asset_candidates),
        screenshots=len(screenshot_candidates),
        selected=len(selected),
        high_score=high_score,
    )
    local_minutes = estimate_minutes(len(selected), 0.05, 0.25)
    review_minutes = estimate_minutes(len(selected), 0.5, 2.0)
    cloud_cost = estimate_cost_per_1000(len(selected), args.cloud_ocr_usd_per_1000)
    vision_cost = None
    if args.vision_model_usd_per_image is not None:
        vision_cost = round(len(selected) * args.vision_model_usd_per_image, 4)
    gate_decision, gate_reasons = gate(len(selected), recommendation, cloud_cost, vision_cost, args.budget_usd, args.approve_budget)
    plan = OcrPlan(
        audit_json=str(args.audit_json.resolve()),
        screenshots_dir=str(args.screenshots_dir.resolve()) if args.screenshots_dir else None,
        total_audited_images=len(asset_candidates),
        total_screenshots=len(screenshot_candidates),
        candidate_images=len(viable),
        selected_for_first_pass=len(selected),
        recommendation=recommendation,
        recommended_default_tool=default_tool,
        fallback_tools=fallback_tools,
        estimated_local_ocr_minutes=local_minutes,
        estimated_manual_review_minutes=review_minutes,
        cloud_ocr_cost_usd=cloud_cost,
        vision_model_cost_usd=vision_cost,
        gate_decision=gate_decision,
        gate_reasons=gate_reasons,
        notes=notes,
    )
    write_outputs(args.out.resolve(), plan, selected, viable, args)
    print(f"Wrote OCR QA plan to {args.out.resolve()}")
    print(f"Recommendation: {plan.recommendation}")
    print(f"Selected candidates: {plan.selected_for_first_pass}")
    print(f"Gate decision: {plan.gate_decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
