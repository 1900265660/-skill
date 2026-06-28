# Personal-Use Mode

Use this mode when the user wants to localize a game for themselves, friends, a small fan group, or a modding community without committing to a commercial-quality full localization project.

## Principle

Lead with the cheapest reversible next step.

Do not lead with a full commercial delivery quote unless the user explicitly asks for one.

When requirements are unclear, ask one question at a time. Do not ask the user to answer a long intake list before they can see progress.

For personal-use work, the first useful questions are usually:

1. "游戏目录在哪里？"
2. "目标语言是简体中文吗？"
3. "这次先只做只读评估，还是允许我在单独输出目录生成样本/补丁文件？"

Ask them sequentially only as needed. Once the next safe action is clear, proceed.

If the next action is a new workflow, UI, report format, provider adapter, OCR review flow, or reusable skill behavior, write a design document before implementation. For prototypes, prefer Claude Design; if it is unavailable, write a `claude-design-brief.md` handoff instead of pretending a prototype exists.

## Default Path

1. Audit the game folder read-only.
2. Identify whether a safe visible text lane exists.
3. Extract text inventory only from safe lanes.
4. Validate placeholders, wrappers, line breaks, duplicate IDs, and mojibake.
5. Translate a 50-100 string sample first.
6. Reuse existing CJK fonts where possible.
7. Generate patch/copy output, not in-place edits.
8. Run static QA.
9. If visible image text is a concern, plan a capped screenshot/OCR sample instead of full image OCR.
10. Let the user decide whether to continue.

## Sample Commands

```bash
python scripts/prepare_sample_translation.py "path/to/translation-inventory.csv" --out "path/to/sample-output" --sample-size 100 --mode manual
```

For local testing without provider calls:

```bash
python scripts/prepare_sample_translation.py "path/to/translation-inventory.csv" --out "path/to/sample-output" --sample-size 100 --mode mock-zh
python scripts/generate_patch.py "path/to/game" "path/to/sample-output/translated-inventory.sample.csv" --out "path/to/patch-output" --target-locale s-cn --require-target
```

For a low-cost OCR/visual text check after the sample patch works:

```bash
python scripts/plan_ocr_qa.py "path/to/localization-audit.json" --out "path/to/ocr-plan" --screenshots-dir "path/to/screenshots" --sample-size 30
```

## User-Facing Cost Framing

Use these buckets:

- Sample translation: tiny spend, minutes of user review.
- Visible text lane: low model spend, a few hours of personal review/fixing.
- Text + font + basic QA: modest personal project.
- Full localization: separate larger project, only quote after the user asks.
- OCR/image text: start with manual screenshot review or local OCR; quote paid vision only after sample evidence.

## Default Exclusions

Exclude these from the first pass unless the user opts in:

- Image text editing.
- Artistic logos.
- OCR over every asset.
- Paid vision over every screenshot.
- Deep package/archive reverse engineering.
- Unity `.assets` full extraction/repacking.
- Automated screenshot traversal.
- Professional literary localization review.

## Recommendation Style

Prefer:

> This is worth a low-cost sample pass.

Over:

> Full delivery may cost many hours.

Warn about full-scope risks, but keep them in a separate "later if needed" section.

## OCR Posture

In personal-use mode, OCR is a QA helper, not the default translation engine.

Default to:

- Manual screenshot review.
- RapidOCR/PaddleOCR local sample if the user wants automation.
- Cloud OCR or vision models only for a small failure set after local tools are not enough.

Avoid presenting image editing or full-asset OCR as part of the first cost estimate unless screenshots prove it matters.
