# Unattended mode

The skill runs unattended when `AskUserQuestion` is not among its tools (as in `claude -p`) or when the argument says nobody will answer.

## Rules

- Ask nothing: no `AskUserQuestion`, no question in the text that waits for a reply.
- Every gap gets a value: your recommendation goes into the block, so `change.md` is complete and `check_intent.py` passes without a human.
- Every recommendation that stands in for an answer gets an entry in `## Wymaga Twojej decyzji`. When it sets something future changes must apply, it also gets a decision-log entry with status `czeka na człowieka` (`references/principles-and-decisions.md`, "What goes into the log").
- A gap is something a human must decide that no file answers: a missing `Kogo dotyczy` or `Ograniczenia` with no support anywhere, a draft without a scenario for `**Scenariusz człowieka.**`, a rejected criterion, a risk level that differs from the draft, a scope question.
- A draft without a scenario: write the agent's own scenario into the block (built as `references/intent-block.md` says) and add an entry, e.g. `- **Szkic nie opisuje, co człowiek robi i widzi po kolei, więc scenariusz w bloku ułożył agent**`, with that scenario in short as the `Rekomendacja`.
- A fact you can read in the repository is not a gap. Read it.

## The section

`## Wymaga Twojej decyzji` is the last section of `change.md`. Create it when it is missing; append to it when it exists. One entry per gap, in three parts:

```markdown
- **<what is missing, in plain language>**
  - Rekomendacja: <value> — <one sentence why>
  - Odpowiedź do zatwierdzenia: „tak” przyjmuje rekomendację
```

- The first line says what is missing in words a person can answer without opening the code.
- `Rekomendacja` is the value already written into the block, with one sentence of reason.
- `Odpowiedź do zatwierdzenia` lets the human approve with one word.

## A rejected criterion

The rewording goes into the criteria block. The original wording appears only in the escalation entry:

```markdown
- **Kryterium R3 „Lista biurek jest przejrzysta.” wymaga oceny człowieka, więc w tej postaci nie da się go sprawdzić**
  - Rekomendacja: „R3. Lista pokazuje przy każdym biurku numer i piętro, posortowane po numerze.” — opisuje sprawdzalny efekt, o który chodziło w pierwotnym kryterium.
  - Odpowiedź do zatwierdzenia: „tak” przyjmuje rekomendację
```

## A smaller intent

A smaller intent that reaches the same goal (step "Smaller intent" of `SKILL.md`) is a scope question from the rules above. The smaller intent goes into the block. The draft's scope becomes the entry: its first line names what the draft asked for and what the block keeps instead; `Rekomendacja` is the smaller intent with one sentence why; a human who wants the draft's scope answers with it instead of „tak”. The scope of one change gets no decision-log entry (`references/principles-and-decisions.md`, "What goes into the log").

```markdown
- **Szkic prosi o listę wolnych biurek na dowolny dzień z kalendarzem, a blok zostawia tylko listę na jutro**
  - Rekomendacja: lista wolnych biurek na jutro — to pytanie, które pracownik zadaje w szkicu, a kalendarz można dodać później bez zmiany listy.
  - Odpowiedź do zatwierdzenia: „tak” przyjmuje rekomendację; „pełny zakres” przywraca listę na dowolny dzień z kalendarzem
```

## The final message

List every entry of the section under the line `Wymaga Twojej decyzji:` so the person sees what waits for them without opening the file, then the next command. With no entries, the message says `- nic nie czeka na Ciebie`.
