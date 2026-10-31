# 10xfactory

Automation for the 10xDevs 3.0 workflow in Claude Code. You describe what you want, approve the important decisions, and the factory runs the rest of the 10x workflow on its own: from an empty folder to a planned, reviewed, tested and merged application.

> **You need your own copy of the original 10xDevs 3.0 skills.** This package does not contain the course skills. The installer changes the copy you already have.

## What it adds to the plain 10x skills

With the plain 10x skills you run each step yourself (`/10x-plan`, `/10x-implement`, `/10x-impl-review` …). 10xfactory runs them for you:

- **Autopilot.** One command takes a change through the whole chain, each step in a fresh Claude Code process: intent → research (when needed) → plan → plan review → implementation → code review → archive → merge and push. It stops only where a human decision is required.
- **Project start from an empty folder.** A shaping conversation with you (`/10x-shape`), then PRD, tech stack, infrastructure, your one-time acceptance, project skeleton with CI, guardrails, roadmap, test plan and a private GitHub repo, without further questions.
- **Roadmap slices.** Each roadmap item is built as a separate change through the full chain.
- **Deployment as a roadmap item.** Deploys through GitHub Actions; secrets go from local files to GitHub secrets without passing through the chat.
- **The `intent` skill.** Every change starts with a contract: problem, expected effect, your scenario step by step, numbered acceptance criteria that a command or a verifier agent can check, and a risk level.
- **Situational steps, like in 10x.** Low-risk changes skip research. When your request looks like "X is broken, do Y", the session first runs `/10x-frame` with you. Plan review and code review always run.
- **Review triage.** Review findings are fixed, deferred to a limitations register, or escalated to you by written rules, with a limit on review rounds.
- **Guardrails.** Hooks that block writes to protected files, secrets in code and edits to locked tests, plus sandbox defaults for the agent.
- **Human gates.** Paid runs, sending data to outside services, publishing, changes to protected files and irreversible operations always wait for you.


## Requirements

- **Original 10xDevs 3.0 skills** in the `skills/` folder of your Claude Code configuration (`~/.claude/skills`, or `$CLAUDE_CONFIG_DIR/skills` if you set that variable). Only this edition is supported. If any file the package changes differs from the original, the installer lists the files and changes nothing.
- Claude Code 2.1.295 or newer.
- Python 3 and git.
- macOS. Other systems are untested.

## Installation

Clone the repository into a folder whose path has no spaces or special characters, then run these three commands in that folder:

```
python3 scripts/instaluj.py
```
Preview. Shows your Claude Code version, the check of your course files, the files it would write and the two entries it would add to `settings.json` (session-start hook and a sandbox exception for the autopilot). Writes nothing.

```
python3 scripts/instaluj.py --zapisz
```
Install. Makes a backup first (`<config>/fabryka-kopie/<date-time>/`) and prints its path, then writes the skills and the two settings entries. Running it again adds nothing twice.

```
python3 scripts/instaluj.py --sprawdz
```
Check. Compares every installed file with the package and lists any difference.

If your course skills are in another folder, add `--kurs <folder>` to the first two commands.

Do not also install the package as a Claude Code plugin: the session-start hook would run twice.

To undo the installation, copy the files from the backup folder back into your configuration folder and delete the files listed in `nowe-pliki.txt` there.

## Getting started

Open Claude Code in an empty folder and describe the application you want to build. The session asks once whether to build it with the factory or as plain Claude Code. Choose the factory and follow the shaping conversation; after you accept the PRD, tech stack and infrastructure, the factory builds the project and the roadmap.

For later work in that project, write (in Polish) „zrób zmianę: <what you want>” for a single change or „zrób kolejny kawałek” for the next roadmap slice. You can also type `/fabryka` in an empty folder to start a project directly.

## Known limitations

- **The factory speaks Polish.** Its instructions, questions and reports are in Polish.
- **Deployment from the package is untested.** It was tested only in the lab.
- **Setting up outside services is manual.** Before a slice that needs accounts or keys (for example a database, hosting or an AI API), you create the accounts and save the keys yourself, following the session's instructions. Version 1.1 will guide you step by step and do everything except creating accounts.
- **Tests that need local containers run in your terminal.** The agent works in a sandbox without access to Docker, so you run one command for tests that need a local database, and you check each slice in the browser.
- **The project start may ask you to install `gitleaks`**, and the first CI run may need a one-time fix of the CI file that the session gives you.
- **Claude Code may ask to read files outside the project** (the package folder). Allow it once ("Yes, but ask again next time"), not for every folder.
- **Agent steps cannot read skill files in your configuration folder**, so reviews run without some reference files.
- **Only 10xDevs 3.0 skills are supported.**

## Changelog

### 1.0.0 — 2026-10-31
First public release: autopilot for changes, project start from an empty folder, roadmap slices, deployment as a roadmap item, the `intent` skill, shorter path with situational research and frame, review triage, guardrails and the installer with backup and check.

## What's inside

- `scripts/instaluj.py` — installer (preview, `--zapisz`, `--sprawdz`).
- `.claude-plugin/plugin.json` — Claude Code plugin manifest; the installer does not use it.
- `zmiany-10x.json` — recipe the installer uses to apply the factory's changes to your 10x skills. It does not contain the course text.
- `scripts/` — autopilot, session-start hook and helper scripts.
- `skills/` — the `intent`, `guardrails` and `fabryka` skills and files the factory adds to 10x skills.
- `docs/` — instructions for the session, project start, build rules, human gates, and descriptions of the changes to 10x skills.
- `CLAUDE.md` — the factory's rules; the session reads them from the package folder.
- `VERSION` — package version.

## License

MIT, see `LICENSE`.
