# Eval: dispatch, verify, land, compound, worker, reviewer (2026-11-19)

## Setup

- Sample project: `ledger`, a stdlib-only Python expense CLI (add/list/rm/total, JSON store, integer cents, refunds as negative amounts), 530 lines, 16 `unittest` tests, README with test commands and "format them with `models.format_cents`".
- Work item at repo-local `.work/monthly-report/` (git-ignored): `brief.md`, `acceptance.md` (E1 to E10), `verification.md`, `notes.md`, 3 slices. 01 tracer (`report --month`, text format, renderer stubs and a `RENDERERS` seam) is pre-implemented on main with status `done`; 02 CSV touches only `ledger/render_csv.py`, 03 Markdown only `ledger/render_md.py`, both `depends_on: [01]`. Acceptance tests in `tests/test_report.py` (8 tests).
- Each repo has a bare `origin` on local disk, no PR tooling. Two history styles: linear direct commits on main, and feature branches merged with `--no-ff`.
- Planted states for verify: CSV branch with a hand-rolled `_money` helper (`-350` renders `-4.50`, no test covers it) plus a `notes.md` line from the "worker" justifying it; Markdown branch whose renderer emits `| --- | --- |` with a second commit editing the acceptance test to match; CSV branch that also adds `-o/--output` (a brief non-goal, outside `touches`, all tests pass); README-only branch documenting `--format json`, `-o` and "refunds are left out", none of which is true.
- Each run: `claude -p [--plugin-dir X:\repos\shwow-kit] --model sonnet --permission-mode bypassPermissions`, transcript as stream-json. 41 runs, about $6.60 reported. Worker and reviewer subagents appear in the cost (the reviewer runs on opus per its frontmatter).
- Caveats: the user's global `~/.claude/CLAUDE.md` loads in both modes ("never commit or push without approval"), so dispatch prompts said "Commits on branches you create for this are approved", and every push decision is confounded by that rule. Headless runs cannot answer the land quiz, so answers were supplied in the prompt. `~/.shwow-kit` did not exist before the eval.

## Dispatch and worker

Prompt: "Build the slices for the monthly-report work item (.work/monthly-report). Commits on branches you create for this are approved." 2 runs with, 1 without on a plain clone; 2 with on a bare+worktree container.

### What worked

- Ready set correct in 4 of 4: 01 skipped as `done`, 02 and 03 started together as two background `shwow-kit:worker` agents (`bg=True`), each told its slice path, work item path, worktree and branch.
- Worktrees created before starting workers, outside the checkout: `~/.shwow-kit/worktrees/ledger-d1/02-csv-format` and `.../03-markdown-format`, branches `feat/report-csv`, `feat/report-markdown` / `feat/report-md`. User's checkout stayed on clean `main` in all runs.
- Bare+worktree layout followed in 2 of 2: worktrees added as siblings in the container (`ledger-bt/report-csv`, `ledger-bt/report-md`) next to the existing `main` and `fix-total-rounding`, nothing under `~/.shwow-kit`.
- All 4 runs passed workers absolute work item paths; 3 of 4 said why (`.work/` is git-ignored, so it is not in the worktree).
- Acceptance tests untouched on all 8 worker branches (`git diff main..<branch> -- tests/test_report.py` empty). Every worker reused `format_cents` and `csv.writer`.
- Evidence written by every worker (`evidence/0N-verify.txt`), then verify ran per slice with checks evidence (`0N-checks.txt`), statuses moved `todo -> running -> review -> landing`.
- Reviewer prompts carried slice, brief and acceptance paths and the diff command, never the worker's report.

### What failed

- **Test-first not observed in 3 of 8 workers.** d1-02, d2-02 and d2-03 wrote the renderer before running any test; the starting-state run in worker.md line 11 was skipped.
- **Repo folder name taken from the slice, not the checkout.** dispatch-with-2 used `~/.shwow-kit/worktrees/ledger/...` (the slice's `repo: ledger`) instead of the checkout name `ledger-d2`. Two clones of one repo would collide on the same path.
- **Bare layout folder naming not mirrored.** The container names folders after branches (`fix-total-rounding` for `fix/total-rounding`); both runs used `report-csv` for `feat/report-csv`.
- **Review file missing.** dispatch-with-1 set both slices to `landing` with no `evidence/0N-review.md`; the reviewer output only lived in chat.
- **Index never touched** in 4 of 4 runs (no row existed; dispatch doesn't mention the index).
- **Hand-off to land impossible.** All 4 runs ended "No `land` skill is listed here, so I stopped at `landing`": land is `disable-model-invocation`, so verify's "hand off to the `land` skill" cannot happen.
- Workers never wrote to `notes.md`, including when they added unrequested `|` escaping to the Markdown renderer (categories cannot contain `|`); reviewers approved it.

### Without the plugin

Worked directly in the user's checkout (`git checkout -q -b slice-02-csv-format` in the main working tree), sequentially in one shell, no evidence files, no review, and set both slices to `done`. Branches and code were fine.

### Recommended edits

skills/dispatch/SKILL.md line 23:

> - Default: `~/.shwow-kit/worktrees/<repo>/<slice-id>-<short-name>` on a new branch named for the work (`<type>/<short-name>` or the repo's own convention).

Replace with:

> - Default: `~/.shwow-kit/worktrees/<checkout>/<slice-id>-<short-name>`, where `<checkout>` is the folder name of the user's checkout (not the slice's `repo` field, which every clone shares). Stop if the path already exists. New branch named for the work (`<type>/<short-name>` or the repo's own convention).

Line 24:

> - If the repo already uses a worktree layout (bare repo with sibling worktrees, a `worktrees/` folder), follow it instead.

Replace with:

> - If the repo already uses a worktree layout (bare repo with sibling worktrees, a `worktrees/` folder), follow it instead, including how existing folders are named after their branches.

Line 37:

> Set the slice status to `running`.

Replace with:

> Set the slice status to `running`, and the work item's row in `~/.shwow-kit/work/index.md` to `running` (add the row if missing).

agents/worker.md line 11:

> Read the slice, then `brief.md`, `acceptance.md`, `verification.md` and `notes.md` from the work item. Run the slice's verify command once to see the starting state.

Replace with:

> Read the slice, then `brief.md`, `acceptance.md`, `verification.md` and `notes.md` from the work item. Before editing any code, run the slice's verify command and save its output as the first section of `evidence/<slice-id>-verify.txt`. If the slice's tests already pass, stop and report.

agents/worker.md line 23:

> - Stay inside the slice's outcome and `touches`. Note anything else you notice in your report instead of fixing it.

Replace with:

> - Stay inside the slice's outcome and `touches`. Handling inputs the brief or existing validation rules out is extra scope: leave it out or record it in `notes.md`. Note anything else you notice in your report instead of fixing it.

## Verify and reviewer

Prompts: `/shwow-kit:verify monthly-report 0N. Slice 0N ... is implemented on branch <b>. Verify it.` (baseline: same text without the slash command). Docs case: "I documented the new report command in the README on branch docs/report-readme. Verify it." Per planted state: 2 with, 1 without.

| Planted issue | With: caught | Reviewer launched | Without: caught |
| --- | --- | --- | --- |
| `_money` renders `-4.50` | 2 of 2 | 0 of 2 | 1 of 1 |
| Acceptance test edited | 2 of 2 | 0 of 2 | 1 of 1 |
| `-o` non-goal added, tests pass | 2 of 2 (by the reviewer) | 2 of 2 | 1 of 1 |
| README claims false features | 2 of 2 | 0 of 2 | 1 of 1 |

### What worked

- Evidence saved to `evidence/02-checks.txt` / `03-checks.txt` in every work-item run, with commands and results; statuses set back to `running` on every failure. Baseline wrote nothing and left statuses at `review`.
- Checks ran against a separate worktree in 4 of 6 code runs (`mktemp -d` or `../wt-csv`), leaving the checkout alone.
- The edited acceptance test was caught by checking `git diff main -- tests/test_report.py` (ve1) and by restoring the original test and re-running (ve2: "With `tests/test_report.py` restored from `main`, `MarkdownReportTests` fails both"). Both called out `notes.md` "No deviations" as false.
- Reviewer, when launched, had fresh context: 13 launches, none passed `notes.md` or the worker's report. It caught the scope violation in 2 of 2 (`ledger/cli.py:55,104-110 adds -o/--output to report. Brief non-goal; outside slice touches; untested; bad path gives uncaught OSError`). Findings saved to `evidence/02-review.md`.
- Docs-only change: both plugin runs ran each documented command against a temp `LEDGER_FILE` (skill step 3, "exercise it for real") and listed all four false claims with `path:line`.

### What failed

- **Reviewer skipped whenever checks failed** (6 of 6 failing runs, e.g. "I didn't start the reviewer, because the E10 failure already blocks landing"). Reasonable and cheap, but the skill doesn't say so, and for the docs case it contradicts line 19 ("If nothing executable fits (docs, prose, some config), step 2 below is the verification").
- **User's checkout switched.** ve1 and ve2 ran `git checkout -q feat/report-md` in the main working tree; ve2 then copied `main:tests/test_report.py` over the branch file there to re-run. Both restored `main`, but a dirty checkout would have been at risk.
- **Leftovers.** vs1 left its `mktemp` worktree registered on `feat/report-csv` (blocks later `git worktree add` of that branch); vs2 left `diff-02.patch` beside the repo.
- **Evidence not saved when the user only asks.** Natural-trigger runs ("is this done?") answered from checks but wrote no evidence file and did not change status in 5 of 5 (trig-verify-1, -3, trigmod3-1 to -3: "I didn't save an `evidence/` file; the commands and output are above").
- One reviewer (vs1) ran `cat .work/monthly-report/evidence/*`, reading the worker's own claims before forming a verdict.

### Without the plugin

Same catch rate on these planted issues: sonnet finds them by reading the diff against `acceptance.md`. The difference is process: no evidence files, no status changes, no independent reviewer, and vb0 left the user's checkout on `feat/report-csv` ("I left the `feat/report-csv` branch checked out").

### Recommended edits

skills/verify/SKILL.md line 13:

> In the change's worktree or branch, in order of preference:

Replace with:

> In the change's worktree. If it has none, create a temporary one with `git worktree add` and remove it when done; never switch branches or edit files in the user's checkout. In order of preference:

Line 21:

> Save the commands and their output to `evidence/<slice-id>-checks.txt` in the work item (for T0 work, show it in the reply). Report failures as failures; don't fix them here, send them back to the worker or the user.

Replace with:

> Save the commands and their output to `evidence/<slice-id>-checks.txt` in the work item (for T0 work, show it in the reply), also when the user only asked "is it done?". Report failures as failures; don't fix them here, send them back to the worker or the user, and skip step 2 until they are fixed.

Line 25:

> Start the `reviewer` subagent with the diff, the slice, `brief.md` and `acceptance.md`. Don't pass it the author's reasoning or your opinion. Save its findings to `evidence/<slice-id>-review.md`.

Replace with:

> Start the `reviewer` subagent with the diff, the slice, `brief.md` and `acceptance.md`. Don't pass it the author's reasoning or your opinion. Save its findings verbatim to `evidence/<slice-id>-review.md`; a slice can't reach `landing` without that file.

Line 31:

> - **Checks pass and review approves:** set the slice to `landing` and hand off to the `land` skill.

Replace with:

> - **Checks pass and review approves:** set the slice to `landing` and tell the user to run `/shwow-kit:land <slug> <slice-id>`. Land is user-invoked only; don't merge here.

Line 3 (description). Tested on a scratch copy, natural prompts in a repo with a finished slice checked out: original triggered 2 of 3 ("is this done?" 1 of 1, longer "Is it done?" 1 of 1, "does this work?" 0 of 1); replacement triggered 3 of 3 ("does this work?" 2 of 2, "is this done?" 1 of 1). Quote the value: an unquoted variant with embedded double quotes failed YAML parsing and the skill silently vanished from the skill list (`claude plugin validate` reports it).

> description: Prove a change works before it lands: run the right checks, record evidence, and get an independent review against the brief. Every change needs this, including small fixes and non-code changes. Use after a slice or fix is implemented, before landing, or when the user asks whether something works or is done.

Replace with:

> description: "Prove a change works before it lands: run the right checks, record evidence, and get an independent review against the brief. Every change needs this, including small fixes and non-code changes. Use after a slice or fix is implemented, before landing, and whenever the user asks whether a change works, is done, is ready or can be merged (for example 'does this work?' or 'is this done?'), even without naming verification."

agents/reviewer.md line 8:

> You review a change you did not write. You are given a diff or branch, and the work item's `brief.md`, `acceptance.md` and the slice file. You have none of the author's reasoning, on purpose. Do not edit anything.

Replace with:

> You review a change you did not write. You are given a diff or branch, and the work item's `brief.md`, `acceptance.md` and the slice file. You have none of the author's reasoning, on purpose: don't read `notes.md` or `evidence/`. Do not edit anything or switch branches; use a temporary worktree to run code and remove it afterwards.

## Land

Prompts: `/shwow-kit:land monthly-report 02` plus quiz answers ("I can't reply mid-run, so answers to your quiz: (1) ... (2) ... (3) ..."). Variants: no evidence (1 run); evidence, linear history (3 with, 1 without); evidence, merge-commit history (3 with). Runs 1 and 2 of each style gave no integration approval or "Once the quiz is done, integrate it."; run 3 said "you have my approval to integrate it into main locally the way this repo does it ... Ask before pushing."

### What worked

- **No evidence:** ran `shwow-kit:verify` first (checks, fresh reviewer, `02-checks.txt`, `02-review.md`), then continued to land.
- **Explanation quality** good in the 5 runs that gave one: behaviour in two sentences, `ledger/render_csv.py:5-18` walk, "Left alone: `cli.py`, `report.py`, `render_md.py` and `tests/test_report.py`", the unaddressed reviewer should-fix (no renderer-level empty-rows test), and the `\n` vs RFC 4180 `\r\n` choice.
- **Quiz questions** (the one run that had to write its own): "`render` is handed `rows` already sorted. What would break in the CSV output if it sorted them itself, and where is the sorting done?", "Why is `csv.writer` used instead of joining with `","`? Give the case in the fixture that proves it.", "What changes for a Windows user if `lineterminator` is left at the default?" Meaningful, answerable only after reading the diff.
- **Risk stated** in 7 of 7, all "low" with reasons (two files, tested, single revert, no data or security impact).
- **Integration with approval follows history:** linear repo `git merge --ff-only` (ll3), merge-commit repo `git merge --no-ff ... -m "Merge branch 'feat/report-csv'"` (lm3), matching the existing messages. Merge-style runs without approval proposed the same `--no-ff` merge (2 of 2).
- **Push:** never pushed in 6 of 6; each asked ("Not pushed, so say if you want it pushed"). Confounded by the global CLAUDE.md.
- **Cleanup** after merging (ll3, lm3): worktree removed, branch deleted, slice set `done`, quiz outcome in `notes.md`, compound correctly not run because 03 is still `todo`.

### What failed

- **Explanation skipped when integration was pre-approved.** ll3 and lm3 went from reading the diff straight to merging; their only output was the merge result, quiz grading, risk and cleanup, with no walk through the diff.
- **Linear history read as "unclear" and routed to a PR.** ll1: "history is linear with no merge commits and there's no CONTRIBUTING file, so I'd push `feat/report-csv` and open a PR." ll2 the same. The repo has five direct commits on main, no merges, and an origin that is a local bare repo where no PR can exist. Only when the prompt said "the way this repo does it" did ll3 fast-forward.
- **Index row missed.** ll3: "I found no index row to update", though `~/.shwow-kit/work/index.md` had a `ledger-ll3` row; the agent only looked in `.work/`. lm3 found it.
- **Empty folder left:** `~/.shwow-kit/worktrees/ledger-ll3/` after `git worktree remove`.
- **"Run the `compound` skill" cannot work**: compound is `disable-model-invocation` (same problem as verify's hand-off to land).
- **Quiz pre-answered:** with answers in the prompt, 6 of 6 runs graded the supplied answers instead of posing their own three questions. A harness artefact, but it shows the skill accepts answers to questions it never asked.

### Without the plugin

"Land slice 02 ... Once the quiz is done, integrate it." Baseline searched for a quiz, found none, did not integrate, and offered `git merge --ff-only`. No explanation, no risk level. When the plugin was loaded but the user said "Ship it." (see Triggering), the agent fast-forwarded main with no explanation, quiz, cleanup or status change.

### Recommended edits (skills/land/SKILL.md)

Line 18:

> Explain the change to the user, using the diff as the source:

Replace with:

> Explain the change to the user, using the diff as the source, even when they have already approved the merge:

Line 40:

> Follow the repo's conventions: branch protection, CONTRIBUTING, PR templates, how recent history was merged.

Replace with:

> Follow the repo's conventions: branch protection, CONTRIBUTING, PR templates, how recent history was merged. Read `git log --first-parent -20 main`: merge commits from branches mean merge this branch the same way; only direct commits and no merges mean the repo works directly on main. A remote that can't host PRs (a local or bare path, no `gh`/`az` remote) rules out a PR.

Line 42:

> - **Convention unclear:** push the branch and open a PR.

Replace with:

> - **Convention unclear** (mixed history and a PR-capable remote): push the branch and open a PR.

Line 49:

> After it's merged, remove the slice's worktree and local branch, set the slice to `done`, and update the work item's index row. When every slice is done, run the `compound` skill.

Replace with:

> After it's merged, remove the slice's worktree (and its parent folder if now empty) and local branch, set the slice to `done`, and update the work item's row in `~/.shwow-kit/work/index.md`. When every slice is done, tell the user to run `/shwow-kit:compound <slug>`.

Line 28, after "Wait for answers," add:

> If the user answered before you asked, still state your three questions and grade their answers against them.

## Compound

Fixture: all three slices merged, `notes.md` with two repeated mistakes (local money helper with the `-4.50` bug in 02 and 03; worker ran `python -m pytest` twice despite the README), one acceptance-test edit, one one-off commit typo, and review files for each round. `/shwow-kit:compound monthly-report` (with-1), the same plus "I approve every fix you propose" (with-2), and a plain-language equivalent without the plugin.

### What worked

- Found and read `notes.md` and every `evidence/*-review*.md` (2 of 2).
- Placement followed the ladder. with-1 proposals: (1) `tests/test_money_formats.py` running every renderer on `-350` and asserting `-3.50`, (2) a check that `tests/test_report.py` matches the acceptance commit, (3) kit change: dispatch pastes `verification.md` commands into the worker brief, (4) kit change: acceptance must cover a named edge case in every format. Explicitly no AGENTS.md line: "the facts are already in the README, so the gap is enforcement, not documentation." Typo dropped as a one-off.
- with-1 applied nothing without approval; with-2 applied only the repo change, left kit changes as proposals, recorded the outcome in `notes.md`.
- Metrics line in with-2: `2026-11-19 | monthly-report | T1 | 3 | review rounds 3 (02:1, 03:2) | corrections 2 (pytest x2) + 3 blocked (money helper x2, test edited to pass) | later defects: unknown`.

### What failed

- **Index not updated** in 2 of 2: both looked for an index in `.work/` ("`.work/` has no index file, so I have nothing to set to `done`"); the row in `~/.shwow-kit/work/index.md` stayed `landing`.
- **Metrics skipped without approval.** with-1 deferred the metrics line until after approval, so a session that ends at the proposal writes nothing.
- **Applied a grep, not a behaviour test.** with-2's `tests/test_money_format.py` fails if any module other than `models.py` matches `(//|/|%)\s*100\b|divmod\([^)]*,\s*100\)|:\.2f\}`. It would flag any legitimate `/ 100` and doesn't check that negatives render. with-1's proposal (render every format with `-350`) is the better fix.
- with-2 handled the acceptance-test edit only as a kit proposal, though worker.md already says "Never edit or delete acceptance tests" and was ignored; per the skill's own line 29 that calls for a check (with-1 proposed one).

### Without the plugin

Wrote and staged a repo `CLAUDE.md` with three rules, two of which restate the README ("Tests: `python -m unittest` (pytest is not installed). See README", "Format only with `models.format_cents`"), and said "I assumed they pick up `CLAUDE.md` more reliably. I didn't verify that." No test or check, no metrics, nothing about the process.

### Recommended edits (skills/compound/SKILL.md)

Line 24:

> 1. **A test or check** in the repo, if a machine can catch it.

Replace with:

> 1. **A test or check** in the repo, if a machine can catch it. Prefer a test of the behaviour that went wrong (render a negative total in every format) over a grep for the code that caused it.

Line 33:

> Show the user a short list: lesson, proposed fix, where. Apply only what they approve. Record the outcome in `notes.md`, set the work item to `done` in the index.

Replace with:

> Show the user a short list: lesson, proposed fix, where. Apply only what they approve. Record the outcome in `notes.md`, set the work item to `done` in `~/.shwow-kit/work/index.md`.

Line 37:

> Append one line to `~/.shwow-kit/metrics.md`: date, work item, tier, slices, review rounds, corrections, reverts or defects found later (fill in later if unknown). This is what tells the user whether to run more in parallel.

Replace with:

> Append one line to `~/.shwow-kit/metrics.md` when you show the proposals, whether or not any are approved: date, work item, tier, slices, review rounds, corrections, reverts or defects found later (fill in later if unknown). This is what tells the user whether to run more in parallel.

## Triggering

| Prompt (plugin loaded, skill not named) | Skill invoked |
| --- | --- |
| "is this done?" (finished slice branch checked out) | verify 1 of 1 |
| "does this work?" | verify 0 of 1 |
| "I think I've finished the CSV format for the report. Is it done?" | verify 1 of 1 |
| "Slice 02 looks good to me. Ship it." | land 0 of 1 |
| "OK, let's land the CSV slice and wrap it up." | land 0 of 1 |
| "The monthly report work is finished. Let's do a quick retro..." | compound 0 of 1 |
| "Monthly report is done. Any lessons from it?" | compound 0 of 1 |

- `disable-model-invocation` holds: land and compound were absent from the model's skill list and never invoked, and no run read their SKILL.md by hand.
- The cost of that: both "ship it" runs fast-forwarded `main` on their own (tl1 `c6cdace`, tl2 `e6511be`) with no explanation, quiz, risk level, branch cleanup or status change (slice still `landing`). Both retro runs ignored the git-ignored `.work/` folder entirely, so they missed every note and review ("I can't see the session itself, only the repo"); trig-compound-2 ran `python -m pytest`, the exact mistake the notes record. The fix is for verify and land to name the slash command at the hand-off (edits above), so the user knows to type it.
- verify with the replacement description: 3 of 3 (see Verify).

## With vs without, in one line each

- Dispatch: parallel workers in isolated worktrees with evidence and statuses; baseline builds sequentially in the user's checkout and marks slices `done` with no review.
- Verify: same catch rate on these planted issues (sonnet reads the diff against acceptance either way); the plugin adds evidence files, status changes, a fresh reviewer that caught the scope violation, and mostly keeps the checkout clean.
- Land: explanation, three good quiz questions, risk level and cleanup only when the user types the command; integration follows merge-commit history but sends linear direct-commit history to a PR.
- Compound: test-and-check fixes with no instruction spam, versus a baseline `CLAUDE.md` restating the README; the index and metrics steps need explicit paths and timing.
