# Discovery Answers

Date: 2026-06-24

## Product Form

The desired product should feel plug-and-play for people. If a standalone app is too expensive to build and maintain, the preferred first form is a cost-effective Codex/Claude Code skill.

Decision:

- MVP form: skill-first.
- Future option: standalone app only if the workflow proves valuable and repeatable.

## Target Users

Primary users:

- Independent fan translation groups.
- Ordinary players.
- Mod authors.

## Input Game Type

Primary input is an already packaged game, not a source project.

Known target examples for later audit:

- `E:\SteamLibrary\steamapps\common\Tactical Breach Wizards`
- `E:\SteamLibrary\steamapps\common\Order of the Sinking Star Demo`

The latter is known by the user to be a custom engine and already Chinese-localized, but with poor localization quality.

## Engine Priority

First priority:

- Godot.

Second priority:

- Unknown engine detection from packaged game folders.

## First Output

The skill's first step should be a risk and cost-effectiveness assessment.

If operation difficulty is too high, the skill should recommend not translating rather than pushing forward.

## Project Reading Scope

The AI should read and infer the game structure when the user does not know it. It may inspect broad project/game directories, but should begin read-only.

## Risk Dimensions

The assessment should cover:

- Text volume.
- Text-location dispersion.
- Ratio of image-based text.
- Font support.
- Whether the game can be built or run.
- Ease of rollback.
- Ease of modification.
- Required tools or support.

## Assessment Format

Use qualitative judgment. Show the difficulty clearly and let the user decide whether the project is worth doing.

## Translation Style

Support configurable styles. These can mostly be prompt/style-guide differences.

The user should be able to customize style configuration.

## Glossary And Termbase

The skill should generate an initial glossary/style guide/termbase draft and let the user modify it.

## Translation Provider Integration

Start simple. Define provider/MCP/model interfaces first rather than building full integrations in v1.

## Cost Control

Estimate:

- Tokens.
- Characters.
- Approximate money cost.
- Approximate time cost.

## Bug Handling

The skill should create a report and support automatic fix or rollback where possible.

## QA Scope

Desired QA includes:

- Static file format checks.
- Running available build/test commands where possible.
- Launching the game and taking screenshots where possible.
- OCR/vision-model checks to detect untranslated UI text.

This implies a vision model or OCR lane may be needed.

## Image Text / Art Text Approach

The user asks for a suitable plan. Recommended interpretation:

- This is not only "multi-model collaboration".
- The better architecture is lane-based:
  - deterministic unpack/scan/extract scripts first
  - text translation lane
  - OCR/vision detection lane
  - image editing/art-text lane
  - font/glyph lane
  - QA reviewer lane

Images and stylized text should be discovered and reported in v1, with optional handoff to OCR/image-editing tools later.

## Output Mode

Generate patches by default.

## Legal / Protected Games

For games without clear permission or with DRM/anti-cheat concerns, the skill should only provide high-level assessment and not provide modification steps.

## Minimum Successful Demo

First demo target:

- A small Ren'Py project.
- Scan text.
- Estimate cost.
- Translate into Chinese.
- Generate patch.
- Pass placeholder checks.
