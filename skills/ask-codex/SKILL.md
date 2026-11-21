---
name: ask-codex
description: "Hand a task to OpenAI Codex and get back its last message and any files it wrote. Use for things Codex can do and Claude can't, first of all generating or editing images ('make an icon', 'generate a picture of', 'draw a logo'), or when the user asks to have Codex do something."
argument-hint: "<task for Codex>"
---

# Ask Codex

Codex runs the task in a fresh folder of its own, never in a repo checkout. Anything worth keeping, you copy into the repo yourself.

## Run

1. Write the prompt as a complete task: what to make, sizes, formats, and file names if they matter. Codex sees nothing of this conversation.
2. Run it. A run takes a minute or more and can pass the Bash tool's 2-minute default, so set the timeout to 600000 ms or run it in the background:

   ```
   python ${CLAUDE_PLUGIN_ROOT}/skills/ask-codex/ask_codex.py "<prompt>"
   ```

   For a long prompt, pipe it on stdin instead of passing an argument. Add `-m <model>` only if the user names a Codex model.
3. If the script prints one line saying Codex isn't installed or isn't logged in, pass that line to the user and stop. Nothing was run and no folder was made.
4. If Codex fails, the script prints its exit code and last output lines, and keeps the run folder. Report the exit code and the error; don't retry blindly.
5. Otherwise the script prints the run folder, the Codex session id, the files Codex wrote, and Codex's last message. View any image before describing it.
6. Report Codex's last message and the paths of the files it wrote. If the user wants a file in the repo, copy it there; don't point the repo at the run folder.

## Run folder layout

Each run is `~/.shwow-kit/codex/<run>/`, where `<run>` is `YYYYMMDD-HHMMSS-<4 hex>` (UTC). Codex's working directory is the run folder, and its output lands there. Bookkeeping lives in `<run>/.ask-codex/`:

- The `.ask-codex/` folder itself marks the run folder as created by ask-codex. Anything under `~/.shwow-kit/codex/` without it was not.
- `session-id`: the Codex session (thread) id, one line.
- `last-used`: the UTC time the run was last used, one ISO 8601 line. Rewritten at the start and end of every run.
- `last-message.txt`: Codex's last message.
- `events.jsonl`, `stderr.txt`: Codex's raw output, for diagnosing a failed run.
