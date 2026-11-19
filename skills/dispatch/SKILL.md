---
name: dispatch
description: Run a work item's slices with worker subagents, each in its own isolated git worktree, several at once where slices are independent. Use when slices are agreed and the user wants them built, says "run/start/dispatch the slices", or asks to work on several things in parallel.
argument-hint: "[work item slug] [slice ids]"
---

# Dispatch

Run slices in parallel without agents tripping over each other or the user's working directory.

## Pick what to run

Read `slices/` in the work item. A slice is ready when its status is `todo` and everything in `depends_on` is `done`, or when it is `running` but no worker from this session is on it (resume it in its existing worktree). From the ready set:

- Run AFK slices. For HITL slices, ask the user the decision the slice names first, record it in the slice, then treat it as AFK.
- Run two slices in parallel only if their `touches` don't overlap and at most one of them has `needs_services: true`.
- Run at most 3 at once. Fewer if outputs are already waiting for the user: if 3 slices are at `review`, don't start more; tell the user what's waiting instead.

## Isolate

Each worker gets its own worktree, outside the user's working directory:

- Default: `~/.shwow-kit/worktrees/<checkout>/<slice-id>-<short-name>`, where `<checkout>` is the folder name of the user's checkout (not the slice's `repo` field, which every clone shares). If the path already exists and is this slice's worktree from an earlier session (same branch, listed by `git worktree list`), reuse it; otherwise stop. New branch named for the work (`<type>/<short-name>` or the repo's own convention).
- If the repo already uses a worktree layout (bare repo with sibling worktrees, a `worktrees/` folder), follow it instead, including how existing folders are named after their branches.
- Branch from the repo's current main line unless the slice depends on another slice's branch.

Create the worktree yourself before starting the worker, so its path and branch are known. Never let a worker run in the user's checkout.

## Start workers

Start one `worker` subagent per slice, in parallel, in the background. Give each:

- the slice file path and the work item path (it reads brief, acceptance, verification, notes from there),
- its worktree path and branch,
- the instruction to work only inside that worktree.

Set the slice status to `running`, and the work item's row in `~/.shwow-kit/work/index.md` to `running` (add the row if missing).

## When a worker finishes

- **Done with evidence:** set status to `review`, then run the `verify` skill for that slice.
- **Stopped (blocked or two failed attempts):** set status to `blocked`, show the user the worker's report, and ask how to proceed. Don't restart it with the same instructions.

Start newly ready slices as others finish, within the limits above.

## Report

Keep the user informed with one line per change of state: slice, status, branch. No narration in between.
