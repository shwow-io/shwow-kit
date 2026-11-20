---
name: diagnose
description: "Find and prove the root cause of a bug, failure, flaky test or slowdown with a check that fails on it, before fixing anything. Use when something is broken, throwing, failing, flaky, slow or wrong (locally, in CI or in a deployed environment) and the cause isn't already proven, when the user says 'debug', 'diagnose', 'why is X happening', or when a fix attempt has already failed."
argument-hint: "[symptom, or work item slug]"
---

# Diagnose

A cause is proven by a check that fails on this bug, on the surface where it was seen, and passes once only that cause is changed. Reading code until a theory fits is a guess, and a guess gets labelled as one.

Work read-only in the user's checkout. Anything that changes code (probes, harnesses, the fix) happens in a worktree under `~/.shwow-kit/worktrees/<checkout>/diagnose-<short-name>`, or a slice's worktree when this runs inside one. Never print secrets: write `<REDACTED>` in their place, and keep credentials in env vars rather than in commands you show.

## 1. Pin the symptom

What was seen against what should happen: the error text, wrong value or timing; where (local, CI, which environment, which version); since when; how often. In a deployed environment, read its logs or telemetry first with the environment and time range pinned (whatever logs skill, CLI or MCP server exists): the failing request, its correlation id and stack often name the path. Confirm it still happens on the latest code, and on the version where it was seen.

Done when the symptom is precise enough to tell this bug from a nearby one.

## 2. Build the failing check

This is most of the work. One command that drives the real path and asserts the symptom and its mechanism (the error and where it's thrown), since a catch-all handler makes different failures look alike. Try, roughly in order:

- a failing test at the nearest seam that reaches it;
- a request or CLI call against the app running locally;
- a captured request, payload or event replayed through the path;
- a throwaway harness around the failing path (kept outside the repo, so it can be rerun);
- a differential run: the same input through the old and new version, or two configs;
- `git bisect run` with that check, when it appeared between two known states.

Flaky: loop the trigger until the failure rate is high enough to work with, and record the rate. A captured artifact (profile, trace, dump): a `scout` subagent reduces it to the finding, mapped to source.

Done when it fails on the symptom and its mechanism, the same way every run (or at a pinned rate). If no check is possible, say what would give one (access, a captured artifact, temporary logging) and ask the user; until then, any cause is a guess.

## 3. Shrink it

Remove inputs, data, config and steps one at a time, rerunning after each. Done when every remaining piece is needed.

## 4. Hypothesise, then test

List three to five ranked causes, each with the result that would prove it wrong ("if X, changing Y makes it pass"). Include config, flags, stored data and environment differences, and test those first: they're cheap and often the cause. Show the list to the user in one line each and carry on; they may rule one out.

Test one variable at a time, picking the probe that splits the most hypotheses: a debugger first, then logs at the boundaries, each tagged with one unique prefix. For a slowdown, measure a baseline, then bisect or profile. For a deployed environment you can't reach, give the user read-only commands to run, one per hypothesis it would split. If two fixes resting on the same assumption both failed, write the assumption down as one sentence and test it before a third.

Done when one prediction held and the others failed. For a regression, name the change that introduced it.

## 5. Fix (unless only the cause was asked for)

- Revert every probe, so the regression test can fail first.
- Ask whether the bad state should be possible at all; if not, fix what produced it, not a guard where it lands. Fix every instance of the pattern.
- Write the regression test at the seam that reaches the cause, see it fail, make the fix, see it pass, and see the original check pass.
- Bad data already stored is an instance too: propose its repair to the user, never write it unasked.
- A fix that changes a contract, data or config: run the `impact` skill on it.
- Then the `verify` skill, as for any change. Other things found on the way are proposals, not part of this fix.

Inside a work item, the fix is a slice (or this slice's work); a standalone bug is T0 and lands through `land`.

## 6. Clean up

Remove every tagged log (search for the prefix) and any harness left in the repo. Done when the diff holds only the fix and its tests.

## Record

In the work item's `evidence/diagnose-<short-name>.md`, or the reply for T0:

```
Cause: <one line, with where> (<ran | observed | guess>: <check command>, failed before, passed after)
Ruled out: <hypothesis>: <the result that killed it>
Fix: <what changed, and why it's at the cause>
Open: <stored data to repair, probes for the user>
Would have caught it sooner: <a cheap always-on check or signal>, proposed for `compound`
```

A cause short of "ran" (failed then passed by changing only that cause): a fresh `reviewer` subagent tries to refute it from the evidence before you report it as the cause.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
