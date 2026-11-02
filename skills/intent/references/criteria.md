# When a criterion can be checked

A criterion is accepted only when something other than a human's opinion can decide it. Two kinds of check count:

- **A command** (`- Sprawdzenie: polecenie `<command>``): its exit code decides. Prefer the project's verify command from `CLAUDE.md` or `AGENTS.md`, a test file, or a script that already exists. A command that does not exist yet is fine when the change itself adds it (a new test), as long as the criterion names what it proves. A command that creates a temporary directory in the shell uses `mktemp -d "${TMPDIR:-/tmp}/<name>.XXXXXX"`: a bare `mktemp -d` fails in the Claude Code sandbox on macOS, and the verifier then answers NOT MET for a reason unrelated to the criterion. A command that measures a file's difference against the main branch uses `git diff --numstat "$(git merge-base master HEAD)" -- <file>`, not `master...HEAD`: the phase gate runs it before the commit, and `master...HEAD` then compares only committed work, so the criterion passes without measuring the current phase.
- **The verifier agent** (`- Sprawdzenie: weryfikator — <what it checks>`): `.claude/agents/verifier.md` reads the code, runs read-only commands and the verify command, and answers MET or NOT MET with evidence. It cannot ask a person, judge taste or watch a user. Describe what it looks at: a file and the behaviour in it, the output of a command, a section of a document.

A criterion whose check leaves the laboratory repository (another repository, the network, `gh`, the home directory) says in `Sprawdzenie` who runs it and where the result is written: the main session in its run report, or the human in a terminal. That is a run outside the verifier's sandbox, not a manual test. When `Sprawdzenie` only reads a file outside the laboratory repository (e.g. a note in the home directory), the intent copies that file into the change folder as an input and points the check at the copy, so the verifier can read it.

## Not accepted as written

Propose a rewording for each of these; `references/examples.md` shows typical ones.

1. **A human's judgement or impression.** Words such as "intuicyjny", "czytelny", "ładny", "wygodny", "przyjazny", "szybki" without a number. Nobody but a person can decide them, and the factory does not ask a person to test by hand.
2. **A mechanism the problem does not need.** The criterion prescribes how instead of what: it names a new channel of evidence, a new mode, a new file format or a new command, while the problem would be solved by an observable effect that existing parts can deliver. Ask: if the effect happened by a simpler route, would the criterion fail? If yes, it prescribes a mechanism.
3. **Several results in one criterion that could pass and fail separately.** Split it, so a NOT MET points at one thing.
4. **A result that depends on the future or on production data** ("users will adopt it", "fewer support tickets"). Reword to what the change itself makes true and checkable now. The same holds for a measurement result or a human decision that will be made during the change: the criterion does not presume it. Do not write "a new value" when the measurement may give the same one, and do not close the list of outcomes when `docs/spec.md` knows another (e.g. adoption on trial). The criterion says the result is recorded and the rest of the repository agrees with it.

## A good rewording

- Names an observable effect: a step count, a number, a value returned, a line printed, an exit code, a file that exists with given content.
- Keeps the intent of the original. If the original cannot be reworded without changing what the human wanted, do not invent a replacement: ask (interactive) or escalate with your best proposal (unattended).
- Adds no mechanism the original did not ask for.

## The closing criterion

A final umbrella criterion ("the checks pass and only the files needed for C1–C5 are changed") is accepted when each part has a command: the verify command, the repository checks, a scope check. Write the commands in its `- Sprawdzenie:` line.

## In the block

The block holds only accepted wordings. Interactive: show the original, the proposed rewording and why, and let the human pick (your rewording as the first option). Unattended: put the rewording into the block and record the original in an escalation entry (`references/unattended.md`). The original wording never stays in the criteria block, not even in parentheses.
