# Evolution Signals

## Signal: Discovery Was Skipped For A Vague Idea

Source:

User correction on 2026-06-22: "有问题，你没有向我反问更多信息，我的想法非常模糊不能直接做规划".

What failed:

The workflow generated a full product planning package from a vague idea before asking enough clarifying questions. This violated the product-spec-builder acceptance rule that a developer should not need to guess the core problem, users, scope, flows, or success criteria.

Why it may recur:

When a user says "开始测试" and expects artifact generation, the agent may optimize for producing files instead of enforcing the discovery gate.

Candidate rule:

When testing autonomous-product-manager with a vague idea, do not generate the full planning package immediately. First run a discovery question pass. If the user explicitly asks to skip Q&A, mark all outputs as assumption-backed drafts and fail the review until discovery is completed.

Target location:

`autonomous-product-manager` test guidance, `product-spec-builder` rules, and `reviewer` checklist.

Decision:

Promote. This is a real observed workflow failure and directly maps to an existing operating rule.

## Signal: Universal Game Translation Scope Is Too Broad

Source:

Product scoping during skill test on 2026-06-21.

What failed:

The raw idea could be interpreted as a universal game translator that handles source code, binary resources, runtime OCR, image text, fonts, and QA all at once. That scope is too broad for a safe MVP.

Why it may recur:

Game localization users often describe the desired outcome as "translate the game" even though the technical path varies drastically by engine and asset format.

Candidate rule:

For game localization workflows, always classify the project into localization lanes before proposing translation: engine-native, structured data, code literals, binary/packed, image/textures, runtime OCR/hook, and unknown.

Target location:

Future `game-localization` skill `SKILL.md` and `references/localization-risk-rubric.md`.

Decision:

Promote when implementing the skill. This directly prevents unsafe scope expansion.

## Signal: Image Text Must Not Be Claimed Complete Without Visual QA

Source:

User explicitly identified image text, fonts, and art text as a hard problem.

What failed:

Naive localization workflows often focus on strings and overlook texture text, font atlases, stylized logos, and screenshots. This can produce a "translated" patch with visible untranslated art.

Why it may recur:

Images are easy to miss during text extraction and hard to verify without OCR or visual inspection.

Candidate rule:

If image assets may contain user-visible text, create a separate image-text lane and mark it unverified until OCR/manual visual review and edited asset checks pass.

Target location:

Future `game-localization` skill `SKILL.md`, image/OCR handoff reference, and QA checklist.

Decision:

Promote when implementing the skill. It maps to a real known failure mode in localization.

## Signal: Cost Must Be A Preflight Gate

Source:

User explicitly raised cost estimation and control.

What failed:

If the skill sends inventories to LLMs before estimating cost, users may spend money before understanding the scope.

Why it may recur:

Large games can contain tens or hundreds of thousands of words, and repeated context/glossary prompts can multiply token usage.

Candidate rule:

Before any remote translation/model call, perform a dry-run cost estimate and require budget approval or manual override.

Target location:

Future `game-localization` skill `SKILL.md` and `references/cost-control.md`.

Decision:

Promote when implementing the skill. This should be a hard operating rule.

Implementation status:

Promoted into Phase 3 on 2026-06-24. `estimate_cost.py` now blocks paid provider routes when pricing is unknown, budget is missing, budget is exceeded, validation blockers exist, validation warnings are unaccepted, or explicit budget approval is absent.

## Signal: Provider Pricing Must Stay Configurable

Source:

Phase 3 implementation and provider pricing research on 2026-06-24.

What failed:

Provider pricing is unstable. Treating a remembered or stale price as an implementation constant can silently produce bad budget advice.

Why it may recur:

Cost gates are easier to implement with hardcoded sample prices, and model names/prices change frequently.

Candidate rule:

Keep paid provider pricing in an external user-owned JSON config. If pricing is unknown or not verified, report character/token counts but block paid provider calls until current official pricing is supplied.

Target location:

`game-localization` cost-control reference, provider interface, and future provider adapters.

Decision:

Promoted into Phase 3. OpenAI example pricing is intentionally null until the user fills current official values.

## Signal: Planning Package Without Interactive Discovery

Source:

This test generated documents directly from the user's idea and stated concerns.

What failed:

The autonomous product-manager framework says to ask questions until the intent is buildable. This test proceeded with reasonable assumptions because the user asked to start testing and supplied enough direction for a planning package.

Why it may recur:

Skill tests often need complete artifact generation in one turn, while real product discovery benefits from Q&A.

Candidate rule:

When generating a planning package without interactive discovery, label the product spec as assumption-backed and keep open questions visible before implementation.

Target location:

`autonomous-product-manager` operating rules or test guidance.

Decision:

Keep raw signal. Do not promote from this test alone.

## Signal: Steam API And Substrings Caused False Protected-Game Block

Source:

Phase 1 real audit on 2026-06-24 against `Tactical Breach Wizards` and `Order of the Sinking Star Demo`.

What failed:

The first protected-indicator regex treated `steam_api` as a hard blocker and matched `eac` inside ordinary words such as `breach` and `Beach`, causing both games to be incorrectly classified as `HIGH_LEVEL_ONLY`.

Why it may recur:

Naive substring matching is common in packaged-game scans and can misclassify normal file names as DRM or anti-cheat indicators.

Candidate rule:

Separate hard protected-game indicators from platform indicators. Use word-boundary or explicit-name matching for anti-cheat/DRM terms, and treat Steam/GOG/Epic files as risk notes rather than automatic blockers.

Target location:

`game-localization` scanner and `references/localization-risk-rubric.md`.

Decision:

Promoted into scanner implementation and risk rubric on 2026-06-24.

## Signal: Logs And Licenses Were Misclassified As Translatable Game Text

Source:

Phase 1 real audit on 2026-06-24 against `Order of the Sinking Star Demo`.

What failed:

The scanner initially counted `Software Licenses.txt` and log files as translatable source text, producing a misleading `PROCEED` recommendation before discovering the actual `data/strings/*.localization` and `.subtitles` files.

Why it may recur:

Packaged games often contain logs, licenses, debug output, and middleware notices with lots of readable text. These are easy to overcount if the scanner only checks extension and readability.

Candidate rule:

Separate support text from translatable game text. Exclude logs, licenses, notices, readmes, changelogs, and middleware docs from translation cost/recommendation counts, while still reporting them as auxiliary evidence if useful.

Target location:

`game-localization` scanner and future inventory extractor.

Decision:

Promoted into scanner implementation on 2026-06-24.

## Signal: Unity Technical JSON Was Misclassified As Player Text

Source:

Phase 2 inventory extraction on 2026-06-24 against `Tactical Breach Wizards`.

What failed:

The first inventory extractor included Unity service/package configuration strings such as package IDs and version numbers. These are not player-facing localization strings.

Why it may recur:

Generic JSON extraction can over-include technical metadata in packaged games.

Candidate rule:

Treat JSON extraction as schema-sensitive. Skip known technical config files and strings that look like package IDs, versions, assembly-qualified names, or hashes unless the user explicitly asks for technical text extraction.

Target location:

`game-localization` inventory extractor and Unity field notes.

Decision:

Promoted into `extract_inventory.py` and `engine-field-notes.md` on 2026-06-24.

## Signal: Natural-Language Wrappers Were Misclassified As Protected Tokens

Source:

Phase 2.5 validation on 2026-06-24 against `Order of the Sinking Star Demo`.

What failed:

The first validator treated arrow-wrapped menu strings such as `<- Graphics Mode: Auto (Performance) ->` as protected tokens. Because the Chinese target correctly translated the inner natural language, the validator falsely reported missing protected tokens.

Why it may recur:

Localization files often use wrappers or decoration around translatable text. A placeholder detector that treats every angle-bracket-like pattern as protected syntax can confuse formatting wrappers with immutable tokens.

Candidate rule:

Separate immutable placeholders/tags from translatable decorated strings. Validate wrapper preservation separately from placeholder parity, and do not require natural-language content inside wrappers to remain unchanged.

Target location:

`game-localization` `extract_inventory.py`, `validate_inventory.py`, and inventory validation guidance.

Decision:

Promoted into Phase 2.5 implementation on 2026-06-24.
