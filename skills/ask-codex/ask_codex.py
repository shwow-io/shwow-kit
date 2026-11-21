"""Run a task in Codex inside its own run folder and print the result.

Usage: python ask_codex.py [-m MODEL] [--follow-up RUN] "<prompt>"    (or pipe the prompt on stdin)

Each run gets a new folder under ~/.shwow-kit/codex/<run>/, which is Codex's working
directory. Bookkeeping lives in <run>/.ask-codex/ (see SKILL.md for the layout).
--follow-up resumes an earlier run's Codex session in that run's folder instead.
Before running, deletes ask-codex run folders last used more than 30 days ago.
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
SUFFIX = "\n\nSave the files you produce in the current directory."
TAIL = 10
MAX_IDLE = datetime.timedelta(days=30)


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def preflight():
    """Return the codex executable, or exit with one line saying what's wrong."""
    codex = shutil.which("codex")
    if not codex:
        sys.exit("Codex isn't installed: `codex` is not on PATH.")
    try:
        status = subprocess.run([codex, "login", "status"], capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        sys.exit(f"Couldn't check the Codex login: `codex login status` failed ({e.__class__.__name__}).")
    if status.returncode:
        sys.exit("Codex isn't logged in: run `codex login`.")
    return codex


def last_used(run):
    try:
        used = datetime.datetime.fromisoformat((run / META / "last-used").read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    return used if used.tzinfo else used.replace(tzinfo=datetime.timezone.utc)


def sweep(keep=None):
    """Delete ask-codex run folders last used more than MAX_IDLE ago. Anything without the marker is left alone."""
    if not ROOT.is_dir():
        return
    cutoff = now() - MAX_IDLE
    for run in ROOT.iterdir():
        if run == keep or not (run / META).is_dir():
            continue
        used = last_used(run)
        if used is not None and used < cutoff:
            try:
                shutil.rmtree(run)
            except OSError as e:
                print(f"Couldn't delete idle run folder {run}: {e}", file=sys.stderr)


def follow_up_folder(name):
    """Return the run folder and session id to resume, or exit with one line saying what's wrong."""
    if not name.strip():
        sys.exit("--follow-up needs a run folder name or path.")
    run = (ROOT / name).resolve()
    if run.parent != ROOT.resolve():
        sys.exit(f"Not an ask-codex run folder: {name} is not directly under {ROOT}.")
    run = ROOT / run.name
    try:
        session = (run / META / "session-id").read_text(encoding="utf-8").strip()
    except OSError:
        session = ""
    if not session:
        sys.exit(f"No ask-codex run with a session id at {run}.")
    return run, session


def new_run_folder():
    name = now().strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)
    run = ROOT / name
    (run / META).mkdir(parents=True)
    return run


def touch_last_used(meta):
    (meta / "last-used").write_text(now().isoformat(timespec="seconds") + "\n", encoding="utf-8")


def snapshot(run):
    return {p: p.stat().st_mtime_ns for p in run.rglob("*") if p.is_file() and META not in p.relative_to(run).parts}


def tail(path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-TAIL:]


def main():
    ap = argparse.ArgumentParser(description="Run a task in Codex in a fresh folder under ~/.shwow-kit/codex/.")
    ap.add_argument("prompt", nargs="?", help="the task for Codex; read from stdin if omitted")
    ap.add_argument("-m", "--model", help="Codex model to use instead of its default")
    ap.add_argument("--follow-up", metavar="RUN", help="resume the Codex session of this earlier run (folder name or path)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stdin.reconfigure(encoding="utf-8")

    prompt = args.prompt if args.prompt is not None else sys.stdin.read()
    if not prompt.strip():
        ap.error("no prompt given")

    codex = preflight()
    run, resumed = follow_up_folder(args.follow_up) if args.follow_up is not None else (None, None)
    sweep(keep=run)
    if run is None:
        run = new_run_folder()
    meta = run / META
    touch_last_used(meta)
    last_file = meta / "last-message.txt"
    last_file.unlink(missing_ok=True)
    before = snapshot(run)

    # The workspace-write sandbox blocks writes outside the run folder; exec never prompts for approval.
    # `resume` rejects -s, so it goes before the subcommand.
    cmd = [codex, "exec", "-s", "workspace-write"]
    if resumed:
        cmd.append("resume")
    cmd += ["--skip-git-repo-check", "--json", "-o", str(last_file)]
    if args.model:
        cmd += ["-m", args.model]
    if resumed:
        cmd.append(resumed)
    cmd.append("-")
    with open(meta / "events.jsonl", "a", encoding="utf-8") as events, \
         open(meta / "stderr.txt", "a", encoding="utf-8") as err:
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
                    if session != resumed:
                        (meta / "session-id").write_text(session + "\n", encoding="utf-8")
        code = proc.wait()

    touch_last_used(meta)
    after = snapshot(run)
    written = sorted(p for p, m in after.items() if before.get(p) != m)
    last = last_file.read_text(encoding="utf-8").strip() if last_file.exists() else ""

    print(f"Run folder: {run}")
    print(f"Session id: {session or '(none)'}")
    print("Files written:" + ("" if written else " none"))
    for p in written:
        print(f"  {p}")
    print("Last message:")
    print(last or "(none)")
    if code:
        print(f"Codex failed with exit code {code}. Run folder kept. Last output:")
        for name in ("events.jsonl", "stderr.txt"):
            lines = tail(meta / name)
            if lines:
                print(f"  {name}:")
                for line in lines:
                    print(f"    {line}")
    return code


if __name__ == "__main__":
    sys.exit(main())
