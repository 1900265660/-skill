# Evolution Loop

Use this when the user corrects the workflow, a review finds process failure, a bug reveals a repeated blind spot, or `evolution-signals.md` contains pending items.

## Inputs

- `evolution-signals.md`
- user corrections in the current session
- failed review findings
- bugfix learnings
- contradictions between durable documents and actual behavior

## Digest Process

1. Restate each raw signal in plain language.
2. Classify it as:
   - reusable rule candidate;
   - project-specific decision;
   - already covered;
   - one-off preference;
   - rejected because it would add harmful ceremony.
3. For reusable candidates, identify the owner location:
   - `SKILL.md` operating rule;
   - `references/framework.md`;
   - `references/document-templates.md`;
   - `references/goal-patterns.md`;
   - a more specific reference file.
4. Decide whether the change adds, replaces, weakens, or deletes a rule.
5. Present a concise proposal and ask for approval before modifying durable skill rules.
6. Apply approved changes, then update or clear processed signals.

## Proposal Shape

```markdown
## Proposal: [name]

Signal:

Failure:

Why it may recur:

Proposed rule:

Target file:

Change type:

Risks:

Decision:
```

## Clean State

End the loop only after approved proposals are applied, rejected proposals have reasons, processed signals leave the active queue, and the next product action is clear.

## Red Lines

- Do not silently mutate reusable skill rules.
- Do not turn temporary taste feedback into universal process.
- Do not keep duplicate rules that make the agent more rigid without preventing a real failure.
