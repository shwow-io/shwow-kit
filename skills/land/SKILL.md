---
name: land
description: "Get a verified change merged in a way the user understands: explain the diff, quiz the user, scale review to risk, and integrate the way the repo does it (PR or direct). Use whenever the user wants a change merged or shipped, however phrased ('ship it', 'merge it', 'land this', 'open a PR', 'wrap it up'). Never merge, fast-forward or open a PR for a change without going through this skill."
argument-hint: "[work item slug] [slice id]"
---

# Land

The user merges only what they can explain. This step makes that quick.

## 1. Check it's ready

The slice must have evidence (`evidence/<slice-id>-checks.txt`) and an approving review (`evidence/<slice-id>-review.md`). If either is missing, run the `verify` skill first.

## 2. Explain the diff

Explain the change to the user, using the diff as the source, even when they have already approved the merge:

- What changed and why, in a few sentences, in terms of behaviour.
- A walk through the diff in reading order (entry point first), grouped by purpose, with `path:line` references. Mention what was deliberately left alone.
- Anything surprising: deviations from `notes.md`, reviewer "should fix" items not addressed, risks.

Keep it short enough to read in a few minutes.

## 3. Quiz

Ask the user 3 questions that someone who understood the change could answer and someone who skimmed couldn't (what happens when X fails, why is Y here, what would break if Z changed). Wait for answers, then say which were right and correct the rest. If the user answered before you asked, still state your three questions and grade their answers against them. If the user gets most wrong, offer a deeper walkthrough before continuing. The user can skip the quiz; record that in `notes.md`.

## 4. Scale review to risk

- **Low risk** (small, covered by tests, easy to revert, no data or security impact): the explanation and evidence are enough.
- **Medium:** the user reads the diff's key files.
- **High** (data, auth, money, public interfaces, migrations, hard to revert): the user reviews the whole diff, and another person if the repo requires it.

Say which level applies and why.

## 5. Integrate

Follow the repo's conventions: branch protection, CONTRIBUTING, PR templates, how recent history was merged. Read `git log --first-parent -20` on the main line: merge commits from branches mean merge this branch the same way; only direct commits and no merges mean the repo works directly on main. A remote that can't host PRs (a local or bare path, no GitHub/Azure DevOps/GitLab remote) rules out a PR.

- **Convention unclear** (mixed history and a PR-capable remote): push the branch and open a PR.
- **Direct commit to the main line:** only when the repo clearly works that way and the change is low risk and easy to revert.

A PR description states what changed, why, how it was verified (summarise the evidence) and anything the reviewer should look at. Ask the user before pushing or merging.

## 6. Clean up

After it's merged, remove the slice's worktree (and its parent folder if now empty) and local branch, set the slice to `done`, and update the work item's row in `~/.shwow-kit/work/index.md`. When every slice is done, run the `compound` skill.
