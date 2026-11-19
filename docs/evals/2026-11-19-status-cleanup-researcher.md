# Eval: status, cleanup, researcher (2026-11-19)

## Setup

- Each run: `claude -p [--plugin-dir X:\repos\shwow-kit] --settings <json> --model sonnet --permission-mode bypassPermissions`, transcript as stream-json. The settings JSON sets `"enabledPlugins": {"shwow-kit@shwow-kit": false}` so the user-scope v0.1 install never loads. Checked once: with `--plugin-dir`, the skill list showed one copy of every shwow-kit skill and agent including `status`, `cleanup` and `researcher`; without it, none.
- 33 runs, about $4 reported (worker and reviewer subagents included). 7 of them used a scratch copy of the plugin with the edits proposed below ("kit2" runs).
- Status fixtures: a temp repo `shop` with a git-ignored `.work/export-csv` (01 done, 02 landing, 03 running with an existing worktree at `~/.shwow-kit/worktrees/shop/03-quoting` holding an uncommitted stub); user-level `billing-migration` (T2: 01 review, 02 blocked with the reason in `notes.md`, 03 HITL `todo` naming a decision, 04 landing); `auth-refresh` (index row `slicing`, slices 01 landing and 02 done); `dark-mode` (brief only); `order-search` (both slices landing, real branches, evidence); `readme-badges` (`done`); `legacy-reports` (location missing). Real branches for every landing slice.
- Cleanup fixture: `stockroom`, a stdlib Python inventory CLI, 344 lines in `inventory/`, 14 `unittest` tests. Planted: identical `_format_money` (`report.py:4`) and `_cents_to_str` (`export.py:6`); dead `legacy_parse_date` (`utils.py:21`) plus its `datetime` import; `notify_low_stock` (`alerts.py`) referenced only from `hooks.json` as a string and loaded with `importlib`, and every `cmd_*` handler reached only via `getattr(commands, "cmd_" + name)`, with no test covering the hook; README `python -m inventory valuation` (the command is `value`); `store.py:52` comment "sorted by name, A to Z" over a sort by `(quantity, sku)`.
- Researcher fixture: `bookings` repo pinning `pydantic==1.10.13` and `fastapi==0.99.1`, models using v1 `@validator` and `class Config: anystr_strip_whitespace`.
- Caveats: the user's global `~/.claude/CLAUDE.md` loads in both modes (no commits without approval, terse replies), so pre-approved prompts said "Commits on branches you create for this are approved". Headless runs cannot answer questions. `~/.shwow-kit` did not exist before the eval and was deleted afterwards.

## Status: overview

Prompts: "what's going on with my work?" (from the repo) and "what's waiting on me?" (from a non-repo folder), 2 with, 1 without, plus 1 kit2.

### What worked

- Triggered in 2 of 2 (`shwow-kit:status`), one `cat` of the index and one shell loop over every location. About $0.10 each.
- One table, `done` item hidden (2 of 2), `legacy-reports` shown as `missing` with the row left in place (2 of 2), blocked reason taken from `notes.md` ("ledger-svc staging DB credentials expired. Ops needs to rotate the secret"), and the 3-or-more warning given (2 of 2).
- Next commands correct: `/shwow-kit:land order-search 01`, `/shwow-kit:land auth-refresh 01`, `/shwow-kit:land export-csv 02`, `/shwow-kit:acceptance dark-mode`.
- Index fixed in 2 of 2: `auth-refresh` `slicing` to `landing`, and said so.

### What failed

- **HITL decision missed** in 2 of 2: `billing-migration` 03 (`mode: HITL`, "user must choose cutover window") was reported as "Slice 03 is still `todo`", not as waiting on the user. The skill tells the agent to read only the slices' `status` fields (line 14), and the loop grepped `^status` only.
- **`review` listed as waiting on the user** in 2 of 2 ("04 (landing), 01 (review)"); review is the verify step's job.
- **Invalid index status written:** s1 set `dark-mode` to `acceptance`, as did resume r1. `docs/work-items.md` allows only `framing, slicing, running, landing, done, parked`. `updated` never changed.
- **Order** undefined: the blocked T2 item came 4th of 6 both times; the warning went above the table, not under it (s1, s2).
- Count off by one in s2 ("6 slices are waiting on you to land"; 5 were landing).

### Without the plugin

"Not much in flight": listed `main` and the `feat/csv-quoting` worktree from `git`, never opened `~/.shwow-kit` or `.work/`. Missed every work item, waiting slice and blocker.

### With the edits below (kit2, 1 run)

HITL caught ("03 (cutover plan, your decision)"), `review` described as "at review, waiting on verify", index left with valid statuses only.

## Status: resume

Prompts: "carry on with <slug>". 4 with, 1 without, 1 kit2.

| Item state | Step picked | Skill continued | Result |
| --- | --- | --- | --- |
| `dark-mode`: brief, no acceptance | acceptance | `shwow-kit:acceptance` invoked | correct; wrote `verification.md` and a draft `acceptance.md`, asked 3 questions |
| `export-csv`: 01 done, 02 landing, 03 running in existing worktree | both named | none | stopped and asked which first; found the worktree; nothing redone |
| `export-csv`: 01, 02 done, 03 running in existing worktree | dispatch | none | implemented 03 itself in the existing worktree |
| `order-search`: all landing | land | `shwow-kit:land order-search 01` | explanation with `src/search.py:1-4`, risk low, integration "merge directly" (no remote, linear), stacked 02 noted, 3 quiz questions, no merge |

### What worked

- Step chosen correctly in 4 of 4 and no finished step redone. The existing worktree was found with `git worktree list` and reused in both `export-csv` runs.
- The land hand-off works now that land is model-invocable: r3 invoked it directly and stopped at the quiz.

### What failed

- **Dispatch bypassed.** r2b went from status straight to writing `test_quoting.py` and `src/csvq.py` in the main session: no `dispatch`, no `worker`, no evidence file, no verify; set 03 to `review` and suggested `/shwow-kit:verify`. Test-first was followed. Line 31 says "continue with that step's skill" but doesn't say to invoke it.
- **Dispatch would refuse the reuse anyway:** dispatch line 23 says "Stop if the path already exists", and line 13 only treats `todo` slices as ready, so a `running` slice from a dead session is never picked up.

### Without the plugin

r2b-without found `.work/export-csv` by searching (10 turns vs 6), implemented 03 in the existing worktree the same way, and did not update the slice status. Same result, minus the bookkeeping.

### With the edits below (kit2, 1 run)

`status` → `shwow-kit:dispatch` ("Reuse existing worktree ... on branch feat/csv-quoting") → background `worker` → `verify` → fresh `reviewer`. The reviewer found a real gap: `quote()` is never called and slice 01's code is on no branch (a fixture shortcut). Slice set `blocked`, review saved to `evidence/03-review.md`. $0.34.

### Recommended edits (skills/status/SKILL.md)

Line 14:

> 2. For each row not `done` or `parked`, open its location and read the slice files' `status` fields. If the location is missing, mark the row `missing` in the reply (don't delete it).

Replace with:

> 2. For each row not `done` or `parked`, open its location and read the slice files' `status`, `mode` and `depends_on` fields. If the location is missing, mark the row `missing` in the reply (don't delete it).

Line 15:

> 3. Reply with one table, most urgent first:

Replace with:

> 3. Reply with one table: items with something waiting on you or blocked first, then items with work running, then the rest; `missing` rows last.

Line 20:

> - **Waiting on you:** slices at `landing` (ready to land), HITL decisions, briefs or acceptance examples awaiting confirmation.

Replace with:

> - **Waiting on you:** slices at `landing` (ready to land); HITL slices at `todo` whose dependencies are done (name the decision from the slice); briefs or acceptance examples awaiting confirmation. Slices at `review` are waiting on the verify step, not on the user.

Line 31:

> 3. Tell the user in two or three lines where it stands and what you'll do next, then continue with that step's skill. Check for worktrees from a previous session (`git worktree list` in the repo) before creating new ones, and reuse them.

Replace with:

> 3. Tell the user in two or three lines where it stands and what you'll do next, then invoke that step's skill rather than doing the step yourself (for `todo` or `running` slices that is `dispatch`, which starts workers; don't implement a slice in this session). Check for worktrees from a previous session (`git worktree list` in the repo) before creating new ones, and pass them on for reuse.

Line 35:

> If a row's status disagrees with its slice files, fix the row and mention it.

Replace with:

> If a row's status disagrees with its slice files, fix the row (status and `updated`) and mention it. Use only the statuses in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`; acceptance counts as `framing`.

### Recommended edits (skills/dispatch/SKILL.md)

Line 13:

> Read `slices/` in the work item. A slice is ready when its status is `todo` and everything in `depends_on` is `done`. From the ready set:

Replace with:

> Read `slices/` in the work item. A slice is ready when its status is `todo` and everything in `depends_on` is `done`, or when it is `running` but no worker from this session is on it (resume it in its existing worktree). From the ready set:

Line 23, replace "Stop if the path already exists." with:

> If the path already exists and is this slice's worktree from an earlier session (same branch, listed by `git worktree list`), reuse it; otherwise stop.

## Cleanup

Prompt: "can you do a cleanup pass on this repo". 2 with (stop at the list), 2 with pre-approval ("I can't reply mid-run, so I approve whatever list you pick ... Commits on branches you create for this are approved" / "... Run it through the usual loop ..."), 1 without, 1 kit2 pre-approved.

| Planted item | c1 | c2 | Baseline |
| --- | --- | --- | --- |
| Duplicate money formatter | found | found | found, fixed |
| `legacy_parse_date` dead | found | found | found, deleted |
| `notify_low_stock` (string-referenced) | left alone | left alone | left alone |
| README `valuation` | found | found | found, fixed |
| Contradicting comment `store.py:52` | found, comment fix | found, delete comment | flagged as a question |

### What worked

- Triggered in 6 of 6 plugin runs. The list came before any edit in 2 of 2 unapproved runs: finding, `path:line`, proposed change, risk, then "Tell me which to drop". 4 findings each, under the cap.
- The comment contradiction was handled as the skill asks: fix the comment, and list "is sort-by-quantity intended for `list`? If the comment was right, that's a bug" as a design question (4 of 4).
- No behaviour change on any branch (tests pass on each; the new `format_money` test in 3 runs).
- With the edits (kc6): slice files from the template with `touches`, `dispatch` invoked, four `worker` agents in `~/.shwow-kit/worktrees/stockroom-k6/0N-*`, user's checkout untouched on `main`, and 02 held back because 01 and 02 both touch `utils.py`. Workers ran all 7 README commands against a temp data file.

### What failed

- **The string-referenced function was never tested.** Every run read `hooks.json` and `cli.py` up front (a 344-line repo fits in two `cat` calls), so `notify_low_stock` was never a candidate. The trap needs a larger repo; no conclusion either way.
- **README commands not run** in c1 and c2: `valuation` was found by grepping, not by running the documented commands (skill line 17 says "run them"). No `scout` was started (fine at this size).
- **Pre-approved runs skipped the whole loop (2 of 2):**
  - c3 wrote slices with a loop that left each file as one line (`slice 1-dedupe-money`), then made all changes in the user's checkout with `git checkout -q main -b cleanup/drop-legacy-date` per finding. No dispatch, worker, worktree, evidence or review. Index row written with no header and a shell path (`/c/Users/shwow/.shwow-kit/work/...`).
  - c5 created no slices at all, put all four findings on one branch `cleanup/2026-11-19` and left the user's checkout on it. Slug `cleanup-stockroom-2026-11-19` used the repo's name, not the checkout's, so two clones would share it.
- **kc6 (with edits) still stopped before verify:** all slices at `review`, `evidence/0N-verify.txt` from workers only, no reviewer, yet the index row was set to `landing` ("I haven't run the independent review or the land step"). Dispatch line 41 already says to run verify after each worker.
- c2 claimed "`.gitignore` may not cover `__pycache__`. I didn't check." It does (line 1).

### Without the plugin

Applied three fixes straight into the user's checkout (unstaged), no list, no approval, one combined change; asked about the sort order. Same findings, no review, nothing independent or revertible.

### Recommended edits (skills/cleanup/SKILL.md)

Line 28:

> Create a T1 work item `cleanup-<repo>-<yyyy-mm-dd>` per `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`. Skip frame and acceptance: write a short `brief.md` listing the approved findings, and the `verification.md` for the repo. Each finding becomes one AFK slice whose acceptance is "behaviour unchanged": existing tests pass, plus a test first if the touched code has none.

Replace with:

> Create a T1 work item `cleanup-<checkout>-<yyyy-mm-dd>` (`<checkout>` is the folder name of the user's checkout) per `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`, including the index row. Skip frame and acceptance: write a short `brief.md` listing the approved findings, and the `verification.md` for the repo. Each finding becomes one slice file from `${CLAUDE_PLUGIN_ROOT}/skills/slice/slice-template.md` (AFK, `depends_on: []`, its `touches`, status `todo`) whose acceptance is "behaviour unchanged": existing tests pass, plus a test first if the touched code has none.

Line 30:

> Then follow the normal loop: `dispatch` → `verify` → `land` → `compound`. Cleanup changes land separately from feature work, never mixed into a feature branch.

Replace with:

> Then invoke the `dispatch` skill for the work item, even when the user approved everything up front and the changes are one-liners: one worker and one branch per finding, each in its own worktree. Never edit or switch branches in the user's checkout. Don't report back until every slice has been through `verify` (checks and reviewer) or is blocked; leave landing to the user (`/shwow-kit:land <slug> <slice-id>`). Cleanup changes land separately from feature work, never mixed into a feature branch.

(Tested in kc6 without the "Don't report back" sentence; everything up to verify then followed.)

Line 24, append:

> For each README or doc command in the findings, say you ran it and what it printed.

## Researcher

Prompts in the `bookings` repo, all ending "Just tell me, don't change any code" / "Don't change any code":
- A: "What's the right way to make Booking reject an end_date before start_date? I've seen a few different validator APIs around and I'm not sure which applies to us."
- A+links: A plus "Back it up with links to the official docs."
- B: "We're thinking about upgrading pydantic to the latest release. What in bookings/models.py would break, and what replaces each thing?"
- B+named: B plus "Have the researcher look it up."

| Prompt | With: researcher used | With: web used | Without: web used | Kit2: researcher used |
| --- | --- | --- | --- | --- |
| A | 0 of 2 | 0 of 2 | 0 of 1 | 0 of 1 |
| A+links | 0 of 2 (built-in `web-fetch` agent instead) | 2 of 2 | 1 of 1 (`web-fetch`) | 1 of 1 |
| B | 0 of 2 | 0 of 2 | 0 of 1 | 0 of 2 |
| B+named | 1 of 1 | 1 of 1 | - | 1 of 1 |

### What worked

- Pinned version respected in 11 of 11 answers, with or without the plugin: `requirements.txt:1` cited, v2 `field_validator`/`model_validator` ruled out for 1.10.
- When it ran, the researcher used primary sources only: the migration guide, the validators page, `pypi.org/pypi/pydantic/json`, GitHub releases. It named the latest release ("pydantic 2.14.3 (2026-11-04)") where every from-memory answer said only "v2". Format followed (Answer, Details with URLs, Caveats), about 30 lines, under the 50 limit. It marked what it could not confirm ("I'm recalling from memory that leaving it off works but is discouraged, and I didn't confirm that").
- With the body edit below (k5) it read `requirements.txt` itself and flagged "`fastapi==0.99.1`, which predates pydantic v2 support. It will likely conflict" and "2.14.3 needs Python >=3.10". No other run, with or without, mentioned the FastAPI pin, which is the real blocker (FastAPI supports pydantic v2 from 0.100.0).

### What failed

- **Not chosen on its own.** 0 of 6 unnamed plugin runs used it; when the user asked for links, the main agent picked the built-in `web-fetch` agent (2 of 2). Upgrade questions (B) were answered from memory in 5 of 5 unnamed runs, every one admitting it ("This is from my knowledge of v2, not a test run").
- **Leading brief.** In q10 the main agent's prompt already contained the answer ("replacement `field_validator`, needs @classmethod?"; "replacement: `model_config = ConfigDict(str_strip_whitespace=True)`; confirm key rename"), and told it the pinned version, so the agent didn't read the repo itself and missed the FastAPI pin.
- The new description fixes the choice when the main agent already wants the web (A+links 1 of 1) but cannot make it want the web: B stayed from memory (0 of 2). An agent description has no other lever; a line in the skills that do research-shaped work (frame, acceptance, slice) would be needed for that.

### Without the plugin

Same answer quality on A, same from-memory answers on B, `web-fetch` when links were asked for. No difference except the latest-version and FastAPI points that only the researcher produced.

### Recommended edits (agents/researcher.md)

Line 3:

> description: Answers a question that needs outside sources (library or API docs, error messages, standards, how other projects do something) and returns a short summary with citations. Use for background research during framing, acceptance or a slice, so the main context gets the answer instead of the reading.

Replace with (tested: A+links 1 of 1, was 0 of 2):

> description: "Use this instead of WebFetch, WebSearch or a web-fetch agent whenever an answer depends on anything outside the repo: library or API docs, which API applies to a pinned version, upgrade or migration questions, the latest release, error messages, standards. Reads the repo's pinned versions, checks primary sources and returns a short cited answer, so the main context gets the answer instead of the reading. Brief it with the question and the repo path, not your guess at the answer."

Line 11:

> - Check versions and dates. If the codebase pins a version (read its package or build files), answer for that version.

Replace with (tested: k5 found the FastAPI conflict):

> - Check versions and dates. Read the repo's package or build files yourself, even if the caller named a version, and answer for the pinned version. Check whether other pinned packages constrain the answer (a framework that requires the old major version, for example).

## Triggering

| Prompt (plugin loaded, nothing named) | Invoked |
| --- | --- |
| "what's going on with my work?" (in a repo) | status 1 of 1 (+1 kit2) |
| "what's waiting on me?" (not a repo) | status 1 of 1 |
| "carry on with <slug>" | status 4 of 4 (+1 kit2) |
| "can you do a cleanup pass on this repo" (+ variants) | cleanup 4 of 4 (+1 kit2) |
| version or upgrade question about a dependency | researcher 0 of 6 (kit2: 1 of 3) |

## With vs without, in one line each

- Status overview: a correct cross-item table with blockers, next commands and an honest index in about $0.10, versus a `git branch` summary that misses every work item.
- Status resume: right step every time and existing worktrees reused; it only runs the loop (dispatch, worker, verify, reviewer) once line 31 tells it to invoke the skill. Baseline gets to the same code with more searching and no bookkeeping.
- Cleanup: same findings as baseline, but shown for approval first and split per finding; pre-approved runs ignore the loop and edit the user's checkout until the skill names `dispatch` and the template.
- Researcher: better than baseline when used (latest version, FastAPI conflict, primary sources), but the main agent never picks it unprompted; version pinning is respected either way.
