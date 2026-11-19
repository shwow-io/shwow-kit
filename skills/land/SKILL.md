---
name: land
description: "Ship a landing (a group of verified slices on one branch) in a way the user understands: check it as a whole, explain the diff, scale review to risk, and integrate the way the repo does it (PR or direct). Use whenever the user wants a change merged or shipped, however phrased ('ship it', 'merge it', 'land this', 'open a PR', 'wrap it up'), and when dispatch finishes a landing. Never push to or merge into a default branch, or open a PR, without going through this skill."
argument-hint: "[work item slug] [landing]"
---

# Land

The user ships only what they can explain. This step makes that quick, and it is the only step that waits on them by design.

The unit is a landing from the work item's `landings.md`: its slices are already merged into the landing branch. For a change with no work item (T0), the landing is that one change and its branch.

## 1. Check it's ready

Every slice in the landing is done (State in `${CLAUDE_PLUGIN_ROOT}/docs/work-items.md`), with evidence (`evidence/<slice-id>-checks.txt`) and an approving review (`evidence/<slice-id>-review.md`). Run any missing step first (`dispatch` or `verify`).

Then check the landing as a whole, in its worktree: rebase or merge the current main line in if it has moved, and run every slice's verify command plus the repo's fast checks. Save the output to `evidence/<landing>-checks.txt`. A failure here goes back to `dispatch` as a fix slice, not to the user.

## 2. Explain the diff

Explain the landing's diff against the main line:

- What changed and why, in a few sentences, in terms of behaviour.
- A walk through the diff in reading order (entry point first), grouped by purpose, with `path:line` references. Mention what was deliberately left alone.
- Anything surprising: deviations from `notes.md`, reviewer "should fix" items not addressed, risks.
- What the user has to do after it ships (live checks, keys, accounts), from the slices' notes.

Keep it short enough to read in a few minutes.

## 3. Scale review to risk

- **Low risk** (small, covered by tests, easy to revert, no data or security impact): the explanation and evidence are enough.
- **Medium:** the user reads the diff's key files.
- **High** (data, auth, money, public interfaces, migrations, hard to revert): the user reviews the whole diff, and another person if the repo requires it.

Say which level applies and why.

## 4. Integrate

Use the method in `landings.md`. If it isn't set, decide from the repo's conventions: branch protection, CONTRIBUTING, PR templates, and `git log --first-parent -20` on the main line. Merge commits from branches mean merge this branch the same way; only direct commits and no merges mean the repo works directly on main. A remote that can't host PRs (a local or bare path, no GitHub/Azure DevOps/GitLab remote) rules out a PR. With mixed history and a PR-capable remote, use a PR.

- **PR:** push the landing branch and open the PR without asking; it changes nothing on the main line. The description states what changed, why, how it was verified (summarise the evidence) and anything the reviewer should look at. Give the user the link. The user merges, or tells you to.
- **Direct to the main line:** only when the repo clearly works that way and the change is low risk and easy to revert. Show the explanation and ask the user to approve the push. Push only after they say so.

Pushing to or merging into the default branch always needs the user's approval of that landing.

## 5. Clean up

Once it's merged or pushed: write `evidence/<landing>-shipped.txt` (the commit on the main line, or the PR's URL), then remove the landing's worktree (and its parent folder if now empty) and its local branch, and the slice branches merged into it. If later landings were built on this branch, rebase them onto the main line. When every landing is shipped, run the `compound` skill.

## Talking to the user

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".
