"""Run a task in Codex inside its own run folder and print the result.

Usage: python ask_codex.py "<prompt>"    (or pipe the prompt on stdin)

Each run gets a new folder under ~/.shwow-kit/codex/<run>/, which is Codex's working
directory. Bookkeeping lives in <run>/.ask-codex/ (see SKILL.md for the layout).
Prints the run folder, the Codex session id, Codex's last message and the files it wrote.
"""

import argparse
import datetime
import json
import pathlib
import secrets
import shutil
import subprocess
import sys

ROOT = pathlib.Path.home() / ".shwow-kit" / "codex"
META = ".ask-codex"
SUFFIX = "\n\nWork only in the current directory and save any files you create there."


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def new_run_folder():
    name = now().strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)
    run = ROOT / name
    (run / META).mkdir(parents=True)
    return run


def touch_last_used(meta):
    (meta / "last-used").write_text(now().isoformat(timespec="seconds") + "\n", encoding="utf-8")


def snapshot(run):
    return {p: p.stat().st_mtime_ns for p in run.rglob("*") if p.is_file() and META not in p.relative_to(run).parts}


def main():
    ap = argparse.ArgumentParser(description="Run a task in Codex in a fresh folder under ~/.shwow-kit/codex/.")
    ap.add_argument("prompt", nargs="?", help="the task for Codex; read from stdin if omitted")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    prompt = args.prompt if args.prompt is not None else sys.stdin.read()
    if not prompt.strip():
        ap.error("no prompt given")

    codex = shutil.which("codex")
    run = new_run_folder()
    meta = run / META
    touch_last_used(meta)
    before = snapshot(run)

    # --approve-for-me runs commands in the workspace-write sandbox, so writes stay in cwd.
    cmd = [codex, "exec", "--skip-git-repo-check", "--approve-for-me", "--json",
           "-o", str(meta / "last-message.txt"), "-"]
    with open(meta / "events.jsonl", "w", encoding="utf-8") as events, \
         open(meta / "stderr.txt", "w", encoding="utf-8") as err:
        proc = subprocess.Popen(cmd, cwd=run, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err,
                                text=True, encoding="utf-8", errors="replace")
        proc.stdin.write(prompt + SUFFIX)
        proc.stdin.close()
        session = None
        for line in proc.stdout:
            events.write(line)
            if session is None:
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("type") == "thread.started":
                    session = e.get("thread_id")
                    (meta / "session-id").write_text(session + "\n", encoding="utf-8")
        code = proc.wait()

    touch_last_used(meta)
    after = snapshot(run)
    written = sorted(p for p, m in after.items() if before.get(p) != m)
    last_file = meta / "last-message.txt"
    last = last_file.read_text(encoding="utf-8").strip() if last_file.exists() else ""

    print(f"Run folder: {run}")
    print(f"Session id: {session or '(none)'}")
    print("Files written:" + ("" if written else " none"))
    for p in written:
        print(f"  {p}")
    print("Last message:")
    print(last or "(none)")
    if code:
        print(f"Codex exited with code {code}.")
    return code


if __name__ == "__main__":
    sys.exit(main())
