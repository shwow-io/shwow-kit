# shwow-kit

A process and a Claude Code plugin for building software with coding agents. The process is in [docs/PROCESS.md](docs/PROCESS.md); the skills and agents implement its steps.

## Install

```sh
claude plugin marketplace add <path-or-github-repo>
claude plugin install shwow-kit@shwow-kit
```

## Layout

- `skills/`: one folder per process step (`SKILL.md` plus references and scripts)
- `agents/`: subagent definitions (worker, reviewer, scout)
- `docs/`: the process and design notes
