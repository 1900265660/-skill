# Intake Question Flow

Use this reference before audit, planning, pricing, provider setup, OCR, or patch work when the user's localization request is still ambiguous.

## Principle

Ask one question at a time.

Do not send a long questionnaire. A vague localization idea should become clear through a short sequence of focused turns, not a single wall of questions.

## Flow

1. Identify the one missing answer that most affects the next safe step.
2. Ask only that question.
3. Wait for the user's answer.
4. Update the working assumptions.
5. Ask the next most important question.
6. Continue until the minimum required information is available.
7. Summarize the collected answers in plain language.
8. Write the required design document when the task changes workflow, user-facing behavior, provider integration, QA process, or reusable skill behavior.
9. If a prototype is needed, prefer Claude Design; otherwise write a `claude-design-brief.md` handoff.
10. Only then proceed to audit, estimate, sample planning, patch planning, provider work, or implementation.

## Minimum Information

Collect only what is needed for the next lane.

For a first audit, the minimum is:

- Game folder or project folder.
- Target language/locale.
- Whether the user wants read-only assessment only or allows generating files in a separate output directory.

For translation planning after audit, add:

- Intended user: personal use, friends, fan patch, mod group, or commercial delivery.
- Preferred output: patch folder, CSV for manual editing, provider-translated sample, or high-level report.
- Budget posture: zero API spend, local-only, small paid sample, or user-specified budget.

For provider/model work, add:

- Provider/model choice or permission to keep it manual/local.
- Current pricing config or explicit approval to use user-supplied prices.
- Budget limit.

For OCR/image-text work, add:

- Whether screenshots are available.
- Whether local OCR setup is acceptable.
- Whether paid cloud OCR or vision-model calls are allowed after estimate.

## Question Style

Ask in the user's language.

Keep each question concrete and answerable. Prefer one of these forms:

- "这个游戏目录是哪个？"
- "这次你只想做只读评估，还是允许我在单独输出目录生成补丁文件？"
- "目标语言是简体中文吗？"
- "这次预算倾向是零 API 成本、本地模型，还是可以接受一个小额样本？"

Avoid:

- Asking 8-20 questions at once.
- Mixing product strategy, technical constraints, budget, provider setup, OCR, and release goals in one message.
- Treating unanswered optional questions as blockers.

## When To Stop Asking

Stop the intake loop when the next safe action is clear.

Examples:

- If the user provides a game folder and asks for assessment, run the read-only audit.
- If the audit is `CAUTION`, ask one approval/tooling question before extraction.
- If the user wants a low-cost personal attempt, prepare a sample flow instead of asking about commercial delivery.
- If the user does not know the engine or file structure, do not ask them to inspect it; the skill should audit it.

## Design After Intake

After the intake loop is complete, do not jump straight into broad implementation.

Read `design-and-prototype-flow.md` and create a design document first when the next step is a new workflow, product behavior, provider adapter, OCR lane, UI/report format, or reusable skill change.

For visual or interactive prototypes, Claude Design is the preferred prototype path. If Claude Design is not available, write a `claude-design-brief.md` and clearly mark the prototype as not yet generated.

## Summary Before Action

Before moving from questions to action, summarize:

- What the user wants.
- What is known.
- What remains unknown but non-blocking.
- The next safe step.

Example:

> 我现在理解是：你想做个人/同好用的简中汉化，先只做低成本可回滚尝试。你给了游戏目录，但还不确定引擎和文本位置。下一步我会只读扫描目录，把结果写到单独输出文件夹，不修改游戏本体。

Then proceed.
