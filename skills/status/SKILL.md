---
name: status
description: "Show what work is in flight across all work items (running, waiting for review, blocked, ready) and resume any of them from any session. Use when the user asks what's going on, what's waiting, where they were, what to do next, or wants to pick up or continue a piece of work ('resume X', 'carry on with X', 'where was I')."
argument-hint: "[work item slug to resume]"
---

# Status

The user may have several work items and parallel slices going. Show them what needs their attention, then get them back into any one quickly.

## Overview (no slug given)

1. Read `~/.shwow-kit/work/index.md`. If it doesn't exist, say there is no tracked work and stop.
2. For each row not `done` or `parked`, open its location and read `landings.md` and the slice files' `status`, `mode` and `depends_on` fields. If the location is missing, mark the row `missing` in the reply (don't delete it).
3. Reply with one table: items with something waiting on you or blocked first, then items with work running, then the rest; `missing` rows last.

| Work item | Tier | Step | Waiting on you | Running | Blocked | Next |
| --- | --- | --- | --- | --- | --- | --- |

- **Waiting on you:** landings at `ready` or `waiting` (name what's needed: push approval, or the open PR's link); HITL slices at `todo` whose dependencies are done (name the decision from the slice); briefs or acceptance examples awaiting confirmation. Slices at `review` are waiting on the verify step, and slices merged into a landing branch need nothing from the user until their landing is ready.
- **Next:** the single next action and the command for it (`/shwow-kit:land <slug> <landing>`).

4. Under the table, at most three lines: anything blocked and why (from the slice or `notes.md`), and a warning if three or more landings are waiting on the user (dispatch starts no new slices until those ship).

Don't list `done` items unless asked.

## Resume (slug given, or the user picks one)

1. Find the row and open the work item. Read `brief.md`, the slice files, and the latest entries in `notes.md`.
2. Work out the current step from the files: no brief → frame; brief but no `acceptance.md` → acceptance; no slices → slice; slices `todo`, `running` or `review` → dispatch; a landing `ready` or `waiting` → land; every landing `shipped` → compound.
3. Tell the user in two or three lines where it stands and what you'll do next, then invoke that step's skill rather than doing the step yourself (for `todo` or `running` slices that is `dispatch`, which starts workers; don't implement a slice in this session). Check for worktrees from a previous session (`git worktree list` in the repo) before creating new ones, and pass them on for reuse.

## Keep the index honest

If a row's status disagrees with its slice files, fix the row (status and `updated`) and mention it. Use only the statuses in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`; acceptance counts as `framing`.
