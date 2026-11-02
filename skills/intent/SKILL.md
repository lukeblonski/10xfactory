---
name: intent
description: >
  Turn a short description or a draft of a change into a complete intent block in
  context/changes/<change-id>/change.md: problem, expected effect, the human's scenario (what the
  person does and sees, step by step), who it affects, constraints,
  what we do not do, decisions made up front, numbered acceptance criteria that a command or the
  verifier agent can check, risk with a one-sentence reason and, for a change that checks or
  blocks something, a threat model. Starts the change through /10x-new when the folder does not
  exist. Works unattended (claude -p): instead of asking, it records what is missing for a human.
  Trigger phrases: "ustal intencję", "nowa zmiana", "napisz intencję", "write the intent",
  "start a change", "new change". Use BEFORE /10x-research.
argument-hint: "<change-id> <opis albo szkic intencji>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - Skill
  - AskUserQuestion
---

# intent — the intent block of a change

One path starts a change: `/intent <change-id> <description or draft>`. The skill creates the folder through `/10x-new`, so `change.md` keeps its one format, and then writes the intent block into `## Notes`. Every criterion leaves with a way to check it, every change leaves with a risk level, and nothing a human must decide is guessed silently.

## Co czytam

- **Always:** the argument; the change's `change.md` when it exists; the change's `context/changes/<change-id>/frame.md` (the brief of `/10x-frame`) when it exists; in `context/foundation/`: `prd.md`, `product-principles.md`, the decision log `decisions.md` and `lessons.md` when they exist; `CLAUDE.md` or `AGENTS.md` (the verify command); `references/intent-block.md`, `references/criteria.md`, `references/risk.md`.
- **Only when needed:** `references/threat-model.md` (the change checks or blocks something); `references/unattended.md` (no human is answering, or before you ask a question: a question takes the shape of its entry); `references/principles-and-decisions.md` (before writing to the decision log); `references/examples.md` (a criterion needs rewording); source files the description names, to confirm a fact instead of asking; each `retro.md` whose path the draft gives with decisions on retrospective proposals, to copy the `Co ma się zmienić` field of the accepted proposals (`references/principles-and-decisions.md`).
- **Never:** `context/archive/`, except those `retro.md` files; other changes, run reports in `runs/`; the limitation register `context/foundation/limitations.md` and the archive `context/foundation/decisions-archive.md`, except a `grep` of their `## D-` headings for the next number (`references/principles-and-decisions.md`).

## Steps

1. **Mode.** When `AskUserQuestion` is not among your tools (a tool the session names as deferred counts as present), or the argument says the run is unattended (e.g. "unattended", "bez człowieka", "claude -p"), work unattended: ask nothing and follow `references/unattended.md`. Do not search for the tool with ToolSearch; its absence is the signal.

2. **Argument.** The first token is the change-id; the rest is the description or the draft (it may span many lines). Without a change-id: interactively ask for one; unattended, STOP with one line saying the change-id is missing (there is no `change.md` yet to hold an escalation).

3. **Branch.** Run `git branch --show-current`. On any branch other than `master`, do nothing here. On `master`, nothing may be written there, so before the first write:
   - the change-id must be kebab-case, by the same rule `/10x-new` applies (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`); otherwise STOP the way a missing change-id stops;
   - when a branch named after the change-id already exists, run `git switch <change-id>`; otherwise run `git switch -c <change-id>`;
   - when a git command fails, STOP and show its output; nothing is written yet.

4. **The change.**
   - No `context/changes/<change-id>/`: invoke `/10x-new <change-id> <one sentence that sums up the description>` with the Skill tool. Its own next-step suggestion does not end this run; continue with step 5. If `/10x-new` prints `error:`, or `context/changes/<change-id>/change.md` does not exist afterwards, STOP and show its output; never write `change.md` yourself.
   - The folder exists with `status: new` or `status: preparing`: work in it. The current body of `## Notes` is part of the draft.
   - Any later status (`planned` and beyond): STOP. Changing the intent after a plan exists is a human decision; say so and name the current status.
   - A `**Kryteria akceptacji.**` block in a section other than `## Notes`: STOP and name that section. Merging two criteria blocks is a human decision.
   - When step 3 switched branches and this step stops, the STOP message also says that the person is now on branch `<change-id>`, not on `master`.

5. **Smaller intent.** Before you write the criteria, check whether a smaller intent reaches the same user goal. Look for two forms: the same thing with a narrower reach (fewer cases, one role, one file), or a smaller thing that leans on a part the repository or the user already has. When neither form keeps the goal named in `Problem`, skip this step.
   - interactive: the smaller intent is one option of a question in the round of step 6, described by its effect (what the person gets and what they give up); the draft's scope is another option; the first option is your recommendation with one sentence why.
   - unattended: write the smaller intent into the block, and record the draft's scope as an entry in `## Wymaga Twojej decyzji` (`references/unattended.md`, "A smaller intent"); it is a decision of this change, so it gets no decision-log entry.

6. **Block.** Build it in the shape of `references/intent-block.md`. Take everything the draft and the files from "Co czytam" already settle. Never ask about something a file answers (a principle, a logged decision, the verify command, the code). For the rest:
   - interactive: one round of at most 4 questions with `AskUserQuestion`. Each question follows the entry in `references/unattended.md` ("The section"): it says in plain language what has to be settled and what for; each option is described by its effect; the first option is your recommendation with one sentence why;
   - unattended: put your recommendation into the block and record the gap as `references/unattended.md` says.

   Every block gets the paragraph `**Scenariusz człowieka.**` (how to build it: `references/intent-block.md`, "Filling the paragraphs"):
   - interactive: show the scenario for confirmation as one of the questions of that round; the first option is the scenario you built, with one sentence why, and the person may correct it;
   - unattended: write the scenario the draft gives; when the draft gives none, write the scenario you built and add an entry to `## Wymaga Twojej decyzji` (`references/unattended.md`).

7. **Criteria.** Judge each one with `references/criteria.md`. Each criterion gets an indented `- Sprawdzenie:` line. A criterion that needs a human's judgement, or that prescribes a mechanism the problem does not need, is not accepted as written: propose a rewording (`references/examples.md`), then take the human's choice, or unattended, keep the rewording and escalate the original.

8. **Risk and threat model.** Set the risk with `references/risk.md`: `Wysokie` or `Niskie`, one sentence naming the condition that decided it. When the change checks or blocks something, add a threat model with `references/threat-model.md`.

9. **Write.** Replace the body of `## Notes` in `change.md` with the block; keep the frontmatter and every other section (`## Interwencje`, `## Wymaga Twojej decyzji`). Set `updated:` to today; leave `status` as it is.

10. **Check.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_intent.py context/changes/<change-id>/change.md`.
    - Exit 0: continue.
    - Exit 1: fix the problems it lists and run it again, at most 2 fixes; if it still fails, STOP and show its output.
    - Exit 2: STOP and show its output (a missing file or a missing skill it depends on).

11. **Decision log.** Append to `context/foundation/decisions.md`, as `references/principles-and-decisions.md` describes, only the decisions future changes must apply and the decisions on retrospective proposals: the human's answers to your questions and, unattended, the recommendations you put in place of an answer, when they set a rule, a format, a threshold or a default behaviour for later changes; and the decisions on retrospective proposals the draft gives (accepted and rejected, with the `Retrospektywa:` path and proposal numbers from the draft, and the `Co ma się zmienić` field of the accepted proposals copied from the `retro.md` at that path). Every other answer or recommendation (the scope, budget or measurement of this change) stays in "Decyzje z góry" in `change.md`, and unattended also in `## Wymaga Twojej decyzji`.

12. **Finish.** Print a short summary and nothing after it:
    - the number of criteria and the risk level with its reason;
    - the line `Wymaga Twojej decyzji:` followed by the entries of that section, one line each, or by the single line `- nic nie czeka na Ciebie` when the section has none;
    - the last line: `Następny krok: po zatwierdzeniu intencji łańcuch uruchamia sesja (ręcznie: /10x-research <change-id>)`.

## Example

```
/intent wolne-biurka Pracownik nie wie, które biurka są jutro wolne. Chcę listę wolnych biurek na wybrany dzień.
```

Creates `context/changes/wolne-biurka/change.md` through `/10x-new`, writes the block with criteria such as `- **W1.** freeDesks("2026-11-02") zwraca tylko biurka bez rezerwacji na ten dzień.` checked by `npm test`, sets `**Ryzyko.** Niskie. …`, and ends with `Następny krok: po zatwierdzeniu intencji łańcuch uruchamia sesja (ręcznie: /10x-research wolne-biurka)`.

## What this skill does NOT do

- It does not start a new product (vision, persona, MVP); `/10x-shape` stays for that.
- It does not write `product-principles.md`; it only reads it.
- It does not plan, research or change the status of the change.
- It does not use the risk level for anything; later stages read it.
- It does not change an intent once a plan exists.
