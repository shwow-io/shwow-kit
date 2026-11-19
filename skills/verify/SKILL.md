---
name: verify
description: "Prove a change works before it lands: run the right checks, record evidence, and get an independent review against the brief. Every change needs this, including small fixes and non-code changes. Use after a slice or fix is implemented, before landing, and whenever the user asks whether a change works, is done, is ready or can be merged (for example 'does this work?' or 'is this done?'), even without naming verification."
argument-hint: "[work item slug] [slice id]"
---

# Verify

No change lands on a claim. It lands on evidence.

## 1. Run checks

In the change's worktree. If it has none, create a temporary one at `~/.shwow-kit/worktrees/<checkout>/verify-<id>` with `git worktree add --detach`, and remove it with `git worktree remove --force` when done (never anywhere else, least of all a drive root); never switch branches or edit files in the user's checkout. In order of preference:

1. **Existing checks** that cover the change: the slice's verify command, related tests, lint, typecheck, build. Take commands from the work item's `verification.md`; if there isn't one, discover them (AGENTS.md, CLAUDE.md, README, CI config, build files) and record what you found in `verification.md`.
2. **A new check** if nothing existing covers the change: a test, a script, or a command with expected output. Add it to the repo if it belongs there.
3. **Exercise it for real** where tests can't reach: run the app, call the endpoint, drive the UI, dry-run the deployment. Capture the output or screenshot.

If nothing executable fits (docs, prose, some config), step 2 below is the verification.

Save the commands and their output to `evidence/<slice-id>-checks.txt` in the work item (for T0 work, show it in the reply), also when the user only asked "is it done?". Report failures as failures; don't fix them here, send them back to the worker or the user, and skip step 2 until they are fixed. Exception: when nothing executable fits, step 2 is the verification and always runs.

## 2. Independent review

Start the `reviewer` subagent, described as `<slug> <slice-id> review` (the cost log matches on it), with the diff, the slice, `brief.md` and `acceptance.md`. Don't pass it the author's reasoning or your opinion. Save its findings verbatim to `evidence/<slice-id>-review.md`; a slice can't be merged without that file.

For T0 work, a reviewer is optional when the change is tiny and fully covered by a failing-then-passing test; otherwise use one.

## 3. Decide

- **Checks pass and review approves:** the slice is ready to merge into its landing branch. Under `dispatch`, return to it; it merges without asking the user. Run on its own (no work item, or a T0 fix), hand over to the `land` skill.
- **Anything blocking:** list it and send the findings to the worker (or the user for HITL). The fix comes back through this skill with a fresh reviewer every round; don't approve a fix yourself. A slice still failing after its second fix round is blocked: add a `blocked:` line with the reason to the slice file, and ask the user.

## Report

Three lines at most after the opening line (below): checks (pass/fail, evidence path), review verdict, next step.

## Talking to the user

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".

While anything is still waiting on the user, every later message repeats the full **Needs you** list as first written: each step's options, recommendation, commands and what to reply, not a shortened version. The user may come back after a while and read only the last message; they should never have to scroll up to find what's asked.
