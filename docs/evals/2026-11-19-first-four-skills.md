# Eval: triage, frame, acceptance, slice (2026-11-19)

## Setup

- Sample project: `tasklog`, a stdlib-only Python CLI (add/list/done/rm, tags, due dates, JSON file store), 468 lines, 17 `unittest` tests, README with test commands. One real bug planted: `is_overdue` uses `due <= today`, so tasks due today show as OVERDUE.
- Each run: fresh copy of the project, `git init`, one commit, then `claude -p --model sonnet --permission-mode bypassPermissions` with or without `--plugin-dir X:\repos\shwow-kit`, transcript captured as stream-json.
- 40 runs, $5.64 total. Fixtures for acceptance and slice: a hand-written `brief.md`; for slice also `acceptance.md` (E1 to E12), `verification.md` and 12 failing tests in `tests/test_export.py`, all under `.work/export-tasks/`.
- Caveats: the user's global `~/.claude/CLAUDE.md` and other installed plugins load in both modes (so "no commit without approval" and terse reporting apply to every run). Runs ran in parallel against the real `~/.shwow-kit/work/index.md`, which turned up the slug-collision findings below more often than a single user would. Headless runs cannot answer questions, so the interview loop itself was not exercised; answers were supplied in the prompt.

## Triage

### Triggering (natural phrasing, skill not named)

| Prompt | With plugin: triage invoked | Tier when invoked |
| --- | --- | --- |
| T0 bug with repro (`due today` shown OVERDUE) | 0 of 4 | - |
| T1 recurring tasks, plain repo | 0 of 5 | - |
| T1 recurring tasks, repo has `.work/` | 1 of 2 | T1 |
| T2 shared sync service + tasklog-web + migration | 2 of 2 | T2 |
| Vague idea ("smarter about nudging me?") | 0 of 4 | - |

3 of 17 overall. When it did not trigger, behaviour was indistinguishable from the no-plugin baseline: T0 runs made the one-line fix and ran the 17 existing tests with no regression test (4 of 4 with plugin, 1 of 1 without, each saying "I didn't add a test for the due-today case"); T1 runs implemented recurring tasks straight away with semantics the agent chose itself (5 of 5 with, 1 of 1 without); vague-idea runs gave an options list and asked a question (same with and without).

Trigger experiment on a scratch copy of the plugin with only the description changed (proposed text below): triage invoked in 5 of 6 runs (T0 1 of 2, T1 2 of 2, vague 2 of 2).

### What worked when it ran

- Tiering was sensible: T0 for the bug (2 of 2 explicit `/shwow-kit:triage`, 1 of 1 modified-description run), T1 for recurring tasks, T2 for the cross-repo sync work (2 of 2), T1 for the vague idea (3 of 3, reasoning "becomes T2 if it needs a background daemon").
- T0 path skipped documents and went test-first: both explicit runs added `test_due_today_not_overdue`, ran it failing, fixed, ran the full suite (18 pass), stated "T0, so no work item", and did not commit.
- Location rules were followed: T2 and vague-idea items went to `~/.shwow-kit/work/<slug>/` with an index row; in the repo with `.work/`, the item went to `.work/recurring-tasks/` with an index row (work-with-1). `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md` resolved correctly every time.
- T2 framing (chained into `frame`) asked one question at a time with a recommendation, after reading `store.py`/`models.py` itself. Baseline asked six questions in one message and proposed a backend design.

### What failed

- **Does not auto-trigger** for anything but an obviously large request (table above).
- **Tier message skipped when chaining into frame.** In 5 of 7 runs that went triage then frame (t2-with-1, t2-with-2, mt1-with-1, mt1-with-2, xtamb-with-1) the user never saw the tier or the work item path; the only output was frame's first question.
- **T0 failing test not always run before the fix.** mt0-with-1: "I didn't run the test before the fix, so I haven't seen it fail on the old code."
- **Duplicate and colliding work items.** The index matches by slug and repo name only. xt1-with-1 found a `recurring-tasks` row pointing at another checkout and stopped to ask; mtamb-with-1 silently reused another session's `nudge-reminders`; mtamb-with-2 created `smarter-nudges` next to it and asked; t2-with-2 created `shared-sync-service`, then deleted it to reuse `tasklog-sync-service`.
- **Index location written in a shell-only form.** work-with-1 recorded `/tmp/claude/.../work-with-1/repo/.work/recurring-tasks` (the sandboxed bash view of a Windows temp path), which other shells cannot open.

### Recommended edits (skills/triage/SKILL.md)

Line 3:

> description: Start any new piece of software work. Sizes the request into a tier (T0 quick, T1 feature, T2 project), creates the work item in the right place, and routes to the next step. Use when the user brings a new task, feature, bug or idea, says "let's build/fix/add", or invokes triage, even if they don't name a process.

Replace with (tested, 5 of 6 triggers):

> description: Use FIRST, before reading code or editing anything, whenever the user asks for a code change of any size, however it is phrased - a bug report ("X is wrong, can you fix it"), a feature ("I'd like X to support Y", "let's add"), a refactor, or a vague idea ("maybe it should..."). Sizes the work into a tier (T0 quick, T1 feature, T2 project), sets up the work item, and routes to the next step; for a T0 fix it adds seconds, then continues test-first. Skip only for pure questions that change no code.

Line 21:

> | **T2 Project** | Spans repos or services; ambiguous goal; changes interfaces, data or architecture; risky or hard to reverse. |

Replace with (matches what the agent did, and avoids the conflict with "pick the lower"):

> | **T2 Project** | Spans repos or services; changes interfaces, data or architecture; risky or hard to reverse. A vague goal inside one repo is T1: framing resolves it. |

Line 28:

> 1. Write a failing test or reproduce the problem (or name the check that will prove the fix).

Replace with:

> 1. Write a test that reproduces the problem and run it: show it failing before changing code. Only if no test fits, reproduce by hand or name the check that will prove the fix.

Line 33:

> **T1 / T2:** create the work item following `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md` (location rules, index row, folder). Then tell the user, in two or three lines: the tier and why, where the work item lives, and that the next step is framing. Start the `frame` skill unless the user wants to stop there.

Replace with:

> **T1 / T2:** read `~/.shwow-kit/work/index.md` first. If a row looks like the same work and its location is in this repo, offer to resume it; ignore rows for other checkouts. Never write into a slug folder that already exists. Then create the work item following `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md` (location rules, index row, folder). Print two or three lines (tier and why, work item path, framing is next) before starting the `frame` skill, unless the user wants to stop there.

Also in `docs/work-items.md`, under Index, add: "`location` is an absolute path in the OS's native form; for repo-local items it includes the repo root, so rows from different checkouts don't collide."

## Frame

Prompt: export tasks to CSV and Markdown, with nine supplied answers and "stop once the brief is written". 2 runs with, 1 without. The skill triggered directly in both plugin runs (triage did not run first).

### What worked

- Brief in the right place: `~/.shwow-kit/work/export-tasks/brief.md` with an index row at `framing` (correctly not `slicing`, since the user had not agreed it yet). Baseline wrote `docs/export-brief.md` into the repo.
- Length: 570 and 458 words, template headings kept. Baseline: 667 words with "Design" and "Tests" sections (proposes `tasklog/export.py` with `write_csv(tasks, fh)` and lists eight test cases).
- Outcome checkable: exact CSV header, `;`-joined tags, header-only on no match, exit 1 on existing `-o` file without `--force`. Non-goals present and matching the supplied answers (import, JSON, column selection, `list` changes, new dependencies, file format).
- Agent-made defaults were flagged for the user (BOM on `-o` CSV, formula-injection prefix, `--force` without `-o`), not silently decided.

### What failed

- **Implementation leaks into the brief** despite "Don't plan implementation, list files to change". frame-with-2: "Selection reuses `filter_tasks` / `sort_tasks`", "write through a stream opened with `newline=""`", "Tests call `tasklog.cli.main` directly". frame-with-1: "`tasklog/cli.py` (new subcommand; `list` filters live in `query.py`), likely a new export module". The template's "Repos / areas: where the change lands" invites this.
- **Slug collision overwrote a brief.** Both runs picked `export-tasks`; neither checked whether the folder existed, so the second `cat >` overwrote the first, and frame-with-1 then had to dedupe a doubled index row with `awk`. frame creates the work item itself when invoked directly, but the skill does not say to, or how.
- frame-with-1 added a "Decisions made here" section not in the template.

### Recommended edits (skills/frame/SKILL.md, brief-template.md)

SKILL.md line 24:

> Write `brief.md` in the work item (see `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`) using [brief-template.md](brief-template.md). One page at most. Plain statements, no padding.

Replace with:

> Write `brief.md` in the work item using `${CLAUDE_PLUGIN_ROOT}/skills/frame/brief-template.md`. If there is no work item yet, create it first per `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`, with a slug whose folder does not already exist. One page at most. Defaults you chose for the user go under Open questions, marked as your recommendation; don't add sections.

SKILL.md line 32:

> - Plan implementation, list files to change, or write code. That comes later.

Replace with:

> - Plan implementation, name files, functions or libraries, or write code. If a constraint seems to need one, state the observable constraint instead ("`list` output byte-identical", not "reuse `filter_tasks`").

brief-template.md line 11:

> **Repos / areas:** where the change lands.

Replace with:

> **Repos / areas:** which repos, and which user-facing surfaces change (commands, endpoints, screens). No file names.

## Acceptance

Prompt: brief at `.work/export-tasks/brief.md`, "define exactly what done means", auto-approve, don't implement. 2 runs with, 1 without.

### What worked

- `verification.md` written in both plugin runs with whole-suite, one-module and one-test commands, "no linter, type checker or CI", no services, and the baseline count; `python -m unittest` was run first to confirm it works. Baseline wrote no verification file.
- Examples concrete and linked: with-1 has 14 examples over a 4-task fixture, with exact CSV lines such as `2,"Email ""Bob"", re: Q1",normal,work,2026-03-01,false,2026-03-03T10:15:00,`, each naming its test; with-2 has 17 in a given/when/then table plus a "must not change" table. Baseline: a list of decisions and a checklist, no examples, no example-to-test links.
- Tests fail for the right reason. Re-run independently: with-1 22 fail, all from `invalid choice: 'export'` (SystemExit 2 or assertion on that usage text), 1 guard passes (`test_list_output_unchanged`); with-2 18 fail the same way, 1 guard passes. with-1 noticed two tests passing because argparse rejects the unknown command with the same exit code, and tightened them. Baseline left exactly those two vacuous tests passing ("They only become meaningful once `export` exists").
- No mocks, no implementation code, open choices listed for the user (`done` as `true`/`false` vs `yes`/`no`, line endings, `-o` stdout).
- Contract stated: "Implementing agents must not edit tests/test_export.py".

### What failed

- **Pinned an existing bug as the contract.** with-2 example 6: "`--overdue` | ids 1,4 (due today counts)". Task 4 is due on `today`, so the contract now requires the planted `<=` bug. The brief only says "same filters as `list`"; the agent copied current behaviour without flagging that the boundary is a choice.
- with-1 example 5 ("Markdown default hides done tasks") has no values.
- Neither run touched the index row. The repo-local item had no row (the fixture had none), and the skill does not mention the index; frame already moves the row to `slicing` before acceptance runs, so no status covers this step.

### Recommended edits (skills/acceptance/SKILL.md)

Line 19, after "Use real values, not placeholders. Ten examples beat a page of prose." add:

> When an example pins existing behaviour the brief doesn't spell out (a boundary like "due today", a default, an error code), say so in the example, so the user can spot a bug being written into the contract.

Line 25:

> Where the repo has a suitable test level, write the examples as failing tests in the repo, next to similar tests and in the repo's style. Run them and confirm they fail for the right reason (missing behaviour, not a broken test).

Replace with:

> Where the repo has a suitable test level, write the examples as failing tests in the repo, next to similar tests and in the repo's style. Run them and confirm they fail for the right reason (missing behaviour, not a broken test). Any new test that passes now must be a deliberate "must not change" guard; otherwise it passes by accident (e.g. an unknown command exits with the same code) and needs tightening.

Line 35:

> Then move to the `slice` skill.

Replace with:

> Add an index row if the work item has none, then move to the `slice` skill.

## Slice

Prompt: brief, acceptance (E1 to E12), verification and failing tests in place; "break into pieces agents can pick up, several at once"; auto-accept; don't implement. 2 runs with, 1 without.

### What worked

- Files written in `.work/export-tasks/slices/` using the template frontmatter (`mode`, `depends_on`, `touches`, `needs_services`, `status`). Baseline wrote no files; its plan only lived in chat.
- Vertical and tracer first in both runs: 01 CSV end to end, 02 Markdown, 03 `-o`/`--force`. Baseline started with "Slice 0: skeleton" (subparser plus stubs, Markdown stub raising `NotImplementedError`) then split CSV and Markdown formatters into separate slices, a layer-style split.
- Parallel safety reasoned from `touches`: both runs had 01 declare the `-o`/`--force` flags and a format registry (`render(fmt, tasks)` or a `RENDERERS` dict) so 02 edits only `export.py` and 03 only `cli.py`, making 02 and 03 parallel-safe. `depends_on` was `[01]` for both.
- Each slice has a verify block with the exact commands from `verification.md` (`python -m unittest tests.test_export.CsvExportTests` then `python -m unittest`). Coverage checked: E1 to E12 each map to a slice.
- with-1 spotted that the fixture test `test_table` uses a non-raw `'\|'` literal (SyntaxWarning on 3.12+) and left the test alone as the contract requires.

### What failed

- **Fat tracer bullet.** 01 covers E1 to E6 plus E12 (7 of 12 examples: all filters, sort, quoting, empty file) in both runs. The simplest path is `export --format csv --all` printing rows; filters could be their own slice.
- **Non-behaviour slice.** with-2 added `04-final-check.md` ("No new behaviour", `touches: []`), which is the verify step's job.
- **Index not updated.** Both runs: "no index row to set to `running`" / "the work item has no index file". The skill only says "set the index row".
- **Template path guessed.** slice-with-1 ran `cat ~/.claude/plugins/*/skills/slice/slice-template.md 2>/dev/null || cat /x/repos/shwow-kit/...`; slice-with-2 tried `../../skills/slice/slice-template.md` from the repo before finding it. The relative link does not resolve from the working directory.
- Notes drift toward code ("raise `ValueError("<path> exists (use --force to overwrite)")`", "`csv.writer` with `lineterminator="\n"`"), past the seams that parallel slices actually need.
- with-1 also wrote `00-index.md`, which looks like slice number 00.

### Recommended edits (skills/slice/SKILL.md)

Line 13:

> - **Vertical.** Each slice delivers a thin piece of working behaviour end to end (through every layer it needs), not a layer on its own. The first slice is a tracer bullet: the simplest path through the whole system.

Replace with:

> - **Vertical.** Each slice delivers a thin piece of working behaviour end to end (through every layer it needs), not a layer on its own. The first slice is a tracer bullet: the simplest path through the whole system, making one or two examples pass. Options, filters and edge cases go in later slices.

Line 24:

> 3. Write one file per slice in `slices/`, named `NN-<short-name>.md`, using [slice-template.md](slice-template.md). Number in dependency order.

Replace with:

> 3. Write one file per slice in `slices/`, named `NN-<short-name>.md`, using `${CLAUDE_PLUGIN_ROOT}/skills/slice/slice-template.md`. Number in dependency order, starting at 01. No other files in `slices/`.

Line 26:

> 5. Show the user a short table: slice, mode, depends on, parallel-safe. Ask them to confirm, reorder or merge. Then set the index row to `running`.

Replace with:

> 5. Show the user a short table: slice, mode, depends on, parallel-safe. Ask them to confirm, reorder or merge. Then set the index row to `running`, adding the row if the work item has none.

Line 31:

> - Plan the implementation line by line. A slice states outcome, boundaries and verification, not code.

Replace with:

> - Plan the implementation line by line. A slice states outcome, boundaries and verification, not code. Name only the seams other slices depend on (a function signature, a registry).
> - Add slices that only re-run checks; final verification belongs to the verify step.

## With vs without, in one line each

- Triage: no difference unless it triggers (3 of 17); when it does, T0 becomes test-first and T1/T2 stop for framing instead of building on guessed semantics.
- Frame: shorter brief, in the work item instead of the repo, no design or test plan; still leaks some implementation detail.
- Acceptance: biggest gain. Adds `verification.md`, concrete linked examples, and catches vacuous tests the baseline left in.
- Slice: files with dependencies, touch points and verify commands, vertical split with a parallel-safe seam; baseline produced a chat-only layer split.
