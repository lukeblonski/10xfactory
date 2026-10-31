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
| `context/foundation/decisions.md` (the decision log) | decisions every future change must apply, and decisions on retrospective proposals | `intent`; `retro` (entries of the change, decisions on proposals, rejected proposals) |
| `context/foundation/limitations.md` (the limitation register) | limitations: findings knowingly left unfixed, each with `Kiedy wrócić` | the triage of `10x-impl-review` and `10x-plan-review` (writes LIMIT entries); `retro` (`Kiedy wrócić`, entries of the change) |
| `context/foundation/decisions-archive.md` (the archive) | closed entries (a fixed limitation, a replaced decision) and decisions of one change | nobody in ordinary work; a skill that writes an entry reads only its `## D-` headings, for the number |

### What goes into the log

- A decision future changes must apply: a rule, a format, a threshold, a default behaviour.
- Every decision on retrospective proposals (accepted and rejected); `retro` reads them in the log.
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

- Heading: `## D-<nnn> <topic>`, numbered as "Numbering" says. All three kinds of entry below share this one sequence; the start of the topic and the extra fields tell the kind.
- Fields, one per line, in this order:
  - `Pytanie`: the question in one line;
  - `Wybór`: the answer taken;
  - `Kto zdecydował`: `człowiek`, `model (<skill name>)`, `recenzent i autor (<skill name>)` or, for a proposal merged by the retrospective's PR step, `testy skilli i recenzent (retro_pr)`;
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
- Podstawa: reviews/impl-review.md F4, reguła L2
- Kiedy wrócić: zmiana dotyka `src/week/` albo aplikacja ma prawdziwych użytkowników.
- Źródło: widok-tygodnia — `reviews/impl-review.md` F4
- Status: obowiązuje
- Zmiana: widok-tygodnia
```

- Fields in this order: `Pytanie`, `Wybór`, `Kto zdecydował`, `Podstawa`, `Kiedy wrócić`, `Źródło`, `Status`, `Zmiana`.
- `Kto zdecydował`: `model (<skill>)` for a policy decision, `człowiek` for a limitation the human accepted, `recenzent i autor (<skill>)` for a loop closed by both agents.
- `Podstawa`: the report and finding, the rule (`L1`–`L4`, or `E4 w rundzie <N>`), and `poza polityką` for L4; for a human, their words.
- `Kiedy wrócić`: the condition under which the limitation starts to matter, named so a retrospective can recognise it in a change's traces: a file or directory the change touches, a skill it changes, an event in its traces (a paid run, a new fixture, a publication, real users).
- `Źródło`: the change the limitation comes from and the place, in backticks: `<change-id> — \`<path>:<line>\`` or `<change-id> — \`<report>\` F<n>`. `Zmiana` names the change that writes the entry; when the two differ, `Źródło` keeps the origin.
- Status: `obowiązuje` while the limitation stands; `naprawione w <change-id> (<sha>)` once a change fixes it (only `Status` changes), and that change moves the entry to the archive.

### A decision on retrospective proposals

The human's decision on the proposals of one retrospective that the PR step does not merge (see the end of this section), plus one separate entry for each rejected proposal.

```markdown
## D-035 Propozycje retrospektywy etap-8a-polityka-triage
- Pytanie: które propozycje z `context/archive/2026-10-21-etap-8a-polityka-triage/retro.md` przyjąć?
- Wybór: przyjęte P1, P2, P4; odrzucone P3 (D-038)
- Kto zdecydował: człowiek
- Podstawa: przyjęte przez człowieka; dowody w retro.md
- Retrospektywa: `context/archive/2026-10-21-etap-8a-polityka-triage/retro.md`
- Co ma się zmienić: P1: …; P2: …; P4: niesprawdzalne: …
- Data: 2026-10-22
- Status: obowiązuje
- Zmiana: etap-8b-rejestr-ograniczen

## D-038 Odrzucona propozycja etap-8a-polityka-triage P3: Lekcja 5 obejmuje poprawki z review i szuka zasady po znaczeniu
- Pytanie: czy przyjąć propozycję P3 z `context/archive/2026-10-21-etap-8a-polityka-triage/retro.md`?
- Wybór: odrzucona
- Kto zdecydował: człowiek
- Podstawa: wróć, gdy się powtórzy (`docs/zasady-budowy.md`, punkt 9).
- Retrospektywa: `context/archive/2026-10-21-etap-8a-polityka-triage/retro.md` P3
- Data: 2026-10-22
- Status: obowiązuje
- Zmiana: etap-8b-rejestr-ograniczen
```

- Headings: `Propozycje retrospektywy <change-id>` and `Odrzucona propozycja <change-id> P<n>: <proposal title>`.
- Fields in this order: `Pytanie`, `Wybór`, `Kto zdecydował`, `Podstawa`, `Retrospektywa`, `Co ma się zmienić`, `Data`, `Status`, `Zmiana`.
- `Retrospektywa`: the full path of the retrospective's output file in backticks; in a rejection, followed by the proposal number.
- `Co ma się zmienić`: only in the entry with the accepted proposals, and only for accepted proposals that have this field in `retro.md` (`skills/retro/references/retro-format.md`). Each one is `P<n>: <the field from retro.md>`, and they are joined with `; `. The field itself contains `; `, so the line splits into proposals only before `; P<digits>: `. A proposal without the field in `retro.md` (older retrospectives) is left out; when no accepted proposal has it, the line is left out. A rejection never has this line: it gets no verdict.
- `Data`: the day the human decided (`YYYY-MM-DD`); a retrospective compares later evidence against it.
- `Podstawa` of a rejection: the human's reason in one sentence.

A proposal with its target in `skills/` that the retrospective's PR step merges (`python3 scripts/retro_pr.py <change-id>`) gets its own entry, which the script appends as the last commit of the PR branch, right before the merge. Heading `Propozycja <change-id> P<n>: <proposal title>`, the same fields in the same order, `Kto zdecydował: testy skilli i recenzent (retro_pr)`, `Podstawa` naming the tests and the reviewer's verdict, and `Retrospektywa` followed by the proposal number. When the proposal has a `Co ma się zmienić` field, the entry has it in the same place: the field of that one proposal, without the `P<n>:` prefix, since its number is in `Retrospektywa`. The template is in `skills/retro/references/pr.md`, section "Wpis w dzienniku". A PR that waits for the human gets no entry from the script; the human records the decision as above.

## What `intent` writes

- Only into the log, and only what "What goes into the log" sends there; the number by "Numbering". Create the file with the `# Decisions` heading at the first entry.
- Interactive: one entry per question the human answered whose answer future changes must apply, `Kto zdecydował: człowiek`, `Status: obowiązuje`.
- Unattended: one entry per recommendation that stands in for such an answer, `Kto zdecydował: model (intent)`, `Status: czeka na człowieka`; the same gap has its entry in `## Wymaga Twojej decyzji`.
- An answer or recommendation about this change alone gets no entry: it stays in "Decyzje z góry" in `change.md`, and unattended also in `## Wymaga Twojej decyzji`.
- Decisions on retrospective proposals given in the draft: one `Propozycje retrospektywy` entry per retrospective with the accepted proposals, and one `Odrzucona propozycja` entry per rejected proposal with the human's reason. Interactive: `Kto zdecydował: człowiek`, `Status: obowiązuje`. Unattended: `Kto zdecydował: model (intent)`, `Podstawa: szkic człowieka`, `Status: czeka na człowieka`. The path in `Retrospektywa:` and the proposal numbers come from the draft. The `Co ma się zmienić` field of each accepted proposal comes from the `retro.md` at that path: the `retro.md` files named in the draft are the only files of `context/archive/` that `intent` reads.
- Do not log facts read from files, or the shape of the block.

## What `intent` reads

Before asking anything, look for the answer in the principles and the decision log. A principle or a decision with status `obowiązuje` or `zmienione przez człowieka` settles the question; a decision with status `czeka na człowieka` is a recommendation you may follow, naming it in the block.
