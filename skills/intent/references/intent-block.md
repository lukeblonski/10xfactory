# The intent block

The block is the whole body of `## Notes` in `change.md`. `validate_change.py` (owned by `/10x-impl-review`) reads its criteria; `scripts/check_intent.py` checks its shape. Labels are Polish, as in the drafts the factory already uses and in the criteria parser.

## Shape

Bold labels start at column 0, in this order, each opening its own paragraph:

```markdown
**Problem.** <what hurts today, for whom, and what it costs; facts, not the solution>

**Oczekiwany efekt.**
- <observable outcome once the change is done>

**Scenariusz człowieka.**
1. <what the person does first, in their own situation>
2. <what they see in answer, and what happens next, step by step until they have the outcome>

**Kogo dotyczy.** <the people or roles who notice the change; "autor fabryki" for a factory change>

**Ograniczenia.**
- <limits the solution must respect: tools, files that stay unchanged, budget, compatibility>

**Czego nie robimy.**
- <work that sounds related and stays out of this change>

**Decyzje z góry.**
- <choice already made, with the reason>. Źródło: człowiek|agent — <where it was made>; or the single word `brak`

**Kryteria akceptacji.**

- **C1.** <observable result>
  - Sprawdzenie: polecenie `<command whose exit code decides>`
- **C2.** <observable result>
  - Sprawdzenie: weryfikator — <what the review reads in the code or sees when it runs a read-only command>

**Ryzyko.** Wysokie|Niskie. <one sentence naming the condition from references/risk.md that decided it>

**Model zagrożenia.** <only for a change that checks or blocks something; see references/threat-model.md>
```

## Rules

- Every mandatory label appears exactly once: `**Problem.**`, `**Oczekiwany efekt.**`, `**Scenariusz człowieka.**`, `**Kogo dotyczy.**`, `**Ograniczenia.**`, `**Czego nie robimy.**`, `**Decyzje z góry.**`, `**Kryteria akceptacji.**`, `**Ryzyko.**`. `**Model zagrożenia.**` appears only when it applies.
- A criterion is a line `- **<ID>.** <text>` at column 0. Its `- Sprawdzenie:` line is indented by two spaces, directly under it or after other indented sub-points. The parser counts indented lines as part of the criterion above them, so the format of criteria does not change.
- Criterion IDs from the draft keep their numbers, as `/10x-new` keeps them. A new criterion takes the next number with the same prefix. With no criteria in the draft, the prefix is the first letter of the change-id, upper case (`cena-brutto` → `C1`, `C2`, …).
- A draft paragraph like `Sposób sprawdzenia.` (one paragraph mapping criteria to checks) is replaced by the `- Sprawdzenie:` lines; do not keep both.
- A `## Zasady pracy` section of the draft (how the agent should work on this change) stays after the block as a bold paragraph `**Zasady pracy.**` with its bullets.
- Draft content that fits no label (links, background notes) stays after the block as a bold paragraph `**Uwagi ze szkicu.**`, word for word; nothing from the old `## Notes` is dropped.
- A source line of the draft (`Źródło: …`, branch name) stays as the last paragraph of the block.
- The risk line is one line: `**Ryzyko.** Wysokie. <reason>` or `**Ryzyko.** Niskie. <reason>`. No other level exists.
- Nothing in the block may end the criteria block early: inside it, no line at column 0 starts with `**` or `#` except the criteria themselves.

## Filling the paragraphs

- Take a paragraph from the draft when the draft has it, keeping the author's words; fix only what breaks the shape.
- `Kogo dotyczy` and `Ograniczenia` are often missing from drafts. Derive them from the draft, the PRD and the repository first (who uses the changed part, what the draft says must stay unchanged). Ask, or escalate unattended, only when nothing supports a value.
- `Scenariusz człowieka` tells, from the person's side, how they will use the change: numbered steps, each saying what they do, what they see and what follows. Take it from the draft when the draft describes such a sequence. Otherwise build it from `Problem` and `Oczekiwany efekt`: who starts, in which situation, and which steps lead them to the expected outcome. Asking the human or escalating the scenario is described in `SKILL.md`, step 6.
- `Decyzje z góry` lists only decisions someone has made. A decision you would make yourself is a question for the human (or an escalation), not an up-front decision.
- Every item of `Decyzje z góry` ends with its source: `Źródło: człowiek — <where>` when the human made or accepted it (an acceptance sitting, an answer to a question), `Źródło: agent — <where>` when it comes from a document an agent wrote or accepted without the human (for instance a test plan accepted by an agent). Whoever later wants to change the decision reads from the source whether that needs the human. A decision without a clear source counts as the human's decision.
- Look at every point of the human's scenario, of `Oczekiwany efekt` and of `Decyzje z góry`. When a point narrows something down or takes something away, write right after it one sentence that opens with `Czego nie będzie:` and gives an example seen by the human: what they will see, or what they will no longer get. A point that neither narrows nor takes away anything gets no such sentence. For instance, "dodajemy listę" stays without it, while "kroki nie widzą Tavily" gets `Czego nie będzie: research nie użyje Tavily włączonego w projekcie, wynik będzie słabszy i nic tego nie zgłosi.`
