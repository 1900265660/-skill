# Patch Safety

Use patches by default. The installed game folder should remain untouched until the user explicitly approves direct modification.

## Safe Output Order

1. Read-only audit.
2. Translation inventory.
3. Cost estimate and approval.
4. Personal-use sample translation.
5. Patch directory or patch archive.
6. Static validation.
7. Optional copy/apply step.
8. Runtime/screenshot/OCR QA.

## Phase 4 Commands

Prepare a low-cost sample translation package:

```bash
python scripts/prepare_sample_translation.py "path/to/translation-inventory.csv" --out "path/to/sample-output" --sample-size 100 --mode manual
```

Generate patch/copy output from a translated sample:

```bash
python scripts/generate_patch.py "path/to/game" "path/to/sample-output/translated-inventory.sample.csv" --out "path/to/patch-output" --target-locale s-cn --require-target
```

## Patch Rules

- Preserve original encoding and newline style when practical.
- Keep a manifest of source file paths, hashes, generated files, and tool versions.
- Never overwrite the only copy of a game file.
- Validate structured files before marking patch usable.
- Block release on placeholder mismatch.
- Prefer sample patches before full-inventory patches in personal-use mode.
- Use rollback by deleting patch output or restoring from manifest, not by editing blind.

## Direct Modification

Only consider direct modification when:

- The user explicitly requests it.
- A backup exists.
- The patch output has passed validation.
- No DRM/anti-cheat/protected-game concern exists.

Even then, prefer a copied game folder over live install mutation.
