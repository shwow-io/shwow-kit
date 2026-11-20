# Work items

Every piece of T1/T2 work has a folder. T0 work has none.

## Location

Every work item lives in `~/.shwow-kit/work/<slug>/`, whether it touches one repo or several, next to the worktrees in `~/.shwow-kit/worktrees/`. Nothing about the work goes into a repo except the code and tests the work changes: a work folder in the repo would sit as uncommitted files on the user's branch, and agents would have to decide whether to commit it.

Work items created by earlier versions inside a repo (`.scratch/`, `.work/`) keep working where they are; their index row says where. Move one to `~/.shwow-kit/work/` only when the user asks, and never while a session is running it.

## Index

`~/.shwow-kit/work/index.md` lists every work item, whichever location it lives in, so any session can find one:

```
| slug | tier | location | repos | closed |
```

Add the row when the work item is created. `closed` is empty while the work is open, `done` once `compound` finishes it, or `parked` when the user sets it aside; those are the only edits a row gets. Everything else about the work's state is worked out from the files and git (see State).

`location` is the work item's absolute path in the OS's native form; `repos` names the repos it touches (folder names of the checkouts), so a session can find the work for the repo it's in. Pick a slug whose folder doesn't exist yet; never overwrite an existing work item.

## Contents

```
<slug>/
  brief.md          problem, outcome, non-goals, constraints (frame)
  acceptance.md     examples and where their checks live (acceptance)
  verification.md   how each repo involved is verified (acceptance, reused by verify)
  design.md         T2 only: interfaces, decisions, blind spots (frame)
  slices/NN-<name>.md
  landings.md       groups of slices that ship together and their branches (slice)
  notes.md          deviations, decisions, corrections made during the work
  evidence/         command output, screenshots, review findings
```

Slug: short kebab-case description, e.g. `export-invoices-csv`.

Executable acceptance checks are code and live in the repo with the change. Everything else stays in the work item.

## State

Nothing records "running" or "in review": a session can stop at any moment, and a stored status would then be wrong. State is read from what exists, each time it is needed. The only things written down are events, as files in `evidence/`, written right after they happen, and facts only an agent or the user knows, in the slice file.

**A slice** is, in order of precedence:

- **Done:** `evidence/<id>-merged.txt` exists (the merge commit, written right after merging into the landing branch), or the slice's branch is already contained in its landing branch (`git merge-base --is-ancestor`), or its landing is shipped. If the branch is merged but the file is missing, write the file.
- **Blocked:** the slice file has a `blocked:` line (the reason). Removed when the user resolves it.
- **Approved:** the last round in `evidence/<id>-review.md` approves: merge it.
- **Started:** its worktree or branch exists. Whether a worker is still on it or a session died, the next step is the same: resume in that worktree.
- **Ready:** none of the above and every slice in `depends_on` is done. A ready HITL slice with no `decision:` line is waiting on the user.

**A landing** is:

- **Shipped:** `evidence/<landing>-shipped.txt` exists (the commit on the main line or the merged PR's URL), or its branch's tip is in the main line, or its PR is merged. Write the file if it is missing.
- **Waiting on the user:** every slice is done and it isn't shipped. With an open PR, the user's step is merging it; otherwise it's approving the push.
- **Building:** otherwise.

**A work item's** next step: no `brief.md` → frame; no `acceptance.md` → acceptance; no slices → slice; any slice not done → dispatch; a landing waiting → land; every landing shipped and `closed` empty → compound.
