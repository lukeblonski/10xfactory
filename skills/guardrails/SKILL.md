---
name: guardrails
description: >
  Install hard guardrails into a project: the Claude Code sandbox for every shell command
  (protected paths, a locked test, allowed domains), hooks that block edits to protected files,
  writing secrets and editing a locked test, a post-edit fast check, one `verify` command
  (lint + typecheck + tests + secret scan), and a read-only verifier agent. Trigger phrases: "install guardrails",
  "add hooks", "protect .env", "set up verify", "zabezpieczenia", "dodaj hooki".
  Use AFTER /10x-bootstrapper or /10x-health-check, BEFORE /10x-agents-md.
argument-hint: "[project-path]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
---

# 10x Guardrails — sandbox, hooks, one verify command, a verifier agent

Questions to the user are not a safety mechanism. This skill installs checks the agent cannot skip:

- **The Claude Code sandbox** (`sandbox` in `.claude/settings.json`) is the hard boundary for shell commands. The operating system enforces it on every command Claude runs and on the processes it starts, whatever the command looks like:
  - `enabled: true`, `allowUnsandboxedCommands: false` (no command runs outside it) and `failIfUnavailable: true` (Claude Code refuses to start rather than run commands unsandboxed);
  - `filesystem.denyWrite` holds the `"protected"` patterns of `.claude/guardrails.json` and the guardrails' own files; Claude Code also protects its settings, `.claude/hooks` and `.claude/agents` on its own;
  - a locked test is added to `sandbox.filesystem.denyWrite` in `.claude/settings.local.json` while it is locked (the `lock_tests.py` hook keeps that list in sync with `.claude/locked-tests` and records the entries it added in `.claude/locked-tests.sandbox`, so it removes only those and never an entry someone else wrote; the installer adds both files to the git exclude file);
  - `network.allowedDomains` comes from `"allowed_domains"` (default: the npm registry and GitHub) and `filesystem.allowWrite` from `"allow_write"` (e.g. `~/.npm` for the npm cache), so ordinary work such as `npm install` runs without prompts.
- **Hooks** (an extra layer: they also cover Claude's file tools, which the sandbox does not, and stop a shell command before it runs, with a message that names the rule, only for a locked test and for a secret) (Claude Code `PreToolUse`/`PostToolUse`, copied into `.claude/hooks/guardrails/` and registered in `.claude/settings.json`):
  - `protect_paths.py` covers the file tools (a shell command that writes to a protected path is stopped by `sandbox.filesystem.denyWrite`, not by this hook) and blocks writes to the paths in `"protected"` of `.claude/guardrails.json` (default `.env`, `.env.*`, `**/secrets/**`, `.github/workflows/**`) and, always, to the guardrails' own files (`.claude/guardrails.json`, `.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks/guardrails/**`, `.claude/agents/verifier.md`) and to the user's `~/.claude/settings.json` and `~/.claude/settings.local.json` (where `disableAllHooks` would switch every hook off); a `"protected"` entry that uses a wildcard and has no `/` (such as `.env.*`) leaves out a file whose name ends in `.example` (`.env.example` holds sample values, not secrets) when the wildcard hits only that file name, while a hit on a folder, an entry with `/`, an entry without a wildcard, an entry that itself contains `example` (such as `*.example`) and the guardrails' own files still guard such a file;
  - `block_secrets.py` blocks content with a private key, an AWS access key, an `sk-` token or a `ghp_` token, except files matching `"secret_allow"`;
  - `lock_tests.py` blocks edits to the tests listed in `.claude/locked-tests` (used by the bug-fix mode of `/10x-tdd`);
  - `post_edit_check.py` runs `"fast_check"` (e.g. the linter) on each edited file, 30 s limit, and shows the agent the tail of a failure.

  `lock_tests.py` and `block_secrets.py` cover the file tools and Bash, `protect_paths.py` the file tools. The three protective hooks fail closed: unreadable input, a missing or broken `.claude/guardrails.json`, a crash or a timeout blocks the action (`"onFailure": "block"`). The Bash parsing of `lock_tests.py` is a heuristic; the sandbox is what holds when it misses a form.
- **One `verify` command** that runs lint, typecheck, tests and a rule-based secret scan of the git history and exits non-zero when anything fails, documented in `AGENTS.md` or `CLAUDE.md` with real output. The scan, not a model's judgement or a hand-written `grep`, answers "no secret value in the history".
- **The `verifier` agent** (`.claude/agents/verifier.md`): read-only tools, runs `verify`, judges each acceptance criterion of a change as MET or NOT MET with evidence, never edits.

## Steps

1. **Resolve the project root**: the argument if given, else `git rev-parse --show-toplevel`, else the current directory. If the root contains `skills/guardrails/SKILL.md`, it is the skills repository itself: STOP, guardrails are not installed there.

2. **Pick the fast check** from what the project already uses (read `package.json`, `pyproject.toml`, config files; do not install anything):

   | Found | `--fast-check` | `--fast-check-include` (one quoted pattern per argument) |
   | --- | --- | --- |
   | ESLint (`eslint` in devDependencies or an `eslint.config.*`) | `"npx eslint {file}"` | `'*.ts' '*.tsx' '*.js' '*.jsx' '*.mjs' '*.cjs'` |
   | Ruff (`ruff` in dependencies or `[tool.ruff]`) | `"ruff check {file}"` | `'*.py'` |
   | none | (omit both flags) | |

   Example: `--fast-check "npx eslint {file}" --fast-check-include '*.ts' '*.tsx'`. Quote each pattern so the shell does not expand it.

   Then pick what the project's own tools need inside the sandbox (the defaults already allow `registry.npmjs.org`, `github.com`, `*.github.com`, `*.githubusercontent.com`):

   | Found | `--allow-write` | `--allow-domain` |
   | --- | --- | --- |
   | npm (`package-lock.json` or no other lock file) | `'~/.npm'` (the npm cache; confirm with `npm config get cache`) | (default) |
   | another package manager (pnpm, yarn, pip, uv, …) | the directory its own command reports (`pnpm store path`, `yarn cache dir`, `pip cache dir`, `uv cache dir`), written with `~/` | its registry hosts, e.g. `pypi.org files.pythonhosted.org` |
   | hosts the project's scripts or docs name (a private registry, an API used by tests) | | that host |

   Add only what the project uses; each entry widens the sandbox. Quote `~` paths so the shell does not expand them.

3. **Install**: run `python3 ${CLAUDE_SKILL_DIR}/scripts/install.py <project-root> [--fast-check "<cmd>" --fast-check-include <globs>] [--allow-write <paths>] [--allow-domain <hosts>]` and show its output. Exit code 1 means `.claude/settings.json` or `.claude/guardrails.json` is unreadable: STOP and report it (nothing was written). Exit code 2: STOP and report the message. Exit code 3: a write failed part way; `.claude/settings.json` was not touched. When the error is `Operation not permitted`, the sandbox is already on and protects these files: STOP and give the user the exact command to run themselves (`! python3 …`). The installer never overwrites an existing `.claude/guardrails.json` or a changed `.claude/agents/verifier.md`, and never changes a `sandbox` switch the project already set; pass its `kept` notes and `WARN` lines on to the user. A second run prints `Nothing changed.` On Linux and WSL2 the sandbox needs `bubblewrap` and `socat`; tell the user to install them, because with `failIfUnavailable` Claude Code will not start without them.

4. **Make sure there is one `verify` command.**
   - npm project: run `python3 ${CLAUDE_SKILL_DIR}/scripts/setup_verify.py <project-root>`. Exit 0: it printed the command (created or already present) and `WARN missing:` lines for absent parts; report those to the user, do not invent scripts. Exit 1: there is no lint, typecheck or test script; STOP and report that a `verify` command cannot be built from nothing. Exit 2: `package.json` is broken; STOP.
   - Other projects (exit 3): build the equivalent from the tools the project already has, e.g. a `verify` target in the `Makefile` that runs lint, typecheck and tests in sequence and fails on the first failure. Do not add tools the project does not have.
   - Add the secret scan as the last part of `verify`, unless it is already there: the scanner the project already uses, else `gitleaks git --redact --no-banner .` (it checks every commit by its rules, prints no secret value and exits non-zero on a find). When the project writes logs inside its own tree, add `gitleaks dir --redact --no-banner <log-dir>` for each such folder. If `gitleaks version` fails, STOP and give the user the install command for their system (e.g. `brew install gitleaks`); do not leave the scan out and do not replace it with `grep`.
   - `references/required-programs.json` is the one list of programs these steps run that a project does not ship itself; a new program called here goes onto that list. Every program of that list is also installed or checked in `templates/ci.yml`, the CI template of a new project, which fetches the full history for the scan of every commit.
   - Run the command (e.g. `npm run verify`). If it fails, STOP: report the failing output and do not write any "passing run" text.

5. **Document it** in `AGENTS.md` if that file exists, else in `CLAUDE.md` if that exists, else create `AGENTS.md`. Add (or, on a re-run, replace) one section:

   ````markdown
   ## Verify

   Run `<command>` before every commit. It runs lint, typecheck, tests and a secret scan of the git history and exits non-zero if anything fails.

   Last passing run (<YYYY-MM-DD>):

   ```
   <2–3 lines copied verbatim from the output of the run in step 4>
   ```
   ````

   Copy the lines; never paraphrase or invent output. Pick lines that show the result and stay true when tests are added: e.g. `ℹ fail 0` rather than `ℹ tests 4`. Lines with counts of passing tests go stale with the next test.

6. **Tell the user** what is now enforced and how to work with it:
   - Only a human grants an exception: they edit `.claude/guardrails.json` themselves, outside Claude (`"protected"`, `"secret_allow"`, `"fast_check"`, `"allowed_domains"`, `"allow_write"`), then re-run the installer outside Claude so the sandbox lists in `.claude/settings.json` pick it up (the installer adds entries; it never removes one). The agent cannot edit either file.
   - Shell commands run in the sandbox without prompts. A host outside `allowed_domains` prompts in default mode; under `--permission-mode bypassPermissions` it is allowed, unless the user sets `sandbox.network.strictAllowlist: true` in their own `~/.claude/settings.json` (a project cannot set it).
   - A secret scan that stops `verify` on something that is not a secret is a human's exception too: they add the fingerprint the scanner printed to `.gitleaksignore` (and may list that file in `"protected"`); the agent reports the find and does not silence it.
   - `.claude/locked-tests` (one path per line) locks tests; `/10x-tdd <change-id> bug` manages it.
   - Ask for the verifier with "use the verifier agent to verify change `<change-id>`".
   - Known limits:
     - The Bash checks of `lock_tests.py` are a heuristic layer on top of the sandbox. They catch redirects, `tee`, `sed -i`/`perl -i`/`ruby -i`/`awk -i inplace`, `rm`, `mv`, `cp`, `rsync`, `curl -o`, `wget -O`, `patch FILE`, `dd of=`, `git checkout/restore/rm/mv`, `bash -c`/`-lc`, `eval`, wrappers such as `sudo`, `env`, `timeout`, `nice`, `$(...)`, paths with `$CLAUDE_PROJECT_DIR`/`$PWD`/`$HOME`/`$(pwd)`, other variables (checked by the path after them), any letter case, and inline interpreter code that names a locked test.
     - Forms `lock_tests.py` misses and the sandbox stops: globs and brace expansion (`rm src/*.test.ts`, `tee {src/a.test.ts,x}`), a variable inside or at the end of a path (`src/$NAME`), ANSI-C quoting (`$'src/a.test.ts'`), here-strings and a quoted `<<EOF` before the write, code fed to a shell on stdin (`bash <<EOF`, `echo … | bash`, `bash <<<'…'`), formatters on one file (`prettier --write <file>`, `eslint --fix <file>`), `tar -C`, `unzip -d`, `vim`/`ex`, `env -C`, `busybox`, whole-tree tools (`find -delete`, `xargs`, `git clean -x`), commands that take paths from a diff or another revision (`git apply`, `git reset --hard <rev>`, `git switch`), a target that is only a variable (`> "$OUT"`), and paths built at runtime inside programs. These are blocked only while the sandbox runs: under `failIfUnavailable` Claude Code does not start without it.
     - The sandbox covers shell commands only. Claude's file tools (Write, Edit) rely on the hooks; hooks, MCP servers and commands the user types at `!` run outside the sandbox.
     - A broad wildcard entry that does not contain `example` (such as `*`, `config.*` or `*secret*`) no longer guards a file ending in `.example` for Edit and Write; to guard such a file, list it by its exact name, with a `/` pattern, or with a pattern that contains `example`.
     - The `.example` exception lives only in the hook: the sandbox entry `./.env.*` in `denyWrite` still stops a shell command from writing `.env.example` (the agent edits that file with Edit or Write), and re-running the installer does not drop the entry, because it only adds entries and never removes them.
     - On Linux and WSL2 the sandbox skips `denyWrite` entries with `*`, `?` or `[` (e.g. `./**/.env`, `./.env.*`, `./**/secrets`), so only the literal entries (`./.env`, `./.github/workflows`, a locked test) hold there for shell commands; on macOS all of them hold. A path protected only by such an entry (e.g. `sub/.env`, `.env.local`, `x/secrets/`) has nothing there that stops a shell write, because `protect_paths.py` does not check Bash.
     - A lock reaches `.claude/settings.local.json` when the hook runs after the tool call that wrote `.claude/locked-tests` (a lock written outside Claude: at the next tool call), and Claude Code applies that file to the sandbox on its own schedule. So for 5 seconds after a lock change the hook refuses every shell command with `lock-pending`, except the probe `touch -c <locked test>` (it changes no content), which fails with "Operation not permitted" once the sandbox has the lock. The 5 seconds are a measured margin, not a guarantee from Claude Code; `/10x-tdd` bug-fix mode runs the probe before it continues.
     - A `sandbox` switch the project already set (e.g. `"enabled": false`) is kept, with a `WARN`; with `"enabled": false` nothing stops a shell write to a protected path, because `protect_paths.py` does not check Bash, and the same holds for a command that runs outside the sandbox through `"allowUnsandboxedCommands": true` set earlier by the project or through `sandbox.excludedCommands` in the project's or the user's settings; a user's own `~/.claude/settings.json` may also weaken the sandbox, which a project cannot prevent.
     - Hooks do not run under `claude --bare`.
     - A personal skill in `~/.claude/skills` with the same name overrides the project's.

7. **Next step**: `/10x-agents-md` to write or refresh `AGENTS.md`, which picks up the `verify` command.

## What this skill does NOT do

- It does not commit; the user (or the calling workflow) commits the new files.
- It does not change CI, managed settings, or an existing `.claude/guardrails.json`.
- It does not install linters, type checkers or test runners.
- It does not install itself into the skills repository.
