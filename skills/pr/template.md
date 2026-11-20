# PR description template

Write for a reviewer who knows the product but not this code. The first two sections are plain English: no class, method, file or field names, no library internals. Someone should understand the problem and the fix from them alone, without reading further. Technical detail comes after, for those who want it.

Some hosts cap the length (Azure DevOps: 4,000 characters). Over it, cut from Technical changes and Evidence first, never the first two sections. Keep each section to what a reviewer needs. Skip a section only if it would be empty. Follow the repo's own PR template if it has one, fitting these sections into it.

```markdown
## Problem

<What goes wrong today, or would go wrong without this change, and who or what it affects. Concrete consequences ("customers get the email twice"), not mechanisms. Where this change fits in a larger piece of work, in one line.>

## How this fixes it

<One bullet per idea, each a plain sentence about behaviour ("each event is processed once: a repeat is acknowledged and skipped"). What users or operators will notice, if anything.>

## Risk

**Can be undone:** <yes, by reverting | partly: what stays behind | no: what can't be undone>
**If it's wrong:** <what breaks and for whom, in plain words>
**Breaking for others:** <no | yes, what and for whom>

## Technical changes

<The smallest picture that makes the change clear (a call tree, a diff sketch of the flow, or a mermaid diagram), then short bullets per area, with names. This is where class, file and field names go.>

## Evidence

- Before: <the failing test or check, the wrong output>
- After: <the same run passing>
- <other checks run, with results>

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
