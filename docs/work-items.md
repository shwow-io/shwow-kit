# Work items

Every piece of T1/T2 work has a folder. T0 work has none.

## Location

Decide once, when the work item is created:

1. Work confined to one repo, and that repo (or the `.claude` config of the current directory) already has a work folder: use it. Recognised names: `.work/`, `.scratch/`, `work/`, or a path named under a "Work items" heading in the repo's AGENTS.md or CLAUDE.md.
2. Anything else, including all multi-repo work: `~/.shwow-kit/work/<slug>/`.
3. The user can override either.

Never create a work folder inside a repo that doesn't already have one.

## Index

`~/.shwow-kit/work/index.md` lists every work item, whichever location it lives in, so any session can find one:

```
| slug | tier | status | location | repos | updated |
```

Status: `framing`, `slicing`, `running`, `landing`, `done`, `parked`. Update the row whenever status changes; add it if missing.

`location` is an absolute path in the OS's native form; for repo-local items it includes the repo root, so rows from different checkouts don't collide. Pick a slug whose folder doesn't exist yet; never overwrite an existing work item.

## Contents

```
<slug>/
  brief.md          problem, outcome, non-goals, constraints (frame)
  acceptance.md     examples and where their checks live (acceptance)
  verification.md   how each repo involved is verified (acceptance, reused by verify)
  design.md         T2 only: interfaces, decisions, blind spots (frame)
  slices/NN-<name>.md
  notes.md          deviations, decisions, corrections made during the work
  evidence/         command output, screenshots, review findings
```

Slug: short kebab-case description, e.g. `export-invoices-csv`.

Executable acceptance checks are code and live in the repo with the change. Everything else stays in the work item.
