#!/usr/bin/env python3
"""Run an offline fixture smoke test for the game-localization skill.

The harness validates the current safe chain without calling remote providers,
OCR engines, paid services, or modifying the fixture source folder.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


OWNER_MARKER = ".fixture-smoke-owned.json"
ALLOWED_OCR_GATES = {
    "READY_WITHOUT_OCR",
    "READY_FOR_LOCAL_OR_MANUAL_OCR",
    "READY_FOR_MANUAL_SCREENSHOT_REVIEW",
    "READY_FOR_USER_APPROVED_PAID_OCR_STEP",
}


@dataclass
class StageResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass
class AssertionResult:
    name: str
    passed: bool
    detail: str


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def generated_root() -> Path:
    return skill_root().parent


def default_fixture() -> Path:
    return skill_root() / "assets" / "fixtures" / "renpy-small"


def default_output() -> Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return generated_root() / "smoke-output" / "renpy-small" / timestamp


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def prepare_output(out: Path, fixture: Path, overwrite: bool) -> None:
    out = out.resolve()
    fixture = fixture.resolve()
    if is_relative_to(out, fixture):
        raise SystemExit("Output directory must not be inside the fixture source folder.")
    if out.exists():
        if not overwrite:
            raise SystemExit(f"Output directory already exists; pass --overwrite for harness-owned paths: {out}")
        marker = out / OWNER_MARKER
        if not marker.exists():
            raise SystemExit(f"Refusing to overwrite an unmarked directory: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / OWNER_MARKER).write_text(
        json.dumps({"owned_by": "game-localization fixture smoke harness"}, indent=2),
        encoding="utf-8",
    )


def file_hashes(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = str(path.relative_to(root)).replace("\\", "/")
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def run_stage(name: str, command: list[str], cwd: Path) -> StageResult:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    result = StageResult(name, command, proc.returncode, proc.stdout.strip(), proc.stderr.strip())
    print(f"[{name}] exit={proc.returncode}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def add_assert(assertions: list[AssertionResult], name: str, passed: bool, detail: str) -> None:
    assertions.append(AssertionResult(name, passed, detail))


def required_file(assertions: list[AssertionResult], path: Path, label: str) -> None:
    add_assert(assertions, f"artifact:{label}", path.exists() and path.is_file(), str(path))


def validate_results(out: Path, before_hashes: dict[str, str], after_hashes: dict[str, str]) -> list[AssertionResult]:
    assertions: list[AssertionResult] = []
    required = {
        "audit_json": out / "audit" / "localization-audit.json",
        "audit_md": out / "audit" / "localization-audit.md",
        "inventory_csv": out / "inventory" / "translation-inventory.csv",
        "inventory_json": out / "inventory" / "translation-inventory.json",
        "validation_json": out / "validation" / "inventory-validation.json",
        "validation_md": out / "validation" / "inventory-validation.md",
        "cost_json": out / "cost" / "cost-estimate.json",
        "dry_run_json": out / "cost" / "provider-dry-run.json",
        "sample_csv": out / "sample" / "translated-inventory.sample.csv",
        "patch_manifest": out / "patch" / "patch-manifest.json",
        "patch_qa": out / "patch" / "translation-qa-report.json",
        "ocr_plan": out / "ocr-plan" / "ocr-qa-plan.json",
        "ocr_candidates": out / "ocr-plan" / "ocr-candidates.csv",
    }
    for label, path in required.items():
        required_file(assertions, path, label)

    add_assert(assertions, "fixture_source_unchanged", before_hashes == after_hashes, "fixture file hash snapshot matches")

    if required["inventory_csv"].exists():
        inventory_rows = read_csv(required["inventory_csv"])
        add_assert(assertions, "inventory_has_rows", len(inventory_rows) > 0, f"rows={len(inventory_rows)}")
    if required["validation_json"].exists():
        findings = read_json(required["validation_json"])
        blockers = sum(1 for item in findings if item.get("severity") == "blocker")
        add_assert(assertions, "validation_no_blockers", blockers == 0, f"blockers={blockers}")
    if required["cost_json"].exists():
        estimate = read_json(required["cost_json"])
        gate = estimate.get("gate_decision", "")
        add_assert(assertions, "cost_gate_manual_ready", gate == "READY_FOR_LOCAL_OR_MANUAL_STEP", f"gate={gate}")
    if required["sample_csv"].exists():
        sample_rows = read_csv(required["sample_csv"])
        targets = [row.get("target_text", "").strip() for row in sample_rows]
        add_assert(
            assertions,
            "sample_targets_filled",
            bool(sample_rows) and all(targets),
            f"rows={len(sample_rows)}, filled={sum(1 for item in targets if item)}",
        )
    if required["patch_manifest"].exists():
        patches = read_json(required["patch_manifest"])
        add_assert(assertions, "patch_files_generated", len(patches) > 0, f"patch_files={len(patches)}")
    if required["patch_qa"].exists():
        findings = read_json(required["patch_qa"])
        blockers = sum(1 for item in findings if item.get("severity") == "blocker")
        add_assert(assertions, "patch_qa_no_blockers", blockers == 0, f"blockers={blockers}")
    if required["ocr_plan"].exists():
        plan_data = read_json(required["ocr_plan"])
        gate = plan_data.get("plan", {}).get("gate_decision", "")
        add_assert(assertions, "ocr_gate_not_blocked", gate in ALLOWED_OCR_GATES, f"gate={gate}")
    return assertions


def markdown_report(args: argparse.Namespace, stages: list[StageResult], assertions: list[AssertionResult], out: Path) -> str:
    failed = [item for item in assertions if not item.passed]
    command_failures = [stage for stage in stages if stage.returncode != 0]
    decision = "FAIL" if failed or command_failures else "PASS"
    lines = [
        "# Fixture Smoke Report",
        "",
        f"Decision: **{decision}**",
        f"Fixture: `{args.fixture}`",
        f"Output: `{out}`",
        f"Target language: `{args.target_language}`",
        f"Target locale: `{args.target_locale}`",
        "",
        "## Stages",
        "",
        "| Stage | Exit |",
        "| --- | ---: |",
    ]
    for stage in stages:
        lines.append(f"| {stage.name} | {stage.returncode} |")
    lines.extend(["", "## Assertions", "", "| Assertion | Result | Detail |", "| --- | --- | --- |"])
    for assertion in assertions:
        result = "PASS" if assertion.passed else "FAIL"
        detail = assertion.detail.replace("|", "\\|")
        lines.append(f"| {assertion.name} | {result} | `{detail}` |")
    lines.extend(
        [
            "",
            "## Safety",
            "",
            "- No remote provider, MCP, OCR engine, cloud OCR, or vision model was called.",
            "- The fixture source folder hash snapshot was compared before and after the run.",
            "- Output artifacts were written outside the fixture source folder.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(out: Path, args: argparse.Namespace, stages: list[StageResult], assertions: list[AssertionResult]) -> None:
    report = {
        "fixture": str(args.fixture),
        "output": str(out),
        "target_language": args.target_language,
        "target_locale": args.target_locale,
        "stages": [asdict(stage) for stage in stages],
        "assertions": [asdict(item) for item in assertions],
        "decision": "FAIL" if any(stage.returncode for stage in stages) or any(not item.passed for item in assertions) else "PASS",
    }
    (out / "fixture-smoke-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "fixture-smoke-report.md").write_text(markdown_report(args, stages, assertions, out), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the offline game-localization fixture smoke test.")
    parser.add_argument("--fixture", type=Path, default=default_fixture())
    parser.add_argument("--out", type=Path, default=default_output())
    parser.add_argument("--target-language", default="zh-Hans")
    parser.add_argument("--source-locale", default="en")
    parser.add_argument("--target-locale", default="s-cn")
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    scripts = skill_root() / "scripts"
    fixture = args.fixture.resolve()
    out = args.out.resolve()
    if not fixture.exists() or not fixture.is_dir():
        raise SystemExit(f"Fixture folder does not exist: {fixture}")
    if args.sample_size < 1:
        raise SystemExit("--sample-size must be at least 1")

    prepare_output(out, fixture, args.overwrite)
    before_hashes = file_hashes(fixture)
    stages: list[StageResult] = []

    py_files = sorted(scripts.glob("*.py"))
    stages.append(run_stage("py_compile", [sys.executable, "-m", "py_compile", *[str(path) for path in py_files]], skill_root()))
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "audit",
                [
                    sys.executable,
                    str(scripts / "scan_project.py"),
                    str(fixture),
                    "--out",
                    str(out / "audit"),
                    "--target-language",
                    args.target_language,
                ],
                skill_root(),
            )
        )
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "inventory",
                [
                    sys.executable,
                    str(scripts / "extract_inventory.py"),
                    str(fixture),
                    "--out",
                    str(out / "inventory"),
                    "--source-locale",
                    args.source_locale,
                    "--target-locale",
                    args.target_locale,
                ],
                skill_root(),
            )
        )
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "validation",
                [
                    sys.executable,
                    str(scripts / "validate_inventory.py"),
                    str(out / "inventory" / "translation-inventory.csv"),
                    "--out",
                    str(out / "validation"),
                    "--target-locale",
                    args.target_locale,
                ],
                skill_root(),
            )
        )
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "cost",
                [
                    sys.executable,
                    str(scripts / "estimate_cost.py"),
                    str(out / "inventory" / "translation-inventory.csv"),
                    "--out",
                    str(out / "cost"),
                    "--route",
                    "manual_csv",
                    "--provider",
                    "manual_csv",
                    "--model",
                    "manual_csv",
                    "--validation-json",
                    str(out / "validation" / "inventory-validation.json"),
                    "--audit-json",
                    str(out / "audit" / "localization-audit.json"),
                ],
                skill_root(),
            )
        )
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "sample",
                [
                    sys.executable,
                    str(scripts / "prepare_sample_translation.py"),
                    str(out / "inventory" / "translation-inventory.csv"),
                    "--out",
                    str(out / "sample"),
                    "--mode",
                    "mock-zh",
                    "--sample-size",
                    str(args.sample_size),
                    "--source-locale",
                    args.source_locale,
                    "--target-locale",
                    args.target_locale,
                ],
                skill_root(),
            )
        )
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "patch",
                [
                    sys.executable,
                    str(scripts / "generate_patch.py"),
                    str(fixture),
                    str(out / "sample" / "translated-inventory.sample.csv"),
                    "--out",
                    str(out / "patch"),
                    "--source-locale",
                    args.source_locale,
                    "--target-locale",
                    args.target_locale,
                    "--require-target",
                ],
                skill_root(),
            )
        )
    if stages[-1].returncode == 0:
        stages.append(
            run_stage(
                "ocr-plan",
                [
                    sys.executable,
                    str(scripts / "plan_ocr_qa.py"),
                    str(out / "audit" / "localization-audit.json"),
                    "--out",
                    str(out / "ocr-plan"),
                    "--sample-size",
                    str(args.sample_size),
                ],
                skill_root(),
            )
        )

    after_hashes = file_hashes(fixture)
    assertions = validate_results(out, before_hashes, after_hashes)
    write_report(out, args, stages, assertions)

    failed_commands = [stage for stage in stages if stage.returncode != 0]
    failed_assertions = [item for item in assertions if not item.passed]
    print(f"Wrote fixture smoke report to {out}")
    print(f"Decision: {'FAIL' if failed_commands or failed_assertions else 'PASS'}")
    print(f"Assertions: {len(assertions) - len(failed_assertions)} passed, {len(failed_assertions)} failed")
    return 1 if failed_commands or failed_assertions else 0


if __name__ == "__main__":
    raise SystemExit(main())
