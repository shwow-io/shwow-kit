# shwow-kit

A process and a Claude Code plugin for building software with coding agents: size the work, frame it, pin down what "done" means, slice it, build the slices in parallel, verify every change, and ship it in reviewable landings. The process is in [docs/PROCESS.md](docs/PROCESS.md); the skills and agents implement its steps.

## Install

```sh
claude plugin marketplace add shwow-io/shwow-kit
claude plugin install shwow-kit@shwow-io
```

Then ask for a change as you normally would; `triage` starts the process. `/shwow-kit:status` shows what's in flight.

## Layout

- `skills/`: one folder per process step (`SKILL.md` plus templates and references)
- `agents/`: subagents (worker, reviewer, scout, researcher)
- `scripts/cost.py`: token use and estimated cost per work item, from Claude Code transcripts
- `docs/`: the process and the work-item format

## Contributing

This is a personal toolkit, published to read and reuse. Issues and pull requests aren't accepted.

## Licence

MIT, see [LICENSE](LICENSE).
