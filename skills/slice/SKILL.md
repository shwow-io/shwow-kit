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

## Steps

1. Read `brief.md`, `acceptance.md`, `verification.md` (and `design.md` for T2) from the work item.
2. Look at the code enough to know where each slice lands. Use a `scout` subagent for broad exploration.
3. Write one file per slice in `slices/`, named `NN-<short-name>.md`, using `${CLAUDE_PLUGIN_ROOT}/skills/slice/slice-template.md`. Number in dependency order, starting at 01. No other files in `slices/`.
4. Check coverage: every acceptance example is covered by at least one slice; every slice traces back to the brief. Flag anything that doesn't.
5. Show the user a short table: slice, mode, depends on, parallel-safe. Ask them to confirm, reorder or merge. Then set the index row to `running`, adding the row if the work item has none.

## Don't

- Write horizontal slices ("add the model", "add the API", "add the UI").
- Plan the implementation line by line. A slice states outcome, boundaries and verification, not code. Name only the seams other slices depend on (a function signature, a registry).
- Add slices that only re-run checks; final verification belongs to the verify step.
- Exceed what the brief asks for.
