# The shwow-kit process

Agents write code faster than anyone can check it, so the amount of work that can run at once depends on how much of it can be verified and reviewed. Human time goes on framing the problem, defining what "done" means, and understanding what gets merged. Agents do the rest, in parallel, within those limits.

## Principles

1. **Done means a check passed.** Every change finishes with verification: an existing test or check, a new one written for the change, or (when nothing executable fits) an independent review against the brief. Evidence is recorded either way.
2. **Match the process to the size of the work.** A one-line fix gets no documents; a cross-repo change gets a design note. Size it first, then pick the tier.
3. **One writer per slice, plus an independent reviewer.** Parallel writers work on separate slices in isolated worktrees. The reviewer starts from a fresh context, without the writer's reasoning.
4. **Evidence, not claims.** "Tests pass" is a claim. Show the command and its output, the screenshot, or the review findings.
5. **Merge only what you can explain.** If the human can't explain a change without the agent, it isn't ready to land.
6. **Fix repeated mistakes for good.** When an agent makes the same mistake twice, the fix goes into a test, a check, or a skill, not a correction in chat.
7. **Add parallel work only while quality holds.** Take on another concurrent thread only when rework, failures and understanding are steady at the current level.

## Tiers

| Tier | Typical work | Path |
| --- | --- | --- |
| **T0 Quick** | bug with a repro, config tweak, small refactor | triage → run → verify → land. No documents. |
| **T1 Feature** | a feature within one repo | the full loop |
| **T2 Project** | cross-repo, ambiguous, architectural or risky | the full loop, plus a design note (and ADR), a blind-spot pass and a slice dependency graph. The human owns interfaces and architecture. |

## The loop

| # | Step | Who | Output |
| --- | --- | --- | --- |
| 0 | **Triage**: size it, pick a tier, decide where the work lives | agent, human confirms | tier, work item |
| 1 | **Frame**: the agent interviews the human until problem, outcome, non-goals and constraints are clear | human + agent | `brief.md` (one page max) |
| 2 | **Pin done**: turn the brief into concrete examples and failing acceptance checks; the human reviews these, not a long plan | agent, human approves | acceptance checks |
| 3 | **Slice**: thin vertical slices in dependency order, each with its verification, the area it touches, AFK or HITL, and whether it needs running services; grouped into landings (each one PR or one push), at least one per repo | agent, human confirms | `slices/NN-*.md`, `landings.md` |
| 4 | **Run**: one worker per slice in its own worktree, about 3 at once; test first; stop and report after two failed attempts; log deviations | agents | branch, `notes.md` |
| 5 | **Verify**: run the slice's verification and record evidence; a fresh-context reviewer checks against the brief, the acceptance checks and the repo's written rules; approved slices merge into their landing branch without asking | agents | evidence, review findings |
| 6 | **Land**: check the landing as a whole (its checks, a spec review, a standards review and an impact check), explain it in plain English; review depth scales with risk; open the PR, or push to the main line once the human approves | human | shipped landing |
| 7 | **Compound**: what needed correcting, and where should the fix live? | agent proposes, human approves | updated tests, checks or skills |

Human attention goes to steps 1, 2, 3 (confirming the slices and landings, which is the go-ahead to build) and 6. Between 3 and 6 agents run unattended: they build, verify, commit and merge each AFK slice into its landing branch, and stop only for a HITL decision, a blocked slice, or a landing ready to ship. Pushing to or merging into a default branch always waits for the human. Don't start new slices while three landings are waiting on the human.

**Talking to the human:** every message has the same shape: the answer first, details if needed, and last, always, what the human must do (numbered steps with exact commands and where to run them) or "Nothing needed from you" and what is running. While something is waiting on the human, each later message about that work repeats the full request, not a summary; requests pending on other work get one line.

**AFK / HITL:** AFK slices are well specified and verifiable, so an agent can run them alone. HITL slices need a human decision partway through.

## Where work lives

Every work item lives in `~/.shwow-kit/work/<item>/`, outside every repo, next to the worktrees. A repo only ever receives the code and tests the work changes, so the user's checkout never carries uncommitted work files.

`~/.shwow-kit/work/index.md` lists every work item and its location, so any session can find and resume one. Acceptance checks that are code live in the repo; briefs, slices, notes and evidence live in the work item.

Contents of a work item are listed in [work-items.md](work-items.md). Durable decisions become ADRs in the affected repo when that repo keeps ADRs.

## Isolation

- Every worktree the kit creates, in any skill, goes under `~/.shwow-kit/worktrees/<checkout>/<name>`, where `<checkout>` is the folder name of the user's checkout. Never beside the checkout (`../<repo>-<name>`), inside it, or at a drive root. The one exception is a bare repo whose worktrees sit in its own folder (the `/wt` layout): new worktrees go there too. Existing sibling worktrees of a normal clone are not a convention to follow.
- Parallel writers each get their own worktree there, removed once merged into the landing branch.
- The scout reads without a worktree. Reviewers and verify that need to run code use a temporary worktree in the same place, removed afterwards; nothing touches the user's checkout.
- Slices that need running services (ports, databases) declare it and don't run in parallel with each other.
- Agents work out the repo layout (plain clone, bare with worktrees, monorepo) from what they see; the kit assumes none.

## Verification

Each repo verifies differently. The kit requires verification, not a method:

1. Discover what the repo already has (tests, linters, type checks, build, scripts, documented commands) and use what applies.
2. If nothing covers the change, write a check for it.
3. If nothing executable fits, an independent reviewer checks the change against the brief.

How a repo verifies is recorded in the work item (or in the repo's own docs if it already has them), so later slices reuse it.

## Integrating changes

Work ships in landings, planned at slice time: a large build can be split into several, and multi-repo work has at least one per repo, so a repo that finishes early ships early. Each landing integrates the way its repo does (branch protection, CONTRIBUTING, PR templates, history). With no clear convention, it defaults to a PR. It goes directly to the main line only when the repo clearly works that way and the change is low risk and easy to revert. Agents commit, merge slices into landing branches, push those branches and open PRs on their own; pushing to or merging into the default branch is the human's call. In every case the land step (whole-landing checks, explanation, review scaled to risk) happens first.

## Parallel and cloud

Local worktrees come first. Each slice is self-contained (brief, verification and notes on disk; nothing depends on a particular session), so moving AFK slices to cloud agents later is a change in where they run, not a redesign.

## Side work (background, safe to parallelise)

- **Scout**: read-only exploration that returns a short summary ("where would this change go?").
- **Research**: external docs and APIs, summarised with sources.
- **Cleanup**: periodic passes for duplication, dead code and doc drift, delivered as small changes.

## Measures

Checked weekly: merged slices, cost per slice (from `scripts/cost.py`), median change size, review minutes, corrections per slice, reverts or defects after landing, and discarded sessions. Concurrency changes only when these are steady.

## Components

| Step | Component |
| --- | --- |
| Triage | `triage` skill; `diagnose` skill for bugs whose cause isn't proven |
| Frame | `frame` skill |
| Pin done | `acceptance` skill |
| Slice | `slice` skill |
| Run | `dispatch` skill, `worker` agent |
| Verify | `verify` skill, `reviewer` agent |
| Impact | `impact` skill, on the plan (frame) and on each landing (land) |
| Land | `land` skill: whole-landing checks, spec and standards reviews (`reviewer`), impact, plain-English explanation, PR description from the `pr` skill |
| Compound | `compound` skill, with `scripts/cost.py` for each work item's cost |
| Status and resume | `status` skill |
| Side work | `scout` and `researcher` agents, `cleanup` skill |
