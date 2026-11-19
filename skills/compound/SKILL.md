---
name: compound
description: "After a work item (or a painful session) finishes, find what needed human correction or rework and turn each repeat-worthy lesson into a durable fix: a test, a check, a repo instruction, or a skill change. Use when all slices of a work item are landed, after a frustrating session, or when the user asks for a retro, lessons learned, or 'don't let that happen again'."
argument-hint: "[work item slug]"
---

# Compound

Make the next piece of work easier than this one. Every mistake the user had to correct should cost them once.

## 1. Gather

From the work item: `notes.md` (deviations, decisions), `evidence/*-review.md` (blocking findings), `evidence/*-impact.md` (breaks found late or missed), blocked or re-run slices. Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/cost.py <slug>` and save its output to `evidence/cost.md`; a slice that cost several times the others is a lesson to look at (too big, unclear, flaky checks, too many review rounds). From the session: corrections the user made, things they had to repeat, instructions the agent ignored.

## 2. Pick what matters

Keep only lessons likely to recur. Drop one-offs and anything that was just this task's detail.

## 3. Choose where each fix lives

Prefer the most reliable place:

1. **A test or check** in the repo, if a machine can catch it. Prefer a test of the behaviour that went wrong (render a negative total in every format) over a grep for the code that caused it.
2. **A repo instruction** (AGENTS.md / CLAUDE.md), if it's a fact about this repo agents can't discover by reading it: a non-obvious command, a gotcha, where something lives. One line each.
3. **A change to a shwow-kit skill or agent**, if the process itself went wrong. Describe the change for the user to make in the kit; don't edit the installed plugin.
4. **The user's personal instructions**, if it's about how they want to work with agents generally.

Don't add instructions that restate what the code or README already makes clear, and don't add emphasis to lines agents already ignore; make those a check instead.

## 4. Propose, then apply

Show the user a short list: lesson, proposed fix, where. Apply only what they approve. Record the outcome in `notes.md`, set the work item's `closed` to `done` in `~/.shwow-kit/work/index.md`.

## Measures

Append one line to `~/.shwow-kit/metrics.md` when you show the proposals, whether or not any are approved: date, work item, tier, slices, review rounds, corrections, estimated cost (US$, from `evidence/cost.md`), reverts or defects found later (fill in later if unknown). This is what tells the user whether to run more in parallel.

## Talking to the user

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".

While anything is still waiting on the user, every later message repeats the full **Needs you** list as first written: each step's options, recommendation, commands and what to reply, not a shortened version. The user may come back after a while and read only the last message; they should never have to scroll up to find what's asked.
