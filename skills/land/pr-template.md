# PR description

Keep each section to what a reviewer needs. Skip a section only if it would be empty. Follow the repo's own PR template if it has one, fitting these sections into it.

```markdown
## What and why

<two or three sentences, in terms of behaviour>

<the smallest picture that makes the change clear: a call tree, a diff sketch of the flow or file layout, or a mermaid diagram. One, rarely two.>

## Evidence

- Before: <the failing test or check, the wrong output>
- After: <the same run passing>
- <other checks run on the whole landing, with results>

## Impact

**Breaking:** <no | yes, what and for whom> (from the impact report)
**Blast radius:** <who or what is affected if this is wrong>
**Can be undone:** <yes, by reverting | no: what can't be undone, e.g. a migration that drops data, an external call>

## Shipping

<order, manual steps, release gates, live checks after, and the rollback; omit for a plain revert-safe change>

## Look at

<the two or three places a reviewer's attention is worth most, with paths>
```

A diff sketch shows only the shape that changed:

```diff
 receive webhook
+  already processed? return 200
   save event
   start orchestration
```
