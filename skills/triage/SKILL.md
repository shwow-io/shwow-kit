---
name: triage
description: Use FIRST, before reading code or editing anything, whenever the user asks for a code change of any size, however it is phrased - a bug report ("X is wrong, can you fix it"), a feature ("I'd like X to support Y", "let's add"), a refactor, a vague idea ("maybe it should..."), or planning a change to do later ("write up the switch for when I'm ready", "spec this out", "plan the migration"), even when nothing is built now. Sizes the work into a tier (T0 quick, T1 feature, T2 project), sets up the work item, and routes to the next step; for a T0 fix it adds seconds, then continues test-first. Skip only for pure questions that neither change code nor plan a change.
argument-hint: "<what you want done>"
---

# Triage

Decide how much process this work needs, set it up, then hand off. Keep it quick: a few minutes, not an analysis.

## 1. Understand just enough

Read the request. If it names code, look at it briefly (or send a scout subagent for anything broad). Ask at most two questions, only if the tier depends on the answer.

## 2. Pick the tier

| Tier | Signals |
| --- | --- |
| **T0 Quick** | One clear change; a repro or obvious target; touches one area; easy to verify and revert. |
| **T1 Feature** | New behaviour in one repo; needs decisions about what "done" means; more than one slice. |
| **T2 Project** | Spans repos or services; changes interfaces, data or architecture; risky or hard to reverse. A vague goal inside one repo is T1: framing resolves it. |

When torn between two tiers, pick the lower and say what would bump it up.

## 3. Route

**A bug whose cause isn't proven yet** (something broken, flaky or slow, with no obvious single-line cause): run the `diagnose` skill first, whatever the tier. Its proven cause and failing check are what the fix, or the work item, starts from.

**T0:** no work item. Do it now:
1. Write a test that reproduces the problem and run it: show it failing before changing code. Only if no test fits, reproduce by hand or name the check that will prove the fix.
2. Make the change.
3. Verify (the `verify` skill's rules apply: evidence, not claims).
4. Land it the way the repo does it.

**T1 / T2:** read `~/.shwow-kit/work/index.md` first. If a row looks like the same work and its location is in this repo, offer to resume it; ignore rows for other checkouts. Never write into a slug folder that already exists. Then create the work item following `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md` (location rules, index row, folder). Print two or three lines (tier and why, work item path, framing is next) before starting the `frame` skill, unless the user wants to stop there.

## Output

One short message: tier, reason, work item path (T1/T2), next step. No restating the request.

## Talking to the user

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".
