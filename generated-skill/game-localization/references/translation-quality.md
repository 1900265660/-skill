# Translation Quality

Translation quality depends on context and consistency. Do not rely on one generic prompt.

## Required Context

- Target language and locale.
- Style profile: faithful, naturalized, humorous, serious, fan-patch, UI concise.
- Character names and speaker context.
- Term glossary.
- Do-not-translate list.
- Protected placeholders and tags.
- Length/layout hints where available.

## Personal-Use Translation Approach

For a solo user or small friend group, prefer the smallest safe translation pass first:

- Sample 50-100 strings.
- Reuse existing Chinese fonts when possible.
- Favor patch/copy output over modifying the original install.
- Keep the first QA pass static and visual-light.
- Use capped screenshot/OCR QA only after the text sample patch works.
- Expand only after the user sees the sample result and likes the tone.

## Protected Tokens

Preserve exactly:

- `{name}`, `{0}`, `${var}`
- `%s`, `%d`, printf-like formats
- `<color=red>`, `[b]`, `{i}`, Ren'Py text tags
- `\n`, `\t`, escaped quotes
- Engine commands, labels, variable names

## QA Expectations

- Check placeholder parity.
- Check missing translations.
- Check duplicate source strings with different context.
- Check style consistency for character names and terms.
- Flag strings that need human context.
- Flag mojibake in existing target files before treating those files as reusable translation memory.
- Treat validation blockers as hard stops before provider calls or patch generation.
- Treat OCR hits as review evidence, not final translation memory.
- Do not rely on OCR alone for stylized logos, map labels, signs, or other art text; those may need manual image edits.

## Tone Guidance

When giving recommendations to a personal user, do not lead with commercial-level delivery scope or cost unless explicitly asked. Start with the least scary reversible step.
