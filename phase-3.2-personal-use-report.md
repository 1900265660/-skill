# Phase 3.2 Personal-Use Reframe

Date: 2026-06-24

## Scope

The `game-localization` skill has been reframed from a commercial delivery estimator toward a low-cost personal localization assistant.

## Change

Default recommendations now prioritize:

- Cheap sample translation first.
- Safe visible text lanes first.
- Patch/copy output instead of in-place edits.
- Static QA before runtime automation.
- Image/OCR, art text, deep archive tooling, and commercial delivery estimates as opt-in later lanes.

## Files Updated

- `product-spec.md`
- `development-plan.md`
- `release-report.md`
- `decisions.md`
- `PROJECT_STATE.md`
- `TODO.md`
- `personal-use-quickstart.md`
- `generated-skill/game-localization/SKILL.md`
- `generated-skill/game-localization/references/personal-use-mode.md`
- `generated-skill/game-localization/references/cost-control.md`
- `generated-skill/game-localization/references/translation-quality.md`

## Product Rule

For personal-use mode, never lead with commercial delivery cost. Lead with the cheapest reversible next step:

1. Audit.
2. Extract safe text lane.
3. Translate 50-100 sample strings.
4. Validate placeholders.
5. Generate patch/copy.
6. Let the user decide whether to continue.

## Next Implementation Implication

Phase 4 should implement a sample translation and patch flow before a full-batch translation flow.
