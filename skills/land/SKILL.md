---
name: land
description: "Ship a landing (a group of verified slices on one branch) in a way the user understands: check it as a whole, explain the diff, scale review to risk, and integrate the way the repo does it (PR or direct). Use whenever the user wants a change merged or shipped, however phrased ('ship it', 'merge it', 'land this', 'open a PR', 'wrap it up'), and when dispatch finishes a landing. Never push to or merge into a default branch, or open a PR, without going through this skill."
argument-hint: "[work item slug] [landing]"
---

# Land

The user ships only what they can explain. This step makes that quick, and it is the only step that waits on them by design.

The unit is a landing from the work item's `landings.md`: its slices are already merged into the landing branch. For a change with no work item (T0), the landing is that one change and its branch.

## 1. Check it's ready

Every slice in the landing is done (State in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`), with evidence (`evidence/<slice-id>-checks.txt`) and an approving review (`evidence/<slice-id>-review.md`). Run any missing step first (`dispatch` or `verify`). Non-blocking review items recorded in `notes.md` for this landing are done (their fix slice merged) or listed for the user under anything surprising.

Then check the landing as a whole, in its worktree: rebase or merge the current main line in if it has moved, and run every slice's verify command plus the repo's fast checks. Save the output to `evidence/<landing>-checks.txt`. A failure here goes back to `dispatch` as a fix slice, not to the user.

Then, in parallel:

- **Landing review:** two `reviewer` subagents on the landing's diff against the main line, one asked for the spec review and one for the standards review (described as `<slug> <landing> review-spec` and `<slug> <landing> review-standards`). Give them the diff, `brief.md`, `acceptance.md`, `landings.md` and the slice files, not the notes or your opinion. Save both verbatim, under separate headings, to `evidence/<landing>-review.md`. Report the two side by side; don't merge or rerank them. Blocking findings go back to `dispatch` as a fix slice in this landing (and through `verify`), then this step runs again; a landing still blocked after two rounds goes to the user. Skip it for a one-slice landing whose slice review already ran on the same diff, unless it's high risk.
- **Impact:** the `impact` skill on the same diff (subagents described as `<slug> <landing> impact`). Its open breaking changes and risks, and its deploy steps, become steps in the user's **Needs you** list.

## 2. Explain the diff

Explain the landing's diff against the main line:

- The problem and how this fixes it, in plain English with no code names, so it can be understood without reading the diff.
- A walk through the diff in reading order (entry point first), grouped by purpose, with `path:line` references. Mention what was deliberately left alone.
- Anything surprising: deviations from `notes.md`, reviewer "should fix" items not addressed (slice and landing reviews), risks.
- What the user has to do after it ships (live checks, keys, accounts), from the slices' notes.
- The impact verdict (`evidence/<landing>-impact.md`): breaking or not, and what its safety rests on.
- What it cost so far: the total line from `python ${CLAUDE_PLUGIN_ROOT}/scripts/cost.py <slug>`.

Keep it short enough to read in a few minutes.

## 3. Scale review to risk

- **Low risk** (small, covered by tests, easy to revert, no data or security impact): the explanation and evidence are enough.
- **Medium:** the user reads the diff's key files.
- **High** (data, auth, money, public interfaces, migrations, hard to revert): the user reviews the whole diff, and another person if the repo requires it.

Say which level applies and why.

## 4. Integrate

Use the method in `landings.md`. If it isn't set, decide from the repo's conventions: branch protection, CONTRIBUTING, PR templates, and `git log --first-parent -20` on the main line. Merge commits from branches mean merge this branch the same way; only direct commits and no merges mean the repo works directly on main. A remote that can't host PRs (a local or bare path, no GitHub/Azure DevOps/GitLab remote) rules out a PR. With mixed history and a PR-capable remote, use a PR.

- **PR:** push the landing branch and open the PR without asking; it changes nothing on the main line. Write the description with the `pr` skill, which reads the evidence, the impact report and `landings.md` from the work item. Give the user the link. The user merges, or tells you to.
- **Direct to the main line:** only when the repo clearly works that way and the change is low risk and easy to revert. Show the explanation and ask the user to approve the push. Push only after they say so.

Pushing to or merging into the default branch always needs the user's approval of that landing.

## 5. Clean up

Once it's merged or pushed: write `evidence/<landing>-shipped.txt` (the commit on the main line, or the PR's URL), then remove the landing's worktree (and its parent folder if now empty) and its local branch, and the slice branches merged into it. If later landings were built on this branch, rebase them onto the main line. When every landing is shipped, run the `compound` skill.

## Talking to the user

Every message has the same shape, in this order, every time:

1. **The answer:** what the user just asked, or what happened, leading with the point.
2. **Details,** only if needed: explanations, evidence, paths.
3. **Last, always:** `**Needs you:**` with numbered steps, or the line `**Nothing needed from you.**` and one line on what is running and what you'll report next. Never at the top or in the middle, so the answer is always first and the user's actions always sit right above where they type.

Each **Needs you** step is one action, complete enough to do without reading anything above it: what to do, the exact command and where to run it (which checkout or worktree), and what to reply ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation. Never end with a bare "OK?".

**Needs you** holds only what the work being discussed needs: the work the user just asked about, or the work you've been running for them. While those items are pending, every later message on that work repeats them in full as first written, not shortened, so the user never has to scroll up. Items pending on other work aren't listed: at most one line before **Needs you** ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
