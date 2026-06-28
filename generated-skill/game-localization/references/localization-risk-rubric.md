# Localization Risk Rubric

Use qualitative labels. Show evidence so the user can decide whether the work is worth doing.

## Recommendation Labels

- `PROCEED`: readable text lane exists, patch path is plausible, rollback is easy, no protected-game concerns.
- `CAUTION`: feasible but needs tools, manual QA, OCR, font work, or packaging research.
- `HIGH_LEVEL_ONLY`: DRM, anti-cheat, unclear permission, executable tampering, or protected package concern. Provide assessment only.
- `DO_NOT_TRANSLATE`: no practical text path, too much binary/custom packaging, high image/font burden, or cost exceeds value.

## Dimensions

Assess at least:

- Engine confidence.
- Text volume.
- Text-location dispersion.
- Package/archive complexity.
- Image-text ratio.
- Font/CJK glyph support.
- Ability to launch/build/test.
- Rollback ease.
- Patch feasibility.
- Required external tools.
- Legal/modding/DRM/anti-cheat risk.
- Cost and time.

## Red Flags

- Anti-cheat directories or services.
- DRM/protection indicators.
- Only huge binary archives and no readable text candidates.
- Custom package extensions with no known tool.
- Heavy UI text embedded in textures.
- Bitmap fonts without CJK glyphs.
- No way to launch or inspect result.
- User asks for bypass or executable cracking.

## Green Flags

- Loose localization files.
- Existing locale files such as `.localization`, `.subtitles`, `.po`, `.csv`, or translation catalogs.
- Readable script/dialogue files.
- Existing target-language files.
- Official engine localization structure.
- Patch/mod folder support.
- Small string count.
- Good rollback path.

## Platform Indicators

Steam/GOG/Epic libraries are platform indicators, not automatic blockers. Treat them as a permission/distribution risk note unless stronger DRM, anti-cheat, or executable-tampering evidence appears.
