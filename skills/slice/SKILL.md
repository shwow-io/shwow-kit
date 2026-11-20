---
name: slice
description: Break an agreed brief and its acceptance checks into thin, vertical, independently verifiable slices in dependency order, each ready for an agent to run alone or with the user. Use after acceptance, or when the user asks to plan, break down, decompose or ticket a piece of work.
argument-hint: "[work item slug]"
---

# Slice

Turn the brief into work that agents can run, mostly in parallel, and that the user can review in small pieces.

## Rules for a slice

- **Vertical.** Each slice delivers a thin piece of working behaviour end to end (through every layer it needs), not a layer on its own. The first slice is a tracer bullet: the simplest path through the whole system, making one or two examples pass. Options, filters and edge cases go in later slices.
- **Verifiable alone.** It names which acceptance checks it makes pass, plus the exact command to verify it (from `verification.md`).
- **Reviewable.** About 30 minutes of review for the user. If larger, split it.
- **Explicit about touch points.** Which repo and area it changes. Two slices that edit the same files can't run in parallel; make one depend on the other.
- **AFK or HITL.** AFK: specified and verifiable enough for an agent to finish alone. HITL: needs a human decision or judgement partway. Prefer AFK; when a slice is HITL, say what decision is needed.
- **Services.** Whether verifying it needs running services (database, ports, external systems). Such slices don't run in parallel with each other.

## Landings

A landing is a group of slices that ships together: one PR, or one push to the main line. Slices are merged into their landing's branch as they pass verification, with no user step; the user's gate is the landing. Plan them now:

- **At least one per repo,** so a repo whose slices finish early ships without waiting for the others.
- **Split a large build** into several landings when one would be too big to review in one sitting (more than about five slices, or several hundred changed lines), or when part of it is worth shipping early. Each landing must work on its own once merged, so split along the dependency order: no landing depends on a later one.
- **One landing** is the default for a small build in one repo.
- **How each integrates,** from the repo's conventions (see the `land` skill, step 4): PR or direct to the main line.

Write them to `landings.md` in the work item:

```
| landing | repo | branch | slices | integrates by |
```

Branch: `<type>/<work-item>` or `<type>/<work-item>-<landing>` (or the repo's convention). Set each slice's `landing` field to match. Don't record a status here; see State in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`.

## Steps

1. Read `brief.md`, `acceptance.md`, `verification.md` (and `design.md` for T2) from the work item.
2. Look at the code enough to know where each slice lands. Use a `scout` subagent for broad exploration.
3. Write one file per slice in `slices/`, named `NN-<short-name>.md`, using `${CLAUDE_PLUGIN_ROOT}/skills/slice/slice-template.md`. Number in dependency order, starting at 01. No other files in `slices/`.
4. Group the slices into landings and write `landings.md`.
5. Check coverage: every acceptance example is covered by at least one slice; every slice traces back to the brief. Flag anything that doesn't.
6. Show the user a short table: slice, mode, depends on, parallel-safe, landing. Ask them to confirm, reorder, merge or regroup. Their confirmation is the go-ahead for agents to build, commit and merge every AFK slice into its landing branch without asking again. Add the index row if the work item has none, then invoke `dispatch`.

## Don't

- Write horizontal slices ("add the model", "add the API", "add the UI").
- Plan the implementation line by line. A slice states outcome, boundaries and verification, not code. Name only the seams other slices depend on (a function signature, a registry).
- Add slices that only re-run checks; final verification belongs to the verify step.
- Exceed what the brief asks for.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
