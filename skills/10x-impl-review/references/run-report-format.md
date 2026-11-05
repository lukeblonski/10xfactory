# Run Report Reference

A run report is the file a run of an implementation skill leaves behind: which commands it actually ran, with what result, on which version of the code. Run reports live in `context/changes/<change-id>/runs/`. `validate_change.py` (owned by `/10x-impl-review`) reads them for rule 2. `## Progress` in `plan.md` stays the single source of execution state; reports hold evidence, never state.

## Run report

- **Path**: `context/changes/<change-id>/runs/<YYYY-MM-DD>-<HHMMSS>-<skill>.md`, e.g. `runs/2026-10-20-142501-10x-goal-implement.md`. One file per run (one session of the skill). The file of an interrupted run stays; a resumed run starts a new file.
- **Writers**: only `/10x-implement`, `/10x-goal-implement`, `/10x-tdd` and `/10x-e2e` (not in standalone mode, which has no change folder), and the main session of the laboratory (`docs/sesja-glowna.md`), which writes `runs/<YYYY-MM-DD>-<HHMMSS>-sesja-glowna.md` for the `#### Manual` rows a human confirmed in conversation.
- **Header**:

  ```markdown
  # Run report: <change-id>

  - **Skill**: /10x-goal-implement
  - **Model**: claude-opus-5-5
  - **Started**: 2026-10-20T14:25:01+02:00
  - **Start commit**: 9e4b91f
  ```

- **Model**: the exact model ID of the session, as the system prompt states it (e.g. `claude-opus-5-5`), never an alias such as `opus`: an alias points to a different model as Claude Code versions change. `validate_change.py` does not read the header, so older reports without `Model` stay valid.
- **Sections**: exactly `## Observed`, `## Reported` and `## Skipped`, in this order. An empty section holds the line `None.`
- **Entry**: a heading `### O<n>`, `### R<n>` or `### S<n>` (numbered per section from 1), then one line per field: `- **<Name>**: <value>`.

### Observed

Commands the skill ran itself, or checks a human confirmed.

| Field      | Value                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------------------- |
| `Step`     | the Progress row `N.M` the command proves, or `—` for a command outside any row                          |
| `Criteria` | the numbers from the `**Criteria**:` line of the phase the step belongs to, or `—` without a step        |
| `Command`  | the command in backticks; for a human's check `manual: <what was checked>`                               |
| `Exit`     | the exit code as a number; for a human's check `0` means confirmed                                       |
| `Output`   | a short excerpt of the output in backticks, or the human's words                                         |
| `Commit`   | the SHA of the code the command saw                                                                      |
| `Observer` | optional: `agent` (default) or `user`                                                                    |

Only an entry with `Exit: 0` proves its step (rule 2). An entry with another exit code (a RED test run, a deliberate break) is a trace, not proof.

### Reported

Claims the skill did not check itself: a sub-agent's result, a user's statement without an observation, "already done".

Fields: `Step`, `Criteria` (as in Observed), `Claim`, `Source`.

### Skipped

Steps or gates the run did not perform.

Fields: `Step`, `Criteria` (as in Observed), `Reason`.

### Writing rules

- An Observed entry is written right after the phase commit, with the SHA of that commit: the gates ran on the uncommitted tree that became this commit.
- If a file outside `context/` changed after the command ran, run the command again before the commit.
- Never write into Observed what the skill did not run itself or what a human did not confirm.
- A human's confirmation of a Manual row is an Observed entry with `Observer: user`, `Command: manual: …`, `Exit: 0` and the human's words in `Output`; the row gets the SHA of the checked code.
- The report file belongs to the touched-file set of the run, like `plan.md`: it lands in the next phase commit or in the epilogue.
- Write only your own report; never edit a report of another run.

### Example

```markdown
# Run report: cena-brutto

- **Skill**: /10x-goal-implement
- **Model**: claude-opus-5-5
- **Started**: 2026-10-20T14:25:01+02:00
- **Start commit**: 48808a8

## Observed

### O1

- **Step**: 1.1
- **Criteria**: C1, C2
- **Command**: `npm test -- pricing`
- **Exit**: 0
- **Output**: `Tests: 4 passed, 4 total`
- **Commit**: 3f2a9c1

## Reported

None.

## Skipped

### S1

- **Step**: 1.3
- **Criteria**: C1, C2
- **Reason**: Manual row; needs a human.
```
