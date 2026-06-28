# Text + Font + Basic QA Quote

Date: 2026-06-24

## Pricing Assumptions

Exchange rate used for this estimate:

- `1 USD ~= 6.81 CNY`

Token prices provided by user:

- Input: `$25 / 1M tokens`
- Cache read: `$2.5 / 1M tokens`

Labor assumption carried forward from Phase 3:

- `$25 / hour`

Important limit:

- Output token price was not provided, so the model/API total below only includes input and cache-read cost.
- If output is also charged at `$25 / 1M tokens`, add about `$0.55` / `¥3.78` for the current `Order of the Sinking Star Demo` text lane.

## Baseline Inventory

Baseline: `Order of the Sinking Star Demo`

- Rows: 885
- Unique translation units after dedupe: 871
- Source characters: 44,480
- Deduped source characters: 44,361
- Estimated input tokens: 37,548
- Estimated output tokens: 22,181
- Estimated total tokens: 59,729
- Text files to modify: 2
- Font assets seen in audit: 20

## API Cost

| Mode | Formula | USD | CNY |
| --- | --- | ---: | ---: |
| No cache | `37,548 / 1M * $25` | `$0.94` | `¥6.39` |
| With prompt/cache reuse | `27,548 / 1M * $25 + 10,000 / 1M * $2.5` | `$0.71` | `¥4.86` |
| Optional output add-on if output uses `$25 / 1M` | `22,181 / 1M * $25` | `$0.55` | `¥3.78` |

Interpretation:

The model input/cache-read fee is negligible compared with human delivery work. It should not be presented as the project price.

## Package Options

| Package | Scope | Estimated Hours | Labor USD | Labor CNY | API CNY With Cache | Estimated Total CNY |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Low | Existing text lane translation, reuse existing CJK font if possible, placeholder/static checks, manual patch handoff. | `12-24h` | `$300-$600` | `¥2,043-¥4,085` | `¥4.86` | `¥2,050-¥4,090` |
| Standard | Text translation, glossary/style pass, font coverage check, generated patch/copy, placeholder validation, length-risk review, one smoke launch/screenshot if safe. | `20-45h` | `$500-$1,125` | `¥3,404-¥7,660` | `¥4.86` | `¥3,410-¥7,665` |
| Careful | Standard scope plus second review pass, term consistency cleanup, more UI length checks, rollback package, small bug-fix loop, and release notes. | `35-70h` | `$875-$1,750` | `¥5,958-¥11,916` | `¥4.86` | `¥5,965-¥11,925` |

## Not Included

- Image text editing or art recreation.
- Full OCR over all image assets.
- Deep package/archive reverse engineering.
- Unity `.assets` full localization extraction/repacking.
- Runtime automation across many screens.
- Professional literary/cultural localization review.

## Recommendation

For this product workflow, quote users in two numbers:

- API/model estimate: usually a few yuan for small text lanes.
- Engineering delivery estimate: usually thousands of yuan once patching, font checks, QA, and review are included.

For the current `Order of the Sinking Star Demo` lane, the practical starter offer should be the `Standard` package:

- About `20-45h`
- About `¥3,410-¥7,665`
- Plus output-token charges if the selected provider bills output separately.
