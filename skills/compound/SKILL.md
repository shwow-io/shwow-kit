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

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
