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

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".

While anything is still waiting on the user, every later message repeats the full **Needs you** list as first written: each step's options, recommendation, commands and what to reply, not a shortened version. The user may come back after a while and read only the last message; they should never have to scroll up to find what's asked.
