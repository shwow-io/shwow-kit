---
name: cleanup
description: "Find and fix accumulated mess in one repo (duplicated code, dead code, stale docs and comments, drift from the repo's own conventions) as a set of small, independent, verified changes. Use when the user asks for a cleanup, tidy-up, debt pass or 'garbage collection', or on a schedule. Not for feature work or refactors the user hasn't asked for."
argument-hint: "[repo path] [focus, e.g. duplication|dead-code|docs]"
---

# Cleanup

Agents add code faster than they remove it. This is the regular pass that keeps a codebase from rotting, done as small changes that are each easy to review and revert.

## 1. Find

In one repo (the current one unless named), look for:

- **Duplication:** near-identical functions or blocks that should share one implementation. Use the repo's duplication tooling if it has any; otherwise search for repeated shapes.
- **Dead code:** unused exports, functions, files, flags, dependencies. Confirm with references across the repo (and its consumers, if known) before calling anything unused.
- **Stale docs and comments:** README commands that no longer work (run them), comments that contradict the code, docs for removed features.
- **Convention drift:** places that break patterns the repo clearly uses elsewhere, or rules in its AGENTS.md / CLAUDE.md / contributing docs.

Use `scout` subagents to search different areas in parallel. Skip anything that is really a behaviour change or a design question; list it for the user instead.

## 2. Pick

Keep at most 5 findings per run, highest value and lowest risk first. Each must be independent of the others and easy to revert. Show the user the list (finding, `path:line`, proposed change, risk) and let them drop any. For each README or doc command in the findings, say you ran it and what it printed.

## 3. Run it as a work item

Create a T1 work item `cleanup-<checkout>-<yyyy-mm-dd>` (`<checkout>` is the folder name of the user's checkout) per `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`, including the index row. Skip frame and acceptance: write a short `brief.md` listing the approved findings, and the `verification.md` for the repo. Each finding becomes one slice file from `${CLAUDE_PLUGIN_ROOT}/skills/slice/slice-template.md` (AFK, `depends_on: []`, its `touches`, landing `cleanup`) whose acceptance is "behaviour unchanged": existing tests pass, plus a test first if the touched code has none.

Write `landings.md` with one landing, `cleanup`, on branch `chore/cleanup-<yyyy-mm-dd>` (or the repo's convention), integrated per the repo. Then invoke the `dispatch` skill for the work item, even when the user approved everything up front and the changes are one-liners: one worker and one branch per finding, each in its own worktree. Never edit or switch branches in the user's checkout. Don't report back until every slice is done or blocked; shipping goes through `land`, which waits on the user for the default branch. Cleanup changes land separately from feature work, never mixed into a feature branch.

## Don't

- Change behaviour, public interfaces or formatting across the whole repo.
- Delete anything you can't prove is unused.
- Touch more than one repo per run.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
