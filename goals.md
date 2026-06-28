# Goals

## Goal: Implement Phase 1 Packaged-Game Audit Skill Skeleton

Objective:

Create a reusable `game-localization` skill skeleton that can inspect an installed game folder read-only and generate a localization feasibility, risk, cost/time, and tool-requirement audit before translation or file edits.

Inputs:

- `product-spec.md`
- `design-brief.md`
- `development-plan.md`
- Target skill root where the new skill should be created.
- Sample or synthetic packaged-game fixtures.
- Discovery answers in `discovery-answers.md`.

Scope:

- Create `SKILL.md` for the game localization skill.
- Create references for engine patterns, risk rubric, cost control, and patch safety.
- Create a read-only scanner script.
- Generate `localization-audit.md` from a project path.
- Include safety rules for no mutation, no DRM/anti-cheat bypass, high-level-only handling for protected games, and explicit uncertainty labels.

Non-scope:

- Actual translation.
- Provider/MCP integration.
- Applying patches.
- OCR/image editing.
- Build execution.
- Full engine-specific extractors.
- Reading real Steam game folders unless separately approved for audit.

Acceptance criteria:

- Given an installed game folder path, the skill produces an audit report without modifying the game folder.
- Given Godot-like, Ren'Py-like, and generic packaged-game fixtures, the scanner identifies likely engine markers or reports unknown with evidence.
- Given readable text files, the audit estimates rough text volume, characters, likely token count, cost range, and time range.
- Given image assets, the audit lists them as potential image-text lane candidates without claiming they contain text unless OCR is configured.
- Given likely font assets, the audit flags CJK/glyph risk for Chinese localization.
- Given no build/test/launch commands, the audit marks runtime verification as unavailable.
- Given unsupported binary or packed files, the audit marks them as unsupported/risky rather than attempting to patch them.
- Given DRM/anti-cheat indicators, the audit stays high-level and does not provide modification steps.

Verification:

- Run scanner fixture tests.
- Compare project file modification timestamps before and after audit.
- Inspect generated `localization-audit.md`.
- Run lint/typecheck for scanner if the repo provides commands.

Loop policy:

- Continue implementing, testing, and fixing until Phase 1 acceptance passes.
- If engine detection or file scanning produces the same incorrect result after two fix attempts, stop and research known engine/project patterns before continuing.
- Stop only for a named blocker such as missing target skill root, missing runtime, or unclear supported language/runtime decision.

Report:

- Summarize files created.
- List fixtures tested.
- Include audit output path.
- State unresolved risks and next phase recommendation.

## Goal: Execute Full Game Localization Skill MVP

Objective:

Build the full MVP described in `development-plan.md`: packaged-game audit, inventory extraction, glossary/style draft, cost/time estimation, provider/manual translation route, patch generation, static QA, runtime/screenshot/OCR QA where possible, and image-text handoff.

Inputs:

- `product-spec.md`
- `design-brief.md`
- `development-plan.md`
- Current skill implementation
- Fixture projects, including a small Ren'Py demo fixture for the first end-to-end path.
- Optional translation provider or mock provider

Scope:

- Execute Phases 1 through 5.
- Keep documents updated when implementation decisions change the skill behavior.
- Use mock providers where real provider credentials are unavailable.

Non-scope:

- DRM bypass.
- Anti-cheat bypass.
- Universal binary patching.
- Fully automatic image art recreation.
- Professional human localization QA.

Acceptance criteria:

- Every phase acceptance criterion in `development-plan.md` passes.
- The skill can audit a fixture project, produce inventory, estimate cost/time, translate via mock/manual path, generate a safe patch, and validate it.
- Placeholder mismatches block release.
- Budget gates prevent unapproved provider calls.
- Image text remains a separate verified/unverified lane.
- Runtime/screenshot/OCR verification is either performed with evidence or marked blocked.
- Review and release reports honestly state what was and was not tested.

Verification:

- Run all scanner, extraction, cost, provider mock, writer, and validation tests.
- Run fixture end-to-end smoke test.
- Inspect generated inventory, patch, QA report, review report, and release report.
- Perform manual review of at least one translated fixture file.

Loop policy:

- Work phase by phase.
- Do not proceed from translation to application until cost gate and placeholder protection pass.
- If the same failure persists after two attempts, stop and research official docs or known issue reports before continuing.
- Stop if real provider credentials, OCR plugin, or runnable game environment are required and unavailable.

Report:

- Final status by phase.
- Files changed.
- Tests/checks run.
- Cost estimate and actual mock/real usage.
- Release readiness.
- Open risks and recommended next goal.
