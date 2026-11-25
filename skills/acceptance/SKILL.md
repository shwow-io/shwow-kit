---
name: acceptance
description: Turn an agreed brief into concrete examples and failing acceptance checks that define "done", and record how each repo involved is verified. Use after framing, before slicing or implementing, or when the user asks for acceptance criteria, test cases, examples or a definition of done.
argument-hint: "[work item slug]"
---

# Acceptance

Pin down "done" as checks a machine can run, so agents can verify their own work and the user reviews a handful of examples instead of a long plan.

## 1. Learn how the repo verifies

For each repo in the brief, find what already exists: test frameworks and how to run one test, linters, type checks, build, scripts, CI steps, documented commands, API collections, end-to-end tooling. Check the repo's AGENTS.md, CLAUDE.md, README, CI config and package or build files. Run the fastest relevant command once to confirm it works. If an example depends on how a library or external API behaves at the pinned version, confirm it with the `researcher` subagent, not memory.

Write `verification.md` in the work item: per repo, the exact commands (whole suite, single test, lint, typecheck, build) and anything that needs services running. Later steps reuse this instead of rediscovering it.

## 2. Write examples

From the brief's outcome, write concrete examples in `acceptance.md`: given a situation, when something happens, then this observable result. Cover the main path, the edge cases the brief names, and each failure mode. Use real values, not placeholders. Ten examples beat a page of prose.

When an example pins existing behaviour the brief doesn't spell out (a boundary like "due today", a default, an error code), say so in the example, so the user can spot a bug being written into the contract.

For a bug or change to existing behaviour, also list what must **not** change.

## 3. Make them executable

Where the repo has a suitable test level, write the examples as failing tests in the repo, next to similar tests and in the repo's style. Write them in the landing's worktree, `~/.shwow-kit/worktrees/<checkout>/<landing branch with / as ->` (created from the main line if missing, on the landing branch), which `dispatch` reuses; never in the user's checkout or a worktree beside it. Run them and confirm they fail for the right reason (missing behaviour, not a broken test). Any new test that passes now must be a deliberate "must not change" guard; otherwise it passes by accident (e.g. an unknown command exits with the same code) and needs tightening.

Where nothing executable fits (docs, config, prose, infrastructure without a dry-run), say how the example will be checked instead: a command with expected output, or an independent review against that example.

In `acceptance.md`, link each example to its check (test name and file, or method).

## 4. Confirm with the user

Show the examples (not the test code) and ask the user to add, remove or correct them. These examples are the contract: once agreed, implementing agents must not edit these tests to make them pass. Changing them needs the user's say-so.

Add an index row if the work item has none, then move to the `slice` skill.

## Don't

- Write implementation code.
- Write tests that pass before the change, or that only check mocks were called.
- Invent behaviour the brief doesn't support; raise it as a question.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
