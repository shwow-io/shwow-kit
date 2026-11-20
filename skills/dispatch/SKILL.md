---
name: dispatch
description: Run a work item's slices with worker subagents, each in its own isolated git worktree, several at once where slices are independent, and keep going on its own until the work is built or needs the user. Use when slices are agreed and the user wants them built, says "run/start/dispatch the slices", or asks to work on several things in parallel.
argument-hint: "[work item slug] [slice ids]"
---

# Dispatch

Build every slice the user agreed to, in parallel where safe, without asking between slices. The user is needed only for decisions, blockers and shipping.

## Pick what to run

Read `slices/` and `landings.md` in the work item. If `landings.md` is missing (older work items), create it now: one landing per repo, integrating the way the `land` skill's step 4 decides, and tell the user in one line.

Older work items also have a `status:` line in each slice. Convert them once, before anything runs: for a slice at `done`, or one whose work is already on the main line (ask the user if unsure), write `evidence/<id>-merged.txt` saying so, then delete every `status:` line. Never re-run a slice the user says has shipped.

Work out each slice's state from the rules under State in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`; nothing in the files says "running", so an interrupted session leaves nothing to clean up. Run the slices that are ready, and resume started ones that no worker in this session is on, in their existing worktree. Merge approved ones (below). From what's left to run:

- Run AFK slices. For a HITL slice, ask the user the decision the slice names, record it in the slice as a `decision:` line, then treat it as AFK. Keep other slices running while you wait.
- Run two slices in parallel only if their `touches` don't overlap and at most one of them has `needs_services: true`.
- Run at most 3 at once.

Before the first worker starts, list every step the user will have to do by hand for this work (keys to add, scripts only they can run, accounts, live checks after shipping), per slice, from the slices' notes. Ask now for anything that can be done before landing, so it doesn't block later.

## Isolate

Each landing has a branch (from `landings.md`), created from the repo's current main line the first time a slice of it starts. Each slice gets its own worktree and branch, created from its landing's branch, so it starts with every slice already merged there:

- Default: `~/.shwow-kit/worktrees/<checkout>/<slice-id>-<short-name>`, where `<checkout>` is the folder name of the user's checkout (not the slice's `repo` field, which every clone shares). If the path already exists and is this slice's worktree from an earlier session (same branch, listed by `git worktree list`), reuse it; otherwise stop. Branch: `<landing branch>-<slice-id>`, or the repo's convention.
- If the repo already uses a worktree layout (bare repo with sibling worktrees, a `worktrees/` folder), follow it instead.
- The landing branch gets its own worktree (`~/.shwow-kit/worktrees/<checkout>/<landing branch with / as ->`) for merging into.

Create worktrees yourself before starting a worker, so paths and branches are known. Never let a worker run in the user's checkout, and never check out a branch there.

## Start workers

Start one `worker` subagent per slice, in parallel, in the background, with the description `<slug> <slice-id> worker` (the cost log matches on it). Give each the slice file path, the work item path, its worktree path and branch, and the instruction to work only inside that worktree.

Add the work item's row to `~/.shwow-kit/work/index.md` if it's missing. Don't write any status.

## When a worker finishes

- **Done with evidence:** run the `verify` skill for it. Any fixes go back to the same worker (SendMessage) and through `verify` again, so every round gets a fresh review.
- **Verify approves:** merge the slice branch into its landing branch in the landing's worktree, the way the repo merges (fast-forward or merge commit, per `git log --first-parent`). If it conflicts, rebase the slice branch onto the landing branch in the slice's worktree, re-run the slice's verify command, then merge. Write `evidence/<id>-merged.txt` with the merge commit, then remove the slice's worktree (keep its branch until the landing ships). Don't ask the user.
- **Stopped (blocked, two failed attempts, or two failed review rounds):** add a `blocked:` line with the reason to the slice file, and tell the user. Don't restart it with the same instructions. Keep running slices that don't depend on it.

Then start newly ready slices, within the limits above.

## When a landing's slices are all done

Invoke the `land` skill for it. Keep building landings that don't depend on it. Don't start slices of a landing whose branch is built on one that's waiting on the user: the user's review or checks may change the base, and work queued behind an unsigned landing is mostly rework. Say so in the report, and pick those slices up once the landing below ships. Stop starting new slices if three landings are waiting on the user.

## Stop and report

Run until no slice is ready or running. Then report once, in the message shape below (user's steps last): what was merged into which landing branch, what is waiting on the user (landings to ship, HITL decisions, blocked slices with the reason), and what is left. Between start and that report, one line per change of state at most: slice, status, branch.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
