# Raw Idea

Test date: 2026-06-21

User idea:

一个“电子游戏翻译 skill”。首先 Codex 或 Claude Code 读取游戏代码及结构，了解游戏的编码方式以及文本存放的位置，评估汉化的难度以及风险。然后对文本进行翻译，或者接上外部的翻译 MCP，或者接入指定的模型。

用户设想的难点：

1. 图片型文本、字体以及艺术字，可能要借助其他插件或者 agent。
2. 会不会出现 Bug，能否检查、修改、订正。
3. 成本问题，能否评估成本和控制成本。

Skill under test:

`E:\Projects\chanpin\autonomous-product-manager`

Required references read:

- `SKILL.md`
- `references/framework.md`
- `references/document-templates.md`
- `references/goal-patterns.md`

Execution constraint:

- Create outputs inside `E:\Projects\chanpin\skill-test-env\game-localization-skill`.
- Do not modify the original skill body.
