---
name: dispatch
description: Run a work item's slices with worker subagents, each in its own isolated git worktree, several at once where slices are independent, and keep going on its own until the work is built or needs the user. Use when slices are agreed and the user wants them built, says "run/start/dispatch the slices", or asks to work on several things in parallel.
argument-hint: "[work item slug] [slice ids]"
---

# Dispatch

Build every slice the user agreed to, in parallel where safe, without asking between slices. The user is needed only for decisions, blockers and shipping.

## Pick what to run

Read `slices/` and `landings.md` in the work item. If `landings.md` is missing (older work items), create it now: one landing per repo, integrating the way the `land` skill's step 4 decides, and tell the user in one line.

A slice is ready when its status is `todo` and everything in `depends_on` is `done`, or when it is `running` but no worker from this session is on it (resume it in its existing worktree). From the ready set:

- Run AFK slices. For a HITL slice, ask the user the decision the slice names, record it in the slice, then treat it as AFK. Keep other slices running while you wait.
- Run two slices in parallel only if their `touches` don't overlap and at most one of them has `needs_services: true`.
- Run at most 3 at once.

## Isolate

Each landing has a branch (from `landings.md`), created from the repo's current main line the first time a slice of it starts. Each slice gets its own worktree and branch, created from its landing's branch, so it starts with every slice already merged there:

- Default: `~/.shwow-kit/worktrees/<checkout>/<slice-id>-<short-name>`, where `<checkout>` is the folder name of the user's checkout (not the slice's `repo` field, which every clone shares). If the path already exists and is this slice's worktree from an earlier session (same branch, listed by `git worktree list`), reuse it; otherwise stop. Branch: `<landing branch>-<slice-id>`, or the repo's convention.
- If the repo already uses a worktree layout (bare repo with sibling worktrees, a `worktrees/` folder), follow it instead.
- The landing branch gets its own worktree (`~/.shwow-kit/worktrees/<checkout>/<landing branch with / as ->`) for merging into.

Create worktrees yourself before starting a worker, so paths and branches are known. Never let a worker run in the user's checkout, and never check out a branch there.

## Start workers

Start one `worker` subagent per slice, in parallel, in the background. Give each the slice file path, the work item path, its worktree path and branch, and the instruction to work only inside that worktree.

Set the slice status to `running`, the landing to `building`, and the work item's row in `~/.shwow-kit/work/index.md` to `running` (add the row if missing).

## When a worker finishes

- **Done with evidence:** set the slice to `review` and run the `verify` skill for it. Any fixes go back to the same worker (SendMessage) and through `verify` again, so every round gets a fresh review.
- **Verify approves:** merge the slice branch into its landing branch in the landing's worktree, the way the repo merges (fast-forward or merge commit, per `git log --first-parent`). If it conflicts, rebase the slice branch onto the landing branch in the slice's worktree, re-run the slice's verify command, then merge. Remove the slice's worktree and branch, set the slice to `done`. Don't ask the user.
- **Stopped (blocked, two failed attempts, or two failed review rounds):** set the slice to `blocked`, record why in `notes.md`, and tell the user. Don't restart it with the same instructions. Keep running slices that don't depend on it.

Then start newly ready slices, within the limits above.

## When a landing's slices are all done

Set the landing to `ready` and invoke the `land` skill for it. Keep building other landings meanwhile. Stop starting new slices if three landings are waiting on the user.

## Stop and report

Run until no slice is ready or running. Then report once: what was merged into which landing branch, what is waiting on the user (landings to ship, HITL decisions, blocked slices with the reason), and what is left. Between start and that report, one line per change of state at most: slice, status, branch.
