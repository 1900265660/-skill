# Product Spec

## Summary

Build a reusable "电子游戏翻译 skill" for Codex or Claude Code. The skill inspects an already packaged game or modding workspace read-only, identifies the likely engine and where translatable text or image text may live, estimates localization difficulty, risk, cost, and time, then recommends whether the project is worth attempting. When the project is feasible and permitted, it extracts or prepares text, translates through a chosen model/interface, generates a patch by default, and verifies that the output is structurally safe.

The first version should be skill-first rather than standalone-app-first. It should focus on audit, feasibility, patch generation, and QA for games where modification is practical. Godot is the first engine priority, but the minimum demo can use a small Ren'Py project because its text extraction/patching path is easier to prove end to end.

## Target Users

- Independent fan translation groups.
- Ordinary players who want to assess whether a game can realistically be localized.
- Mod authors.
- AI-assisted users who want a plug-and-play skill before investing in a standalone localization app.

## Problem

Game localization is not just translating strings. For packaged games, the user may not know the engine, file layout, archive format, text encoding, font system, or whether modification is practical at all. Text may be scattered across resource tables, loose data files, images, font atlases, dialogue files, UI assets, subtitle files, binary archives, and engine-specific localization systems. Naive AI translation can break placeholders, code syntax, encodings, layouts, fonts, or game startup. Users need to know whether a translation job is feasible, safe, affordable, and reversible before spending effort or model credits.

## Current Workaround

Users manually inspect installed game folders, guess engines from file names, search for readable strings, run ad hoc tools, use runtime OCR/text hookers, or edit loose JSON/CSV/script files by hand. They often discover too late that the game uses packed archives, missing CJK fonts, image text, checksums, or custom formats. Runtime tools help players read some games, but they do not produce clean patches and usually do not estimate engineering difficulty or cost.

## Desired Outcome

Given an installed game folder or modding workspace path, the skill can:

1. Inspect the folder read-only and identify likely engine/framework, packaging format, text storage locations, font assets, image-text candidates, and runnable executable.
2. Produce a localization audit with qualitative difficulty, risk, cost/time estimate, required tools, and a proceed/caution/do-not-translate recommendation.
3. Extract translatable units with context and protected tokens.
4. Generate an initial glossary/style guide/termbase draft for user editing.
5. Translate using configured model/interface under a budget.
6. Generate a reviewable patch by default.
7. Run validation and report bugs, unresolved risks, screenshot/OCR findings, and next corrections.

## Core Flows

1. Packaged-game audit:
   - User provides installed game folder path, target language, source language if known, and permission/modding constraints.
   - Skill scans file tree read-only, detects engine signals, packed archives, loose data files, executables, font assets, image assets, localization files, and possible launch/build/test commands.
   - Skill writes a risk and cost-effectiveness report before modifying anything.

2. Scope and risk decision:
   - Skill classifies work into lanes: engine-native localization, loose structured data, script/dialogue files, packed archives, image/textures, fonts/glyphs, runtime OCR/vision, executable/build/run QA, and unknowns.
   - Skill estimates difficulty and recommends proceed, proceed with caution, high-level assessment only, or do not translate.

3. Extraction:
   - Skill extracts candidate text units with file path, key/id, surrounding context, speaker if available, protected tokens, and confidence.
   - Skill deduplicates repeated strings and marks strings that require human context.

4. Translation:
   - Skill translates in batches through a selected provider:
     - built-in LLM prompt/style profile
     - external translation MCP
     - local model
     - manual CSV handoff
   - Skill enforces glossary, style guide, placeholder preservation, length hints, and budget caps.

5. Application:
   - Skill writes changes as a patch by default.
   - Skill avoids modifying binary/unknown assets unless a supported adapter exists.

6. QA and correction:
   - Skill validates placeholder parity, syntax/format validity, encoding, missing translations, duplicate keys, line length risk, and build/test status.
   - Skill runs build/tests/launch checks when available and permitted.
   - Skill may take screenshots and use OCR/vision checks to detect remaining untranslated text.
   - Skill produces a bug/fix queue and can revise translations, auto-fix safe structural issues, or roll back patches.

7. Image/art text lane:
   - Skill detects image assets likely containing text and creates an OCR/image-editing handoff.
   - It may call another plugin/agent if configured.
   - It does not claim image text is complete until visual verification passes.

## Requirements

- R1: The skill shall begin with read-only inspection of an installed game folder or modding workspace and produce an audit before editing files.
- R2: The skill shall detect common game engines or frameworks when possible, with Godot as the first priority and Ren'Py as the first end-to-end demo path.
- R3: The skill shall identify text storage candidates by extension, engine conventions, and content patterns.
- R4: The skill shall classify localization lanes: engine-native, structured data, code literal, binary/packed, image/texture, runtime hook/OCR, and unknown.
- R5: The skill shall estimate difficulty, risk, tool requirements, cost, and time before translation.
- R6: The skill shall support a dry run that extracts and estimates without translating or editing.
- R7: The skill shall protect placeholders, markup, escape sequences, interpolation syntax, color tags, control codes, and line-break-sensitive strings.
- R8: The skill shall preserve file encoding, newline style, and formatting where practical.
- R9: The skill shall allow translation provider selection: model name, external MCP, local model, or manual export.
- R10: The skill shall generate an initial glossary, termbase, character-name list, tone guide, and do-not-translate list for user editing.
- R11: The skill shall deduplicate identical source strings while preserving per-location context.
- R12: The skill shall track cost using estimated characters, input/output tokens, image/OCR counts, provider prices, cache assumptions, estimated time, and actual usage when available.
- R13: The skill shall stop before exceeding a user-configured budget unless the user approves continuation.
- R14: The skill shall produce a reviewable patch by default rather than silently mutating the installed game folder.
- R15: The skill shall run validation after generating or applying translations.
- R16: The skill shall generate a QA report listing bugs, likely layout/font issues, missing translations, screenshot/OCR findings, and unverified areas.
- R17: The skill shall separate image/art-text work from normal text-string work and require explicit plugin/agent handoff for image editing.
- R18: For games without clear permission or with DRM/anti-cheat concerns, the skill shall provide only high-level feasibility assessment and shall not provide modification steps.
- R19: The skill shall record failures as evolution signals only when they are real observed failures.

## Non-Goals

- A universal game cracker or DRM bypass tool.
- Fully automatic high-quality literary localization without human review.
- Guaranteed support for every custom engine or packed binary format.
- Real-time OCR overlay as the primary v1 workflow.
- Automatic image recreation for every art style in v1.
- Replacing professional localization QA for commercial releases.
- Making legal judgments about whether a fan translation is permitted.

## Data And Permissions

- Input data:
  - Installed game folder or modding workspace path.
  - Source and target language.
  - Optional glossary, style guide, character list, and sample translations.
  - Optional model/API/MCP configuration.

- Output data:
  - Project audit.
  - Translation inventory.
  - Cost estimate.
  - Translation files or patch.
  - QA report.
  - Evolution signals.

- Permissions:
  - Read access to game files.
  - Write access only to an output patch directory or user-approved project copy.
  - Network access only when using remote translation/model providers.

- Sensitive data:
  - Unreleased game scripts, story, character names, private source code, API keys, and provider credentials.

## Integrations

- Codex or Claude Code as the host coding agent.
- Optional translation MCP interface definition.
- Optional LLM provider adapter interface definition.
- Optional local model adapter.
- OCR/vision model lane for screenshot and image-text detection.
- Optional image-editing plugin for texture/art text.
- Engine-specific tools:
  - Unity localization tables and asset tables.
  - Unreal localization dashboard/export data.
  - Godot TranslationServer/CSV/gettext files.
  - Ren'Py translation files.
- Optional spreadsheet/CSV export for human translators.

## Edge Cases

- Project has no build command.
  - Skill must run static validation and mark runtime verification as blocked.
- Game stores strings in binary archives.
  - Skill must mark unsupported unless a safe adapter exists.
- Same source string has different meanings in different contexts.
  - Skill must keep per-location context and allow different translations.
- Strings contain variables or formatting tags.
  - Skill must protect and validate placeholder parity.
- Target font lacks CJK glyphs.
  - Skill must flag font risk and recommend font asset work.
- Image text is detected.
  - Skill must create image-lane tasks and not claim complete localization.
- Model output changes JSON/XML/YAML syntax.
  - Skill must reject patch and retry or send to manual fix.
- Budget is exceeded mid-translation.
  - Skill must stop, save progress, and report remaining estimated cost.
- User requests a game they do not have permission to modify.
  - Skill must refuse bypass-oriented steps and offer general localization advice.

## Acceptance Tests

- Given a packaged Godot game folder, when audit runs, then the skill identifies Godot engine signals, `.pck` or related package structure when present, likely executable, and modification risk.
- Given a Unity project with localization tables, when audit runs, then the skill identifies string table and asset table candidates.
- Given a Ren'Py project, when extraction runs, then the skill identifies dialogue/string translation files or scripts and produces translatable units.
- Given JSON strings with `{playerName}` and `<color=red>`, when translation runs, then placeholders and tags remain unchanged.
- Given duplicate strings in multiple files, when inventory is produced, then duplicates are deduped for translation but retain all locations.
- Given a budget cap, when estimated translation cost exceeds it, then the skill stops before provider calls.
- Given image assets with visible text, when audit runs, then image-text lane tasks are created and marked unverified.
- Given translated files, when QA runs, then missing translations, placeholder mismatches, invalid structured files, and encoding changes are reported.
- Given no build command, when release report is produced, then runtime verification is marked blocked rather than passed.
- Given a user budget and provider config, when estimate runs, then the report includes estimated characters, tokens, money cost, and time.
- Given a game with DRM/anti-cheat concern, when audit completes, then the report remains high-level and does not provide modification steps.

## Open Questions

- Which exact Godot packaged-game formats and extraction/repacking tools should v1 support?
- Should the first real-world audit target be `Tactical Breach Wizards` or `Order of the Sinking Star Demo`, and should it be audit-only?
- Which translation MCP/provider should be used in the first implementation test?
- Which OCR/vision model should be used for screenshot checks and image-text detection?
- How strict should the legal/modding permission gate be?
- Should the skill include a standard Chinese game localization style guide by default?

## Personal-Use Revision

Default posture: low-cost personal use. The skill should help one person or a small group try the cheapest reversible localization step first.

Implications:

- Lead with a 50-100 string sample translation.
- Prefer visible text lanes before image/OCR or deep package work.
- Prefer patch/copy output over in-place edits.
- Show token/API spend first, but explain that full project delivery cost is optional and secondary.
- Do not lead with commercial full-delivery pricing unless the user explicitly asks for it.
- Treat full localization as a later opt-in project, not the first offer.

## Change Log

- 2026-06-21: Initial product spec generated from user idea and research. Assumes v1 is source/modding-workspace-first, with OCR/image text as a separate lane.
- 2026-06-24: Revised after discovery answers. Product is now skill-first, packaged-game-first, Godot-priority, audit-first, patch-output, and cost/time/risk-gated.
- 2026-06-24: Reframed default posture to low-cost personal-use mode for solo users, friends, and hobby communities.
