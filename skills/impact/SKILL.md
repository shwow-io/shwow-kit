---
name: impact
description: "Find what a change breaks or affects beyond its diff, in any repo: contracts, consumers, data, deploys, security, operations, the next change; and prove the fact its safety rests on. Use on a plan before building (frame, T1/T2), on a landing before it ships, or when the user asks 'any breaking changes?', 'what does this affect?' or 'is this safe to deploy?'."
argument-hint: "[work item slug] [landing, or 'plan']"
---

# Impact

Find what a change breaks somewhere else, and prove the fact its safety rests on. Look past this repo's callers to what its search won't show: another service, an old client version, an external consumer, existing data, deployed config, a deploy order.

Run it on the plan before building, so the design avoids the break, and on the landing's diff before it ships. Scale it to the change: an internal change with no contract, data or config effect gets one line saying so and why.

**Breaking** means an existing consumer, unchanged, fails or gets a different result once this deploys. That includes removed or renamed fields, routes, events or config keys; changed types, formats, limits, defaults, status codes, error shapes, ordering or timing; new required input; stricter validation or auth; stored data old code can't read; a required deploy order. A consumer built on a promise the change makes but doesn't keep (a documented error code that never arrives) counts too. A break that only hits local dev or a test environment is a risk, not a breaking change.

## Steps

1. **Change.** State what behaves differently, including what the diff doesn't spell out: defaults, error paths, timing. Note where it is: planned, on a branch, merged, or deployed. Once deployed, telemetry shows its effect directly.
2. **Contracts.** List every contract it touches: routes and payloads, events and messages, schemas and stored data, packages and SDKs, config, env vars, secrets and their keys, feature flags, shared resources (queues, tables, storage, keys).
3. **Consumers.** Find each contract's consumers across the org, reading other repos as `${CLAUDE_PLUGIN_ROOT}/skills/impact/repos.md` describes, including client versions still installed.
   - External consumers (public API, SDK, webhooks, partner events) never show in code search. A contract reachable from outside has them unless the user said otherwise.
   - Test suites outside the build (API collections, end-to-end, smoke tests) are consumers too.
   - Operations are consumers too: deploy pipelines and slot swaps that gate on an endpoint, health probes, alert rules and dashboards. A change in what they see (a health endpoint that now fails on a dependency, a renamed metric) is breaking.
   - Live usage comes from telemetry or the user. Use whatever logs or telemetry skill, CLI or MCP server is available; otherwise ask the user.
   - A search across many repos goes to `scout` subagents, one per contract or group of repos, each returning consumers with cites.
   - Done when each contract has its consumers named, or the search that found none.
4. **Beyond the code.** Check each that applies:
   - Data: migrations, backfills, existing rows the new rules reject and how many. Count with a read-only query when you have read access, otherwise hand the query to the user.
   - Environment: deployed settings, environment names, and infra that overrides the app (platform settings, gateways, CDNs), against what the repo assumes. Read-only reads only; never open or print secret values.
   - Deploy: order across services, manual steps (config, secrets, flags), rollback, safe stopping points when it ships in stages.
   - Runtime: background jobs, caches, retries, flag evaluation, performance, cost.
   - Security: auth, permissions, data exposure, lockouts.
   - Ops: logs, metrics and alerts that change or go blind, and whether a break would be noticed at all.
   - Long term: does it make the next change easier or harder, does it add a second way to do one thing.
5. **Safety fact.** Find the one fact the change's safety rests on ("only v2 callers send this field") and push its proof as far up this ladder as is cheap: guess, read (`repo@sha:path`), traced (walked the failure path and it doesn't reach), ran (a test or script calling the real code), observed (the running system or telemetry). Say where it stopped and what blocked the next rung.
6. **Avoid the break.** For each breaking change, propose the non-breaking route if one exists: additive change, expand then migrate then contract, a new version, a flag.

## Record

Save the report to `evidence/<landing>-impact.md` (or `evidence/plan-impact.md` on a plan; in the reply for T0). Lead with the verdict, one item per line, omit empty sections:

```
Breaking: no | yes, N | unknown (what would settle it)
- <what breaks, for which consumer, the non-breaking route> (open | accepted)
Risks:
- <how it breaks>, likelihood and cost (low, medium, high), how to check
Consumers:
- <repo or service>: <what it uses>, affected or not
Safe because: <fact> (<proof level>: <proof>)
Deploy: <order, manual steps, rollback, stopping points>
Cleared:
- <checked and fine>
```

A breaking change or risk is **open** until it's proven safe or the user accepts it. On a plan, open items go into the brief or design as constraints, or to the user as decisions. On a landing, every open item is a step in the user's **Needs you** list before it ships, and the deploy steps go in it too.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
