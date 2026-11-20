---
name: pr
description: "Write or rewrite a pull request description that a reviewer can understand without reading the code: the problem and the fix in plain English first, then risk, technical detail, evidence and shipping steps. Use whenever a PR is opened or its description written or improved, with or without a shwow-kit work item: 'open a PR', 'write the PR description', 'update the PR body', 'describe this change for review', 'the PR is hard to follow'."
argument-hint: "[PR number or URL, branch, or work item slug and landing]"
---

# PR

A reviewer should understand what problem a change solves and how, in plain English, before they see a single class name. Everything technical comes after, for those who want it.

## 1. Gather

- **The change:** the diff against its base branch (`git diff <base>...<branch>`, the commit list), or the PR's own diff when given a PR. Read enough of it to explain behaviour, not just files.
- **Why it exists:** in order, a shwow-kit work item (`brief.md`, `design.md`, `notes.md`, `landings.md`), a spec or issue the branch or commits point to, the existing PR description, or ask the user one question: what problem does this solve?
- **Evidence:** a work item's `evidence/` (checks, reviews, impact). Without one, run the repo's relevant tests yourself, and say which and with what result. Never claim a check you didn't see run.
- **Risk:** a work item's impact report if there is one. Otherwise judge it from the diff: migrations, deletions, external calls, contracts and config others read. For a change that touches those, run the `impact` skill.
- **The host:** GitHub, Azure DevOps or GitLab, from the remote URL, and the repo's own PR template (`.github/pull_request_template.md`, `.azuredevops/pull_request_template.md`, `docs/pull_request_template.md` and similar).

## 2. Write

Use `${CLAUDE_PLUGIN_ROOT}/skills/pr/template.md`. The rules that matter most:

- **Problem** and **How this fixes it** are plain English: no class, method, file or field names, no library internals. Concrete consequences ("customers get the email twice"), not mechanisms. Someone who reads only these two sections should understand the change.
- **Risk** says whether it can be undone and what breaks, for whom, if it's wrong.
- Names, paths and diagrams belong in **Technical changes**. One small picture (a call tree or a diff sketch of the flow) beats a list of files.
- Only real evidence: before and after runs you or the work item recorded.
- The repo's own template wins on structure: fit these sections into it rather than replacing it.
- Respect the host's length limit (Azure DevOps: 4,000 characters). Over it, cut Technical changes and Evidence first, never the first two sections. Keep the full version in the work item's `evidence/<landing>-pr.md`, or in the reply.
- Follow the user's and the repo's writing rules (punctuation, no ticket numbers, no attribution) as for any text.
- Title: what changes, in plain words, in the repo's commit style (conventional commit prefixes if its history uses them).

## 3. Publish

- **Opening a new PR:** push the branch and create the PR (`gh pr create`, `az repos pr create`, `glab mr create`) with the title and description. Opening a PR changes nothing on the default branch, so it doesn't need approval; merging does. Never open one against a branch the repo says changes only through its pipeline.
- **Updating an existing PR's description:** show the user the draft first (a file path or the text) and replace it only once they say so. Someone may already be reviewing it.
- Pass the description from a file, not inline, so quotes and backticks survive (`--body-file`, or `--description "$(cat file)"`).

Give the user the link.

## Talking to the user

Start every message to the user with one of these, before anything else:

- `**Needs you:**` then numbered steps, one action each, complete enough to do without reading further: what to do, the exact command and where to run it (which checkout or worktree), and what to reply when done ("say `ship`", "say `done`"). A decision is one step: the question and the options, with your recommendation.
- `**Nothing needed from you.**` then one line on what is running and what you'll report next.

Details (explanations, diffs, evidence) go below, after a blank line. Never put a request for the user only in the details, and never end with a bare "OK?".

**Needs you** holds only what the work you're replying about needs: the work the user just asked about, or the work you've been running for them. While those items are still pending, every later message on that work repeats them in full as first written: each step's options, recommendation, commands and what to reply, not a shortened version, so the user never has to scroll up.

When the user asks about something else, answer that first. Items still pending on other work don't lead the reply and aren't repeated in full: at most one line at the end ("Also waiting on you: claude-gemini slice 01 decision; `/shwow-kit:status` has the detail").
