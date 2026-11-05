# Product principles and the decision files

Files in `context/foundation/` hold what a human has already decided, so the skill does not ask again: the product principles and the decision log, which `intent` reads, plus the limitation register and the archive, which share the log's numbering. None has to exist; a missing file is not an error.

## `context/foundation/product-principles.md`

Rules that settle product questions before anyone asks them. One line per principle:

```markdown
# Product principles

- **P1.** Prostsze wygrywa. Z dwóch rozwiązań wybieraj to z mniejszą liczbą kroków dla użytkownika.
- **P2.** Telefon przed komputerem. Każdy ekran działa na szerokości 375 px.
```

- Format: `- **P<n>.** <principle>. <one sentence on what it is for>`.
- `intent` only reads this file. The product mode (a later stage) writes it.
- When a principle answers a question, use it and name it (`P2`) in the block, e.g. in `Ograniczenia` or in the reason of a decision.

## The three decision files

| File | Holds | Who reads it |
|---|---|---|
| `context/foundation/decisions.md` (the decision log) | decisions every future change must apply | `intent`; the analysis across changes |
| `context/foundation/limitations.md` (the limitation register) | limitations: findings knowingly left unfixed, each with `Kiedy wrócić` | the triage of `10x-impl-review` and `10x-plan-review` (writes LIMIT entries); the analysis across changes (`Kiedy wrócić`) |
| `context/foundation/decisions-archive.md` (the archive) | closed entries (a fixed limitation, a replaced decision), decisions of one change, and accepted proposals of retrospectives before 2026-11-02 | nobody in ordinary work; a skill that writes an entry reads only its `## D-` headings, for the number |

### What goes into the log

- A decision future changes must apply: a rule, a format, a threshold, a default behaviour.
- Not a decision on the scope, budget or measurement of one change: it stays in that change's `change.md` ("Decyzje z góry") and plan.

### Numbering

- One sequence across the three files. A number never changes and is never reused (the one exception: the later of two entries that got the same number gets the first free one, with the old number in its `Status`), so a reference `D-<nnn>` anywhere points at the one entry that has it, in whichever file it lies.
- The next number is the highest `D-<nnn>` among the headings of the three files, plus one: `grep -hoE '^## D-[0-9]{3}' context/foundation/{decisions,limitations,decisions-archive}.md | sort | tail -1`. A missing file adds no numbers. Do not take the last heading of one file: after entries move, it is not the highest number.
- Count the number in the same command that appends the entry, and count it again after every `pull` or merge: a number counted earlier may already be taken. `scripts/test_decision_numbers.py` checks that no number appears in two headings.

### The archive

- The change that closes an entry (fixes a limitation, replaces a decision) moves it to the end of `decisions-archive.md` in the same change. Only its `Status` changes; the rest of the entry stays word for word.
- Numbers in the archive need not go up.
- Ordinary work does not read the archive: no skill reads its entries to decide anything.

### A missing file

Create it at its first entry with its heading: `# Decisions`, `# Limitations` or `# Decisions archive`.

### A decision

```markdown
# Decisions

## D-001 Format kwot w aplikacji
- Pytanie: jak aplikacja pokazuje kwoty?
- Wybór: z dwoma miejscami po przecinku i „zł” po spacji, np. „12,50 zł”.
- Kto zdecydował: model (intent)
- Podstawa: szkic pokazuje kwoty w tym formacie; PRD nie mówi o innej walucie.
- Status: czeka na człowieka
- Zmiana: widok-tygodnia
```

- Heading: `## D-<nnn> <topic>`, numbered as "Numbering" says. Both kinds of entry below share this one sequence; the start of the topic and the extra fields tell the kind.
- Fields, one per line, in this order:
  - `Pytanie`: the question in one line;
  - `Wybór`: the answer taken;
  - `Kto zdecydował`: `człowiek` or `model (<skill name>)`;
  - `Podstawa`: the reason: a principle, a file, the human's words;
  - `Status`: a short description of the entry's current state. Base values, recommended when they fit: `obowiązuje`, `obowiązuje na próbę`, `czeka na człowieka`, `zmienione przez człowieka`, `zastąpione przez D-<nnn>` and, for a limitation, `naprawione w <change-id> (<sha>)`. A note in parentheses or after a semicolon may follow;
  - `Zmiana`: the change-id the entry was written in.
- Entries are appended. A later decision that replaces an earlier one gets a new entry; the old one only changes its `Status` to `zastąpione przez D-<nnn>`.

### A limitation

A finding knowingly left unfixed. It lives in the limitation register `context/foundation/limitations.md`, not in the log. The review triage writes it (`10x-impl-review`, `10x-plan-review`, "Recording the decisions"); `intent` does not.

```markdown
## D-002 Ograniczenie: widok tygodnia nie odświeża się sam
- Pytanie: czy naprawić teraz to, że widok tygodnia nie pokazuje rezerwacji zrobionej w innej karcie bez przeładowania?
- Wybór: nie; ograniczenie zostaje. Rezerwacje zmieniają się rzadko, a przeładowanie wystarcza.
- Kto zdecydował: model (10x-impl-review)
- Podstawa: reviews/impl-review.md F4, reguła przypadek szczególny
- Kiedy wrócić: zmiana dotyka `src/week/` albo aplikacja ma prawdziwych użytkowników.
- Źródło: widok-tygodnia — `reviews/impl-review.md` F4
- Status: obowiązuje
- Zmiana: widok-tygodnia
```

- Fields in this order: `Pytanie`, `Wybór`, `Kto zdecydował`, `Podstawa`, `Kiedy wrócić`, `Źródło`, `Status`, `Zmiana`.
- `Kto zdecydował`: `model (<skill>)` for a policy decision, `człowiek` for a limitation the human accepted.
- `Podstawa`: the report and finding and the policy rule (e.g. `przypadek szczególny` or `bramka 2`); for a human, their words.
- `Kiedy wrócić`: the condition under which the limitation starts to matter, named so the analysis across changes can recognise it in a change's traces: a file or directory the change touches, a skill it changes, an event in its traces (a paid run, a new fixture, a publication, real users).
- `Źródło`: the change the limitation comes from and the place, in backticks: `<change-id> — \`<path>:<line>\`` or `<change-id> — \`<report>\` F<n>`. `Zmiana` names the change that writes the entry; when the two differ, `Źródło` keeps the origin.
- Status: `obowiązuje` while the limitation stands; `naprawione w <change-id> (<sha>)` once a change fixes it (only `Status` changes), and that change moves the entry to the archive.

## What `intent` writes

- Only into the log, and only what "What goes into the log" sends there; the number by "Numbering". Create the file with the `# Decisions` heading at the first entry.
- Interactive: one entry per question the human answered whose answer future changes must apply, `Kto zdecydował: człowiek`, `Status: obowiązuje`.
- Unattended: one entry per recommendation that stands in for such an answer, `Kto zdecydował: model (intent)`, `Status: czeka na człowieka`; the same gap has its entry in `## Wymaga Twojej decyzji`.
- An answer or recommendation about this change alone gets no entry: it stays in "Decyzje z góry" in `change.md`, and unattended also in `## Wymaga Twojej decyzji`.
- Do not log facts read from files, or the shape of the block.

## What `intent` reads

Before asking anything, look for the answer in the principles and the decision log. A principle or a decision with status `obowiązuje` or `zmienione przez człowieka` settles the question; a decision with status `czeka na człowieka` is a recommendation you may follow, naming it in the block.
