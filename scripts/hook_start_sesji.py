"""SessionStart hook of the laboratory: tells a Claude Code session in an empty
folder or in an app repo of the laboratory where its start instructions are,
and a session there or in the laboratory which folder `<fabryka>` is.

Claude Code runs it at the start of every session on this computer (also after
`compact`) as `python3 -I -B <lab>/scripts/hook_start_sesji.py`, with the hook
input JSON on stdin (`cwd`, `hook_event_name`, `source`). The folder is `cwd`,
and `os.getcwd()` without it.

- The laboratory itself (`os.path.realpath(folder)` is `<lab>`): prints
  `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
  <text>}}` with the text that the session runs in the laboratory and that
  `<fabryka>` is `<lab>`.
- Folder with the marker file `.fabryka`: the same JSON with the text that
  points to `<lab>/docs/start-projektu.md` and `<lab>/docs/sesja-glowna.md`.
- Empty folder (its listing holds at most `.git` and `.DS_Store`): the same
  JSON with the text that asks once "fabryką czy zwyczajnie?".
- The marker and empty-folder texts also end with the sentence that
  `<fabryka>` is `<lab>`, because the laboratory files say `<fabryka>`
  instead of the full path.
- Everything else is silent (exit 0, empty stdout and stderr):
  `AUTOPILOT_KROK` in the environment (a `claude -p` step of the autopilot,
  also in the laboratory), stdin that is not a JSON object, a folder that
  cannot be listed, any other folder with files and without `.fabryka`, and
  every exception.

`<lab>` is the folder above `scripts/` of this file (`os.path.realpath`), so
the texts carry full paths without hard-coding them; run from an exported
package, `<lab>` is the package folder. The hook uses only the
standard library, opens no network connection, writes no file and reads only
the listing of the folder, so it can never block or change an ordinary
session.
"""

import json
import os
import sys

LAB = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
START_DOC = os.path.join(LAB, "docs", "start-projektu.md")
SESSION_DOC = os.path.join(LAB, "docs", "sesja-glowna.md")
MARKER = ".fabryka"
EMPTY_ALLOWED = {".git", ".DS_Store"}
GUARD = "AUTOPILOT_KROK"

FABRYKA = "<fabryka> to folder " + LAB + "."

PUSTY = (
    "Laboratorium fabryka: ten folder jest pusty. Ta instrukcja dotyczy tylko prośby o zbudowanie "
    "albo zmianę czegoś. Zwykłe pytania (np. „co znaczy ten błąd?”) dostają zwykłą odpowiedź, "
    "bez laboratorium i bez tego pytania. Przy pierwszej prośbie o zbudowanie albo zmianę czegoś "
    "zapytaj człowieka raz: „fabryką czy zwyczajnie?”. Gdy człowiek już wybrał w tej rozmowie, "
    "nie pytaj ponownie. „Fabryką”: przeczytaj " + START_DOC + " i działaj według niego. "
    "„Zwyczajnie”: pracuj jak zwykły Claude Code, bez laboratorium i bez znacznika " + MARKER + ". "
    + FABRYKA
)

ZNACZNIK = (
    "Laboratorium fabryka: to repo aplikacji laboratorium (znacznik " + MARKER + "). Ta instrukcja "
    "dotyczy tylko próśb o budowę albo zmianę czegoś. Zwykłe pytania (np. „co znaczy ten błąd?”) "
    "dostają zwykłą odpowiedź, bez workflow laboratorium. Przy prośbie o budowę albo zmianę: "
    "dopóki context/foundation/start.md nie ma sekcji „## Lista końcowa”, przeczytaj " + START_DOC
    + " i działaj według niego; potem przeczytaj " + SESSION_DOC + " i działaj według niego. "
    + FABRYKA
)

LABORATORIUM = "Laboratorium fabryka: ta sesja działa w folderze laboratorium. " + FABRYKA


def context_for(folder):
    """The text to inject for folder, or None for silence."""
    entries = set(os.listdir(folder))
    if os.path.realpath(folder) == LAB:
        return LABORATORIUM
    if MARKER in entries:
        return ZNACZNIK
    if entries <= EMPTY_ALLOWED:
        return PUSTY
    return None


def main():
    if os.environ.get(GUARD):
        return
    data = json.loads(sys.stdin.read())
    if not isinstance(data, dict):
        return
    folder = data.get("cwd")
    if folder is None:
        folder = os.getcwd()
    if not isinstance(folder, str) or not folder:
        return
    text = context_for(folder)
    if text is None:
        return
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        pass
    os._exit(0)
