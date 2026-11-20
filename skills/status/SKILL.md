---
name: status
description: "Show what work is in flight across all work items (running, waiting for review, blocked, ready) and resume any of them from any session. Use when the user asks what's going on, what's waiting, where they were, what to do next, or wants to pick up or continue a piece of work ('resume X', 'carry on with X', 'where was I')."
argument-hint: "[work item slug to resume]"
---

# Status

The user may have several work items and parallel slices going. Show them what needs their attention, then get them back into any one quickly.

## Overview (no slug given)

1. Read `~/.shwow-kit/work/index.md`. If it doesn't exist, say there is no tracked work and stop.
2. For each row with `closed` empty, open its location and work out the state of every slice and landing, and the work item's step, from the files and git, using State in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`. Don't trust any status written in a file; older work items may still have one. If the location is missing, mark the row `missing` in the reply (don't delete it).
3. Reply with one table (the user's steps for the top items go in **Needs you** at the end): items with something waiting on you or blocked first, then items with work started, then the rest; `missing` rows last.

| Work item | Tier | Step | Waiting on you | Started | Blocked | Next |
| --- | --- | --- | --- | --- | --- | --- |

- **Waiting on you:** landings waiting (name what's needed: push approval, or the open PR's link); ready HITL slices with no `decision:` line (name the decision); briefs or acceptance examples awaiting confirmation. Slices approved or merged into a landing branch need nothing from the user.
- **Started:** slices with a worktree or branch that aren't done. That may be a live worker or a stopped session; either way `dispatch` resumes them.
- **Next:** the single next action and the command for it (`/shwow-kit:land <slug> <landing>`).

4. Under the table, at most three lines: anything blocked and why (the slice's `blocked:` line), and a warning if three or more landings are waiting on the user (dispatch starts no new slices until those ship).

Don't list closed items unless asked.

## Resume (slug given, or the user picks one)

1. Find the row and open the work item. Read `brief.md`, `landings.md`, the slice files, and the latest entries in `notes.md`.
2. Work out the step as in the overview.
3. Tell the user in two or three lines where it stands and what you'll do next, then invoke that step's skill rather than doing the step yourself (for slices not done, that is `dispatch`, which starts or resumes workers; don't implement a slice in this session).

## Old index rows

If a row still has the old `status` and `updated` columns, rewrite it to `| slug | tier | location | repos | closed |` (`closed` is `done` or `parked` if the old status was, otherwise empty) and mention it.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
