# Engine Patterns

Use this file after the read-only audit finds candidate engine markers.

## Godot

Common packaged markers:

- `*.pck`
- `*.exe` plus sibling `.pck`
- `project.godot` in source-like folders
- `.godot/`, `.import/`, `*.translation`, `*.po`, `*.csv`

Audit stance:

- Treat packaged Godot as plausible but not automatically feasible.
- Prefer official patch PCK concepts when source or recovered project layout is available.
- Treat GDRETools/gdsdecomp, GodotPckTool, and similar tools as optional user-approved dependencies, not automatic steps.
- Mark modified/custom/encrypted package formats as `CAUTION` or `DO_NOT_TRANSLATE`.

Useful lanes:

- Translation files: `.translation`, `.po`, `.csv`
- Text data: `.json`, `.cfg`, `.ini`, `.txt`
- Font risk: `.ttf`, `.otf`, `.fnt`, `.font`, `.tres`, `.res`
- Image text risk: `.png`, `.webp`, `.jpg`, `.svg`

## Ren'Py

Common markers:

- `renpy/`
- `game/*.rpy`
- `game/tl/<locale>/`
- `*.rpa`

Audit stance:

- Good first end-to-end demo target when scripts are readable.
- Packed `.rpa` archives require an approved extraction path.
- Translation should preserve labels, interpolation, text tags, and variables.

Useful lanes:

- Dialogue and menu strings in `.rpy`
- Translation files under `game/tl/`
- Image text in `game/images/`

## Unity

Common markers:

- `<GameName>_Data/`
- `globalgamemanagers`
- `resources.assets`, `sharedassets*.assets`
- `Managed/Assembly-CSharp.dll`
- `StreamingAssets/`

Audit stance:

- Often packaged and asset-bundle-heavy.
- Prefer official/localization tables if source or modding data exists.
- Do not patch assets automatically without a selected tool and fixture proof.

## Unreal

Common markers:

- `*.pak`
- `Engine/`
- `Content/Paks/`
- `Binaries/Win64/`

Audit stance:

- Usually high complexity for packaged games.
- Keep high-level unless localization files are loose or the user has a supported modding workflow.

## RPG Maker-Like

Common markers:

- `www/data/*.json`
- `www/js/rpg_*.js`
- `Game.exe`
- `package.json`

Audit stance:

- If JSON data is loose and readable, this can be a good structured-data lane.
- Preserve escape codes and control characters.

## Unknown Or Custom Engine

Use evidence, not guesses:

- Loose readable text data lowers risk.
- `data/strings/*.localization` and `data/strings/subtitles/*.subtitles` are strong signs of a custom but localization-friendly engine.
- Large custom archives, unreadable binaries, or no text candidates raise risk.
- Existing bad Chinese localization may indicate text is reachable, but not necessarily easy to patch.

For unknown engines, produce a clear recommendation and stop before patching unless a safe route emerges.
