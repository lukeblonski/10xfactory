#!/usr/bin/env python3
"""Check the shape of the intent block in a change.md written by /intent.

    python3 check_intent.py <change.md>

Rules (the shape is described in ../references/intent-block.md):

- criteria: the criteria block parses with parse_criteria from
  10x-impl-review/scripts/validate_change.py (the same parser the other tools
  use), with at least one criterion and no format errors;
- check-line: every criterion has an indented `- Sprawdzenie: polecenie
  `<command>`` or `- Sprawdzenie: weryfikator — <what>` line among its
  continuation lines;
- label: every mandatory label starts exactly one line at column 0 in
  `## Notes`, outside fenced code blocks;
- risk: exactly one line matches `**Ryzyko.** Wysokie|Niskie. <reason>`, and
  no other line starts with `**Ryzyko.**`;
- escalation: when `## Wymaga Twojej decyzji` exists, every line at column 0
  in it is a `- ` entry. An entry written by /intent has the sub-points
  `Rekomendacja:` and `Odpowiedź do zatwierdzenia:`. An entry written by a
  review is one line, `- **<report> F<n> — <title>** · Reguła: <rule> · …`,
  and needs no sub-points.

Prints one line per problem, `<line>: <rule>: <what>`. Exit codes: 0 the
shape is correct; 1 problems; 2 the file is missing or unreadable, it has no
criteria block, or validate_change.py (skill 10x-impl-review) is missing or
cannot be loaded.
"""

import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VALIDATE_CHANGE = os.path.join(HERE, "..", "..", "10x-impl-review", "scripts", "validate_change.py")
LABELS = (
    "**Problem.**",
    "**Oczekiwany efekt.**",
    "**Scenariusz człowieka.**",
    "**Kogo dotyczy.**",
    "**Ograniczenia.**",
    "**Czego nie robimy.**",
    "**Decyzje z góry.**",
    "**Kryteria akceptacji.**",
    "**Ryzyko.**",
)
RISK = re.compile(r"^\*\*Ryzyko\.\*\* (Wysokie|Niskie)\. \S")
CHECK_LINE = re.compile(r"^\s+- Sprawdzenie: (polecenie `[^`]+`|weryfikator — \S)")
ESCALATIONS = "## Wymaga Twojej decyzji"
RECOMMENDATION = re.compile(r"^\s+- Rekomendacja:")
ANSWER = re.compile(r"^\s+- Odpowiedź do zatwierdzenia:")
REVIEW_ENTRY = re.compile(r"^[-*] \*\*\S+ F\d+ — .+?\*\* · Reguła: \S")


class Usage(Exception):
    """The check cannot run: exit code 2."""


def load_module(path=VALIDATE_CHANGE):
    """validate_change.py, loaded by its path, with parse_criteria and unfenced."""
    if not os.path.isfile(path):
        raise Usage(f"{os.path.normpath(path)} not found; install the skill 10x-impl-review next to intent")
    try:
        spec = importlib.util.spec_from_file_location("validate_change", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not (callable(module.parse_criteria) and callable(module.unfenced)):
            raise TypeError("parse_criteria or unfenced is not a function")
    except Exception as exc:
        raise Usage(f"cannot load {os.path.normpath(path)} (skill 10x-impl-review): {exc}") from exc
    return module


def load_parser(path=VALIDATE_CHANGE):
    """parse_criteria from validate_change.py, loaded by its path."""
    return load_module(path).parse_criteria


def notes_lines(lines, unfenced):
    """Indices of the lines in `## Notes` outside fenced code blocks."""
    out, inside = [], False
    for index, line in unfenced(lines):
        if line.startswith("## "):
            inside = line.strip() == "## Notes"
        elif inside:
            out.append(index)
    return out


def continuation(lines, start):
    """Indices of the lines that belong to the criterion at index start:
    the indented or blank lines after it, up to the next line at column 0."""
    out = []
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.strip() and not line[0].isspace():
            break
        out.append(index)
    return out


def check(text, parse_criteria, unfenced=None):
    """List of (line number, rule, what) for the intent block in text."""
    unfenced = unfenced or load_module().unfenced
    lines = text.splitlines()
    criteria, errors, has_block = parse_criteria(text)
    if not has_block:
        raise Usage("no **Kryteria akceptacji.** block; nothing to check")
    problems = [(number, "criteria", what) for number, what in errors]
    if not criteria:
        start = next((i for i, line in enumerate(lines) if line.strip().endswith("criteria.**")
                      or line.strip() == "**Kryteria akceptacji.**"), 0)
        problems.append((start + 1, "criteria", "the criteria block has no criterion"))

    for cid, number in criteria:
        if not any(CHECK_LINE.match(lines[i]) for i in continuation(lines, number - 1)):
            problems.append((number, "check-line", f"criterion {cid} has no indented "
                             "'- Sprawdzenie: polecenie `<command>`' or '- Sprawdzenie: weryfikator — <what>' line"))

    notes = notes_lines(lines, unfenced)
    for label in LABELS:
        found = [i for i in notes if lines[i].startswith(label)]
        if not found:
            problems.append((1, "label", f"missing label {label} at column 0 in ## Notes"))
        elif len(found) > 1 and label != "**Ryzyko.**":  # the risk rule counts risk lines
            problems.append((found[1] + 1, "label", f"label {label} appears {len(found)} times; keep exactly one"))

    risk_lines = [i for i, line in enumerate(lines) if line.startswith("**Ryzyko.**")]
    valid = [i for i in risk_lines if RISK.match(lines[i])]
    for i in risk_lines:
        if not RISK.match(lines[i]):
            problems.append((i + 1, "risk", "expected '**Ryzyko.** Wysokie|Niskie. <reason>'"))
    if len(valid) > 1:
        problems.append((valid[1] + 1, "risk", f"{len(valid)} risk lines; keep exactly one"))

    problems.extend(check_escalations(lines))
    return sorted(problems)


def check_escalations(lines):
    problems = []
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == ESCALATIONS)
    except StopIteration:
        return problems
    index = start + 1
    while index < len(lines) and not lines[index].startswith("## "):
        line = lines[index]
        entry = line.startswith("- ") or line.startswith("* ")
        if line.strip() and not line[0].isspace() and not entry:
            problems.append((index + 1, "escalation", "a line at column 0 that is not a '- ' entry"))
        elif entry and not REVIEW_ENTRY.match(line):
            body = [lines[i] for i in continuation(lines, index)]
            missing = [name for name, pattern in (("Rekomendacja:", RECOMMENDATION),
                                                  ("Odpowiedź do zatwierdzenia:", ANSWER))
                       if not any(pattern.match(b) for b in body)]
            if missing:
                problems.append((index + 1, "escalation", "entry without " + " and ".join(missing)))
        index += 1
    return problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: check_intent.py <change.md>", file=sys.stderr)
        return 2
    path = argv[0]
    try:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            raise Usage(f"cannot read {path}: {exc}") from exc
        module = load_module()
        problems = check(text, module.parse_criteria, module.unfenced)
    except Usage as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for number, rule, what in problems:
        print(f"{number}: {rule}: {what}")
    if problems:
        print(f"{len(problems)} problem(s) in the intent block of {path}", file=sys.stderr)
        return 1
    print(f"OK: intent block in {path} has the expected shape")
    return 0


if __name__ == "__main__":
    sys.exit(main())
