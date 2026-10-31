#!/usr/bin/env python3
"""Answer whether a change is really finished, and say why not.

    python3 validate_change.py <change-id> [--repo DIR] [--rules 1,2,...]
                                           [--phases 1,3] [--staged]

Reads context/changes/<change-id>/{change.md,plan.md,runs/*.md} and git. The
formats are defined in references/progress-format.md (plan), the criteria
section of 10x-new/references/change-md.md and references/run-report-format.md.

Rules:

1. every checked Progress row has a SHA of a commit in the history of HEAD;
2. every checked Progress row has an Observed entry with `Exit: 0` in a run
   report (runs/*.md other than *-verifier.md);
3. change.md status is implemented or impl_reviewed and every Automated row
   is checked;
4. every phase has one `**Criteria**:` line naming existing criteria, every
   criterion has a phase, `## Plan Changes` entries name existing phases and
   criteria, and the criteria block has no format errors;
5. the newest verifier report (runs/*-verifier.md) is committed, no later
   commit changes a file outside context/, and it has MET with evidence for
   every criterion;
6. every file outside context/ changed by the change's commits (subject
   `<type>(<change-id>): ...`) is in a `**File**:` line of some phase's
   Changes Required or in the `**Files**` of a `## Plan Changes` entry;
7. no Manual row is unchecked.

--phases narrows rules 1, 2, 4 and 6 to the given phases (rule 4 then skips
the "every criterion has a phase" check). --staged adds the staged files to
rule 6.

The change id is the name of the folder in context/changes/, matched without
regard to case; commit scopes use the folder name.

Malformed input is a problem of the rule that reads it, never skipped: a
checklist line in Progress that is not a step row (rules 1 and 3; rules 2
and 7 when no row is valid), an unknown `####` heading in Progress (rule 3),
a bold bullet in the criteria block that is not a criterion (rule 4; rule 5
when no criterion is valid). No commits of the change is a rule 6 problem
when a Progress row in scope is checked and --staged is not given; otherwise
it is a note on stderr.

Prints one line per problem, `R<n>: <where>: <what>`, sorted by rule. Exit
codes: 0 no problems; 1 problems; 2 missing files or data only: no change
folder, change.md or plan.md, no criteria (rules 4, 5), no Progress rows
(rules 1, 2, 3, 7), no run reports (rule 2), no git repository (rules 1, 5,
6), an unreadable file or git failure, or a bad argument.
"""

import argparse
import fnmatch
import glob
import os
import re
import subprocess
import sys

ALL_RULES = (1, 2, 3, 4, 5, 6, 7)
CRITERIA_STARTS = ("**Acceptance criteria.**", "**Kryteria akceptacji.**")
CRITERION = re.compile(r"^- \*\*([A-Z]+[0-9]+)\.\*\*")
CRITERION_ID = re.compile(r"^[A-Z]+[0-9]+$")
PHASE_HEADING = re.compile(r"^## Phase (\d+):")
CRITERIA_LINE = re.compile(r"^\*\*Criteria\*\*:(.*)$")
FILE_LINE = re.compile(r"^\*\*Files?\*\*:(.*)$")
PLAN_CHANGE = re.compile(r"^- \*\*PC(\d+) \(Phase (\d+)\)\*\*:")
FIELD = re.compile(r"^\s*- \*\*([A-Za-z ]+)\*\*:\s*(.*)$")
ROW = re.compile(r"^- \[([ xX])\] (\d+)\.(\d+)(?:\s|$)(.*)$")
CHECKLIST = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\[[ xX]?\]")
BOLD_BULLET = re.compile(r"^(?:[-*+]|\d+\.)\s+\*\*")
PROGRESS_KINDS = ("Automated", "Manual")
ROW_SHA = re.compile(r" — ([0-9a-f]{7,40})\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
OBSERVED_FIELDS = ("Step", "Criteria", "Command", "Exit", "Output", "Commit")
DONE_STATUSES = ("implemented", "impl_reviewed")
NO_EVIDENCE = ("", "-", "—")


class Usage(Exception):
    """Nothing to check, or a bad argument: exit code 2."""


# ---------------------------------------------------------------- parsing


def unfenced(lines):
    """Yield (index, line) for lines outside fenced code blocks."""
    fence = None
    for index, line in enumerate(lines):
        match = FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                continue
            yield index, line
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
            if line.strip() == match.group(1):
                fence = None


def parse_criteria(text):
    """Return (criteria, errors, has_block).

    criteria: list of (id, line number); errors: list of (line number, text).
    """
    criteria, errors = [], []
    seen = {}
    has_block = False
    inside = False
    for index, line in unfenced(text.splitlines()):
        number = index + 1
        if line.strip() in CRITERIA_STARTS and not line.startswith(" "):
            if has_block:
                errors.append((number, "second acceptance criteria block"))
            has_block = inside = True
            continue
        if not inside:
            continue
        if line.startswith("**") or line.startswith("#"):
            inside = False
            continue
        if not BOLD_BULLET.match(line):
            continue
        match = CRITERION.match(line)
        if not match:
            errors.append((number, f"not a criterion line: {line[:40]!r}"))
            continue
        cid = match.group(1)
        if cid in seen:
            errors.append((number, f"criterion {cid} repeats line {seen[cid]}"))
            continue
        seen[cid] = number
        criteria.append((cid, number))
    return criteria, errors, has_block


def parse_status(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^status:\s*([^\s#]+)", line)
        if match:
            return match.group(1)
    return None


def _sections(lines):
    """Return [(heading, start, end)] for `## ` headings outside fences."""
    heads = [(i, line) for i, line in unfenced(lines) if line.startswith("## ")]
    out = []
    for pos, (start, heading) in enumerate(heads):
        end = heads[pos + 1][0] if pos + 1 < len(heads) else len(lines)
        out.append((heading.strip(), start, end))
    return out


def backtick_spans(text):
    """Return path spans in backticks of a `**File(s)**` line or field.

    The line already says these are paths, so a root file without `/` or `.`
    (`Makefile`) counts; a span with a space is prose or a command.
    """
    spans = []
    for span in re.findall(r"`([^`]+)`", text):
        span = span.strip()
        if not span or " " in span:
            continue
        if span.startswith("./"):
            span = span[2:]
        spans.append(span)
    return spans


def parse_plan(text):
    """Return a dict with phases, plan_changes, progress (None when absent)."""
    lines = text.splitlines()
    fenced = set(range(len(lines))) - {i for i, _ in unfenced(lines)}
    phases, plan_changes, progress = [], [], None
    errors, progress_errors = [], []
    for heading, start, end in _sections(lines):
        body = [(i, lines[i]) for i in range(start + 1, end) if i not in fenced]
        match = PHASE_HEADING.match(heading)
        if match:
            phase = {
                "number": int(match.group(1)),
                "line": start + 1,
                "criteria_lines": [],
                "files": [],
            }
            in_changes = False
            for i, line in body:
                if line.startswith("### "):
                    in_changes = line.strip().rstrip(":") == "### Changes Required"
                    continue
                criteria = CRITERIA_LINE.match(line)
                if criteria:
                    phase["criteria_lines"].append((i + 1, criteria.group(1)))
                    continue
                if in_changes:
                    file_line = FILE_LINE.match(line)
                    if file_line:
                        phase["files"].extend(backtick_spans(file_line.group(1)))
            phases.append(phase)
        elif heading == "## Plan Changes":
            entry = None
            for i, line in body:
                header = PLAN_CHANGE.match(line)
                if header:
                    entry = {
                        "id": "PC" + header.group(1),
                        "phase": int(header.group(2)),
                        "line": i + 1,
                        "fields": {},
                    }
                    plan_changes.append(entry)
                    continue
                if line.startswith("- **"):
                    errors.append((i + 1, f"not a Plan Changes entry: {line[:40]!r}"))
                    entry = None
                    continue
                field = FIELD.match(line)
                if entry is not None and field and line.startswith(" "):
                    entry["fields"][field.group(1).strip()] = field.group(2).strip()
        elif heading == "## Progress":
            progress = []
            kind = None
            for i, line in body:
                if line.startswith("### "):
                    kind = None
                elif line.startswith("#### "):
                    name = line[5:].strip()
                    if name not in PROGRESS_KINDS:
                        progress_errors.append(
                            (i + 1, f"Progress heading {line.strip()!r} is not #### Automated or #### Manual")
                        )
                    kind = "Manual" if name == "Manual" else "Automated"
                row = ROW.match(line)
                if not row and CHECKLIST.match(line):
                    progress_errors.append((i + 1, f"not a Progress step row: {line.strip()[:40]!r}"))
                if row:
                    sha = ROW_SHA.search(row.group(4))
                    progress.append(
                        {
                            "step": f"{row.group(2)}.{row.group(3)}",
                            "phase": int(row.group(2)),
                            "checked": row.group(1) != " ",
                            "sha": sha.group(1) if sha else None,
                            "kind": kind or "Automated",
                            "line": i + 1,
                        }
                    )
    return {
        "phases": phases,
        "plan_changes": plan_changes,
        "progress": progress,
        "errors": errors,
        "progress_errors": progress_errors,
    }


def split_numbers(value):
    """Split `V1, V3` into tokens; `—` and `none` give an empty list."""
    value = value.strip().strip("`")
    if value in ("", "—", "-") or value.lower() == "none":
        return []
    return [token.strip() for token in value.split(",")]


def parse_run_report(text):
    """Return (has_observed, entries) for the `## Observed` section.

    Each entry: {"id", "line", "fields"}.
    """
    lines = text.splitlines()
    outside = {i for i, _ in unfenced(lines)}
    for heading, start, end in _sections(lines):
        if heading != "## Observed":
            continue
        entries, entry = [], None
        for i in range(start + 1, end):
            if i not in outside:
                continue
            line = lines[i]
            if line.startswith("### "):
                entry = {"id": line[4:].strip(), "line": i + 1, "fields": {}}
                entries.append(entry)
                continue
            field = FIELD.match(line)
            if entry is not None and field and not line.startswith(" "):
                entry["fields"].setdefault(field.group(1).strip(), field.group(2).strip())
        return True, entries
    return False, []


def parse_verifier_table(text):
    """Return {criterion id: (verdict, evidence)} from the agent's table."""
    rows = {}
    for line in text.splitlines():
        cells = line.strip()
        if not cells.startswith("|"):
            continue
        cells = cells[1:]
        if cells.endswith("|"):
            cells = cells[:-1]
        parts = cells.split("|", 2)
        if len(parts) < 3:
            continue
        cid = parts[0].replace("*", "").strip()
        if not CRITERION_ID.match(cid):
            continue
        verdict = parts[1].replace("*", "").strip()
        rows.setdefault(cid, (verdict, parts[2].strip()))
    return rows


def _expand_braces(span):
    match = re.search(r"\{([^{}]*)\}", span)
    if not match:
        return [span]
    out = []
    for part in match.group(1).split(","):
        out.extend(_expand_braces(span[: match.start()] + part + span[match.end() :]))
    return out


def path_matches(path, span):
    """True when a repo-relative path is covered by a plan path span.

    A span that is only placeholders and `*` (`<file>`, `*`) covers nothing.
    """
    for pattern in _expand_braces(span):
        pattern = re.sub(r"<[^<>]*>", "*", pattern)
        if not pattern.strip("*/"):
            continue
        if pattern.endswith("/"):
            if path.startswith(pattern) or fnmatch.fnmatchcase(path, pattern + "*"):
                return True
        elif path == pattern or fnmatch.fnmatchcase(path, pattern):
            return True
    return False


# -------------------------------------------------------------------- git


def git(repo, *args):
    # core.quotePath=false: paths with non-ASCII letters come back as written,
    # not as octal escapes that no plan span can match.
    try:
        result = subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", repo, *args],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        raise Usage(f"cannot run git: {exc}") from exc
    return result.returncode, result.stdout


def read_text(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise Usage(f"cannot read {path}: {exc}") from exc


def is_ancestor(repo, sha):
    return git(repo, "merge-base", "--is-ancestor", sha, "HEAD")[0] == 0


def commit_exists(repo, sha):
    return git(repo, "cat-file", "-e", f"{sha}^{{commit}}")[0] == 0


def change_commits(repo, change_id):
    if git(repo, "rev-parse", "--verify", "-q", "HEAD")[0] != 0:
        return []  # a repository without commits yet
    code, out = git(repo, "log", "--no-merges", "--format=%H%x00%s", "HEAD")
    if code != 0:
        raise Usage(f"git log failed in {repo}")
    subject = re.compile(r"^[a-z]+\(" + re.escape(change_id) + r"\)!?: ")
    commits = []
    for line in out.splitlines():
        sha, _, title = line.partition("\x00")
        if subject.match(title):
            commits.append(sha)
    return commits


def commit_files(repo, sha):
    _, out = git(
        repo, "diff-tree", "--root", "--no-commit-id", "-r", "--name-only", "--no-renames", sha
    )
    return [line for line in out.splitlines() if line]


# ------------------------------------------------------------------ rules


class Change:
    def __init__(self, repo, change_id):
        changes = os.path.join(repo, "context", "changes")
        names = [
            n for n in (os.listdir(changes) if os.path.isdir(changes) else [])
            if os.path.isdir(os.path.join(changes, n))
        ]
        # The folder name is the id, so the commit scope match uses its case.
        if change_id not in names:
            same = [n for n in names if n.lower() == change_id.lower()]
            if len(same) > 1:
                raise Usage(f"change id {change_id} matches folders {', '.join(sorted(same))}")
            if not same:
                raise Usage(f"no change folder {os.path.join('context', 'changes', change_id)}/")
            change_id = same[0]
        self.repo = repo
        self.id = change_id
        self.dir = os.path.join(changes, change_id)
        self.rel = os.path.join("context", "changes", change_id)
        self.notes = []
        for name in ("change.md", "plan.md"):
            if not os.path.isfile(os.path.join(self.dir, name)):
                raise Usage(f"no {self.rel}/{name}")
        self.change_text = self._read("change.md")
        self.criteria, self.criteria_errors, _ = parse_criteria(self.change_text)
        self.plan = parse_plan(self._read("plan.md"))
        runs = sorted(glob.glob(os.path.join(self.dir, "runs", "*.md")))
        self.verifier_reports = [p for p in runs if p.endswith("-verifier.md")]
        self.run_reports = [p for p in runs if not p.endswith("-verifier.md")]

    def _read(self, name):
        return read_text(os.path.join(self.dir, name))

    def where(self, name, line=None):
        place = f"{self.rel}/{name}"
        return f"{place}:{line}" if line else place

    def rel_path(self, path):
        return os.path.relpath(path, self.repo).replace(os.sep, "/")

    def rows(self, phases=None):
        return [r for r in self.plan["progress"] if phases is None or r["phase"] in phases]


def rule_1(change, phases):
    problems = [
        f"{change.where('plan.md', line)}: {text}"
        for line, text in change.plan["progress_errors"]
        if text.startswith("not a Progress step row")
    ]
    for row in change.rows(phases):
        if not row["checked"]:
            continue
        where = change.where("plan.md", row["line"])
        sha = row["sha"]
        if not sha:
            problems.append(f"{where}: step {row['step']} is checked but has no commit SHA")
        elif not commit_exists(change.repo, sha):
            problems.append(f"{where}: step {row['step']}: commit {sha} does not exist")
        elif not is_ancestor(change.repo, sha):
            problems.append(f"{where}: step {row['step']}: commit {sha} is not in the history of HEAD")
    return problems


def no_valid_rows(change):
    return [f"{change.where('plan.md')}: no valid ## Progress step rows to check"]


def rule_2(change, phases):
    if not change.plan["progress"]:
        return no_valid_rows(change)
    problems, proven = [], set()
    for path in change.run_reports:
        has_observed, entries = parse_run_report(read_text(path))
        rel = change.rel_path(path)
        if not has_observed:
            problems.append(f"{rel}: run report has no ## Observed section")
            continue
        for entry in entries:
            missing = [f for f in OBSERVED_FIELDS if f not in entry["fields"]]
            if missing:
                problems.append(
                    f"{rel}:{entry['line']}: Observed entry {entry['id']} has no "
                    + ", ".join(missing)
                    + " field" + ("s" if len(missing) > 1 else "")
                )
                continue
            exit_code = entry["fields"]["Exit"].strip("`")
            if not re.fullmatch(r"-?\d+", exit_code):
                problems.append(
                    f"{rel}:{entry['line']}: Observed entry {entry['id']}: Exit is not a number"
                )
                continue
            if int(exit_code) == 0:
                proven.add(entry["fields"]["Step"].strip("`").strip())
    for row in change.rows(phases):
        if row["checked"] and row["step"] not in proven:
            problems.append(
                f"{change.where('plan.md', row['line'])}: step {row['step']} has no "
                "Observed entry with Exit: 0 in a run report"
            )
    return problems


def rule_3(change, phases):
    problems = [f"{change.where('plan.md', line)}: {text}" for line, text in change.plan["progress_errors"]]
    if not change.plan["progress"]:
        return problems
    automated = [r for r in change.rows() if r["kind"] == "Automated"]
    pending = [r for r in automated if not r["checked"]]
    status = parse_status(change.change_text)
    for row in pending:
        problems.append(
            f"{change.where('plan.md', row['line'])}: Automated step {row['step']} is not done"
        )
    if pending:
        expected = "implementing" if any(r["checked"] for r in change.rows()) else "planned"
        if status != expected:
            problems.append(
                f"{change.where('change.md')}: status is {status!r}; "
                f"with Automated rows pending it should be {expected!r}"
            )
    elif status not in DONE_STATUSES:
        problems.append(
            f"{change.where('change.md')}: status is {status!r}; every Automated row is done, "
            "so it should be 'implemented' (or 'impl_reviewed' after review)"
        )
    return problems


def rule_4(change, phases):
    problems = []
    known = {cid for cid, _ in change.criteria}
    for line, text in change.criteria_errors:
        problems.append(f"{change.where('change.md', line)}: {text}")
    for line, text in change.plan["errors"]:
        problems.append(f"{change.where('plan.md', line)}: {text}")
    covered = set()
    phase_numbers = {p["number"] for p in change.plan["phases"]}
    for phase in change.plan["phases"]:
        lines = phase["criteria_lines"]
        for _, value in lines:
            covered.update(split_numbers(value))
        if phases is not None and phase["number"] not in phases:
            continue
        where = change.where("plan.md", phase["line"])
        if not lines:
            problems.append(f"{where}: Phase {phase['number']} has no **Criteria**: line")
            continue
        if len(lines) > 1:
            problems.append(
                f"{where}: Phase {phase['number']} has {len(lines)} **Criteria**: lines"
            )
        for line, value in lines:
            tokens = split_numbers(value)
            if not tokens:
                problems.append(
                    f"{change.where('plan.md', line)}: Phase {phase['number']}: "
                    "**Criteria**: line names no criterion"
                )
            for token in tokens:
                if not CRITERION_ID.match(token):
                    problems.append(
                        f"{change.where('plan.md', line)}: Phase {phase['number']}: "
                        f"{token!r} is not a criterion number"
                    )
                elif token not in known:
                    problems.append(
                        f"{change.where('plan.md', line)}: Phase {phase['number']} names "
                        f"{token}, which is not in change.md"
                    )
    if phases is None:
        for cid, line in change.criteria:
            if cid not in covered:
                problems.append(f"{change.where('change.md', line)}: criterion {cid} has no phase")
    for entry in change.plan["plan_changes"]:
        if phases is not None and entry["phase"] not in phases:
            continue
        where = change.where("plan.md", entry["line"])
        if entry["phase"] not in phase_numbers:
            problems.append(
                f"{where}: {entry['id']} names Phase {entry['phase']}, which is not in the plan"
            )
        if "Criteria" not in entry["fields"]:
            problems.append(f"{where}: {entry['id']} has no Criteria field")
            continue
        for token in split_numbers(entry["fields"]["Criteria"]):
            if token not in known:
                problems.append(f"{where}: {entry['id']} names {token}, which is not in change.md")
    return problems


def rule_5(change, phases):
    if not change.criteria:
        return [
            f"{change.where('change.md')}: no valid acceptance criteria to check "
            f"({len(change.criteria_errors)} format error(s), see rule 4)"
        ]
    if not change.verifier_reports:
        return [f"{change.rel}/runs/: no verifier report (runs/*-verifier.md)"]
    newest = change.verifier_reports[-1]
    rel = change.rel_path(newest)
    _, out = git(change.repo, "log", "--diff-filter=A", "--format=%H", "HEAD", "--", rel)
    added = out.split()
    if not added:
        return [f"{rel}: the newest verifier report is not committed"]
    commit = added[-1]
    if not is_ancestor(change.repo, commit):
        return [f"{rel}: commit {commit[:7]} of the verifier report is not in the history of HEAD"]
    _, out = git(
        change.repo, "log", "--format=%h", f"{commit}..HEAD", "--", ".", ":(exclude)context"
    )
    later = out.split()
    if later:
        return [
            f"{rel}: the verifier report (commit {commit[:7]}) is stale: "
            f"later commits change code: {', '.join(later)}"
        ]
    table = parse_verifier_table(read_text(newest))
    problems = []
    for cid, _ in change.criteria:
        if cid not in table:
            problems.append(f"{rel}: criterion {cid} has no row in the verifier report")
            continue
        verdict, evidence = table[cid]
        if verdict != "MET":
            problems.append(f"{rel}: criterion {cid} is {verdict or 'without verdict'}: {evidence}")
        elif evidence in NO_EVIDENCE:
            problems.append(f"{rel}: criterion {cid} is MET without evidence")
    return problems


def rule_6(change, phases, staged=False):
    commits = change_commits(change.repo, change.id)
    problems = []
    if not commits:
        text = f"no commits with scope ({change.id}) in the history of HEAD"
        if not staged and any(r["checked"] for r in change.rows(phases)):
            problems.append(
                f"{text}, but Progress has checked steps; commit subjects are "
                f"`<type>({change.id}): ...`"
            )
        else:
            change.notes.append(text + ("; rule 6 checked the staged files" if staged else ""))
    if phases is not None:
        shas = [r["sha"] for r in change.rows(phases) if r["sha"]]
        commits = [c for c in commits if any(c.startswith(s) for s in shas)]
    sources = {}
    for sha in reversed(commits):
        for path in commit_files(change.repo, sha):
            sources.setdefault(path, []).append(sha[:7])
    if staged:
        _, out = git(change.repo, "diff", "--cached", "--name-only", "--no-renames")
        for path in out.splitlines():
            if path:
                sources.setdefault(path, []).append("staged")
    spans = [span for phase in change.plan["phases"] for span in phase["files"]]
    for entry in change.plan["plan_changes"]:
        if "Files" not in entry["fields"]:
            if phases is None or entry["phase"] in phases:
                problems.append(
                    f"{change.where('plan.md', entry['line'])}: {entry['id']} has no Files field"
                )
            continue
        spans.extend(backtick_spans(entry["fields"]["Files"]))
    for path in sorted(sources):
        if path.startswith("context/"):
            continue
        if not any(path_matches(path, span) for span in spans):
            problems.append(
                f"{path}: not in Changes Required of any phase nor in ## Plan Changes "
                f"(changed in {', '.join(sources[path])})"
            )
    return problems


def rule_7(change, phases):
    if not change.plan["progress"]:
        return no_valid_rows(change)
    return [
        f"{change.where('plan.md', r['line'])}: Manual step {r['step']} is not done"
        for r in change.rows()
        if r["kind"] == "Manual" and not r["checked"]
    ]


RULES = {1: rule_1, 2: rule_2, 3: rule_3, 4: rule_4, 5: rule_5, 6: rule_6, 7: rule_7}


# ------------------------------------------------------------------- main


def _number_list(value, what):
    try:
        numbers = sorted({int(part) for part in value.split(",") if part.strip()})
    except ValueError:
        raise Usage(f"--{what} takes comma-separated numbers, got {value!r}")
    if not numbers:
        raise Usage(f"--{what} is empty")
    return numbers


def run(argv):
    parser = argparse.ArgumentParser(prog="validate_change.py", add_help=True)
    parser.add_argument("change_id")
    parser.add_argument("--repo")
    parser.add_argument("--rules")
    parser.add_argument("--phases")
    parser.add_argument("--staged", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code in (0, None):
            raise
        raise Usage("bad arguments") from exc

    rules = _number_list(args.rules, "rules") if args.rules else list(ALL_RULES)
    unknown = [r for r in rules if r not in RULES]
    if unknown:
        raise Usage(f"unknown rule(s): {', '.join(map(str, unknown))}")

    start = args.repo or os.getcwd()
    if not os.path.isdir(start):
        raise Usage(f"--repo {start} is not a directory")
    code, out = git(start, "rev-parse", "--show-toplevel")
    has_git = code == 0
    repo = out.strip() if has_git else os.path.abspath(start)
    if not has_git and any(r in (1, 5, 6) for r in rules):
        raise Usage(f"{repo} is not a git repository")

    change = Change(repo, args.change_id)
    # Format errors are problems (exit 1); only absent data is exit 2.
    if not change.criteria and not change.criteria_errors and any(r in (4, 5) for r in rules):
        raise Usage(f"no acceptance criteria in {change.rel}/change.md")
    if (
        not change.plan["progress"]
        and not change.plan["progress_errors"]
        and any(r in (1, 2, 3, 7) for r in rules)
    ):
        raise Usage(f"no ## Progress step rows in {change.rel}/plan.md")
    if not change.run_reports and 2 in rules:
        raise Usage(f"no run reports in {change.rel}/runs/")
    if change.plan["progress"] is None:
        change.plan["progress"] = []

    phases = None
    if args.phases:
        phases = set(_number_list(args.phases, "phases"))
        known = {p["number"] for p in change.plan["phases"]}
        missing = sorted(phases - known)
        if missing:
            raise Usage(f"no Phase {', '.join(map(str, missing))} in the plan")

    problems = []
    for rule in sorted(rules):
        if rule == 6:
            found = rule_6(change, phases, staged=args.staged)
        else:
            found = RULES[rule](change, phases)
        problems.extend(f"R{rule}: {text}" for text in found)
    return change.id, rules, problems, change.notes


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        change_id, rules, problems, notes = run(argv)
    except Usage as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} problem(s)", file=sys.stderr)
        return 1
    print(f"OK: {change_id}: rules {', '.join(map(str, rules))} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
