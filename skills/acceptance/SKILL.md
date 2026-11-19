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

Where the repo has a suitable test level, write the examples as failing tests in the repo, next to similar tests and in the repo's style. Run them and confirm they fail for the right reason (missing behaviour, not a broken test). Any new test that passes now must be a deliberate "must not change" guard; otherwise it passes by accident (e.g. an unknown command exits with the same code) and needs tightening.

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

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".

While anything is still waiting on the user, every later message repeats the full **Needs you** list as first written: each step's options, recommendation, commands and what to reply, not a shortened version. The user may come back after a while and read only the last message; they should never have to scroll up to find what's asked.
