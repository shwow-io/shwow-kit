---
name: frame
description: Interview the user to turn a request into a one-page brief (problem, outcome, non-goals, constraints, open risks) before any planning or code. Use after triage for T1/T2 work, when a request is vague or under-specified, or when the user asks to frame, scope, spec, write up, plan or think through a feature or change, including one to start later.
argument-hint: "[work item slug]"
---

# Frame

Get the problem right before anyone plans or writes code. The output is a brief short enough that the user will actually read it.

## Interview

- One question at a time. With each question, give your recommended answer and why, so the user can reply "yes" instead of writing an essay.
- Don't ask what the code can answer. Read it yourself, or send a `scout` subagent for broad questions, and state what you found. When an answer depends on outside facts (library behaviour at the pinned version, upgrades, standards), send the `researcher` subagent rather than answering from memory.
- Work down the tree: purpose and who it's for → observable outcome → scope and non-goals → constraints (performance, compatibility, security, deadlines) → edge cases and failure modes. Stop a branch once it's resolved.
- Stop when you could explain the work to a new engineer and they'd build the right thing. Usually 4 to 10 questions; fewer for small T1 work.

## Blind-spot pass (T2, or when the user seems sure but the stakes are high)

Before writing the brief, list what nobody has mentioned: affected users or systems, data migration, rollback, observability, security, other repos or teams. Ask about the ones that matter; record the rest as risks.

## Write the brief

Write `brief.md` in the work item using `${CLAUDE_PLUGIN_ROOT}/skills/frame/brief-template.md`. If there is no work item yet, create it first per `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`, with a slug whose folder does not already exist. One page at most. Defaults you chose for the user go under Open questions, marked as your recommendation; don't add sections.

For T2, also write `design.md`: the interfaces between repos or components, key decisions with the alternatives rejected, and risks. The user owns these decisions; propose, don't decide.

When the work changes a contract, stored data, config or deploys, or touches another repo (always for T2), run the `impact` skill on the plan before confirming the brief. Breaking changes it finds become constraints in the brief or decisions for the user, so the design avoids them.

Show the user the brief and confirm it. Once the brief is agreed, move to the `acceptance` skill.

## Don't

- Plan implementation, name files, functions or libraries, or write code. If a constraint seems to need one, state the observable constraint instead ("`list` output byte-identical", not "reuse `filter_tasks`").
- Pad the brief with background the user already knows.
- Invent requirements. If something wasn't discussed, it's a non-goal or an open question, not a feature.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
