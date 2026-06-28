# Engine Field Notes

Use this file to carry forward practical observations from audits. Keep notes evidence-based and portable.

## Godot

- Packaged games commonly expose an executable plus `.pck`.
- Recognizing `.pck` is not enough to translate safely. Custom, encrypted, or modified package formats can block extraction or patching.
- Official Godot workflows support translation resources and patch packs, but packaged-game patching still needs a selected tool path and QA.
- Future migration advice: keep Godot support split into detection, PCK inventory, extraction tool choice, patch strategy, and runtime QA.

## Ren'Py

- Good first end-to-end demo target because scripts and translation files can be text-based.
- `.rpy` dialogue often follows `speaker "text"` or `"menu choice":`.
- Preserve text tags, interpolation variables, labels, and script commands.
- `.rpa` archives need approved extraction tooling; do not treat them like plain folders.

## Unity

- Packaged games commonly expose `<Game>_Data/`, `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `Managed/`, and `StreamingAssets/`.
- Loose `StreamingAssets` files can be easier localization lanes than Unity `.assets` files.
- Unity asset files need engine-specific tools and are not Phase 2 patch targets by default.
- Platform files such as Steamworks are risk notes, not automatic blockers.
- Field note from `Tactical Breach Wizards`: `StreamingAssets/Levels/*/mission.txt` exposed mission titles as simple key/value text, while the larger Unity `.assets` files remained package-risk lanes. Inventory extraction should distinguish this shallow title lane from full dialogue/UI localization.
- Exclude `UnityServicesProjectConfiguration.json` and similar package/config files from translation inventory; they are technical metadata, not player-facing text.

## Unreal

- Packaged games commonly expose `.pak` under `Content/Paks`.
- Treat as high complexity unless loose localization resources or a modding workflow is present.
- Do not unpack/repack `.pak` by default in this skill.

## RPG Maker-Like

- Loose `www/data/*.json` and JS files can be favorable text lanes.
- Preserve escape codes, control sequences, actor names, and event command structure.
- JSON inventory extraction is useful, but patch writing must preserve schema and encoding.

## Custom Engines

- Do not assume unknown means impossible.
- Existing locale files are a strong green flag. Examples seen:
  - `data/strings/*.localization`
  - `data/strings/subtitles/*.subtitles`
- Existing bad Chinese localization is useful because it proves a target-locale lane exists and lets inventory compare source against target.
- Logs and licenses can produce lots of text but should not drive translation recommendations.
- Texture-heavy folders need image/OCR QA, but they do not necessarily block text-lane work.
- Field note from `Order of the Sinking Star Demo`: `.localization` used backtick-prefixed keys followed by text values; `.subtitles` used `:: block_id` plus repeated `= speaker time` entries. Existing `s-cn` files were readable as UTF-8 through Python even when PowerShell display looked garbled.
- For custom engines with existing target locale files, Phase 2 should extract source and existing target side by side before proposing translation. This enables quality improvement rather than blind first-pass translation.

## Image/OCR QA

- OCR is best treated as a QA lane after text patching, not as the first extraction lane.
- Runtime screenshots are usually higher-value than raw image assets because they show text players actually see.
- Raw asset OCR should be ranked and sampled first; many assets are icons, portraits, backgrounds, texture maps, particles, or unused UI pieces.
- RapidOCR is a good default local candidate for Chinese/English sample checks; PaddleOCR is the stronger but heavier fallback.
- Tesseract remains useful for clean UI text, but stylized game fonts and outlined text often need modern scene-text OCR or manual review.
- Cloud OCR and vision-language models should be reserved for small failure sets after local tools are not enough.
