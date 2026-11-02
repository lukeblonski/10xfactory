#!/usr/bin/env python3
"""Numbers of etap 9 (docs/spec.md) from the closed changes in context/archive/.

Usage: python3 scripts/pomiar.py [--repo DIR]

Reads every context/archive/*/change.md (change_id, archived_at), its
`## Decyzje triage` (DT) and the review reports reviews/plan-review*.md and
reviews/impl-review*.md, and prints Markdown on stdout: a header with the date
and the factory commit, one table row per change in archived_at order, then
`## Liczby`, `## Sygnały polityki triage'u`, `## Pytania do człowieka` and
`## Czas i koszt kroków`.
Only reads; standard library.

Rules (plan of etap-9-pomiar, "Decyzje planu"):
- round: one report file; its number is the file number (plan-review.md is 1,
  plan-review-2.md is 2); the last round of a kind has the highest number;
- fixed finding: Decision `AUTO-FIX`/`FIXED` in its `### F<n>` block, or a DT
  line for that report and F<n> with `· commit <sha>`; DT subsections
  `### <path> (runda N)` match a report by the file name of <path>;
- E1: a change without any fixed finding; next to it whether the last plan
  round and the last code round have none;
- E3: rounds with at least one fixed finding;
- E2 stops: the (report, F<n>) pairs whose DT line contains AUTO-ESCALATE
  anywhere, minus the pairs in `Uwagi:` of an approach question line whose
  `Rozstrzyga:` starts with `recenzent i autor`; an executor STOP in `I-n`
  does not count;
- E2 reversals and E7 (signal 1): DT lines with `(było: AUTO-FIX …)` or
  `(było: AUTO-LIMIT …)` that contain `człowiek`, or with
  „zastąpione przez I-<n>”; `AUTO-ESCALATE` is a question, not a reversal;
- E8 (signal 2): a stop is accepted unchanged when its final decision (the
  first of the report Decision and the DT decision that is not AUTO-ESCALATE)
  picks the recommended option and says neither „differently”, „inaczej” nor
  „zamiast”. The recommendation comes from `⭐ Recommended` in the report,
  `Recenzent: X` of the approach question, „zamiast rekomendowanego X”, or the
  report's single `Fix` (then FIXED accepts it). The human's own words in a
  `## Interwencje` entry „manual triage of …” (its main line and „Dlaczego”)
  decide first: „według rekomendacji”, „zgodnie z rekomendacją”, „rekomendowaną
  opcję” accept the findings of the clause, the same with „wszystkie” every
  finding of the entry, „zamiast rekomendowanego” rejects the first finding of
  the clause. A final decision with a reject word is „nie” even without a
  recommendation; a finding joined „razem z F<m>” takes F<m>'s verdict. Any
  other stop is „brak danych” and leaves the denominator;
- E10 (signal 4): a finding of round >= 2 whose first `Detail` sentence names
  F<n> of an earlier round (by report name, „rundy N”, „round-N” or „the
  previous report”) with a word from REGRESSION_WORDS; each fix pointed at
  counts once. Before etap-4a a round >= 2 finding without such a link makes
  the change „brak danych”.
A change without the trace a number needs (no review report for E1, E3, E10;
no DT for E2, E7, E8) prints „brak danych” and leaves the denominator (E11).

Questions to the human (plan of retro-upgrade-c, phase 2; line format in
docs/zasady-budowy.md, point 6):
- `## Pytania do człowieka` of change.md holds one line per question,
  `- rodzaj: <r> · krok: <k> · pytanie: <p> · rekomendacja: <t> · wybór:
  rekomendacja|inny: <t> · rozstrzygnął: człowiek|agent|obserwator`, fields in
  this order (parse_questions); code blocks and blank lines are skipped. A bad
  line is any other line, a missing field, a wrong order, a kind outside
  KINDS, `rozstrzygnął` outside człowiek|agent|obserwator, or `agent` or
  `obserwator` with a choice other than `rekomendacja`; `obserwator` is a
  decision of the laboratory's observer, counted apart from the human and the
  agent;
- an undo is a `  - **Cofnięcie:** <rodzaj> — <powód>` sub-point of an `I-N`
  entry in `## Interwencje` (parse_undo); an unknown kind, no reason or a
  sub-point without indentation is a bad line;
- agreement: `wybór: rekomendacja` among the questions decided by the human;
  the column „Pytania (zgodne z rekomendacją)” is `<agreed>/<decided by the
  human>`, followed by ` · obserwator: <n>` when the observer decided any,
  „brak danych” for a change without the section, which leaves the
  denominator of `## Pytania do człowieka` (one row per kind: decided by the
  human, agreed, changes with such a question, decided by the agent, decided
  by the observer, undos);
- signals 1 and 2 stay as they are: they are the only source for changes
  archived before the questions section existed (D-122).
Bad question or undo lines print `BŁĄD PYTANIA: <file>:<line>: …` after the
full output.

Ratings (D-121) come from context/foundation/oceny-poprawek.md (when present:
`## Poprawione uwagi` with `### <change-id>` subsections, and `## Ograniczenia`)
and from `## Oceny` of each archived retro.md (`### Poprawione uwagi` of that
change, `### Ograniczenia`), in the line shapes of
skills/retro/references/retro-format.md:
- E4: share of „zmieniła działanie” among the rated fixed findings;
- E5: share of R among the rated limitations of limitations.md and
  decisions-archive.md, without „—”; E9 (signal 3): number of R and N.
A limitation rated in several places takes the strongest rating (R > N > W >
0 > —), a finding „zmieniła działanie” over „tylko tekst lub spójność”.
Required (E6): every fixed finding of a change archived (archived_at) from
etap-5a-drugi-model-pomiar on, and every limitation whose `Źródło` (first token
before „ — ”, without backticks; the label may be bold) is such a change. A
limitation entry without a recognised `Źródło` line is a rating error. A missing rating prints `BRAK OCENY: …`, a line
of a wrong shape, R without effect or `path:line`, a rating of something that
is not a fixed finding or not in the register prints `BŁĄD OCENY: <file>:<line>:
…`; both go to stdout after the full output.

Time and cost of the steps (plan of przebudowa-autopilota, phase 3, P24): the
last section, `## Czas i koszt kroków`, reads for every archived change the
costs table the autopilot writes (scripts/autopilot.py, P23):
koszty-krokow.md next to its change.md (the steps before the archive) and the
section `## Koszty kroków` of context/przebiegi/<change_id>.md in --repo (the
archiwum step). A change with at least one row gets `### <change_id>` and the
table `| Krok | Czas (s) | Koszt USD |` with one row per session of a step and
the row `| Suma | … | … |` (the sum of the known values; `—` for a value
missing in the record and for a sum without any value); every change without
a row is one line `- <change_id>: brak danych`, before the tables. A row of
such a table with another number of cells than its header is left out of the
sum and prints `BŁĄD KOSZTÓW: <file>: …` after the full output.

Exit codes: 0 OK; 1 a rating missing or wrong, a bad question or undo line,
or a bad cost row; 2 no context/archive/ or no
change in it, a change without `archived_at` of the form YYYY-MM-DDTHH:MM:SSZ,
or a report without findings section.
"""

import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from evallib import NO_DATA, UsageError, _commit, report_findings  # noqa: E402
except ModuleNotFoundError as exc:
    # The exported package has no scripts/evallib.py; autopilot.py imports this module for
    # parse_questions and section_lines only, so the measurement report itself stays a laboratory tool.
    if exc.name != "evallib":
        raise
    NO_DATA = "brak danych"

    class UsageError(Exception):
        """Missing or unreadable input: the command exits 2."""

    def _commit():
        raise UsageError("the measurement report needs scripts/evallib.py of the laboratory")

    def report_findings(report_text):
        raise UsageError("the measurement report needs scripts/evallib.py of the laboratory")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E10_FROM = "etap-4a-intencja-zmiany"
RATINGS_FROM = "etap-5a-drugi-model-pomiar"
BACKFILL = "context/foundation/oceny-poprawek.md"
REGISTRY = ("context/foundation/limitations.md", "context/foundation/decisions-archive.md")
CHANGED = "zmieniła działanie"
TEXT_ONLY = "tylko tekst lub spójność"
STRENGTH = ("—", "0", "W", "N", "R")
REGRESSION_WORDS = ("regresja", "regresji", "regresję", "regression",
                    "nowa postać", "nową postać", "nowa forma", "nową formę", "new form")
REJECT_WORDS = ("differently", "inaczej", "zamiast")

REPORT_FILE = re.compile(r"^(plan|impl)-review(?:-(\d+))?\.md$")
FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^## ")
FINDING_BLOCK = re.compile(r"^\s*### (F\d+)\b")
ANY_HEADING = re.compile(r"^\s*#{2,3}\s")
FIELD = re.compile(r"^\s*- \*\*([^*]+)\*\*:?\s?(.*)$")
RECOMMENDED = re.compile(r"^\s*- \*\*Fix ([A-Z])\b[^*]*⭐[^*]*\*\*")
DT_SUBSECTION = re.compile(r"^### (\S+)")
DT_FINDING = re.compile(r"^- (F\d+)\b")
DT_APPROACH = re.compile(r"^- Pytanie o podejście\b")
UWAGI = re.compile(r"· Uwagi:([^·]*)")
ROZSTRZYGA = re.compile(r"· Rozstrzyga:\s*([^·]*)")
RECENZENT = re.compile(r"· Recenzent:\s*([A-Z])\b")
F_ID = re.compile(r"\bF(\d+)\b")
COMMIT = re.compile(r"· commit [0-9a-f]{7,}")
FIXED_DECISION = re.compile(r"^(AUTO-FIX|FIXED)\b")
REVERSAL_MARK = re.compile(r"\(było: AUTO-(FIX|LIMIT)\b")
REPLACED = re.compile(r"zastąpione przez I-\d+")
CHOSEN = re.compile(r"\b(?:Fix|opcj[aię]|via|wariant|podejście)\s+([A-Z])\b")
HUMAN_CHOICE = re.compile(r"· Rozstrzyga:\s*człowiek\s*\(([A-Z])\)")
INSTEAD = re.compile(r"zamiast rekomendowanego\s+(?:Fix\s+)?([A-Z])\b")
INSTEAD_LOOSE = re.compile(r"zamiast rekomendowan", re.IGNORECASE)
JOINED = re.compile(r"razem z F(\d+)")
MANUAL_REPORT = re.compile(r"(?:plan|impl)-review(?:-\d+)?\.md")
INTERVENTION_REF = re.compile(r"(?:\b((?:plan|impl)-review(?:-\d+)?)\s+)?\bF(\d+)\b")
ACCEPTED_SOME = re.compile(r"według rekomendacji|zgodnie z rekomendacj|rekomendowan[aą] opcj", re.IGNORECASE)
ACCEPTED_ALL = re.compile(r"wszystk\w*[^.;]*rekomend|rekomend\w*[^.;]*wszystk|wybrał\w* rekomendacje",
                          re.IGNORECASE)
# A reference to an earlier round in the first sentence of Detail.
REPORT_REF = re.compile(r"\b(plan|impl)-review(?:-(\d+))?(?:\.md)?\b")
ROUND_REF = re.compile(r"\b(?:rundy|runda|round)[ -](\d+)\b", re.IGNORECASE)
PREVIOUS_REF = re.compile(r"poprzedni(?:ego|ej) (?:raportu|rundy)|previous report|poprzedniego\b",
                          re.IGNORECASE)
SENTENCE_END = re.compile(r"[.!?](?:\s|$)")
# Ratings (skills/retro/references/retro-format.md, `## Oceny`).
H3 = re.compile(r"^### (.+?)\s*$")
FINDING_RATING = re.compile(r"^- ((?:plan|impl)-review(?:-\d+)?) (F\d+): "
                            r"(zmieniła działanie|tylko tekst lub spójność) — (\S.*)$")
LIMIT_RATING = re.compile(r"^- (D-\d+): (R|N|W|0|—)(?: \(([a-d](?:\+[a-d])*)\))? — (\S.*?)"
                          r"(?: — `([^`\s]+):(\d+)`)?$")
LIMIT_ENTRY = re.compile(r"^## (D-\d+) Ograniczenie:")
SOURCE_FIELD = re.compile(r"^- (?:\*\*Źródło\*\*|Źródło):\s*(.*)$")
ARCHIVED_AT = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
# Questions to the human (docs/zasady-budowy.md, point 6, „Pytania do człowieka”).
QUESTIONS = "Pytania do człowieka"
KINDS = ("spór recenzenta z autorem", "eskalacja", "płatny przebieg", "zakres", "kryterium", "inne")
QUESTION_FIELDS = ("rodzaj", "krok", "pytanie", "rekomendacja", "wybór", "rozstrzygnął")
QUESTION_KEYS = ("kind", "step", "question", "recommendation", "choice", "by")
QUESTION_LINE = re.compile("^- " + " · ".join(f"{name}: (.+?)" for name in QUESTION_FIELDS) + "$")
DECIDERS = ("człowiek", "agent", "obserwator")
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
STEP_COSTS = "Czas i koszt kroków"
COST_COLUMNS = ("Krok", "Czas (s)", "Koszt USD")
NO_VALUE = "—"


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


def parse_report(name, text):
    """Report dict: name, kind, number, findings [{id, title, decision, detail, recommended}]."""
    match = REPORT_FILE.match(name)
    try:
        listed = report_findings(text)
    except UsageError as exc:
        raise UsageError(f"{name}: {exc}") from None
    blocks, current, field = {}, None, None
    for line in unfenced(text):
        heading = FINDING_BLOCK.match(line)
        if heading:
            current = blocks.setdefault(heading.group(1), {"decision": None, "detail": None,
                                                           "recommended": None, "fixes": []})
            field = None
            continue
        if ANY_HEADING.match(line):
            current, field = None, None
            continue
        if current is None:
            continue
        recommended = RECOMMENDED.match(line)
        if recommended and current["recommended"] is None:
            current["recommended"] = recommended.group(1)
        found = FIELD.match(line)
        if found and not line.startswith(" "):
            key, value = found.group(1).strip(), found.group(2).strip()
            field = None
            if key == "Fix" or key.startswith("Fix "):
                current["fixes"].append(key)
            if key == "Decision" and current["decision"] is None:
                current["decision"] = value
            elif key == "Detail" and current["detail"] is None:
                current["detail"] = value
                field = "detail" if not value else None
            continue
        if field == "detail" and line.strip():
            current["detail"] = (current["detail"] + " " + line.strip().lstrip("-* ")).strip()
    findings = []
    for item in listed:
        block = blocks.get(item["id"], {})
        findings.append({"id": item["id"], "title": item["title"],
                         "decision": block.get("decision") or "",
                         "detail": block.get("detail") or "",
                         "recommended": block.get("recommended"),
                         "single_fix": block.get("fixes") == ["Fix"]})
    return {"name": name, "kind": match.group(1), "number": int(match.group(2) or 1),
            "findings": findings}


def parse_dt(lines):
    """DT section lines → {report file name: {"findings": {F<n>: line}, "approach": [lines]}}."""
    dt, current = {}, None
    for line in lines:
        sub = DT_SUBSECTION.match(line)
        if sub:
            current = dt.setdefault(os.path.basename(sub.group(1)),
                                    {"findings": {}, "approach": []})
            continue
        if current is None:
            continue
        finding = DT_FINDING.match(line)
        if finding:
            current["findings"].setdefault(finding.group(1), line)
        elif DT_APPROACH.match(line):
            current["approach"].append(line)
    return dt


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


def read_change(folder, repo=None):
    path = os.path.join(folder, "change.md")
    text = _read(path)
    meta = frontmatter(text)
    if not ARCHIVED_AT.match(meta.get("archived_at", "")):
        raise UsageError(f"{os.path.basename(folder)}: archived_at is not YYYY-MM-DDTHH:MM:SSZ: "
                         f"{meta.get('archived_at', '(missing)')!r}")
    rel = os.path.relpath(path, repo) if repo else path
    questions, undo, q_errors = read_questions(text)
    reviews = os.path.join(folder, "reviews")
    names = sorted(n for n in (os.listdir(reviews) if os.path.isdir(reviews) else [])
                   if REPORT_FILE.match(n))
    reports = [parse_report(n, _read(os.path.join(reviews, n))) for n in names]
    reports.sort(key=lambda r: (r["kind"] != "plan", r["number"]))
    dt_lines = section(text, "Decyzje triage")
    interventions = section(text, "Interwencje")
    cid = meta.get("change_id") or os.path.basename(folder)
    cost_errors = []
    return {"id": cid,
            "folder": folder,
            "costs": read_costs(folder, cid, repo, cost_errors),
            "cost_errors": cost_errors,
            "archived_at": meta["archived_at"],
            "reports": reports,
            "dt": None if dt_lines is None else parse_dt(dt_lines),
            "interventions": parse_interventions(interventions or []),
            "questions": questions,
            "undo": undo,
            "question_errors": [f"{rel}:{n}: {msg}" for n, msg in q_errors]}


def read_archive(repo):
    archive = os.path.join(repo, "context", "archive")
    if not os.path.isdir(archive):
        raise UsageError(f"no archive: {archive}")
    folders = [os.path.join(archive, n) for n in sorted(os.listdir(archive))
               if os.path.isfile(os.path.join(archive, n, "change.md"))]
    if not folders:
        raise UsageError(f"no change in {archive}")
    changes = [read_change(f, repo) for f in folders]
    changes.sort(key=lambda c: (c["archived_at"], c["id"]))
    return changes


# ------------------------------------------------------------------ rules

def _dt_line(change, report, fid):
    if change["dt"] is None:
        return None
    return change["dt"].get(report["name"], {}).get("findings", {}).get(fid)


def is_fixed(change, report, finding):
    if FIXED_DECISION.match(finding["decision"]):
        return True
    line = _dt_line(change, report, finding["id"])
    return bool(line and COMMIT.search(line))


def fixed_rounds(change):
    """{report name: number of fixed findings}."""
    return {r["name"]: sum(is_fixed(change, r, f) for f in r["findings"]) for r in change["reports"]}


def _last_clean(change, kind, fixed):
    rounds = [r for r in change["reports"] if r["kind"] == kind]
    if not rounds:
        return None
    return fixed[rounds[-1]["name"]] == 0


def _approach_pairs(dt, settled_by_pair):
    """Pairs (report, F<n>) of approach question lines; settled_by_pair filters on Rozstrzyga."""
    pairs = set()
    for name, sub in dt.items():
        for line in sub["approach"]:
            uwagi = UWAGI.search(line)
            who = ROZSTRZYGA.search(line)
            if not uwagi or not settled_by_pair(who.group(1).strip() if who else ""):
                continue
            pairs |= {(name, "F" + n) for n in F_ID.findall(uwagi.group(1))}
    return pairs


def stops(change):
    """Sorted (report, F<n>) pairs that went to the human; None without DT."""
    dt = change["dt"]
    if dt is None:
        return None
    escalated = {(name, fid) for name, sub in dt.items()
                 for fid, line in sub["findings"].items() if "AUTO-ESCALATE" in line}
    settled = _approach_pairs(dt, lambda who: who.startswith("recenzent i autor"))
    return sorted(escalated - settled)


def reversals(change):
    """Sorted (report, F<n>) pairs of automatic decisions the human changed; None without DT."""
    dt = change["dt"]
    if dt is None:
        return None
    out = []
    for name, sub in dt.items():
        for fid, line in sub["findings"].items():
            if (REVERSAL_MARK.search(line) and "człowiek" in line) or REPLACED.search(line):
                out.append((name, fid))
    return sorted(out)


def _decision_part(line):
    """The decision of a DT finding line: the text after `(<…>): `."""
    head, sep, rest = line.partition("): ")
    return rest if sep else line


def _approach_line(change, name, fid):
    for line in change["dt"].get(name, {}).get("approach", []):
        uwagi = UWAGI.search(line)
        if uwagi and fid in ["F" + n for n in F_ID.findall(uwagi.group(1))]:
            return line
    return None


def parse_interventions(lines):
    """Manual-triage entries of `## Interwencje`: [(report names, [clauses of the main line and
    of „Dlaczego”])]; „Bez interwencji fabryka” and „Możliwa reguła” describe other paths."""
    entries, current = [], None
    for line in lines:
        if line.startswith("- **I-"):
            title, _, rest = line[4:].partition("**")
            current = None
            if "manual triage of" in title:
                reports = [m.group(0) for m in MANUAL_REPORT.finditer(title)]
                current = (reports, [rest])
                entries.append(current)
            continue
        if current is not None and line.startswith("  - **Dlaczego:**"):
            current[1].append(line.split("**Dlaczego:**", 1)[1])
        elif not line.startswith(" "):
            current = None
    return [(reports, [c for part in parts for c in re.split(r";|, ", part) if c.strip()])
            for reports, parts in entries]


def intervention_verdicts(change):
    """{(report, F<n>): accepted unchanged per the human's own words in a manual-triage entry}."""
    verdicts = {}
    for reports, clauses in change["interventions"]:
        default = reports[0] if len(reports) == 1 else None
        mentioned, last, globally = [], default, False
        for clause in clauses:
            refs = []
            for m in INTERVENTION_REF.finditer(clause):
                if m.group(1):
                    last = m.group(1) + ".md"
                if last:
                    refs.append((last, "F" + m.group(2)))
            mentioned += refs
            if INSTEAD.search(clause) or INSTEAD_LOOSE.search(clause):
                if refs:
                    verdicts[refs[0]] = False
            elif ACCEPTED_ALL.search(clause):
                globally = True
            elif ACCEPTED_SOME.search(clause):
                for ref in refs:
                    verdicts.setdefault(ref, True)
        if globally:
            for ref in mentioned:
                verdicts.setdefault(ref, True)
    return verdicts


def _recommendation(finding, approach, decisions):
    """The recommended option letter, "Fix" for a report's single fix, or None."""
    if finding and finding["recommended"]:
        return finding["recommended"]
    if approach:
        reviewer = RECENZENT.search(approach)
        if reviewer:
            return reviewer.group(1)
    instead = INSTEAD.search(" ".join(decisions))
    if instead:
        return instead.group(1)
    if finding and finding["single_fix"]:
        return "Fix"
    return None


def escalation(change, name, fid, verdicts=None, seen=()):
    """(recommended option or None, accepted unchanged: bool, or None for „brak danych”)."""
    if verdicts is None:
        verdicts = intervention_verdicts(change)
    report = next((r for r in change["reports"] if r["name"] == name), None)
    finding = next((f for f in report["findings"] if f["id"] == fid), None) if report else None
    dt_line = _decision_part(change["dt"][name]["findings"][fid])
    approach = _approach_line(change, name, fid)
    decisions = [d for d in ((finding or {}).get("decision", ""), dt_line)
                 if d and not d.startswith("AUTO-ESCALATE")]
    final = decisions[0] if decisions else ""
    recommended = _recommendation(finding, approach, decisions)
    if (name, fid) in verdicts:
        return recommended, verdicts[(name, fid)]
    if any(word in final.lower() for word in REJECT_WORDS):
        return recommended, False
    if recommended is None:
        joined = JOINED.search(dt_line) or JOINED.search(final)
        main = "F" + joined.group(1) if joined else None
        if main and main != fid and main not in seen and main in change["dt"][name]["findings"]:
            return escalation(change, name, main, verdicts, seen + (fid,))
        return None, None
    if not final:
        return recommended, None
    if recommended == "Fix":
        return recommended, final.startswith("FIXED")
    human = HUMAN_CHOICE.search(approach) if approach else None
    found = CHOSEN.search(final)
    chosen = human.group(1) if human else (found.group(1) if found else None)
    return recommended, chosen == recommended


def first_sentence(text):
    end = SENTENCE_END.search(text)
    return text[:end.start() + 1] if end else text


def regression_targets(report, finding):
    """[(report name, F<n>)] an earlier round's fixes the finding's first sentence points at
    with a regression word; [] when it points at none, None when it has no link at all."""
    sentence = first_sentence(finding["detail"])
    tokens = []
    for m in REPORT_REF.finditer(sentence):
        tokens.append((m.start(), "report", (m.group(1), int(m.group(2) or 1))))
    for m in ROUND_REF.finditer(sentence):
        tokens.append((m.start(), "report", (report["kind"], int(m.group(1)))))
    for m in PREVIOUS_REF.finditer(sentence):
        tokens.append((m.start(), "report", (report["kind"], report["number"] - 1)))
    refs = sorted(t for t in tokens)
    fids = [(m.start(), "F" + m.group(1)) for m in F_ID.finditer(sentence)]
    earlier = [r for r in refs if r[2][0] == report["kind"] and r[2][1] < report["number"]]
    if not fids or not earlier:
        return None
    lower = sentence.lower()
    if not any(word in lower for word in REGRESSION_WORDS):
        return []
    targets = []
    for pos, fid in fids:
        ref = min(earlier, key=lambda r: abs(r[0] - pos))
        kind, number = ref[2]
        name = f"{kind}-review.md" if number == 1 else f"{kind}-review-{number}.md"
        targets.append((name, fid))
    return targets


def regressions(change, before_e10):
    """Sorted distinct fixes followed by a regression; None when a pre-4a change lacks links."""
    found = set()
    for report in change["reports"]:
        if report["number"] < 2:
            continue
        for finding in report["findings"]:
            targets = regression_targets(report, finding)
            if targets is None and before_e10:
                return None
            found |= set(targets or [])
    return sorted(found)


# ------------------------------------------------------------------ ratings

def subsections(numbered):
    """[(heading or None, heading line number, [(line number, line)])] of `### ` blocks;
    the first item holds the lines before any `### ` heading."""
    out = [(None, None, [])]
    for n, line in numbered:
        heading = H3.match(line)
        if heading:
            out.append((heading.group(1), n, []))
        else:
            out[-1][2].append((n, line))
    return out


def _content(numbered):
    """The lines of a block that are neither blank nor `Brak.`."""
    return [(n, line) for n, line in numbered if line.strip() not in ("", "Brak.")]


def _finding_lines(numbered, cid, rel, found, errors):
    for n, line in _content(numbered):
        match = FINDING_RATING.match(line.rstrip())
        if not match:
            errors.append(f"{rel}:{n}: linia nie pasuje do formatu oceny poprawionej uwagi "
                          f"(- <raport> F<n>: {CHANGED}|{TEXT_ONLY} — <powód>)")
            continue
        found.setdefault((cid, match.group(1), match.group(2)), []).append((match.group(3), rel, n))


def _limit_lines(numbered, rel, found, errors):
    for n, line in _content(numbered):
        match = LIMIT_RATING.match(line.rstrip())
        if not match:
            errors.append(f"{rel}:{n}: linia nie pasuje do formatu oceny ograniczenia "
                          f"(- D-<nnn>: <R|N|W|0|—>[ (<a-d>[+…])] — <powód>[ — `<path>:<line>`])")
        elif match.group(2) == "R" and not (match.group(3) and match.group(5)):
            errors.append(f"{rel}:{n}: ocena R bez skutku (a)–(d) w nawiasie albo bez dowodu `path:line`")
        else:
            found.setdefault(match.group(1), []).append((match.group(2), rel, n))


def _stray(numbered, rel, errors, where):
    for n, _ in _content(numbered):
        errors.append(f"{rel}:{n}: linia poza podsekcją {where}")


def read_backfill(repo, ids, findings, limits, errors):
    path = os.path.join(repo, BACKFILL)
    if not os.path.isfile(path):
        return
    text = _read(path)
    fixed = section_lines(text, "Poprawione uwagi")
    if fixed is None:
        errors.append(f"{BACKFILL}:1: brak sekcji `## Poprawione uwagi`")
    else:
        for heading, n, lines in subsections(fixed[1]):
            if heading is None:
                _stray(lines, BACKFILL, errors, "`### <change-id>`")
            elif heading not in ids:
                errors.append(f"{BACKFILL}:{n}: zmiany {heading} nie ma w archiwum")
            else:
                _finding_lines(lines, heading, BACKFILL, findings, errors)
    limited = section_lines(text, "Ograniczenia")
    if limited is None:
        errors.append(f"{BACKFILL}:1: brak sekcji `## Ograniczenia`")
    else:
        _limit_lines(limited[1], BACKFILL, limits, errors)


def read_retro_ratings(repo, change, findings, limits, errors):
    path = os.path.join(change["folder"], "retro.md")
    if not os.path.isfile(path):
        return
    rel = os.path.relpath(path, repo)
    found = section_lines(_read(path), "Oceny")
    if found is None:
        return
    head, numbered = found
    seen = set()
    for heading, n, lines in subsections(numbered):
        if heading is None:
            _stray(lines, rel, errors, "`### Poprawione uwagi` albo `### Ograniczenia`")
        elif heading == "Poprawione uwagi":
            _finding_lines(lines, change["id"], rel, findings, errors)
        elif heading == "Ograniczenia":
            _limit_lines(lines, rel, limits, errors)
        else:
            errors.append(f"{rel}:{n}: nieznana podsekcja `### {heading}` w `## Oceny`")
        seen.add(heading)
    for name in ("Poprawione uwagi", "Ograniczenia"):
        if name not in seen:
            errors.append(f"{rel}:{head}: `## Oceny` bez podsekcji `### {name}`")


def read_registry(repo, errors):
    """{D-<nnn>: change-id of its `Źródło`} of the limitation entries, in file order; an entry
    without a recognised `Źródło` line adds an error (it could not be required, E6)."""
    entries, heads = {}, {}
    for rel in REGISTRY:
        path = os.path.join(repo, rel)
        if not os.path.isfile(path):
            continue
        current = None
        for n, line in enumerate(unfenced(_read(path)), 1):
            entry = LIMIT_ENTRY.match(line)
            if entry:
                current = entry.group(1)
                entries.setdefault(current, None)
                heads.setdefault(current, f"{rel}:{n}")
                continue
            if H2.match(line):
                current = None
                continue
            source = SOURCE_FIELD.match(line)
            if current and source and entries[current] is None:
                head = source.group(1).partition(" — ")[0].split()
                entries[current] = head[0].strip("`") if head else None
    errors += [f"{heads[did]}: {did} bez rozpoznanej linii `Źródło`"
               for did, source in entries.items() if not source]
    return entries


def rate(repo, changes):
    """Ratings summary: E4, E5, E9 counts, missing ratings and rating errors."""
    ids = {c["id"] for c in changes}
    findings, limits, errors = {}, {}, []
    read_backfill(repo, ids, findings, limits, errors)
    for change in changes:
        read_retro_ratings(repo, change, findings, limits, errors)
    registry = read_registry(repo, errors)
    fixed = [(c["id"], r["name"][:-3], f["id"]) for c in changes for r in c["reports"]
             for f in r["findings"] if is_fixed(c, r, f)]
    fixed_set = set(fixed)
    for key, places in sorted(findings.items()):
        if key not in fixed_set:
            errors += [f"{rel}:{n}: {key[1]} {key[2]} nie jest poprawioną uwagą zmiany {key[0]}"
                       for _, rel, n in places]
    for did, places in sorted(limits.items()):
        if did not in registry:
            errors += [f"{rel}:{n}: {did} nie ma w rejestrze ograniczeń" for _, rel, n in places]
    finding_rating = {key: (CHANGED if any(v == CHANGED for v, _, _ in findings[key]) else TEXT_ONLY)
                      for key in fixed if key in findings}
    limit_rating = {did: max((v for v, _, _ in limits[did]), key=STRENGTH.index)
                    for did in registry if did in limits}
    from_at = next((c["archived_at"] for c in changes if c["id"] == RATINGS_FROM), None)
    required = {c["id"] for c in changes if from_at is not None and c["archived_at"] >= from_at}
    missing = [f"uwaga {cid} {report} {fid}" for cid, report, fid in fixed
               if cid in required and (cid, report, fid) not in finding_rating]
    missing += [f"ograniczenie {did} ({source})" for did, source in registry.items()
                if source in required and did not in limit_rating]
    values = list(limit_rating.values())
    return {"fixed": len(fixed), "rated": len(finding_rating),
            "changed": sum(1 for v in finding_rating.values() if v == CHANGED),
            "limits": len(registry), "limits_rated": len(values),
            "exposed": sum(1 for v in values if v != "—"), "dash": values.count("—"),
            "r": values.count("R"), "rn": values.count("R") + values.count("N"),
            "missing": missing, "errors": errors}


# ------------------------------------------------------------------ measure

def measure(changes):
    e10_from = next((c["archived_at"] for c in changes if c["id"] == E10_FROM), None)
    rows = []
    for change in changes:
        fixed = fixed_rounds(change)
        stop_pairs = stops(change)
        esc = None
        if stop_pairs is not None:
            verdicts = intervention_verdicts(change)
            esc = [escalation(change, name, fid, verdicts) for name, fid in stop_pairs]
        before = e10_from is not None and change["archived_at"] < e10_from
        # Without a review report the numbers from reports have no trace (E11).
        reviewed = bool(change["reports"])
        rows.append({
            "id": change["id"],
            "archived_at": change["archived_at"],
            "fixed": sum(fixed.values()),
            "clean": sum(fixed.values()) == 0 if reviewed else None,
            "last_plan_clean": _last_clean(change, "plan", fixed),
            "last_impl_clean": _last_clean(change, "impl", fixed),
            "rounds_plan": sum(1 for r in change["reports"] if r["kind"] == "plan" and fixed[r["name"]])
            if reviewed else None,
            "rounds_impl": sum(1 for r in change["reports"] if r["kind"] == "impl" and fixed[r["name"]])
            if reviewed else None,
            "stops": None if stop_pairs is None else len(stop_pairs),
            "reversals": None if change["dt"] is None else len(reversals(change)),
            "esc_accepted": None if esc is None else sum(1 for _, ok in esc if ok),
            "esc_judged": None if esc is None else sum(1 for _, ok in esc if ok is not None),
            "esc_no_data": None if esc is None else sum(1 for _, ok in esc if ok is None),
            "regressions": (lambda r: None if r is None else len(r))(regressions(change, before))
            if reviewed else None,
            "questions": change["questions"],
            "undo": change["undo"],
            "costs": change.get("costs"),
        })
    return rows


def question_counts(rows):
    """{kind: {human, agreed, changes, agent, observer, undo}} over the rows, and the number of
    rows without a questions section („brak danych”, outside the agreement denominator). The
    counts of the human, the agent and the observer are disjoint."""
    counts = {kind: {"human": 0, "agreed": 0, "changes": 0, "agent": 0, "observer": 0, "undo": 0}
              for kind in KINDS}
    no_data = 0
    for row in rows:
        for kind in row["undo"]:
            counts[kind]["undo"] += 1
        if row["questions"] is None:
            no_data += 1
            continue
        seen = set()
        for q in row["questions"]:
            entry = counts[q["kind"]]
            if q["by"] == "agent":
                entry["agent"] += 1
                continue
            if q["by"] == "obserwator":
                entry["observer"] += 1
                continue
            entry["human"] += 1
            entry["agreed"] += q["agreed"]
            seen.add(q["kind"])
        for kind in seen:
            counts[kind]["changes"] += 1
    return counts, no_data


def _questions_cell(row):
    if row["questions"] is None:
        return NO_DATA
    human = [q for q in row["questions"] if q["by"] == "człowiek"]
    observer = sum(1 for q in row["questions"] if q["by"] == "obserwator")
    cell = f"{sum(q['agreed'] for q in human)}/{len(human)}"
    return cell + (f" · obserwator: {observer}" if observer else "")


def _cell(value):
    return NO_DATA if value is None else str(value)


def _yes(value):
    return NO_DATA if value is None else ("tak" if value else "nie")


def _rounds(row):
    if row["rounds_plan"] is None:
        return NO_DATA
    return f"{row['rounds_plan']} + {row['rounds_impl']}"


def _pct(part, whole):
    return NO_DATA if not whole else f"{100 * part / whole:.0f}%"


def _avg(values):
    data = [v for v in values if v is not None]
    return (NO_DATA, 0) if not data else (f"{sum(data) / len(data):.2f}", len(data))


def render(rows, commit, ratings):
    out = ["# Pomiar z archiwów (etap 9)", "",
           f"- Data: {date.today().isoformat()}",
           f"- Commit fabryki: {commit}",
           f"- Zmian w archiwum: {len(rows)}", "",
           "| # | Zmiana | archived_at | Bez poprawek | Ostatnia runda planu bez poprawek "
           "| Ostatnia runda kodu bez poprawek | Rundy z poprawkami (plan + kod) | Zatrzymania "
           "| Cofnięcia | Sygnał 2: eskalacje według rekomendacji | Sygnał 4: poprawki z regresją "
           "| Pytania (zgodne z rekomendacją) |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        esc = NO_DATA if r["esc_judged"] is None else (
            f"{r['esc_accepted']}/{r['esc_judged']}"
            + (f" ({NO_DATA}: {r['esc_no_data']})" if r["esc_no_data"] else ""))
        out.append(f"| {i} | {r['id']} | {r['archived_at']} | {_yes(r['clean'])} "
                   f"| {_yes(r['last_plan_clean'])} | {_yes(r['last_impl_clean'])} "
                   f"| {_rounds(r)} | {_cell(r['stops'])} "
                   f"| {_cell(r['reversals'])} | {esc} | {_cell(r['regressions'])} "
                   f"| {_questions_cell(r)} |")
    clean_known = [r["clean"] for r in rows if r["clean"] is not None]
    clean = sum(clean_known)
    plan_known = [r["last_plan_clean"] for r in rows if r["last_plan_clean"] is not None]
    impl_known = [r["last_impl_clean"] for r in rows if r["last_impl_clean"] is not None]
    stops_avg, stops_n = _avg(r["stops"] for r in rows)
    rev_avg, rev_n = _avg(r["reversals"] for r in rows)
    rounds = [r["rounds_plan"] + r["rounds_impl"] for r in rows if r["rounds_plan"] is not None]
    rev_total = sum(r["reversals"] for r in rows if r["reversals"] is not None)
    accepted = sum(r["esc_accepted"] for r in rows if r["esc_accepted"] is not None)
    judged = sum(r["esc_judged"] for r in rows if r["esc_judged"] is not None)
    no_rec = sum(r["esc_no_data"] for r in rows if r["esc_no_data"] is not None)
    reg_rows = [r["regressions"] for r in rows if r["regressions"] is not None]
    out += ["", "## Liczby", "",
            f"1. Zmiany, które przeszły review bez poprawek: {clean} z {len(clean_known)} "
            f"({_pct(clean, len(clean_known))}). "
            f"Ostatnia runda review planu bez poprawek: {sum(plan_known)} z {len(plan_known)}; "
            f"ostatnia runda review kodu bez poprawek: {sum(impl_known)} z {len(impl_known)}.",
            f"2. Zatrzymania na zmianę: średnio {stops_avg} ({stops_n} zmian z danymi); "
            f"cofnięte decyzje na zmianę: średnio {rev_avg} ({rev_n} zmian z danymi).",
            f"3. Rundy review z poprawkami: {sum(rounds)} w {len(rounds)} zmianach, "
            f"średnio {_avg(rounds)[0]} na zmianę.",
            f"4. Poprawki, które zmieniły działanie: {ratings['changed']} z {ratings['rated']} "
            f"ocenionych poprawionych uwag ({_pct(ratings['changed'], ratings['rated'])}); "
            f"bez oceny {ratings['fixed'] - ratings['rated']} z {ratings['fixed']}. "
            f"Ograniczenia, które wróciły jako realny błąd (R): {ratings['r']} z {ratings['exposed']} "
            f"ocenionych bez „—” ({_pct(ratings['r'], ratings['exposed'])}); z oceną „—” "
            f"(poza mianownikiem): {ratings['dash']}; bez oceny "
            f"{ratings['limits'] - ratings['limits_rated']} z {ratings['limits']}.",
            "", "## Sygnały polityki triage'u", "",
            f"1. Decyzje automatyczne zmienione przez człowieka: {rev_total} ({rev_n} zmian z danymi).",
            f"2. Eskalacje przyjęte bez zmian według rekomendacji: {accepted} z {judged} "
            f"({_pct(accepted, judged)}); eskalacje bez rekomendacji ({NO_DATA}): {no_rec}.",
            f"3. Ograniczenia, które wróciły jako błąd albo nowa uwaga (R + N): "
            f"{ratings['rn'] if ratings['limits_rated'] else NO_DATA} "
            f"({ratings['limits_rated']} ocenionych ograniczeń).",
            f"4. Poprawki, po których w następnej rundzie przyszła regresja albo nowa postać "
            f"problemu: {sum(reg_rows) if reg_rows else NO_DATA} ({len(reg_rows)} zmian z danymi)."]
    counts, no_data = question_counts(rows)
    human = sum(c["human"] for c in counts.values())
    agreed = sum(c["agreed"] for c in counts.values())
    out += ["", f"## {QUESTIONS}", "",
            "| Rodzaj | Pytania rozstrzygnięte przez człowieka | Zgodne z rekomendacją "
            "| Zmiany z takim pytaniem | Rozstrzygnięte przez agenta "
            "| Rozstrzygnięte przez obserwatora | Cofnięcia |",
            "|---|---|---|---|---|---|---|"]
    for kind in KINDS:
        c = counts[kind]
        out.append(f"| {kind} | {c['human']} | {c['agreed']} ({_pct(c['agreed'], c['human'])}) "
                   f"| {c['changes']} | {c['agent']} | {c['observer']} | {c['undo']} |")
    out += ["",
            f"Zgodne z rekomendacją: {agreed} z {human} pytań rozstrzygniętych przez człowieka "
            f"({_pct(agreed, human)}); zmiany bez sekcji `## {QUESTIONS}` ({NO_DATA}, poza "
            f"mianownikiem): {no_data} z {len(rows)}."]
    out += step_costs_section(rows)
    return "\n".join(out) + "\n"


def _seconds(value):
    return NO_VALUE if value is None else f"{value:.0f}"


def _usd(value):
    return NO_VALUE if value is None else f"{value:.4f}"


def _total(values):
    known = [v for v in values if v is not None]
    return sum(known) if known else None


def step_costs_section(rows):
    """Lines of `## Czas i koszt kroków`: `- <id>: brak danych` for every change without a cost row, then
    `### <id>` with the table of its steps and their sum for every change with one."""
    out = ["", f"## {STEP_COSTS}", ""]
    out += [f"- {r['id']}: {NO_DATA}" for r in rows if not r.get("costs")]
    for r in rows:
        costs = r.get("costs")
        if not costs:
            continue
        if out[-1] != "":
            out.append("")
        out += [f"### {r['id']}", "", "| " + " | ".join(COST_COLUMNS) + " |", "|---|---|---|"]
        out += [f"| {c['step']} | {_seconds(c['seconds'])} | {_usd(c['cost'])} |" for c in costs]
        out.append(f"| Suma | {_seconds(_total(c['seconds'] for c in costs))} "
                   f"| {_usd(_total(c['cost'] for c in costs))} |")
    return out


def main(argv):
    repo = REPO
    args = list(argv)
    try:
        if args[:1] == ["--repo"] and len(args) == 2:
            repo = args[1]
        elif args:
            raise UsageError(f"bad usage: {' '.join(argv)}; usage: pomiar.py [--repo DIR]")
        changes = read_archive(repo)
        rows = measure(changes)
        commit = _commit()
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    ratings = rate(repo, changes)
    sys.stdout.write(render(rows, commit, ratings))
    problems = ([f"BRAK OCENY: {m}" for m in ratings["missing"]]
                + [f"BŁĄD OCENY: {e}" for e in ratings["errors"]]
                + [f"BŁĄD PYTANIA: {e}" for c in changes for e in c["question_errors"]]
                + [f"BŁĄD KOSZTÓW: {e}" for c in changes for e in c.get("cost_errors", [])])
    if problems:
        sys.stdout.write("\n" + "\n".join(problems) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
