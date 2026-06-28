# Research Notes

Research date: 2026-06-21

## Existing Solutions

- Textractor: Windows game text hooker for extracting text from running games, especially visual novels. It solves runtime extraction for some games but is hook-based, platform-specific, and not a source-project localization workflow. Source: https://github.com/Artikash/Textractor
- LunaTranslator/Luna Hook: frequently discussed as a successor-style runtime hook/translator workflow for visual novels. Product implication: users already expect game-specific profiles and re-attachment convenience in runtime translation tools. Source: https://github.com/Artikash/Textractor/issues/1252
- VNTranslationTools / VNTextPatch: extracts original text from and patches translated text into many visual novel formats. Product implication: format-specific extract/patch adapters are more reliable than generic regex. Source: https://github.com/arcusmaximus/VNTranslationTools
- VNTextPatch .NET 8 fork: modernizes the visual novel extract/patch toolchain and hints that cross-platform packaging matters. Source: https://github.com/rafael-vasconcellos/VNTextPatch-net8
- RSTGameTranslation: real-time screen translation using OCR and LLMs, with local options such as Ollama. Product implication: OCR path is viable but should be treated as a different mode from source/resource patching. Source: https://github.com/thanhkeke97/RSTGameTranslation
- pyUGT: screenshot-region OCR plus translation overlay, with online engines and offline Argos support. Product implication: OCR fallback can support games where source/resources are unavailable, but it does not produce a clean patch. Source: https://github.com/lrq3000/pyugt/discussions/6
- filetranslate: collaborative game translation workflow using machine translation and OCR. Product implication: translation memory, collaboration, and OCR-assisted extraction are existing expectations in fan translation workflows. Source: https://github.com/UserUnknownFactor/filetranslate
- Ren'Py translation tooling: Ren'Py has official translation extraction and string translation mechanisms. Product implication: engine-native workflows should be preferred when available. Source: https://www.renpy.org/doc/html/translation.html

## Official Docs And Technical Constraints

- Unity Localization package uses String Tables for translated strings and Asset Tables for textures or other non-text localized assets. Unity docs recommend giving every UI text its own string table entry and using multiple tables for manageable sections. Sources: https://docs.unity3d.com/Packages/com.unity.localization%401.4/manual/StringTables.html and https://docs.unity3d.com/6000.4/Documentation/Manual/best-practice-guides/ui-toolkit-for-advanced-unity-developers/localization.html
- Unreal Engine provides a Localization Dashboard to manage localization targets, gather text, export/import translations, and compile localized resources. Source: https://dev.epicgames.com/documentation/unreal-engine/localization-tools-in-unreal-engine
- Godot uses TranslationServer and supports translations that can be added/removed at runtime, locale switching, CSV/gettext-style workflows, and command-line language testing. Source: https://docs.godotengine.org/en/stable/tutorials/i18n/internationalizing_games.html
- Godot officially supports exporting project resources as PCK/ZIP packs and creating patch PCK files. This makes Godot a plausible first engine target for a patch-oriented workflow, but only when the package format and loading behavior are compatible. Source: https://docs.godotengine.org/en/stable/tutorials/export/exporting_pcks.html
- Godot export docs distinguish playable exports from PCK/ZIP resource packs. Product implication: the skill must detect executable plus package layout rather than assuming source project structure. Source: https://docs.godotengine.org/en/latest/tutorials/export/exporting_projects.html
- Ren'Py supports translation files where source strings map to target strings, including mechanisms to distinguish same-looking strings with tags. Source: https://www.renpy.org/doc/html/translation.html
- Unity and Unreal community issues show common localization failures: empty string tables after restart, gather text finding zero words, dashboard operations hanging after engine upgrades, and font/widget scaling problems. Sources: https://discussions.unity.com/t/localization-1-4-5-string-table-is-empty-in-editor-after-restart/942924 and https://forums.unrealengine.com/t/localization-dashboard-gather-text-found-0-words/593842
- Font atlas and glyph coverage are real technical constraints. CJK fonts can greatly increase atlas size, require dynamic glyph generation, or need used-character subsetting. Relevant issue examples: https://github.com/ocornut/imgui/issues/918 and https://github.com/H-uru/Plasma/issues/1490
- AI translation cost depends on token input/output volume, repeated context, OCR/image input, provider choice, caching, and batch mode. Current public pricing pages show per-token billing and provider differences, so exact cost estimates must be generated from current provider pricing rather than hard-coded. Sources: https://openai.com/api/pricing/ , https://docs.anthropic.com/en/docs/about-claude/pricing , https://ai.google.dev/gemini-api/docs/pricing
- Godot reverse-engineering/modding tools exist, including GDRETools/gdsdecomp for project recovery, PCK extraction/creation, GDScript decompilation, and resource conversion, plus GodotPckTool for standalone PCK unpack/repack. These are useful research references but should be treated as optional tool dependencies and legal/safety risk boundaries, not automatic steps. Sources: https://github.com/GDRETools/gdsdecomp and https://github.com/hhyyrylainen/GodotPckTool
- Known Godot PCK extraction tools have limitations. For example, godotdec notes that modified engine versions may use custom package formats and that not all extraction/conversion tasks are covered. Product implication: packaged Godot games can still be blocked even when the engine is recognized. Source: https://github.com/Bioruebe/godotdec

## Known Issues

- Text may be stored in many places: source code literals, JSON/CSV/XML/YAML, Unity assets, Unreal string tables, Godot translation CSVs, Ren'Py scripts, binary archives, subtitle files, texture atlases, images, shaders, or generated runtime strings.
- For packaged games, text may be inside PCK/PAK/custom archives, embedded into executables, encrypted, compressed, or stored in proprietary formats. A recognized engine does not guarantee practical localization.
- Hardcoded strings and string concatenation can break extraction and translation. Dynamic text with variables, gender/plural forms, control codes, markup, and placeholders requires protected-token handling.
- Text expansion can break layouts. Chinese may be shorter than English but can expose missing CJK fonts, line breaking, glyph fallback, vertical rhythm, and UI clipping.
- Image-based text and stylized art text are not simply translation tasks. They require OCR, image editing, font matching, texture repacking, and visual QA.
- Patching binary game resources can introduce crashes, corrupted archives, broken checksums, invalid encodings, or anti-cheat/security issues.
- Fan translation may raise legal/IP concerns. A skill should support owned/source projects first and avoid guidance that bypasses DRM or anti-cheat.
- LLM translations may be inconsistent across items unless glossary, speaker context, style guide, and translation memory are enforced.
- Cost can explode if the agent sends entire repositories, screenshots, or repeated context to expensive models without deduplication and budget gates.
- Runtime/screenshot/OCR QA requires a vision/OCR lane and can be slow. It should be evidence-producing and optional, not silently assumed.

## Product Implications

- The MVP should be a Codex/Claude Code skill for packaged-game assessment and safe patch workflows, not a universal game-hacking translator or standalone app.
- The default user posture should be personal-use, not commercial delivery. Lead with a low-cost sample translation and visible text lane before showing full project delivery estimates.
- The workflow must begin with a read-only audit: detect engine/framework, package/archive format, text storage formats, encoding, asset pipeline, font system, launch/build/test commands, and modding constraints.
- The skill should output a localization risk and cost-effectiveness report before translating anything. Risk categories: text extraction, package/repack feasibility, code safety, asset/image text, font/glyph support, runtime verification availability, legal/modding risk, and cost/time.
- Translation should happen through an adapter layer: built-in model prompt, external translation MCP, local model, glossary/translation memory, or manual CSV handoff.
- The skill must protect placeholders, markup, escape sequences, speaker labels, variable interpolation, and control codes before sending text to a model.
- Image text should be a separate lane with explicit handoff to OCR/vision and image-editing agents or plugins. It should not block text-string MVP unless those images are core UI.
- QA must include at least static validation, placeholder parity, encoding checks, duplicate/missing translation checks, launch/build/test execution when available, and screenshot/OCR/vision smoke checks for high-risk screens.
- Cost control must be first-class: character/token preflight, unique string dedupe, glossary reuse, batching, max budget, time estimate, per-provider pricing config, dry-run estimate, and stop-on-budget behavior.
- Godot is a rational first packaged-game priority because PCK and patch PCK concepts are official, but the skill must still handle blocked outcomes for custom/modified/encrypted packages.

## Open Research Questions

- Which Godot PCK extraction/repacking path is safest for v1: official patch PCK from a recovered project, GodotPckTool, GDRETools, or assessment-only until user installs tools?
- Should the first real-world audit target be `Tactical Breach Wizards` or `Order of the Sinking Star Demo`, and should it remain read-only?
- Which engines beyond Godot and Ren'Py should v1 support directly?
- What exact patch format should be generated for packaged games: loose files, patch archive, binary diff, or tool-specific patch instructions?
- Which translation MCP protocol or providers should be considered canonical for the first version?
- What OCR/vision model and image editing plugin should be used for image-based text and screenshot QA?
- How should the skill verify translated games without a runnable build or save file near the target scenes?
- How should legal/modding constraints be represented without turning the skill into legal advice?
