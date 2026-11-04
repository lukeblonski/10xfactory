#!/usr/bin/env python3
"""Numbers of the changes and verdicts of the retrospective fixes.

Usage: python3 scripts/pomiar.py [--repo DIR] [--zmiana <change-id>]

Reads every context/archive/*/change.md (change_id, archived_at) with the
files next to it and prints Markdown on stdout: `# Pomiar zmian`, `- Data:
<today>`, `## Liczby zmian`, a table with one row per change in archived_at
order, `## Wersja` in a repo with context/foundation/start.md, and `## Werdykty
poprawek`. `--zmiana <change-id>` adds, as the last
row, the change in context/changes/<change-id>/ with the cell `<change-id>
(przed archiwum)`: skills/10x-archive/SKILL.md runs /retro before it moves the
folder and stamps archived_at, so that folder needs no archived_at. An id that
is already in the archive adds nothing. Only reads; standard library and one
`git log --reverse --format=%h%x1f%ct%x1f%s HEAD`.

Readers: skills/retro/SKILL.md runs `python3 scripts/pomiar.py --zmiana
<change-id>` and copies its sections unchanged into
context/changes/<change-id>/retro.md, in the shape of
skills/retro/references/retro-format.md; docs/testy-fabryki.md describes the
command.

Columns (plan of retro-liczy, phase 1):
- Minuty: the sum of `Czas (s)` of the cost rows / 60, whole minutes; the cost
  rows come from koszty-krokow.md next to change.md and from the section
  `## Koszty kroków` of context/przebiegi/<change_id>.md (read_costs);
- Koszt USD: the sum of `Koszt USD` of the same rows, two decimals;
- Decyzje: lines of `## Pytania do człowieka` with `rozstrzygnął: człowiek`
  and a `krok` other than `intent` (line format in docs/zasady-budowy.md,
  point 6; parse_questions);
- Rundy planu, Rundy kodu: files reviews/plan-review*.md and
  reviews/impl-review*.md (REPORT_FILE), without subfolders;
- Błędy po scaleniu: subjects of `git log --format=%s HEAD` in --repo that
  contain `(błąd po <change_id>)` with the closing parenthesis;
- Zmiana: the id; the row of --zmiana gets ` (bez kroku archiwum)` when it
  has cost rows but none of the step `archiwum` (the retro runs inside that
  step, so its sums are short of the ones after the archive);
- Cofnięcia: `  - **Cofnięcie:** <rodzaj> — <powód>` sub-points of
  `## Interwencje` (parse_undo); 0 without the section;
- Narzut łańcucha: the sum of `Koszt USD` of the cost rows whose `Krok` is
  not `implement`, by the sum of `Koszt USD` of all of them, whole per cent
  (overhead).
No cost row gives `brak danych` in Minuty, Koszt USD and Narzut łańcucha (a
sum of 0 too in Narzut łańcucha); no `## Pytania do człowieka` gives `brak
danych` in Decyzje; a failing `git log` gives `brak danych` in Błędy po
scaleniu.

Under the table one line `Poprawki poza zmianami: <n> (<short shas>)`, an
estimate for the human: commits of `git log HEAD` whose subject starts with
`fix(<scope>)`, where the scope is no change id of context/archive/ or
context/changes/, and which have no `(retro ` in the subject.

Wersja: only when context/foundation/start.md exists (an application repo),
after that line, one row with the measures of the goal of the version in
context/foundation/prd.md (version_row), over start.md and the changes of the
table (the archived ones and the one of --zmiana):
- Zmiany: the number of rows of `## Liczby zmian`;
- Interwencje: lines of `## Pytania do człowieka` of start.md and of every
  change with `rozstrzygnął: człowiek` or `rozstrzygnął: obserwator` and a
  `krok` other than those of NOT_INTERVENTIONS (the owner's idea, the
  acceptance and the consents of the start); `brak danych` when no source has
  the section;
- Błędy po scaleniu: the sum of the rows (0 without a change);
- Cofnięcia: the sum of the rows plus the `Cofnięcie:` sub-points of
  `## Interwencje` of start.md;
- Narzut łańcucha: as in a row, over the cost rows of `## Koszty kroków` of
  start.md and of every change;
- W celu: `nie` when a known value is over the goal (Interwencje over
  MAX_INTERVENTIONS, Błędy po scaleniu or Cofnięcia over 0), `tak` when all
  three are known and within, otherwise `brak danych`; Narzut łańcucha has no
  threshold and does not count.

Werdykty poprawek (plan of retro-liczy, phase 2): one row per proposal
`#### P<n>. <tytuł>` in `## Propozycje` of context/archive/*/retro.md whose
`- **Co ma się zmienić**:` is `<kolumna> (<change-id>: <wartość>); kierunek:
<w dół|w górę>` with a number column of `## Liczby zmian`; any other field is
skipped. A proposal without a row: `Rekomendacja: nie`, a heading
`Odrzucona propozycja <id> P<n>` or `zostaw <target>` for a proposal titled
`Usunąć poprawkę <target>` in context/foundation/decisions.md, or a commit
`Revert "… (retro <id> P<n>)"`. The fix commit is the oldest subject with
`(retro <id> P<n>)` or the commit `chore(archive): close <cid>` of an archived
change that lists `<id> P<n>` in `## Poprawki z retrospektywy`, whichever is
earlier. Before: the last 3 changes archived before that commit; after: the
changes (with the --zmiana row) whose oldest commit with `(<cid>)` is later.
The number is the mean of the column without `brak danych`. Verdict: `nie
weszła` without a commit once a later change is archived (`czeka` before);
`czeka` with fewer than 3 changes after; for k = 3…n the mean of the first k
after against the mean before: worse, or a higher mean of Błędy po scaleniu
or Cofnięcia, is `szkodzi`; better without those is `działa`, or `wróciło`
when the last 3 after no longer give `działa`; nothing by 6 changes after is
`bez skutku`. No mean on one side decides nothing; no mean before stays
`czeka`. Without any row the
section says `Brak.`; a failing `git log` says `Brak danych: <git message>`.

The reading part (section_lines, parse_questions, QuestionError, QUESTIONS,
KINDS, …) is a library: scripts/autopilot.py imports it, also in the exported
package.

Bad question or undo lines print `BŁĄD PYTANIA: <file>:<line>: …`, a cost row
with another number of cells than its header prints `BŁĄD KOSZTÓW: <file>: …`
(of start.md too),
a `Co ma się zmienić` with `; kierunek: w…` (of an archived change or of the
`--zmiana` change) that does not match the shape or has no known column prints
`BŁĄD POPRAWKI: <file>:<line>: …`, all after the full output.

Exit codes: 0 OK; 1 a bad question, undo, cost or fix line; 2 no context/archive/
or no change in it in a repo without context/foundation/start.md (with it the
table of changes is empty), an archived change without `archived_at` of the form
YYYY-MM-DDTHH:MM:SSZ, a bad argument, or `--zmiana` with an id that is
neither in context/changes/ nor in the archive.
"""

import math
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_DATA = "brak danych"


class UsageError(Exception):
    """Missing or unreadable input: the command exits 2."""


REPORT_FILE = re.compile(r"^(plan|impl)-review(?:-(\d+))?\.md$")
FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^## ")
ARCHIVED_AT = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
CHANGE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
# Questions to the human (docs/zasady-budowy.md, point 6, „Pytania do człowieka”).
QUESTIONS = "Pytania do człowieka"
KINDS = ("spór recenzenta z autorem", "eskalacja", "płatny przebieg", "zakres", "kryterium", "inne")
QUESTION_FIELDS = ("rodzaj", "krok", "pytanie", "rekomendacja", "wybór", "rozstrzygnął")
QUESTION_KEYS = ("kind", "step", "question", "recommendation", "choice", "by")
QUESTION_LINE = re.compile("^- " + " · ".join(f"{name}: (.+?)" for name in QUESTION_FIELDS) + "$")
DECIDERS = ("człowiek", "agent", "obserwator")
HUMAN = "człowiek"
INTENT_STEP = "intent"
# Deciders whose line always has `wybór: rekomendacja`.
AUTOMATIC = ("agent", "obserwator")
AGREED = "rekomendacja"
OTHER_CHOICE = re.compile(r"^inny: \S")
UNDO = re.compile(r"^\s+- \*\*Cofnięcie:\*\*\s*(.*)$")
UNDO_TOP = re.compile(r"^- \*\*Cofnięcie:\*\*")
# Costs of the steps (scripts/autopilot.py, P23): files, section and the columns read from the table.
COSTS_FILE = "koszty-krokow.md"
RUNS = "context/przebiegi"
COSTS_SECTION = "Koszty kroków"
COST_COLUMNS = ("Krok", "Czas (s)", "Koszt USD")
# The step whose cost is no overhead of the chain (Narzut łańcucha).
IMPLEMENT_STEP = "implement"
# The table `## Liczby zmian`.
CHANGES = "Liczby zmian"
CHANGES_COLUMNS = ("Zmiana", "Minuty", "Koszt USD", "Decyzje", "Rundy planu", "Rundy kodu", "Błędy po scaleniu",
                   "Cofnięcia", "Narzut łańcucha")
CHANGES_HEADER = "| " + " | ".join(CHANGES_COLUMNS) + " |"
# The section `## Wersja` of an application repo: the goal of the version in context/foundation/prd.md (D-467).
START_FILE = os.path.join("context", "foundation", "start.md")
VERSION = "Wersja"
VERSION_COLUMNS = ("Zmiany", "Interwencje", "Błędy po scaleniu", "Cofnięcia", "Narzut łańcucha", "W celu")
VERSION_HEADER = "| " + " | ".join(VERSION_COLUMNS) + " |"
INTERVENERS = ("człowiek", "obserwator")
# Steps of the owner's idea, the acceptance and the consents of the start: their lines are no interventions.
NOT_INTERVENTIONS = ("intent", "intencja", "akceptacja", "bramki", "dostępy")
MAX_INTERVENTIONS = 3
BEFORE_ARCHIVE = "(przed archiwum)"
ARCHIVE_STEP = "archiwum"
NO_ARCHIVE_STEP = "(bez kroku archiwum)"
OUTSIDE_FIXES = "Poprawki poza zmianami"
FIX_SUBJECT = re.compile(r"^fix\(([^()]+)\)!?: ")
# The table `## Werdykty poprawek`: the number columns of `## Liczby zmian` and the keys of their row values.
VERDICTS = "Werdykty poprawek"
VERDICTS_COLUMNS = ("Poprawka", "Liczba", "Kierunek", "Commit poprawki", "Przed", "Po", "Zmiany po", "Werdykt")
VERDICTS_HEADER = "| " + " | ".join(VERDICTS_COLUMNS) + " |"
NUMBER_KEYS = {"Minuty": "minutes", "Koszt USD": "cost", "Decyzje": "decisions", "Rundy planu": "plan_rounds",
               "Rundy kodu": "impl_rounds", "Błędy po scaleniu": "bugs", "Cofnięcia": "undo",
               "Narzut łańcucha": "overhead"}
DOWN = "w dół"
PROPOSALS = "Propozycje"
PROPOSAL = re.compile(r"^#### P(\d+)\. (.+?)\s*$")
PROPOSAL_FIELD = re.compile(r"^- \*\*(Co ma się zmienić|Rekomendacja)\*\*:(.*)$")
FIELD = re.compile(r"^(?P<column>.+?) \((?P<cid>[^():]+): (?P<value>[^()]+)\); kierunek: (?P<direction>w dół|w górę)$")
# The new shape: old fields have `kierunek: 0 …`, `kierunek: co najwyżej …` and never `kierunek: w…`.
FIELD_MARK = re.compile(r";\s*kierunek:\s*w\b")
# A removal and the undo of a removal: `zostaw <id> P<n>` blocks both.
REMOVAL = re.compile(r"^(?:Usunąć poprawkę|Cofnąć usunięcie) (\S+) P(\d+)$")
FIXES = "Poprawki z retrospektywy"
DECISIONS_FILE = os.path.join("context", "foundation", "decisions.md")
CID_IN_SUBJECT = re.compile(r"\(([^()\s]+)\)")
WINDOW = 3
NO_EFFECT_AFTER = 6
USAGE = "usage: pomiar.py [--repo DIR] [--zmiana <change-id>]"


# ------------------------------------------------------------------ reading

def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def unfenced(text):
    """Lines of text with the lines of code blocks blanked (fences included)."""
    out, fenced = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return out


def section_lines(text, heading):
    """(line number of the heading, [(line number, line)]) of the `## <heading>` section
    outside code blocks; None when absent."""
    lines = unfenced(text)
    target = "## " + heading
    for i, line in enumerate(lines):
        if line.rstrip() == target:
            end = next((j for j in range(i + 1, len(lines)) if H2.match(lines[j])), len(lines))
            return i + 1, [(j + 1, lines[j]) for j in range(i + 1, end)]
    return None


def section(text, heading):
    """Lines of the `## <heading>` section outside code blocks; None when absent."""
    found = section_lines(text, heading)
    return None if found is None else [line for _, line in found[1]]


def frontmatter(text):
    """key: value pairs of the leading `---` block."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return meta


class QuestionError(ValueError):
    """Bad question or undo lines; `errors` holds (line number, message) pairs."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"{n}: {msg}" for n, msg in errors))


def _numbered(lines, first):
    """(line number, line) of lines outside code blocks; lines[0] has number `first`."""
    out, fenced = [], False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            out.append((first + i, line))
    return out


def _question(line):
    """(question dict, None) of one line, or (None, error message)."""
    match = QUESTION_LINE.match(line.rstrip())
    if not match:
        if not line.startswith("- "):
            return None, "linia nie jest linią pytania (- rodzaj: … · rozstrzygnął: …)"
        body = " · " + line[2:]
        missing = [name for name in QUESTION_FIELDS if f" · {name}: " not in body]
        if missing:
            return None, f"brak pola `{missing[0]}`"
        return None, "zła kolejność pól (" + ", ".join(QUESTION_FIELDS) + ")"
    item = dict(zip(QUESTION_KEYS, (value.strip() for value in match.groups())))
    if not all(item.values()):
        return None, "puste pole"
    if item["kind"] not in KINDS:
        return None, f"nieznany rodzaj `{item['kind']}`"
    if item["by"] not in DECIDERS:
        return None, f"`rozstrzygnął` to `{item['by']}`, a nie `człowiek`, `agent` albo `obserwator`"
    if item["choice"] != AGREED and not OTHER_CHOICE.match(item["choice"]):
        return None, f"`wybór` to `{item['choice']}`, a nie `rekomendacja` albo `inny: <tekst>`"
    if item["by"] in AUTOMATIC and item["choice"] != AGREED:
        return None, f"`rozstrzygnął: {item['by']}` z wyborem innym niż `rekomendacja`"
    item["agreed"] = item["choice"] == AGREED
    return item, None


def _parse_questions(lines, first=1):
    items, errors = [], []
    for n, line in _numbered(lines, first):
        if not line.strip():
            continue
        item, error = _question(line)
        if error:
            errors.append((n, error))
        else:
            items.append(item)
    return items, errors


def parse_questions(lines, first=1):
    """Lines of the `## Pytania do człowieka` section → [{kind, step, question, recommendation,
    choice, by, agreed}]; lines[0] has number `first`. Code blocks and blank lines are skipped;
    any other line of a wrong shape raises QuestionError with its line number."""
    items, errors = _parse_questions(lines, first)
    if errors:
        raise QuestionError(errors)
    return items


def _parse_undo(lines, first=1):
    kinds, errors = [], []
    for n, line in _numbered(lines, first):
        if UNDO_TOP.match(line):
            errors.append((n, "podpunkt `Cofnięcie:` bez wcięcia: ma być podpunktem wpisu `I-N`"))
            continue
        match = UNDO.match(line)
        if not match:
            continue
        kind, sep, reason = match.group(1).partition(" — ")
        kind = kind.strip()
        if not sep or not reason.strip():
            errors.append((n, "podpunkt `Cofnięcie:` bez ` — <powód>`"))
        elif kind not in KINDS:
            errors.append((n, f"podpunkt `Cofnięcie:` z nieznanym rodzajem `{kind}`"))
        else:
            kinds.append(kind)
    return kinds, errors


def parse_undo(lines, first=1):
    """Lines of the `## Interwencje` section → kinds of its `  - **Cofnięcie:** <rodzaj> — <powód>`
    sub-points, in order; a sub-point without a reason or with an unknown kind raises
    QuestionError."""
    kinds, errors = _parse_undo(lines, first)
    if errors:
        raise QuestionError(errors)
    return kinds


def _raw_section(text, heading):
    """(number of its first line, raw lines) of the `## <heading>` section outside code blocks;
    None when absent."""
    found = section_lines(text, heading)
    if found is None:
        return None
    raw = text.splitlines()
    return found[0] + 1, [raw[n - 1] for n, _ in found[1]]


def read_questions(text):
    """(questions or None without the section, undo kinds, [(line number, message)])."""
    errors = []
    questions = None
    found = _raw_section(text, QUESTIONS)
    if found is not None:
        questions, errs = _parse_questions(found[1], found[0])
        errors += errs
    undo = []
    found = _raw_section(text, "Interwencje")
    if found is not None:
        undo, errs = _parse_undo(found[1], found[0])
        errors += errs
    return questions, undo, sorted(errors)


def _cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _number(cell):
    """The number of a table cell; None for `—`, an empty cell or anything that is not a number."""
    try:
        return float(cell)
    except ValueError:
        return None


def cost_rows(lines, errors=None):
    """[{step, seconds, cost}] of the first table in lines whose header has the columns Krok, Czas (s) and
    Koszt USD; [] without one. A row with another number of cells than the header is left out and named in
    `errors` (when given), so the sum is never short without a word."""
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        header = _cells(line)
        if not all(name in header for name in COST_COLUMNS):
            continue
        step, seconds, cost = (header.index(name) for name in COST_COLUMNS)
        rows = []
        for row in lines[i + 2:]:
            if not row.startswith("|"):
                break
            cells = _cells(row)
            if len(cells) == len(header):
                rows.append({"step": cells[step], "seconds": _number(cells[seconds]), "cost": _number(cells[cost])})
            elif errors is not None:
                errors.append(f"wiersz z {len(cells)} komórkami zamiast {len(header)}, pominięty w sumie: {row}")
        return rows
    return []


def read_costs(folder, cid, repo=None, errors=None):
    """The cost rows of a change: koszty-krokow.md next to its change.md, then `## Koszty kroków` of
    context/przebiegi/<cid>.md in repo; None when neither has a row. Bad rows go to `errors` as
    `<file>: …`."""
    rows = []
    path = os.path.join(folder, COSTS_FILE)
    run = os.path.join(repo, RUNS, f"{cid}.md") if repo else None
    for source, lines in ((path, lambda: unfenced(_read(path))),
                          (run, lambda: section(_read(run), COSTS_SECTION) or [])):
        if source and os.path.isfile(source):
            found = []
            rows += cost_rows(lines(), found)
            name = os.path.relpath(source, repo) if repo else source
            if errors is not None:
                errors += [f"{name}: {e}" for e in found]
    return rows or None


def read_change(folder, repo=None, archived=True):
    """The traces of one change folder; an archived one needs `archived_at` YYYY-MM-DDTHH:MM:SSZ."""
    path = os.path.join(folder, "change.md")
    text = _read(path)
    meta = frontmatter(text)
    if archived and not ARCHIVED_AT.match(meta.get("archived_at", "")):
        raise UsageError(f"{os.path.basename(folder)}: archived_at is not YYYY-MM-DDTHH:MM:SSZ: "
                         f"{meta.get('archived_at', '(missing)')!r}")
    rel = os.path.relpath(path, repo) if repo else path
    questions, undo, q_errors = read_questions(text)
    reviews = os.path.join(folder, "reviews")
    names = [n for n in (os.listdir(reviews) if os.path.isdir(reviews) else [])
             if REPORT_FILE.match(n) and os.path.isfile(os.path.join(reviews, n))]
    kinds = [REPORT_FILE.match(n).group(1) for n in names]
    cid = meta.get("change_id") or os.path.basename(folder)
    cost_errors = []
    retro = os.path.join(folder, "retro.md")
    proposals, proposal_errors = read_proposals(retro, os.path.relpath(retro, repo) if repo else retro)
    return {"id": cid,
            "proposals": proposals,
            "proposal_errors": proposal_errors,
            "fixes": section(text, FIXES) or [],
            "folder": folder,
            "archived_at": meta.get("archived_at") if archived else None,
            "costs": read_costs(folder, cid, repo, cost_errors),
            "cost_errors": cost_errors,
            "plan_rounds": kinds.count("plan"),
            "impl_rounds": kinds.count("impl"),
            "questions": questions,
            "undo": undo,
            "question_errors": [f"{rel}:{n}: {msg}" for n, msg in q_errors]}


def read_proposals(path, rel):
    """([{n, title, column, direction, no}], [`<rel>:<line>: …`]) of the proposals `#### P<n>. <tytuł>` in
    `## Propozycje` of a retro.md whose `Co ma się zmienić` has a number column and a direction; `no` is
    `Rekomendacja: nie`. A field with `; kierunek: w…` that does not match is an error; any other is skipped."""
    found = section_lines(_read(path), PROPOSALS) if os.path.isfile(path) else None
    proposals, errors, current = [], [], None
    for n, line in (found[1] if found else []):
        head = PROPOSAL.match(line)
        if head or line.startswith("###"):
            current = {"n": int(head.group(1)), "title": head.group(2), "column": None, "no": False} if head else None
            if head:
                proposals.append(current)
            continue
        field = PROPOSAL_FIELD.match(line)
        if current is None or not field:
            continue
        value = field.group(2).strip()
        if field.group(1) == "Rekomendacja":
            current["no"] = re.match(r"nie\b", value) is not None
            continue
        match = FIELD.match(value)
        if match and match.group("column") in NUMBER_KEYS:
            current["column"], current["direction"] = match.group("column"), match.group("direction")
        elif FIELD_MARK.search(value):
            errors.append(f"{rel}:{n}: " + (f"nieznana kolumna `{match.group('column')}`" if match else
                                            "pole nie ma kształtu `<kolumna> (<change-id>: <wartość>); kierunek: …`")
                          + " (kolumny `## Liczby zmian`: " + ", ".join(NUMBER_KEYS) + ")")
    return [p for p in proposals if p["column"]], errors


def read_archive(repo, required=True):
    """The archived changes in archived_at order; without context/archive/ or a change in it UsageError, or []
    when not `required` (a repo with start.md)."""
    archive = os.path.join(repo, "context", "archive")
    if not os.path.isdir(archive):
        if not required:
            return []
        raise UsageError(f"no archive: {archive}")
    folders = [os.path.join(archive, n) for n in sorted(os.listdir(archive))
               if os.path.isfile(os.path.join(archive, n, "change.md"))]
    if not folders and required:
        raise UsageError(f"no change in {archive}")
    changes = [read_change(f, repo) for f in folders]
    changes.sort(key=lambda c: (c["archived_at"], c["id"]))
    return changes


def read_start(repo):
    """The traces of context/foundation/start.md (questions or None, undo kinds, cost rows, errors); None
    without the file."""
    path = os.path.join(repo, START_FILE)
    if not os.path.isfile(path):
        return None
    text = _read(path)
    questions, undo, q_errors = read_questions(text)
    found = []
    costs = cost_rows(section(text, COSTS_SECTION) or [], found)
    return {"questions": questions, "undo": undo, "costs": costs,
            "question_errors": [f"{START_FILE}:{n}: {msg}" for n, msg in q_errors],
            "cost_errors": [f"{START_FILE}: {e}" for e in found]}


def read_open(repo, cid):
    """The change in context/changes/<cid>/, before the archive; UsageError without its change.md."""
    folder = os.path.join(repo, "context", "changes", cid)
    if not CHANGE_ID.match(cid) or not os.path.isfile(os.path.join(folder, "change.md")):
        raise UsageError(f"no change {cid!r} in context/changes/ or context/archive/")
    return read_change(folder, repo, archived=False)


def git_log(repo):
    """([(short sha, committer time in s, subject)] oldest first, None) of one `git log` in repo (never a
    folder above it); (None, the message of git) when git fails."""
    repo = os.path.abspath(repo)
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=os.path.dirname(repo))
    try:
        done = subprocess.run(["git", "-C", repo, "log", "--reverse", "--format=%h%x1f%ct%x1f%s", "HEAD"],
                              capture_output=True, encoding="utf-8", errors="replace", env=env,
                              stdin=subprocess.DEVNULL)
    except OSError as exc:
        return None, str(exc)
    if done.returncode != 0:
        return None, (done.stderr.strip().splitlines() or [f"git log: kod {done.returncode}"])[0]
    commits = []
    for line in done.stdout.splitlines():
        sha, ct, subject = line.split("\x1f", 2)
        commits.append((sha, int(ct), subject))
    return commits, None


# ------------------------------------------------------------------ numbers

def _total(values):
    known = [v for v in values if v is not None]
    return sum(known) if known else None


def overhead(costs):
    """Per cent of the cost of the rows whose step is not `implement` in the cost of all rows, unrounded; None
    without a known cost or with a sum of 0."""
    total = _total(c["cost"] for c in costs)
    if not total:
        return None
    return 100 * (_total(c["cost"] for c in costs if c["step"] != IMPLEMENT_STEP) or 0) / total


def change_row(change, subjects, label=None):
    """The numbers of one change, unrounded, or None for „brak danych”."""
    costs = change["costs"] or []
    seconds = _total(c["seconds"] for c in costs)
    usd = _total(c["cost"] for c in costs)
    minutes = None if seconds is None else seconds / 60
    questions = change["questions"]
    decisions = None if questions is None else sum(
        1 for q in questions if q["by"] == HUMAN and q["step"] != INTENT_STEP)
    mark = f"(błąd po {change['id']})"
    bugs = None if subjects is None else sum(1 for s in subjects if mark in s)
    label = label or change["id"]
    if not change.get("archived_at") and costs and not any(c["step"] == ARCHIVE_STEP for c in costs):
        label += f" {NO_ARCHIVE_STEP}"
    return {"id": change["id"], "label": label, "minutes": minutes, "cost": usd,
            "decisions": decisions, "plan_rounds": change["plan_rounds"], "impl_rounds": change["impl_rounds"],
            "bugs": bugs, "undo": len(change["undo"]), "overhead": overhead(costs)}


def interventions(questions):
    """Lines of the human and the observer outside the steps of NOT_INTERVENTIONS; None without the section."""
    return None if questions is None else sum(
        1 for q in questions if q["by"] in INTERVENERS and q["step"] not in NOT_INTERVENTIONS)


def version_row(start, changes, rows, subjects):
    """The numbers of the version: start.md and the changes of the table, unrounded, or None for „brak danych”."""
    counts = [n for n in [interventions(start["questions"])] + [interventions(c["questions"]) for c in changes]
              if n is not None]
    found = sum(counts) if counts else None
    bugs = None if subjects is None else sum(r["bugs"] for r in rows)
    undo = len(start["undo"]) + sum(r["undo"] for r in rows)
    costs = list(start["costs"]) + [c for change in changes for c in (change["costs"] or [])]
    if (found is not None and found > MAX_INTERVENTIONS) or (bugs is not None and bugs > 0) or undo > 0:
        in_goal = False
    elif found is not None and bugs is not None:
        in_goal = True
    else:
        in_goal = None
    return {"changes": len(rows), "interventions": found, "bugs": bugs, "undo": undo, "overhead": overhead(costs),
            "in_goal": in_goal}


def _anchor(prefix, pid, n):
    """`<prefix><id> P<n>` with a boundary before the id and after the number (`alfa P1` is not `alfa-b P1`
    nor `alfa P12`)."""
    return re.compile(prefix + r"(?<![A-Za-z0-9-])" + re.escape(pid) + rf" P{n}(?![0-9])", re.M)


def _seconds(archived_at):
    return datetime.strptime(archived_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def _mean(rows, key):
    values = [r[key] for r in rows if r[key] is not None]
    return sum(values) / len(values) if values else None


def _judge(before, after, key, direction):
    """`szkodzi`, `działa` or None (no decision) for the changes after against the changes before."""
    b, a = _mean(before, key), _mean(after, key)
    if a is None or b is None:
        return None
    higher = any(None not in (_mean(after, k), _mean(before, k)) and _mean(after, k) > _mean(before, k)
                 for k in ("bugs", "undo"))
    if higher or (a > b if direction == DOWN else a < b):
        return "szkodzi"
    return "działa" if (a < b if direction == DOWN else a > b) else None


def verdict(before, after, key, direction):
    if len(after) < WINDOW or _mean(before, key) is None:
        return "czeka"
    for k in range(WINDOW, len(after) + 1):
        found = _judge(before, after[:k], key, direction)
        if found == "działa" and _judge(before, after[-WINDOW:], key, direction) != "działa":
            return "wróciło"
        if found:
            return found
    return "bez skutku" if len(after) >= NO_EFFECT_AFTER else "czeka"


def verdict_rows(changes, rows, commits, decisions):
    """The rows of `## Werdykty poprawek` for the proposals of the archived changes."""
    first = {}
    for _, ct, subject in commits:
        for cid in CID_IN_SUBJECT.findall(subject):
            first[cid] = min(first.get(cid, ct), ct)
    archived = [(c, r, _seconds(c["archived_at"])) for c, r in zip(changes, rows) if c["archived_at"]]
    out = []
    for change, _, at in archived:
        pid = change["id"]
        for p in change["proposals"]:
            n, mark = p["n"], f"(retro {pid} P{p['n']})"
            removal = REMOVAL.match(p["title"])
            if (p["no"] or _anchor(r"^#+ .*Odrzucona propozycja ", pid, n).search(decisions)
                    or any(s.startswith('Revert "') and mark in s for _, _, s in commits)
                    or (removal and _anchor("zostaw ", removal.group(1), removal.group(2)).search(decisions))):
                continue
            found = [i for i, (_, _, s) in enumerate(commits) if mark in s and not s.startswith('Revert "')]
            for other in changes:
                if other["archived_at"] and any(_anchor("", pid, n).search(line) for line in other["fixes"]):
                    close = re.compile(r"^chore\(archive\): close " + re.escape(other["id"]) + r"(?: \(#\d+\))?$")
                    found += [i for i, (_, _, s) in enumerate(commits) if close.match(s)]
            key = NUMBER_KEYS[p["column"]]
            before, after, sha = [], [], "brak"
            if found:
                sha, ct, _ = commits[min(found, key=lambda i: (commits[i][1], i))]
                before = [r for c, r, t in archived if t < ct][-WINDOW:]
                after = [r for c, r in zip(changes, rows) if first.get(c["id"], ct) > ct]
                judged = verdict(before, after, key, p["direction"])
            else:
                judged = "nie weszła" if any(t > at for _, _, t in archived) else "czeka"
            out.append({"fix": f"{pid} P{n}", "column": p["column"], "direction": p["direction"], "commit": sha,
                        "before": _mean(before, key), "after": _mean(after, key), "count": len(after),
                        "verdict": judged})
    return out


def outside_fixes(commits, ids):
    """[short sha] of the `fix(<scope>)` commits whose scope is no change id and that are no retro fix."""
    ids = {i.lower() for i in ids}
    return [sha for sha, _, s in commits
            if (m := FIX_SUBJECT.match(s)) and m.group(1).lower() not in ids and "(retro " not in s]


def change_ids(repo, changes):
    folder = os.path.join(repo, "context", "changes")
    names = os.listdir(folder) if os.path.isdir(folder) else []
    return {c["id"] for c in changes} | {n for n in names if os.path.isdir(os.path.join(folder, n))}


def _whole(value):
    """Half up to a whole number."""
    return math.floor(value + 0.5)


def _int(value):
    return NO_DATA if value is None else str(_whole(value))


def _pct(value):
    return NO_DATA if value is None else f"{_whole(value)}%"


def _usd(value):
    return NO_DATA if value is None else f"{value:.2f}"


def _yes(value):
    return NO_DATA if value is None else ("tak" if value else "nie")


def render_row(row):
    cells = (row["label"], _int(row["minutes"]), _usd(row["cost"]), _int(row["decisions"]),
             str(row["plan_rounds"]), str(row["impl_rounds"]), _int(row["bugs"]), str(row["undo"]),
             _pct(row["overhead"]))
    return "| " + " | ".join(cells) + " |"


def render_version(version):
    cells = (str(version["changes"]), _int(version["interventions"]), _int(version["bugs"]), str(version["undo"]),
             _pct(version["overhead"]), _yes(version["in_goal"]))
    return ["", f"## {VERSION}", "", VERSION_HEADER, "|" + "---|" * len(VERSION_COLUMNS), "| " + " | ".join(cells) + " |"]


def _avg(value):
    return NO_DATA if value is None else f"{value:.2f}"


def render(rows, verdicts, git_error, fixes=None, version=None):
    out = ["# Pomiar zmian", "", f"- Data: {date.today().isoformat()}", "",
           f"## {CHANGES}", "", CHANGES_HEADER, "|" + "---|" * len(CHANGES_COLUMNS)]
    out += [render_row(r) for r in rows]
    out += ["", f"{OUTSIDE_FIXES}: " + (NO_DATA if fixes is None else
                                         f"{len(fixes)}" + (f" ({', '.join(fixes)})" if fixes else ""))]
    if version is not None:
        out += render_version(version)
    out += ["", f"## {VERDICTS}", ""]
    if git_error is not None:
        out.append(f"Brak danych: {git_error}")
    elif not verdicts:
        out.append("Brak.")
    else:
        out += [VERDICTS_HEADER, "|" + "---|" * len(VERDICTS_COLUMNS)]
        out += ["| " + " | ".join((v["fix"], v["column"], v["direction"], v["commit"], _avg(v["before"]),
                                   _avg(v["after"]), str(v["count"]), v["verdict"])) + " |" for v in verdicts]
    return "\n".join(out) + "\n"


def parse_args(argv):
    """(repo, change-id or None); UsageError on anything else."""
    options, args = {}, list(argv)
    while args:
        flag = args.pop(0)
        if flag not in ("--repo", "--zmiana") or flag in options or not args:
            raise UsageError(f"bad usage: {' '.join(argv)}; {USAGE}")
        options[flag] = args.pop(0)
    return options.get("--repo", REPO), options.get("--zmiana")


def main(argv):
    try:
        repo, cid = parse_args(argv)
        start = read_start(repo)
        changes = read_archive(repo, required=start is None)
        labels = [None] * len(changes)
        if cid is not None and cid not in {c["id"] for c in changes}:
            changes.append(read_open(repo, cid))
            labels.append(f"{cid} {BEFORE_ARCHIVE}")
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    commits, git_error = git_log(repo)
    subjects = None if commits is None else [s for _, _, s in commits]
    rows = [change_row(c, subjects, label) for c, label in zip(changes, labels)]
    decisions = os.path.join(repo, DECISIONS_FILE)
    verdicts = [] if commits is None else verdict_rows(
        changes, rows, commits, _read(decisions) if os.path.isfile(decisions) else "")
    fixes = None if commits is None else outside_fixes(commits, change_ids(repo, changes))
    version = None if start is None else version_row(start, changes, rows, subjects)
    sys.stdout.write(render(rows, verdicts, git_error, fixes, version))
    sources = ([start] if start is not None else []) + changes
    problems = ([f"BŁĄD PYTANIA: {e}" for c in sources for e in c["question_errors"]]
                + [f"BŁĄD KOSZTÓW: {e}" for c in sources for e in c["cost_errors"]]
                + [f"BŁĄD POPRAWKI: {e}" for c in changes for e in c["proposal_errors"]])
    if problems:
        sys.stdout.write("\n" + "\n".join(problems) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
