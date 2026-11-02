#!/usr/bin/env python3
"""Retrospective PR step: turn each proposal of a merged change's retro.md
whose target lies in skills/ or is context/foundation/lessons.md into a pull
request that always waits for a human: the step merges no PR by itself and
runs no paid test by itself (decision of the human 2026-11-02, impl-review-7
F1, F2, F4 of paczka-1-1; AUTO_MERGE_OFF).

Run it from the main folder of the repo after the change was archived,
merged into master with --ff-only and pushed. A proposal is a candidate when
its `Miejsce docelowe` starts with skills/ or equals
context/foundation/lessons.md; a target in docs/ is never a candidate,
whatever the scope says. Every other proposal gets one line "czeka na decyzję
człowieka". A candidate whose `Rekomendacja` is `nie` gets one line "czeka na
potwierdzenie odrzucenia": no session, no branch and no PR; a human confirms
the rejection. For every other candidate, in the order of the numbers:

1. skip it when branch retro/<change-id>-p<n> has a PR in any state;
2. make a fresh copy of origin/master (git archive, checked file by file) in a
   temporary folder;
3. let a fresh `claude -p` session (the author) apply the proposal there;
4. build the commit of the copy's files in the main repo (a temporary index,
   commit-tree): after the author nothing runs in its folder, not even git
   (impl-review-6 F1); an empty diff is an error without a PR;
5. check the diff (git in the main repo, on the checked commit) against
   docs/zgoda-czlowieka.md: scope, the list of paths that need a human,
   removal of a chain step, and any file in skills/ other than .md, which
   goes to the human too (impl-review-6 F1);
6. when no gate hit: the deterministic tests (RETRO_PR_VERIFY, default the
   verify command of CLAUDE.md) in their own fresh copy of the checked commit,
   under sandbox-exec with verify_profile as an extra layer (not the sandbox
   of the `claude -p` steps; impl-review-3 F6), then, when they exit 0, a
   fresh read-only `claude -p` session (the reviewer) with the diff, in
   another fresh copy;
7. note the paid tests of the changed skills: they are always the human's
   decision (`--paid-tests`), whatever they cost;
8. push the branch and open the PR with the results and a marker; every PR
   waits for a human with the reason AUTO_MERGE_OFF next to the others, also
   when the tests and the reviewer passed;
8a. when, besides AUTO_MERGE_OFF and the paid tests, the only reason to wait
   is failed deterministic tests, one fresh `claude -p` session (the fixer:
   the author's flags, the step sandbox through --settings) gets the test
   output in a fresh copy of the checked commit; the commit of its files,
   built in the main repo, goes to the PR's branch with a plain push, and
   every gate of 5-7 runs again on the new head against the same base, with
   a new body and marker (`gh pr edit`). One try; the PR waits for a human
   either way (D-427).

After all proposals, every open PR of a branch retro/<change-id>-p<n> of this
change whose marker has `verify` and a `base` other
than origin/master moves onto origin/master: a merge commit of its head and
origin/master built in the main repo (`git merge-tree --write-tree`,
`git commit-tree`, no checkout of its files), the gates, the deterministic tests
and the reviewer again against the new base, a plain push (never --force) and
a new body with the new marker (`gh pr edit`). Such a PR is never merged here:
its line starts with "czeka na człowieka — przeniesiony na origin/master". A
conflict (merge-tree exits non-zero) comments on the PR and leaves the branch and body
unchanged ("konflikt z origin/master"). A PR whose branch changed after its
check (the marker's head is not the branch's head) is not moved. A move that
fails otherwise keeps the PR waiting ("czeka na człowieka — przeniesienie …
się nie udało") with exit code 1.

When --paid-tests merged a PR, it ends with `git pull
--ff-only -q` in the main folder, which has to be on master with no
uncommitted change to tracked files; the line `master: …` gives the result,
and a skipped or failed pull is exit code 1.

With --paid-tests P<n>, run by the human (any candidate, also one for the
lessons file: the paid tests come from the files its PR changes) it runs the paid tests named in the marker of that proposal's open PR (RETRO_PR_EVALS, default
scripts/run_evals.sh) with the main folder switched to the PR's head,
comments the result and the cost on the PR and, when they exit 0, merges it
(squash, the checked head only, the decision-log entry with the result and the
cost as the last commit of the branch; a failed `gh pr merge` is retried while
GitHub reports UNKNOWN or MERGEABLE, at most MERGE_TRIES times, with
RETRO_PR_MERGE_WAIT seconds between tries); a merge ends with the same
`git pull --ff-only`. A PR whose marker has
another base is refused (D-102); the moved PRs above have origin/master as
their base. One exception (D-303): when origin/master moved from the
marker's base (or, during the test or a merge retry, from the base the step
started on) only by commits that each have one parent and change only files
in context/przebiegi/ (the autopilot's run record), the base still counts;
the commit subject is never read, and any other commit, a merge commit or an
empty one is refused as before. The items of `## Płatne testy skilli` are
folders ending with / or files with an extension.

The list, the prompts for the author and the reviewer and the names of the
skills come from origin/master, never from the PR's branch. The step is
described in skills/retro/references/pr.md.

Usage: python3 scripts/retro_pr.py <change-id> [--paid-tests P<n>]
Exit code 0 when every proposal was handled (waiting for a human or skipped;
merged only with --paid-tests), 1 when at least one ended in an error without a PR (or a failed
merge or move) or `git pull --ff-only` was skipped or failed, 2 when the step cannot start: git
fetch failed, master differs from origin/master, a change is in progress in context/changes/, not exactly one
retro.md, a broken list or prompt file, or a PR whose marker does not match.
"""

import argparse
import contextlib
import datetime
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

LIST = "docs/zgoda-czlowieka.md"
PR_DOC = "skills/retro/references/pr.md"
LESSONS = "context/foundation/lessons.md"
NEVER_MERGED = ("docs/",)
DECISIONS = "context/foundation/decisions.md"
DECISION_FILES = (DECISIONS, "context/foundation/limitations.md", "context/foundation/decisions-archive.md")
CATEGORIES = ("Kryteria przeglądu", "Testy skilli", "Polityka triage'u", "Zabezpieczenia aplikacji", "Ta lista")
VERIFY = ("python3 -m unittest discover -s scripts -p 'test_*.py' && python3 scripts/check_refs.py"
          " && python3 scripts/check_no_copy.py")
EVALS = "scripts/run_evals.sh"
# The cost of a paid test from the evals-*.md files of its --out folder (`budget`, D-426).
EVALLIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evallib.py")
# Automatic merging of the retrospective PRs is off (decision of the human 2026-11-02, impl-review-7 F1, F2, F4 of
# paczka-1-1; limitation D-432 in context/foundation/limitations.md): every PR waits for a human with this reason next to
# the others, also after the tests and the reviewer passed, so its list of reasons is never empty, and the step runs
# no paid test by itself (only --paid-tests, started by the human).
AUTO_MERGE_OFF = "automatyczne scalanie wyłączone"
# The time limit of one run of paid tests in seconds (impl-review F9 of paczka-1-1): a hang would block the step;
# past it the exit is 124 and the PR waits for a human.
PAID_TIMEOUT = 5400
# Seconds between SIGTERM and SIGKILL to the process group of paid tests past PAID_TIMEOUT (impl-review-2 F4 of
# paczka-1-1): the tests and their `claude -p` sessions stop with the runner, so none keeps spending. 30 seconds leave
# the cleanup traps of the tests (temporary clones of eval_chain.sh) time to finish (impl-review-3 F10). Commands that
# the Bash tool of a paid session started run in their own session, outside the group, and may outlive the stop; they
# spend nothing, because the `claude -p` sessions are in the group.
GROUP_GRACE = 30
# The autopilot's run record (context/przebiegi/<id>.md): a commit that changes only this folder does not
# make another base for a paid test (D-303).
RUNS_DIR = "context/przebiegi/"
SESSION_FLAGS = ["--model", "opus", "--restricted", "--strict-mcp-config", "--max-budget-usd", "2",
                 "--output-format", "stream-json", "--verbose", "--no-session-persistence"]
# The places with keys that no session of the step reads (impl-review F3 of paczka-1-1): the fixed places of a
# `claude -p` step of the autopilot (KEY_FOLDERS and KEY_FILES of scripts/autopilot.py, which imports this module;
# a test keeps both lists equal), as rules of --disallowedTools, and no read outside the folder of the session.
KEY_FOLDERS = ("~/.secrets", "~/.ssh", "~/.aws", "~/.gnupg", "~/.config", "~/.docker", "~/.supabase", "~/.wrangler",
               "~/Library/Preferences/.wrangler", "~/Library/Keychains")
KEY_FILES = ("~/.netrc", "~/.npmrc", "~/.git-credentials")
# The files of git under ~/.config that the sandbox of the deterministic tests reads again (READ_AGAIN of
# scripts/autopilot.py).
READ_AGAIN = ("~/.config/git/ignore", "~/.config/git/config", "~/.config/git/attributes")
KEY_DENY = ["--disallowedTools", ",".join([f"Read({path}/**)" for path in KEY_FOLDERS]
                                          + [f"Read({path})" for path in KEY_FILES])]
READ_SETTINGS = {"permissions": {"blockReadsOutsideWorkingDirectories": True}}
EDIT_TOOLS = ["--tools", "Read,Grep,Glob,Edit,Write", "--permission-mode", "acceptEdits"] + KEY_DENY
AUTHOR_TOOLS = EDIT_TOOLS + ["--settings", json.dumps(READ_SETTINGS)]
# The fixer of failed tests (D-427): the author's tools and read limits, in the sandbox of a `claude -p` step of the
# autopilot (the human's condition for P34).
FIXER_SETTINGS = dict(READ_SETTINGS, sandbox={"enabled": True, "failIfUnavailable": True,
                                              "allowUnsandboxedCommands": False})
FIXER_TOOLS = EDIT_TOOLS + ["--settings", json.dumps(FIXER_SETTINGS)]
REVIEWER_TOOLS = ["--tools", "Read,Grep,Glob"] + KEY_DENY + ["--settings", json.dumps(READ_SETTINGS)]
# The deterministic tests of a proposal may run code an agent wrote (impl-review-3 F6 of paczka-1-1, decision of the
# human). They run in a fresh copy of the checked commit, and on top of that under sandbox-exec of macOS with
# verify_profile, an extra layer, not the sandbox of the `claude -p` steps: it starts from (allow default), so Mach
# services, osascript, launchctl, open, securityd and local sockets stay open (limitation in
# context/foundation/limitations.md). RETRO_PR_SANDBOX replaces the program, for the tests; without it the tests
# fail and the PR waits for the human.
SANDBOX_EXEC = "/usr/bin/sandbox-exec"
# A change of a file in skills/ other than .md goes to the human (impl-review-6 F1 of paczka-1-1).
CODE_REASON = "kod skilla (plik w skills/ inny niż .md, decyzja człowieka)"
VERDICTS = {"WERDYKT: ZATWIERDZAM": "ZATWIERDZAM", "WERDYKT: ODRZUCAM": "ODRZUCAM"}
SESSION_TIMEOUT = 1800
TAIL = 20
MERGE_TRIES = 12
MERGE_WAIT = 10
REMINDER = ("Synchronizację skilli do ~/.claude/skills po scaleniach robi autopilot; po uruchomieniu "
            "kroku PR poza autopilotem robi ją człowiek.")

PROPOSAL = re.compile(r"^#### P(\d+)\. (.+)$")
TARGET = re.compile(r"^- \*\*Miejsce docelowe\*\*: `?([^`\s]+)`?\s*$")
EFFECT = re.compile(r"^- \*\*Co ma się zmienić\*\*:(.*)$")
RECOMMENDATION = re.compile(r"^- \*\*Rekomendacja\*\*:\s*(tak|nie)\b")
REJECTED = "czeka na potwierdzenie odrzucenia"
ITEM = re.compile(r"^- `([^`]+)`")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
PAID = re.compile(r"^- `([^`]+)` → `([^`]+)` \(ok\. (\d+(?:,\d+)?) USD\)$")
DECISION = re.compile(r"^## D-(\d{3,})\b", re.M)
MARKER = re.compile(r"<!-- retro-pr: (.*?) -->")
PLACEHOLDER = re.compile(r"\{(change_id|n|proposal|diff|tests)\}")
SPENT = re.compile(r"^wydane: (\d+(?:\.\d+)?)$", re.M)


class Stop(Exception):
    """The step cannot start: exit 2."""


class Failed(Exception):
    """One proposal ended in an error."""


# Pure functions: everything the gates decide on.

def section(text, heading):
    """Lines of the `## <heading>` section of text, without the heading; None when absent."""
    lines = text.splitlines()
    if "## " + heading not in lines:
        return None
    start = lines.index("## " + heading) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def parse_proposals(text):
    """Proposals of `## Propozycje`: dicts with n, title, block, target, effect and recommendation.

    target is None without `Miejsce docelowe`; effect is the trimmed value of the first
    `- **Co ma się zmienić**:` line of the block, or None without it (older retro.md) or
    when it is empty. Only that one line counts: a decision-log field is one line.
    recommendation is `tak` or `nie` from the first `- **Rekomendacja**: tak|nie — …` line,
    or None without such a line."""
    proposals, current = [], None
    for line in section(text, "Propozycje") or []:
        match = PROPOSAL.match(line)
        if match:
            current = {"n": int(match.group(1)), "title": match.group(2).strip(), "lines": [line],
                       "target": None, "effect": None, "effect_seen": False, "recommendation": None,
                       "recommendation_seen": False}
            proposals.append(current)
        elif line.startswith("#"):
            current = None
        elif current is not None:
            current["lines"].append(line)
            target = TARGET.match(line)
            if target:
                current["target"] = target.group(1)
            effect = EFFECT.match(line)
            if effect and not current["effect_seen"]:
                current["effect_seen"] = True
                current["effect"] = effect.group(1).strip() or None
            if line.startswith("- **Rekomendacja**:") and not current["recommendation_seen"]:
                current["recommendation_seen"] = True
                recommendation = RECOMMENDATION.match(line)
                current["recommendation"] = recommendation.group(1) if recommendation else None
    for proposal in proposals:
        proposal["block"] = "\n".join(proposal.pop("lines")).strip()
        del proposal["effect_seen"], proposal["recommendation_seen"]
    return proposals


def is_candidate(target):
    """True when the step itself handles a proposal with this `Miejsce docelowe`:
    skills/ or the lessons file; docs/ never, whatever the scope."""
    if not target or target.startswith(NEVER_MERGED):
        return False
    return target.startswith("skills/") or target == LESSONS


def outside_line(proposal):
    """The summary line of a proposal the step does not handle."""
    target = proposal["target"]
    why = f"Miejsce docelowe {target} poza krokiem PR" if target else "brak Miejsca docelowego"
    return f"P{proposal['n']}: czeka na decyzję człowieka — {why}"


def rejected_line(proposal):
    """The summary line of a candidate the retrospective recommends against: no author session."""
    return f"P{proposal['n']}: {REJECTED} — rekomendacja retro „nie”, bez sesji autora"


def list_items(lines, pattern, where):
    """Matches of pattern for every list item of lines.

    Every line that looks like a list item (`-`, `*`, `+` or `1.`, indented or
    not) must match pattern, otherwise ValueError: an item in another format
    would vanish and the list would check less than it says."""
    found = []
    for line in lines:
        if not LIST_ITEM.match(line):
            continue
        match = pattern.match(line)
        if not match:
            raise ValueError(f"{where}: pozycja w złym formacie: {line}")
        found.append(match)
    return found


def is_paid_item(item):
    """True for an item of `## Płatne testy skilli`: a folder ending with /, or a file whose last part
    has a dot (an extension). `skills/10x-plan` is neither: a folder without its / would cover nothing."""
    return item.endswith("/") or "." in item.rsplit("/", 1)[-1]


def parse_consent(text):
    """The list of docs/zgoda-czlowieka.md: paths by category, scope and paid tests.

    Raises ValueError when a category is missing or empty, the scope or the
    paid tests are empty, or any item is in another format: a list that
    checks nothing must not pass."""
    lines = section(text, "Ścieżki")
    if lines is None:
        raise ValueError("brak sekcji `## Ścieżki`")
    paths, category = {}, None
    for line in lines:
        if line.startswith("### "):
            category = line[4:].strip()
            paths.setdefault(category, [])
            continue
        for match in list_items([line], ITEM, "`## Ścieżki` (- `<ścieżka>` — <dlaczego>)"):
            if category is None:
                raise ValueError(f"pozycja `{match.group(1)}` przed pierwszą kategorią")
            paths[category].append(match.group(1))
    for name in CATEGORIES:
        if not paths.get(name):
            raise ValueError(f"kategoria „{name}” jest pusta albo jej brak")
    scope = [m.group(1) for m in list_items(section(text, "Zakres poprawki skilla") or [], ITEM,
                                            "`## Zakres poprawki skilla` (- `<ścieżka>`)")]
    if not scope:
        raise ValueError("sekcja `## Zakres poprawki skilla` jest pusta albo jej brak")
    paid = []
    for match in list_items(section(text, "Płatne testy skilli") or [], PAID,
                            "`## Płatne testy skilli` (- `<katalog>/` albo `<plik>` → `<test>` (ok. <koszt> USD))"):
        if not is_paid_item(match.group(1)):
            raise ValueError(f"płatny test: `{match.group(1)}` to nie katalog zakończony / ani plik z rozszerzeniem")
        paid.append((match.group(1), match.group(2), float(match.group(3).replace(",", "."))))
    if not paid:
        raise ValueError("sekcja `## Płatne testy skilli` jest pusta albo jej brak")
    return {"paths": paths, "scope": scope, "paid": paid}


def covers(item, path):
    """True when a list item (a file, or a folder ending with /) covers path."""
    return path == item or (item.endswith("/") and path.startswith(item))


def chain_count(text, name):
    """Occurrences of the command `/<name>` in text (not `/<name>-more`, not a path segment)."""
    return len(re.findall(r"(?<![\w./-])/" + re.escape(name) + r"(?![\w-])", text))


def classify(changes, consent, skills, base_texts, head_texts):
    """Reasons why a diff needs a human: scope, the list, removal of a chain step.

    changes: (status letter, [paths]) from `git diff --name-status`;
    skills: skill folder names in the base; base_texts, head_texts: the text
    of each modified file before and after. An empty list means no gate hit."""
    reasons = []

    def add(reason):
        if reason not in reasons:
            reasons.append(reason)

    touched = [path for _, paths in changes for path in paths]
    for path in touched:
        if not any(covers(item, path) for item in consent["scope"]):
            add(f"zakres: {path} leży poza {', '.join(consent['scope'])}")
    for path in touched:
        for category, items in consent["paths"].items():
            if any(covers(item, path) for item in items):
                add(f"lista zgody: {path} ({category})")
    # impl-review-6 F1 of paczka-1-1 (decision of the human): code in skills/ runs in the tests and the apps, so a
    # change of any file there other than .md goes to the human, like skills/guardrails/.
    for path in touched:
        if path.startswith("skills/") and not path.endswith(".md"):
            add(f"{CODE_REASON}: {path}")
    for status, paths in changes:
        if status in ("D", "R") and paths[0].startswith("skills/"):
            add(f"krok łańcucha: {paths[0]} {'usunięty' if status == 'D' else 'przeniesiony'}")
        elif status == "M":
            for name in skills:
                before = chain_count(base_texts.get(paths[0], ""), name)
                after = chain_count(head_texts.get(paths[0], ""), name)
                if after < before:
                    add(f"krok łańcucha: w {paths[0]} spadła liczba /{name} z {before} do {after}")
    return reasons


def paid_tests(changes, consent):
    """(test, cost) pairs for the changed skills that have a paid test, in list order."""
    found = []
    for prefix, test, cost in consent["paid"]:
        if any(covers(prefix, path) for _, paths in changes for path in paths) and (test, cost) not in found:
            found.append((test, cost))
    return found


def paid_total(paid):
    """The sum of the list averages of (test, cost) pairs."""
    return sum(cost for _, cost in paid)


def only_paid_waiting(paid, waiting):
    """True when, besides AUTO_MERGE_OFF, the PR waits only for the human's decision on its paid tests: its body
    gets `## Decyzja do podjęcia`."""
    return bool(paid) and paid_reason(paid) in waiting and all(
        reason in (paid_reason(paid), AUTO_MERGE_OFF) for reason in waiting)


def tests_reason(verify):
    return f"testy skilli: kod wyjścia {verify[1].returncode}"


def fixable(reasons, verify, waiting, paid=()):
    """True when, besides AUTO_MERGE_OFF and the human's decision on the paid tests, the only reason to wait is the
    failed deterministic tests (D-423, D-427)."""
    rest = [reason for reason in waiting if reason != AUTO_MERGE_OFF and not (paid and reason == paid_reason(paid))]
    return not reasons and verify is not None and verify[1].returncode != 0 and rest == [tests_reason(verify)]


def last_result(stream):
    """Text of the last `result` event of a stream-json log; None when it is not a success."""
    text = None
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("type") == "result":
            ok = event.get("subtype") == "success" and not event.get("is_error")
            text = (event.get("result") or "") if ok else None
    return text


def parse_verdict(stream):
    """ZATWIERDZAM or ODRZUCAM from the reviewer's log; None without a success
    result, without the verdict as its last non-empty line, or with more than one verdict line."""
    text = last_result(stream)
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines or lines[-1] not in VERDICTS:
        return None
    if sum(line.startswith("WERDYKT:") for line in lines) != 1:
        return None
    return VERDICTS[lines[-1]]


def next_decision(texts):
    """The next free number: the highest `## D-<nnn>` of the given files, plus one."""
    numbers = [int(n) for text in texts for n in DECISION.findall(text)]
    return f"D-{max(numbers, default=0) + 1:03d}"


def decision_entry(number, change_id, proposal, retro_path, pr_number, basis, day):
    """The decision-log entry of a merged proposal; the `Co ma się zmienić` line only
    when the proposal has the field (skills/retro/references/pr.md, "Wpis w dzienniku")."""
    n = proposal["n"]
    effect = proposal.get("effect")
    return (f"## {number} Propozycja {change_id} P{n}: {proposal['title']}\n"
            f"- Pytanie: czy przyjąć propozycję P{n} z `{retro_path}`?\n"
            f"- Wybór: przyjęta i scalona w PR #{pr_number}\n"
            "- Kto zdecydował: testy skilli i recenzent (retro_pr)\n"
            f"- Podstawa: {basis}\n"
            f"- Retrospektywa: `{retro_path}` P{n}\n"
            + (f"- Co ma się zmienić: {effect}\n" if effect else "")
            + f"- Data: {day}\n"
            "- Status: obowiązuje\n"
            f"- Zmiana: retro-pr {change_id} P{n}\n")


def parse_marker(body):
    """Fields of the last `<!-- retro-pr: … -->` marker of a PR body; None without one."""
    found = MARKER.findall(body or "")
    if not found:
        return None
    return dict(item.split("=", 1) for item in found[-1].split() if "=" in item)


def fill(template, values):
    """Put values into the {change_id}, {n}, {proposal} and {diff} places, in one pass."""
    return PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), template)


def subject_title(title, change_id):
    """The proposal title for a commit subject: without `(<change-id>)`, which retro's
    `--grep='(<change-id>)'` would count as a commit of that change."""
    return title.replace(f"({change_id})", change_id)


def usd(cost):
    return f"{cost:g}".replace(".", ",")


# Programs: git, gh, claude and the test commands.

def run(cmd, cwd, shell=False, timeout=None):
    """Run a program; a missing program or a timeout becomes a non-zero exit."""
    try:
        return subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=timeout)
    except OSError as exc:
        return subprocess.CompletedProcess(cmd, 127, "", str(exc))
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"timeout after {timeout} s")


def sbpl(path):
    """A path as a string of the sandbox profile language."""
    return '"' + path.replace("\\", "\\\\").replace('"', '\\"') + '"'


def verify_profile(wt):
    """The sandbox profile of the deterministic tests in the fresh copy wt (impl-review-3 F6 of paczka-1-1), an extra
    layer: no network except localhost and local sockets, no write except the copy, the temporary folders and the
    devices, no read of the places with keys (KEY_FOLDERS, KEY_FILES) except git's own files. It starts from
    (allow default), so it is not the sandbox of the `claude -p` steps (see SANDBOX_EXEC)."""
    home = os.path.expanduser("~")
    real = os.path.realpath
    writes = [real(wt), real(tempfile.gettempdir()), "/private/tmp", "/private/var/folders"]
    lines = ["(version 1)", "(allow default)",
             "(deny network*)", "(allow network* (remote unix-socket))",
             '(allow network* (remote ip "localhost:*"))', '(allow network* (local ip "localhost:*"))',
             "(deny file-write*)",
             "(allow file-write* " + " ".join(f"(subpath {sbpl(path)})" for path in writes)
             + ' (literal "/dev/null") (literal "/dev/zero") (regex #"^/dev/tty") (regex #"^/dev/fd/"))',
             "(deny file-read* " + " ".join(
                 [f"(subpath {sbpl(path.replace('~', home, 1))})" for path in KEY_FOLDERS]
                 + [f"(literal {sbpl(path.replace('~', home, 1))})" for path in KEY_FILES]) + ")",
             "(allow file-read* " + " ".join(f"(literal {sbpl(path.replace('~', home, 1))})" for path in READ_AGAIN)
             + ")"]
    return "\n".join(lines)


def run_verify(command, wt):
    """The deterministic tests `command` in the fresh copy wt through the shell, under sandbox-exec with
    verify_profile."""
    sandbox = os.environ.get("RETRO_PR_SANDBOX") or SANDBOX_EXEC
    return run([sandbox, "-p", verify_profile(wt), "/bin/sh", "-c", command], wt, timeout=SESSION_TIMEOUT)


def group_alive(pgid):
    """True while some process of the group pgid is still there."""
    try:
        os.killpg(pgid, 0)
    except OSError:
        return False
    return True


def stop_group(proc, grace):
    """Stop the whole process group of proc: SIGTERM, up to grace seconds for it to end, then SIGKILL."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except OSError:
        return
    end = time.monotonic() + grace
    while time.monotonic() < end:
        proc.poll()
        if not group_alive(proc.pid):
            return
        time.sleep(0.1)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except OSError:
        pass


def run_group(cmd, cwd, timeout):
    """Run a shell command like run, in its own process group (impl-review-2 F4 of paczka-1-1): past timeout the
    whole group stops (stop_group), not only the top process, and the exit is 124."""
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL, text=True, start_new_session=True)
    except OSError as exc:
        return subprocess.CompletedProcess(cmd, 127, "", str(exc))
    try:
        out, err = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(cmd, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        stop_group(proc, GROUP_GRACE)
    try:
        out, err = proc.communicate(timeout=GROUP_GRACE)
    except subprocess.TimeoutExpired:
        # A process that left the group still holds the output: the step does not wait for it.
        proc.kill()
        proc.wait()
        proc.stdout.close()
        proc.stderr.close()
        out, err = "", ""
    return subprocess.CompletedProcess(cmd, 124, out or "", (err or "") + f"timeout after {timeout} s")


def git(cwd, *args, error=Failed):
    result = run(["git", "-c", "core.quotepath=off", *args], cwd)
    if result.returncode != 0:
        raise error(f"git {args[0]}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def rev(cwd, ref, error=Failed):
    return git(cwd, "rev-parse", "--verify", "-q", ref + "^{commit}", error=error).strip()


def show(cwd, ref, path, error=Failed):
    return git(cwd, "show", f"{ref}:{path}", error=error)


def gh(cwd, *args):
    result = run(["gh", *args], cwd)
    if result.returncode != 0:
        raise Failed(f"gh {' '.join(args[:2])}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def gh_list(root, *args):
    out = gh(root, "pr", "list", *args)
    try:
        prs = json.loads(out or "[]")
    except ValueError:
        raise Failed("gh pr list: wynik to nie JSON")
    if not isinstance(prs, list):
        raise Failed("gh pr list: wynik to nie lista")
    return prs


def pr_list(root, branch):
    return gh_list(root, "--state", "all", "--head", branch, "--json", "number,state,url")


def session(prompt, tools, cwd):
    """A fresh `claude -p` session: (exit code, stream-json log)."""
    result = run(["claude", "-p", prompt, *SESSION_FLAGS, *tools], cwd, timeout=SESSION_TIMEOUT)
    return result.returncode, result.stdout


def paid_cost(folder):
    """(cost in USD, None) of the evals-*.md files in folder, from `python3 scripts/evallib.py budget`, or
    (None, why) when the cost cannot be read (no folder, a row without a cost)."""
    result = run(["python3", EVALLIB, "budget", folder, "--limit", "1000000", "--next", "0", "--reserve", "0"],
                 os.path.dirname(folder) or None)
    found = SPENT.search(result.stdout or "")
    if result.returncode not in (0, 1) or not found:
        return None, (result.stderr or result.stdout).strip() or f"evallib.py budget: kod {result.returncode}"
    return float(found.group(1)), None


def run_paid(tests, cwd, out):
    """Run the paid tests in cwd with their result in the folder out: (command, result, cost, why)."""
    evals = os.environ.get("RETRO_PR_EVALS") or EVALS
    command = f"{evals} {' '.join(shlex.quote(t) for t in tests)} --out {shlex.quote(out)}"
    result = run_group(command, cwd, PAID_TIMEOUT)
    cost, why = paid_cost(out)
    return command, result, cost, why


def cost_text(cost, why):
    return f"{usd(cost)} USD" if cost is not None else f"koszt nieznany ({why})"


def paid_comment(path, command, result, cost, why):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(["## Płatne testy skilli", "", f"- Polecenie: `{command}`",
                            f"- Kod wyjścia: {result.returncode}", f"- Koszt: {cost_text(cost, why)}", "",
                            "~~~", tail(result), "~~~", ""]))


def tail(result):
    lines = (result.stdout + result.stderr).rstrip().splitlines()
    return "\n".join(lines[-TAIL:])


def moved_only_by_runs(root, base, now):
    """True when origin/master moved from base to now only by run-record commits (D-303): base is an
    ancestor of now, base..now is not empty, and every commit in it has one parent and changes only files
    under RUNS_DIR, at least one. The commit subject is never read. Any git error (an unknown commit, no
    ancestor) gives False, so the caller refuses as before (D-102)."""
    if run(["git", "merge-base", "--is-ancestor", base, now], root).returncode != 0:
        return False
    listed = run(["git", "rev-list", "--parents", f"{base}..{now}"], root)
    if listed.returncode != 0 or not listed.stdout.strip():
        return False
    for line in listed.stdout.splitlines():
        commit, *parents = line.split()
        if len(parents) != 1:
            return False
        files = run(["git", "-c", "core.quotepath=off", "diff-tree", "--no-commit-id", "--name-only", "-r", commit],
                    root)
        names = [name for name in files.stdout.splitlines() if name]
        if files.returncode != 0 or not names or not all(name.startswith(RUNS_DIR) for name in names):
            return False
    return True


# Commits without git in an agent's folder (impl-review-6 F1 of paczka-1-1, decision of the human): an agent works in
# a fresh copy of a commit (git archive); after it, the step only reads that folder's files and builds the commit in
# the main repo; the tests, the reviewer and the paid tests each get their own fresh copy of the checked commit.

def run_input(cmd, cwd, data, env=None):
    """Run a program with the bytes data on stdin: (code, stdout text, stderr text)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, input=data, capture_output=True, env=env, timeout=SESSION_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)
    return (result.returncode, result.stdout.decode("utf-8", "replace"),
            result.stderr.decode("utf-8", "replace"))


def blob_id(data):
    """The git id (sha1) of a blob with the bytes data."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def tree_entries(root, commit):
    """{path: (mode, id)} of the files and links of commit (no folders, no submodules)."""
    found = {}
    for item in git(root, "ls-tree", "-r", "-z", "--full-tree", commit).split("\0"):
        if not item:
            continue
        meta, path = item.split("\t", 1)
        mode, kind, oid = meta.split()
        if kind == "blob":
            found[path] = (mode, oid)
    return found


def tree_files(folder):
    """{path: (mode, bytes)} of every file and link in folder, without folders named .git; nothing is run in it."""
    found, stack = {}, [""]
    while stack:
        rel = stack.pop()
        with os.scandir(os.path.join(folder, rel) if rel else folder) as entries:
            for entry in entries:
                if entry.name == ".git":
                    continue
                path = f"{rel}/{entry.name}" if rel else entry.name
                if entry.is_symlink():
                    found[path] = ("120000", os.fsencode(os.readlink(entry.path)))
                elif entry.is_dir(follow_symlinks=False):
                    stack.append(path)
                elif entry.is_file(follow_symlinks=False):
                    fd = os.open(entry.path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                    with os.fdopen(fd, "rb") as fh:
                        mode = "100755" if os.fstat(fh.fileno()).st_mode & 0o111 else "100644"
                        found[path] = (mode, fh.read())
    return found


def copy_problem(root, commit, folder):
    """Why folder is not exactly the files of commit (a file missing, extra or different), or None."""
    want = tree_entries(root, commit)
    have = {path: (mode, blob_id(data)) for path, (mode, data) in tree_files(folder).items()}
    wrong = sorted(path for path in set(want) | set(have) if want.get(path) != have.get(path))
    return f"kopia commita {commit[:7]} różni się od niego: {', '.join(wrong[:5])}" if wrong else None


@contextlib.contextmanager
def fresh(root, commit, parent):
    """A fresh copy of commit (git archive) in a new folder under parent, checked file by file against the commit,
    removed after use."""
    folder = tempfile.mkdtemp(prefix="kopia-", dir=parent)
    try:
        try:
            archived = subprocess.run(["git", "archive", "--format=tar", commit], cwd=root, capture_output=True,
                                      stdin=subprocess.DEVNULL, timeout=SESSION_TIMEOUT)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Failed(f"git archive {commit[:7]}: {exc}")
        if archived.returncode != 0:
            raise Failed(f"git archive {commit[:7]}: {archived.stderr.decode('utf-8', 'replace').strip()}")
        try:
            with tarfile.open(fileobj=io.BytesIO(archived.stdout), mode="r:") as tar:
                tar.extractall(folder, filter="data")
        except (tarfile.TarError, OSError) as exc:
            raise Failed(f"rozpakowanie kopii commita {commit[:7]}: {exc}")
        problem = copy_problem(root, commit, folder)
        if problem:
            raise Failed(problem)
        yield folder
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def commit_index(root, parent, lines, message):
    """A commit on top of parent whose tree is parent's with the index lines (`<mode> <id>\t<path>`, mode 0 removes)
    applied, built in a temporary index of the main repo; its id."""
    fd, index = tempfile.mkstemp(prefix="retro-pr-index-")
    os.close(fd)
    os.remove(index)
    env = dict(os.environ, GIT_INDEX_FILE=index)
    try:
        for cmd, data in ((["git", "read-tree", parent], b""),
                          (["git", "update-index", "-z", "--index-info"],
                           b"".join(line.encode("utf-8") + b"\0" for line in lines))):
            code, _, err = run_input(cmd, root, data, env)
            if code != 0:
                raise Failed(f"{' '.join(cmd[:2])}: {err.strip()}")
        code, tree, err = run_input(["git", "write-tree"], root, b"", env)
        if code != 0:
            raise Failed(f"git write-tree: {err.strip()}")
    finally:
        if os.path.exists(index):
            os.remove(index)
    code, commit, err = run_input(["git", "commit-tree", tree.strip(), "-p", parent, "-m", message], root, b"")
    if code != 0:
        raise Failed(f"git commit-tree: {err.strip()}")
    return commit.strip()


def write_blob(root, data):
    """Write the bytes data as a blob in the main repo; its id."""
    code, oid, err = run_input(["git", "hash-object", "-w", "--no-filters", "--stdin"], root, data)
    if code != 0 or oid.strip() != blob_id(data):
        raise Failed(f"git hash-object: {err.strip() or oid.strip()}")
    return oid.strip()


def commit_folder(root, parent, folder, message):
    """The commit whose tree is exactly the files of folder (tree_files) on top of parent, or None when it equals
    parent's tree. Only reads folder's files; every git command runs in the main repo."""
    base = tree_entries(root, parent)
    files = tree_files(folder)
    lines = []
    for path, (mode, data) in sorted(files.items()):
        oid = blob_id(data)
        if base.get(path) != (mode, oid):
            if base.get(path, (None, None))[1] != oid:
                write_blob(root, data)
            lines.append(f"{mode} {oid}\t{path}")
    lines += [f"0 {'0' * 40}\t{path}" for path in sorted(set(base) - set(files))]
    return commit_index(root, parent, lines, message) if lines else None


# The step.

def start(root, change_id):
    """Start conditions; everything later reads from what this returns."""
    if run(["git", "fetch", "-q", "origin"], root).returncode != 0:
        raise Stop("git fetch origin się nie udał")
    master, origin = rev(root, "master", Stop), rev(root, "origin/master", Stop)
    if master != origin:
        raise Stop(f"lokalny master ({master[:7]}) różni się od origin/master ({origin[:7]}); "
                   f"wyrównaj je (git pull --ff-only albo git push) i uruchom krok ponownie")
    changes_dir = os.path.join(root, "context", "changes")
    running = sorted(name for name in os.listdir(changes_dir)
                     if os.path.isdir(os.path.join(changes_dir, name))) if os.path.isdir(changes_dir) else []
    if running:
        raise Stop(f"trwa zmiana {', '.join(running)} (context/changes/); krok czeka do jej końca. "
                   f"Po jej scaleniu i git push uruchom: python3 scripts/retro_pr.py {change_id}")
    pattern = re.compile(r"context/archive/\d{4}-\d{2}-\d{2}-" + re.escape(change_id) + r"/retro\.md")
    archived = git(root, "ls-tree", "-r", "--name-only", origin, "--", "context/archive/", error=Stop)
    found = [path for path in archived.splitlines() if pattern.fullmatch(path)]
    if len(found) != 1:
        raise Stop(f"w origin/master jest {len(found)} plików context/archive/<data>-{change_id}/retro.md, "
                   f"a ma być dokładnie jeden")
    try:
        consent = parse_consent(show(root, origin, LIST, Stop))
    except ValueError as exc:
        raise Stop(f"{LIST} w origin/master: {exc}")
    def kind(path):
        result = run(["git", "cat-file", "-t", f"{origin}:{path.rstrip('/')}"], root)
        return result.stdout.strip() if result.returncode == 0 else None

    items = [path for paths in consent["paths"].values() for path in paths]
    missing = [path for path in items if kind(path) is None]
    if missing:
        raise Stop(f"{LIST} w origin/master wymienia ścieżki, których nie ma: {', '.join(missing)}")
    # A folder without the trailing / would cover only itself, i.e. nothing.
    wrong = [path for path in items if kind(path) != ("tree" if path.endswith("/") else "blob")]
    if wrong:
        raise Stop(f"{LIST} w origin/master: katalog ma kończyć się /, a plik nie: {', '.join(wrong)}")
    unknown = [prefix for prefix, _, _ in consent["paid"]
               if kind(prefix) != ("tree" if prefix.endswith("/") else "blob")]
    if unknown:
        raise Stop(f"{LIST} w origin/master: płatne testy wskazują katalogi albo pliki, których nie ma: "
                   f"{', '.join(unknown)}")
    doc = show(root, origin, PR_DOC, Stop)
    prompts = {}
    for key, heading in (("author", "Autor poprawki"), ("reviewer", "Recenzent poprawki"),
                         ("fixer", "Poprawka po testach")):
        lines = section(doc, heading)
        if not lines or not "\n".join(lines).strip():
            raise Stop(f"{PR_DOC} w origin/master nie ma sekcji `## {heading}`")
        prompts[key] = "\n".join(lines).strip()
    skills = [os.path.basename(path) for path in
              git(root, "ls-tree", "-d", "--name-only", origin, "skills/", error=Stop).splitlines()]
    retro_path = found[0]
    proposals = sorted(parse_proposals(show(root, origin, retro_path, Stop)), key=lambda p: p["n"])
    # A candidate with Rekomendacja „nie” waits for the human's confirmation of the rejection: never an author.
    candidates = [p for p in proposals if is_candidate(p["target"]) and p["recommendation"] != "nie"]
    return {"change_id": change_id, "retro_path": retro_path, "consent": consent, "prompts": prompts,
            "skills": skills, "proposals": proposals, "candidates": candidates}


def merge(root, st, proposal, gated, branch, pr_number, url, base, basis):
    """Commit the decision-log entry on top of the checked commit gated as the last commit of the branch (built in
    the main repo, impl-review-6 F1), push it, merge."""
    texts = []
    for path in DECISION_FILES:
        result = run(["git", "show", f"{base}:{path}"], root)
        texts.append(result.stdout if result.returncode == 0 else "")
    entry = decision_entry(next_decision(texts), st["change_id"], proposal, st["retro_path"], pr_number,
                           basis, datetime.date.today().isoformat())
    current = texts[0] or "# Decisions\n"
    current += "" if current.endswith("\n\n") else ("\n" if current.endswith("\n") else "\n\n")
    data = (current + entry).encode("utf-8")
    n, cid = proposal["n"], st["change_id"]
    head = commit_index(root, gated, [f"100644 {write_blob(root, data)}\t{DECISIONS}"],
                        f"docs: wpis decyzji o propozycji (retro {cid} P{n})")
    git(root, "push", "-q", "origin", f"{head}:refs/heads/{branch}")
    merge_checked(root, pr_number, head, url,
                  f"fix(skills): {subject_title(proposal['title'], cid)} (retro {cid} P{n})", base)


def merge_wait():
    """Seconds between the merge tries: RETRO_PR_MERGE_WAIT, default MERGE_WAIT."""
    try:
        return max(0.0, float(os.environ.get("RETRO_PR_MERGE_WAIT", MERGE_WAIT)))
    except ValueError:
        return MERGE_WAIT


def merge_checked(root, pr_number, head, url, subject, base):
    """`gh pr merge` of exactly head; while GitHub has not computed whether the PR can be merged
    (`mergeable` UNKNOWN, PR #6), or computed MERGEABLE after the refusal, it waits and tries again, at
    most MERGE_TRIES times, with the same --match-head-commit. Before each new try it fetches origin:
    origin/master other than base (the tests and the reviewer ran on base) raises Failed without a try.
    CONFLICTING, another error or the end of the tries raise Failed with the last message and the address."""
    waits = 0
    while True:
        try:
            gh(root, "pr", "merge", str(pr_number), "--squash", "--delete-branch", "--match-head-commit", head,
               "--subject", subject)
            return
        except Failed as exc:
            last = str(exc)
        if waits >= MERGE_TRIES:
            raise Failed(f"{last}; GitHub nie policzył, czy PR da się scalić, po {MERGE_TRIES} ponowieniach ({url})")
        try:
            view = json.loads(gh(root, "pr", "view", str(pr_number), "--json", "mergeable,mergeStateStatus") or "{}")
        except (Failed, ValueError) as exc:
            raise Failed(f"{last}; odczyt stanu PR-a się nie udał: {exc} ({url})")
        view = view if isinstance(view, dict) else {}
        if view.get("mergeable") not in ("UNKNOWN", "MERGEABLE"):
            raise Failed(f"{last}; mergeable={view.get('mergeable')}, "
                         f"mergeStateStatus={view.get('mergeStateStatus')} ({url})")
        waits += 1
        time.sleep(merge_wait())
        if run(["git", "fetch", "-q", "origin"], root).returncode != 0:
            raise Failed(f"{last}; git fetch origin przed ponowieniem scalenia się nie udał ({url})")
        now = rev(root, "origin/master")
        if now != base and not moved_only_by_runs(root, base, now):
            raise Failed(f"{last}; origin/master przesunął się z {base[:7]} na {now[:7]} w trakcie ponawiania "
                         f"scalenia, więc nie ponowiono ({url})")


def pr_body(st, proposal, changes, reasons, verify, review, paid, waiting, marker):
    n, cid = proposal["n"], st["change_id"]
    out = ["## Propozycja", "", proposal["block"], "", "## Zmienione pliki", ""]
    out += [f"- `{status}` `{' → '.join(paths)}`" for status, paths in changes]
    out += ["", "## Bramki", ""]
    out += [f"- {reason}" for reason in reasons] or ["- Żadna bramka nie trafiła (zakres, lista zgody, krok łańcucha)."]
    out += ["", "## Testy skilli", ""]
    if verify is None:
        out.append("Nie uruchomiono: bramka trafiła przed testami.")
    else:
        command, result = verify
        out += [f"- Polecenie: `{command}`", f"- Kod wyjścia: {result.returncode}", "", "~~~", tail(result), "~~~"]
    out += ["", "## Recenzent", ""]
    if review is None:
        out.append("Nie uruchomiono: " + ("bramka trafiła przed testami." if verify is None
                                         else "testy skilli nie przeszły."))
    else:
        verdict, text = review
        out.append(f"- Werdykt: WERDYKT: {verdict}" if verdict else
                   "- Werdykt: brak poprawnej linii werdyktu albo brak wyniku sesji; nie zatwierdzono.")
        out += ["", "~~~", text or "(brak wyniku sesji)", "~~~"]
    if waiting:
        out += ["", "## Powód czekania", ""] + [f"- {reason}" for reason in waiting]
    if only_paid_waiting(paid, waiting):
        total = paid_total(paid)
        out += ["", "## Decyzja do podjęcia", "",
                "- Testy: " + ", ".join(f"`{test}` (ok. {usd(cost)} USD)" for test, cost in paid),
                f"- Koszt: ok. {usd(total)} USD",
                f"- Polecenie: `python3 scripts/retro_pr.py {cid} --paid-tests P{n}`",
                "- Rekomendacja: tak — testy deterministyczne przeszły, a recenzent zatwierdził poprawkę; "
                "płatny test sprawdzi zachowanie zmienionego skilla przed scaleniem.",
                "- Odpowiedź: `tak` (uruchom polecenie) albo `nie` (zamknij PR i zapisz odrzucenie "
                "w dzienniku według D-026)."]
    out += ["", "<!-- retro-pr: " + " ".join(f"{k}={v}" for k, v in marker.items()) + " -->", ""]
    return "\n".join(out)


def paid_reason(paid):
    return "płatny test: " + ", ".join(test for test, _ in paid) + " (decyzja człowieka)"


def existing_pr_line(root, n, branch):
    """The `pominięty` line when the branch has a PR in any state; None when it has none."""
    existing = pr_list(root, branch)
    if existing:
        pr = existing[0]
        return f"P{n}: pominięty — PR już istnieje, stan {pr.get('state', '')} ({pr.get('url', '')})"
    return None


def check_branch_free(root, branch):
    if run(["git", "ls-remote", "--exit-code", "-q", "origin", f"refs/heads/{branch}"], root).returncode == 0:
        raise Failed(f"gałąź {branch} jest w origin bez PR-a; usuń ją (git push origin --delete {branch}) "
                     f"albo załóż do niej PR i uruchom krok ponownie")


def handle(root, st, proposal):
    """One proposal in its own temporary folder; returns its summary line."""
    n, cid = proposal["n"], st["change_id"]
    branch = f"retro/{cid}-p{n}"
    if run(["git", "fetch", "-q", "origin"], root).returncode != 0:
        raise Failed("git fetch origin się nie udał")
    skipped = existing_pr_line(root, n, branch)
    if skipped:
        return skipped
    check_branch_free(root, branch)
    base = rev(root, "origin/master")
    tmp = tempfile.mkdtemp(prefix="retro-pr-")
    try:
        return work(root, st, proposal, branch, base, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gates(st, proposal, root, base, gated, tmp):
    """The gates of commit gated against base: scope, the list and chain steps, the paid tests, then the
    deterministic tests and the reviewer when no gate hit. The git commands run in the main repo root; the tests and
    the reviewer each run in a fresh copy of gated under tmp (fresh), so nothing they do reaches the pushed commit
    (impl-review-6 F1 of paczka-1-1).

    Returns (changes, reasons, verify, review, paid, waiting, marker); waiting lists every reason the PR
    waits for a human and is never empty: automatic merging is off (AUTO_MERGE_OFF), and paid tests are always the
    human's decision (paid_reason)."""
    changes = []
    for line in git(root, "diff", "--name-status", "-M", base, gated).splitlines():
        parts = line.split("\t")
        changes.append((parts[0][0], parts[1:]))
    modified = [paths[0] for status, paths in changes if status == "M"]
    base_texts = {path: show(root, base, path) for path in modified}
    head_texts = {path: show(root, gated, path) for path in modified}
    reasons = classify(changes, st["consent"], st["skills"], base_texts, head_texts)
    paid = paid_tests(changes, st["consent"])

    verify = review = None
    if not reasons:
        command = os.environ.get("RETRO_PR_VERIFY") or VERIFY
        with fresh(root, gated, tmp) as copy:
            verify = (command, run_verify(command, copy))
        if verify[1].returncode == 0:
            diff = git(root, "diff", base, gated)
            prompt = fill(st["prompts"]["reviewer"], {"proposal": proposal["block"], "diff": diff})
            with fresh(root, gated, tmp) as copy:
                _, log = session(prompt, REVIEWER_TOOLS, copy)
            review = (parse_verdict(log), last_result(log))
    waiting = list(reasons)
    if verify is not None and verify[1].returncode != 0:
        waiting.append(tests_reason(verify))
    if review is not None and review[0] != "ZATWIERDZAM":
        waiting.append(f"recenzent: {review[0] or 'brak poprawnego werdyktu'}")
    if paid:
        waiting.append(paid_reason(paid))
    waiting.append(AUTO_MERGE_OFF)
    marker = {
        "verify": "skip" if verify is None else ("ok" if verify[1].returncode == 0 else "fail"),
        "review": "skip" if review is None else {"ZATWIERDZAM": "approve", "ODRZUCAM": "reject"}.get(review[0], "none"),
        "paid": ",".join(test for test, _ in paid) or "-",
        "base": base,
        "head": gated,
    }
    return changes, reasons, verify, review, paid, waiting, marker


def move_waiting(root, st):
    """Move every open PR of this change that waits on an older base onto origin/master: (lines, failed).

    A PR counts when its branch is retro/<change-id>-p<n> of a candidate, its marker has `verify`
    and its `base` is not origin/master. Never merges."""
    cid = st["change_id"]
    by_n = {p["n"]: p for p in st["candidates"]}
    if not by_n:
        return [], False
    try:
        if run(["git", "fetch", "-q", "origin"], root).returncode != 0:
            raise Failed("git fetch origin się nie udał")
        origin = rev(root, "origin/master")
        prs = gh_list(root, "--state", "open", "--search", "head:retro/", "--limit", "200",
                      "--json", "number,headRefName,headRefOid,body,url")
    except Failed as exc:
        return [f"Przeniesienie czekających PR-ów: błąd — {exc}"], True
    branch = re.compile(r"retro/" + re.escape(cid) + r"-p(\d+)")
    lines, failed = [], False
    for pr in sorted((pr for pr in prs if isinstance(pr, dict)), key=lambda pr: pr.get("number") or 0):
        match = branch.fullmatch(pr.get("headRefName") or "")
        marker = parse_marker(pr.get("body"))
        if not match or not marker or "verify" not in marker:
            continue
        proposal = by_n.get(int(match.group(1)))
        if proposal is None or marker.get("base") == origin:
            continue
        try:
            line = move(root, st, proposal, pr, marker, origin)
        # The PR stays open and waits, so its line says so (the last P<n> line is its state); exit 1.
        except Failed as exc:
            line, failed = (f"P{proposal['n']}: czeka na człowieka — przeniesienie na origin/master {origin[:7]} "
                            f"się nie udało: {exc} ({pr.get('url', '')})"), True
        except Exception as exc:  # one broken PR must not drop the others
            line, failed = (f"P{proposal['n']}: czeka na człowieka — przeniesienie na origin/master {origin[:7]} "
                            f"się nie udało: nieoczekiwany wyjątek: {type(exc).__name__}: {exc} "
                            f"({pr.get('url', '')})"), True
        lines.append(line)
    return lines, failed


def move(root, st, proposal, pr, marker, origin):
    """One waiting PR onto origin/master (a merge commit built in the main repo with git merge-tree, never a
    rewrite and no checkout of the PR's files); returns its summary line."""
    n, cid = proposal["n"], st["change_id"]
    branch, number, url = pr["headRefName"], pr.get("number"), pr.get("url", "")
    head = pr.get("headRefOid") or ""
    if marker.get("head") != head:
        return (f"P{n}: czeka na człowieka — gałąź {branch} zmieniła się po sprawdzeniu (head ze znacznika "
                f"{marker.get('head', '')[:7]}, obecny {head[:7]}); przeniesienie pominięte ({url})")
    if run(["git", "fetch", "-q", "origin", branch], root).returncode != 0 or \
            run(["git", "cat-file", "-e", head + "^{commit}"], root).returncode != 0:
        raise Failed(f"nie da się pobrać commita {head[:7]} gałęzi {branch}")
    tmp = tempfile.mkdtemp(prefix="retro-pr-")
    try:
        merged = run(["git", "merge-tree", "--write-tree", head, origin], root)
        if merged.returncode != 0:
            comment = os.path.join(tmp, "comment.md")
            with open(comment, "w", encoding="utf-8") as fh:
                fh.write("\n".join([
                    f"Nie przeniesiono na origin/master ({origin[:7]}): `git merge-tree --write-tree` gałęzi "
                    f"`{branch}` z origin/master kończy się konfliktem. Gałąź i opis PR-a zostają bez zmian; "
                    "przeniesienie wymaga człowieka.", "", "~~~", tail(merged), "~~~", ""]))
            gh(root, "pr", "comment", str(number), "--body-file", comment)
            return f"P{n}: czeka na człowieka — konflikt z origin/master {origin[:7]}; przeniesienie wymaga człowieka ({url})"
        tree = merged.stdout.split()[0]
        code, gated, err = run_input(["git", "commit-tree", tree, "-p", head, "-p", origin, "-m",
                                      f"Merge origin/master into {branch}"], root, b"")
        if code != 0:
            raise Failed(f"git commit-tree: {err.strip()}")
        gated = gated.strip()
        changes, reasons, verify, review, paid, waiting, new_marker = gates(st, proposal, root, origin, gated, tmp)
        # A moved PR is never merged here, so its paid tests stay the human's decision (`--paid-tests`).
        if paid and paid_reason(paid) not in waiting:
            waiting.append(paid_reason(paid))
        git(root, "push", "-q", "origin", f"{gated}:refs/heads/{branch}")
        body_file = os.path.join(tmp, "body.md")
        with open(body_file, "w", encoding="utf-8") as fh:
            fh.write(pr_body(st, proposal, changes, reasons, verify, review, paid, waiting, new_marker))
        gh(root, "pr", "edit", str(number), "--body-file", body_file)
        return (f"P{n}: czeka na człowieka — przeniesiony na origin/master {origin[:7]}; "
                f"{'; '.join(waiting) or MOVED_NO_REASON} ({url})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def align_master(root):
    """`git pull --ff-only -q` in the main folder on a clean master: (the `master: …` line, ok)."""
    current = run(["git", "symbolic-ref", "--short", "-q", "HEAD"], root).stdout.strip()
    if current != "master":
        return (f"master: git pull --ff-only pominięty — główny folder jest na {current or 'odłączonym HEAD'}, "
                "a nie na master"), False
    status = run(["git", "-c", "core.quotepath=off", "status", "--porcelain", "--untracked-files=no"], root)
    if status.returncode != 0:
        return f"master: git pull --ff-only pominięty — git status: {status.stderr.strip()}", False
    if status.stdout.strip():
        paths = ", ".join(line[3:] for line in status.stdout.splitlines() if line.strip())
        return f"master: git pull --ff-only pominięty — niezacommitowane zmiany: {paths}", False
    result = run(["git", "pull", "--ff-only", "-q"], root)
    if result.returncode != 0:
        return f"master: git pull --ff-only się nie udał — {(result.stderr or result.stdout).strip()}", False
    return f"master: git pull --ff-only — {rev(root, 'HEAD')[:7]}", True


def fix_tests(st, proposal, root, base, gated, verify, branch, tmp, number):
    """One try of the fixer for failed deterministic tests (D-427): a fresh session in a fresh copy of the checked
    commit gated with the test output, in the step sandbox; its result becomes a commit built in the main repo
    (commit_folder), which goes to the PR's branch with a plain push, after every gate ran again on the new head
    against the same base, and the PR gets a new body and marker. Returns the new result of gates(), or (None, why)
    when the fixer failed or changed nothing (the PR keeps its body). Raises Failed when the new gates or the push
    fail: nothing was pushed or the body is not new."""
    n, cid = proposal["n"], st["change_id"]
    command, result = verify
    tests = f"Polecenie: {command}\nKod wyjścia: {result.returncode}\n\n{tail(result)}"
    prompt = fill(st["prompts"]["fixer"], {"change_id": cid, "n": str(n), "proposal": proposal["block"],
                                           "tests": tests})
    with fresh(root, gated, tmp) as copy:
        code, log = session(prompt, FIXER_TOOLS, copy)
        if code != 0 or last_result(log) is None:
            return None, f"poprawka agenta-autora: sesja zwróciła błąd (kod {code})"
        fixed = commit_folder(root, gated, copy, f"fix(skills): poprawka testów skilli (retro {cid} P{n})")
    if fixed is None:
        return None, "poprawka agenta-autora niczego nie zmieniła"
    result = gates(st, proposal, root, base, fixed, tmp)
    # A fast-forward of the checked head: never --force.
    git(root, "push", "-q", "origin", f"{fixed}:refs/heads/{branch}")
    body_file = os.path.join(tmp, "body.md")
    with open(body_file, "w", encoding="utf-8") as fh:
        fh.write(pr_body(st, proposal, *result))
    gh(root, "pr", "edit", str(number), "--body-file", body_file)
    return result, None


def work(root, st, proposal, branch, base, tmp):
    """One proposal: the author, the commit, the gates, the PR and at most one fixer; the PR always waits for a human
    (AUTO_MERGE_OFF). The author works in a fresh copy of base; after it the step only reads that copy's files
    (commit_folder) and runs nothing in it (impl-review-6 F1 of paczka-1-1)."""
    n, cid, title = proposal["n"], st["change_id"], proposal["title"]
    prompt = fill(st["prompts"]["author"], {"change_id": cid, "n": str(n), "proposal": proposal["block"]})
    with fresh(root, base, tmp) as copy:
        code, log = session(prompt, AUTHOR_TOOLS, copy)
        if code != 0 or last_result(log) is None:
            raise Failed(f"sesja autora zwróciła błąd (kod {code})")
        # The gates judge this commit; it is the one pushed and merged.
        gated = commit_folder(root, base, copy, f"fix(skills): {subject_title(title, cid)} (retro {cid} P{n})")
    if gated is None:
        raise Failed("autor nic nie zmienił")
    result = gates(st, proposal, root, base, gated, tmp)
    changes, reasons, verify, review, paid, waiting, marker = result
    git(root, "push", "-q", "origin", f"{gated}:refs/heads/{branch}")
    body_file = os.path.join(tmp, "body.md")
    with open(body_file, "w", encoding="utf-8") as fh:
        fh.write(pr_body(st, proposal, changes, reasons, verify, review, paid, waiting, marker))
    out = gh(root, "pr", "create", "--base", "master", "--head", branch,
             "--title", f"{title} (retro {cid} P{n})", "--body-file", body_file)
    url = (out.strip().splitlines() or [""])[-1]
    number = re.search(r"/pull/(\d+)", url)
    if not number:
        raise Failed(f"gh pr create nie podał adresu PR-a: {out.strip()}")
    number = int(number.group(1))
    after_fix = ""
    if fixable(reasons, verify, waiting, paid):
        # The PR exists, so a failure here leaves it waiting instead of an error without a PR.
        try:
            fixed, why = fix_tests(st, proposal, root, base, gated, verify, branch, tmp, number)
        except Failed as exc:
            fixed, why = None, f"poprawka agenta-autora się nie udała: {exc}"
        if fixed is None:
            return f"P{n}: czeka na człowieka — {'; '.join(waiting + [why])} ({url})"
        changes, reasons, verify, review, paid, waiting, marker = fixed
        after_fix = "po poprawce agenta-autora: "
    return f"P{n}: czeka na człowieka — {after_fix}{'; '.join(waiting)} ({url})"


def pr_mode(root, st):
    if not st["proposals"]:
        print(f"Brak propozycji w {st['retro_path']}; nic do zrobienia.")
        return 0
    failed = False
    for proposal in st["proposals"]:
        if not is_candidate(proposal["target"]):
            print(outside_line(proposal))
            continue
        if proposal["recommendation"] == "nie":
            print(rejected_line(proposal))
            continue
        try:
            line = handle(root, st, proposal)
        except Failed as exc:
            line, failed = f"P{proposal['n']}: błąd — {exc}", True
        except Stop:
            raise
        except Exception as exc:  # one broken proposal must not drop the others
            line, failed = f"P{proposal['n']}: błąd — nieoczekiwany wyjątek: {type(exc).__name__}: {exc}", True
        print(line)
    # The PRs of this change that wait on an older base move onto origin/master (the step merges nothing itself).
    moved, move_failed = move_waiting(root, st)
    for line in moved:
        print(line)
    failed = failed or move_failed
    print(REMINDER)
    return 1 if failed else 0


def paid_mode(root, st, which):
    match = re.fullmatch(r"P(\d+)", which)
    if not match:
        raise Stop(f"--paid-tests wymaga P<n>, dostał {which!r}")
    n, cid = int(match.group(1)), st["change_id"]
    proposal = next((p for p in st["candidates"] if p["n"] == n), None)
    if proposal is None:
        raise Stop(f"{st['retro_path']} nie ma propozycji P{n} z Miejscem docelowym w skills/ ani {LESSONS}")
    if git(root, "status", "--porcelain", error=Stop).strip():
        raise Stop("główny folder ma niezacommitowane zmiany; test przełącza go na gałąź PR-a")
    current = run(["git", "symbolic-ref", "--short", "-q", "HEAD"], root).stdout.strip()
    if current != "master":
        raise Stop(f"główny folder jest na {current or 'odłączonym HEAD'}, a ma być na master")
    branch = f"retro/{cid}-p{n}"
    try:
        prs = [pr for pr in pr_list(root, branch) if pr.get("state") == "OPEN"]
        if not prs:
            raise Stop(f"gałąź {branch} nie ma otwartego PR-a")
        number = prs[0]["number"]
        view = json.loads(gh(root, "pr", "view", str(number), "--json", "state,headRefOid,body,url") or "{}")
    except (Failed, ValueError) as exc:
        raise Stop(f"odczyt PR-a gałęzi {branch}: {exc}")
    url = view.get("url") or prs[0].get("url", "")
    marker = parse_marker(view.get("body"))
    if view.get("state") != "OPEN":
        raise Stop(f"PR #{number} nie jest otwarty")
    if not marker:
        raise Stop(f"PR #{number} nie ma znacznika retro-pr")
    if marker.get("verify") != "ok" or marker.get("review") != "approve":
        raise Stop(f"PR #{number}: znacznik nie ma verify=ok review=approve; płatny test nie zastąpi testów ani recenzenta")
    tests = [test for test in marker.get("paid", "").split(",") if test and test != "-"]
    if not tests:
        raise Stop(f"PR #{number}: znacznik nie wymienia płatnych testów")
    head = view.get("headRefOid", "")
    if marker.get("head") != head:
        raise Stop(f"PR #{number}: head ze znacznika ({marker.get('head', '')[:7]}) różni się od obecnego commita "
                   f"gałęzi ({head[:7]}); gałąź zmieniła się po sprawdzeniu. Zamknij PR #{number}.")
    base = rev(root, "origin/master", Stop)
    # Only run-record commits since the marker's base (D-303) keep the tests and the reviewer current.
    if marker.get("base") != base and not moved_only_by_runs(root, marker.get("base", ""), base):
        raise Stop(f"PR #{number}: baza ze znacznika ({marker.get('base', '')[:7]}) różni się od origin/master "
                   f"({base[:7]}), więc wynik testów i recenzenta jest nieaktualny. Zamknij PR #{number}; "
                   f"propozycja bez wpisu decyzji wróci do człowieka w `## Zaległe zadania` następnej "
                   f"retrospektywy, a nie jako nowy PR (D-102).")
    if run(["git", "fetch", "-q", "origin", branch], root).returncode != 0 or \
            run(["git", "cat-file", "-e", head + "^{commit}"], root).returncode != 0:
        raise Stop(f"nie da się pobrać commita {head[:7]} gałęzi {branch}")

    tmp = tempfile.mkdtemp(prefix="retro-pr-")
    merged = False
    try:
        try:
            git(root, "switch", "-q", "--detach", head)
            command, result, cost, why = run_paid(tests, root, os.path.join(tmp, "evals"))
        finally:
            back = run(["git", "switch", "-q", "master"], root)
        if back.returncode != 0:
            raise Failed(f"powrót głównego folderu na master się nie udał: {back.stderr.strip()}")
        comment = os.path.join(tmp, "comment.md")
        paid_comment(comment, command, result, cost, why)
        gh(root, "pr", "comment", str(number), "--body-file", comment)
        names = ", ".join(tests)
        if result.returncode != 0:
            print(f"P{n}: czeka na człowieka — płatny test {names} zwrócił {result.returncode}, "
                  f"{cost_text(cost, why)} ({url})")
        else:
            git(root, "fetch", "-q", "origin")
            now = rev(root, "origin/master")
            if now != base and not moved_only_by_runs(root, base, now):
                print(f"P{n}: czeka na człowieka — origin/master przesunął się z {base[:7]} na {now[:7]} ({url})")
            else:
                merge(root, st, proposal, head, branch, number, url, base,
                      f"testy deterministyczne zwróciły 0, recenzent dał WERDYKT: ZATWIERDZAM, "
                      f"płatny test {names} zwrócił 0 ({cost_text(cost, why)})")
                print(f"P{n}: scalony (PR #{number}) (płatny test {names}: {cost_text(cost, why)})")
                merged = True
    except Failed as exc:
        print(f"P{n}: błąd — {exc}")
        print(REMINDER)
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    code = 0
    if merged:
        line, ok = align_master(root)
        print(line)
        code = 0 if ok else 1
    print(REMINDER)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description="Open and merge PRs for the skill proposals of a retrospective.")
    parser.add_argument("change_id", help="the change whose archived retro.md to read")
    parser.add_argument("--paid-tests", metavar="P<n>", help="run the paid tests of proposal P<n>'s open PR")
    args = parser.parse_args(argv)
    top = run(["git", "rev-parse", "--show-toplevel"], os.getcwd())
    if top.returncode != 0:
        print("error: not inside a git repository", file=sys.stderr)
        return 2
    root = top.stdout.strip()
    try:
        st = start(root, args.change_id)
        if args.paid_tests:
            return paid_mode(root, st, args.paid_tests)
        return pr_mode(root, st)
    except Stop as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
