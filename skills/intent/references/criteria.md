# When a criterion can be checked

A criterion is accepted only when something other than a human's opinion can decide it. Two kinds of check count:

- **A command** (`- Sprawdzenie: polecenie `<command>``): its exit code decides. Prefer the project's verify command from `CLAUDE.md` or `AGENTS.md`, a test file, or a script that already exists. A command that does not exist yet is fine when the change itself adds it (a new test), as long as the criterion names what it proves.
- **The code review** (`- Sprawdzenie: weryfikator — <what it checks>`): the full review of `/10x-impl-review` (Step 3) and its closure check read the code, run read-only commands and the verify command, and judge the criterion `spełnione` or `niespełnione` with evidence; an unmet criterion is a finding of the review. It cannot ask a person, judge taste or watch a user. Describe what it looks at: a file and the behaviour in it, the output of a command, a section of a document.

A criterion is checked by a command. Use the review's judgment only when no command can decide it, and say in one sentence why in its `Sprawdzenie` line.

A command that the sandbox of a `claude -p` step cannot run (e.g. `claude …`, which fails there with `operation not permitted`) needs a route the review can take inside that sandbox. The main session runs the command and writes a run report in `runs/` with its result and the commit it ran on; the criterion is checked by that report and by an empty `git diff <commit> HEAD -- <files the result depends on>`. Write both in its `Sprawdzenie` line. Without that route the review judges it `niespełnione` and its finding waits for a human.

## Not accepted as written

Propose a rewording for each of these; `references/examples.md` shows typical ones.

1. **A human's judgement or impression.** Words such as "intuicyjny", "czytelny", "ładny", "wygodny", "przyjazny", "szybki" without a number. Nobody but a person can decide them, and the factory does not ask a person to test by hand.
2. **A mechanism the problem does not need.** The criterion prescribes how instead of what: it names a new channel of evidence, a new mode, a new file format or a new command, while the problem would be solved by an observable effect that existing parts can deliver. Ask: if the effect happened by a simpler route, would the criterion fail? If yes, it prescribes a mechanism.
3. **Several results in one criterion that could pass and fail separately.** Split it, so a `niespełnione` points at one thing.
4. **A result that depends on the future or on production data** ("users will adopt it", "fewer support tickets"). Reword to what the change itself makes true and checkable now.

## A good rewording

- Names an observable effect: a step count, a number, a value returned, a line printed, an exit code, a file that exists with given content.
- Keeps the intent of the original. If the original cannot be reworded without changing what the human wanted, do not invent a replacement: ask (interactive) or escalate with your best proposal (unattended).
- Adds no mechanism the original did not ask for.

## The closing criterion

A final umbrella criterion ("the checks pass and only the files needed for C1–C5 are changed") is accepted when each part has a command: the verify command, the repository checks, a scope check. Write the commands in its `- Sprawdzenie:` line.

The scope check is rule 6 of `validate_change.py` of `/10x-impl-review`: every file outside `context/` changed by the change's commits is in the plan. Write it as `python3 skills/10x-impl-review/scripts/validate_change.py <change-id> --rules 6`, outside the factory repo with `~/.claude/skills/10x-impl-review/scripts/validate_change.py`. Never write a list of allowed files instead (`git diff --name-only … | grep -vE …`): the factory's own steps write files under `context/` (the decision log, the run file, reports), so such a list fails on a file the change never meant to touch, and each change has to extend it.

## In the block

The block holds only accepted wordings. Interactive: show the original, the proposed rewording and why, and let the human pick (your rewording as the first option). Unattended: put the rewording into the block and record the original in an escalation entry (`references/unattended.md`). The original wording never stays in the criteria block, not even in parentheses.
