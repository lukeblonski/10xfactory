#!/usr/bin/env python3
"""Install package 1.0 (paczka 1.0) into the Claude Code config folder.

Run from the package folder:

    python3 scripts/instaluj.py [--kurs FOLDER] [--zapisz | --sprawdz]

The package folder is the folder above scripts/ of this file
(os.path.realpath). The config folder is $CLAUDE_CONFIG_DIR, or ~/.claude
without it. --kurs is the folder with the skills of the course 10xDevs from
the tag upstream-10x (default: skills/ of the config folder); a path
skills/<x> of the recipe is <kurs>/<x>.

Without --zapisz and --sprawdz the installer only shows what it would do
(preview) and writes nothing. Preview and --zapisz check, in this order,
and list every problem at once:
1. the package path is safe for the shell (shlex.quote leaves it as it is);
2. `claude --version` gives a version of at least 2.1.295;
3. zmiany-10x.json of the package exists, is JSON and has format 1;
4. each course file of the map "kurs" is the original (its SHA-256 from the
   tag), installed (it is itself a result of the recipe, with its
   sha256_wyniku) or a mismatch (another SHA-256 or missing);
5. every result of the recipe is computed in memory and checked against
   sha256_wyniku (a target that already has sha256_wyniku is installed);
   a result whose course file is already installed is a partial
   installation;
6. settings.json of the config folder is missing or a JSON object.

--zapisz then writes, only when nothing above failed: first a backup in
<config>/fabryka-kopie/<YYYYMMDD-HHMMSS>/ (settings.json and every file it
overwrites with other content, under the same relative path, and
nowe-pliki.txt with the relative paths of the files it creates), then the
files to <config>/skills (the results of the recipe, every file of skills/
of the package and, when --kurs is another folder, the unchanged files of
the skill folders the package touches), then settings.json atomically with
the SessionStart hook of scripts/hook_start_sesji.py and the entry
sandbox.excludedCommands of scripts/autopilot.py of the package. A file is
written only when it is missing or has other content; an entry is added only
when the same command is not there yet, so a second run adds nothing.
Just before settings.json is written its bytes are read again; when they
changed during the run, the installer stops with exit code 2 and leaves the
file as it is. A link (settings.json, a skill folder) stays a link and its
target gets the data.

--sprawdz compares the SHA-256 of every result of the recipe and every file
of skills/ of the package with the files in <config>/skills; it does not run
claude.

Only the standard library; nothing runs on import.

Exit code 0 when ready or installed, 1 when something on the user's side
must be fixed first (nothing written), 2 when the installer cannot run (no
or a bad zmiany-10x.json, an unknown format, a package without skills/, an
unreadable file, settings.json changed during the run, a write error).
"""

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time

PACKAGE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RECIPE = "zmiany-10x.json"
FORMAT = 1
MIN_VERSION = (2, 1, 295)
VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")
BACKUPS = "fabryka-kopie"
NEW_FILES = "nowe-pliki.txt"


class Broken(Exception):
    """The installer cannot run; exit code 2."""


def config_dir():
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR") or "~/.claude")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_or_none(path):
    """Bytes of a regular file, None when there is none."""
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as fh:
        return fh.read()


def skill_path(rel):
    """skills/<x> of the recipe -> <x>; anything else is a bad recipe."""
    parts = rel.split("/") if isinstance(rel, str) else []
    if len(parts) < 3 or parts[0] != "skills" or any(p in ("", ".", "..") for p in parts):
        raise Broken(f"{RECIPE}: path {rel!r} is not skills/<skill>/<file>")
    return "/".join(parts[1:])


def hook_command(package):
    return f"python3 -I -B {package}/scripts/hook_start_sesji.py"


def autopilot_command(package):
    return f"python3 {package}/scripts/autopilot.py *"


def claude_version():
    """(text, problem or None) of `claude --version`."""
    exe = shutil.which("claude")
    if exe is None:
        return None, "brak polecenia claude w PATH; zainstaluj Claude Code co najmniej 2.1.295"
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"nie da się uruchomić claude --version: {exc}"
    found = VERSION.search(out.stdout or "")
    if not found:
        return None, f"claude --version nie podał wersji (wyjście: {(out.stdout or out.stderr).strip()!r})"
    version = tuple(int(x) for x in found.groups())
    text = found.group(0)
    if version < MIN_VERSION:
        return text, (f"Claude Code {text} jest za stary; potrzebny co najmniej "
                      f"{'.'.join(map(str, MIN_VERSION))}")
    return text, None


def load_recipe(package):
    """The checked recipe of the package."""
    path = os.path.join(package, RECIPE)
    try:
        with open(path, encoding="utf-8") as fh:
            recipe = json.load(fh)
    except FileNotFoundError:
        raise Broken(f"brak {path}; paczka jest niepełna") from None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Broken(f"nie da się odczytać {path}: {exc}") from exc
    if not isinstance(recipe, dict) or type(recipe.get("format")) is not int or recipe["format"] != FORMAT:
        got = recipe.get("format") if isinstance(recipe, dict) else None
        raise Broken(f"{RECIPE}: nieznany format {got!r}; ten instalator zna format {FORMAT}")
    course, files = recipe.get("kurs"), recipe.get("pliki")
    if not isinstance(course, dict) or not isinstance(files, dict):
        raise Broken(f"{RECIPE}: brak map \"kurs\" i \"pliki\"")
    if not files:
        raise Broken(f"{RECIPE}: pusta mapa \"pliki\"; paczka jest niepełna")
    for rel, digest in course.items():
        skill_path(rel)
        if not isinstance(digest, str):
            raise Broken(f"{RECIPE}: skrót {rel} nie jest tekstem")
    for rel, entry in files.items():
        skill_path(rel)
        if not isinstance(entry, dict) or not isinstance(entry.get("operacje"), list) \
                or not isinstance(entry.get("sha256_wyniku"), str) \
                or not isinstance(entry.get("oryginal"), str) or entry["oryginal"] not in course:
            raise Broken(f"{RECIPE}: zły wpis {rel}")
        for op in entry["operacje"]:
            ok = isinstance(op, list) and op and (
                (op[0] == "zachowaj" and len(op) == 3 and all(isinstance(x, int) for x in op[1:]))
                or (op[0] == "dopisz" and len(op) == 2 and isinstance(op[1], str))
                or (op[0] == "wez" and len(op) == 4 and isinstance(op[1], str) and op[1] in course
                    and all(isinstance(x, int) for x in op[2:])))
            if not ok:
                raise Broken(f"{RECIPE}: zła operacja {op!r} w {rel}")
    return recipe


def apply_entry(entry, texts):
    """Text the entry gives from the course texts ({recipe path: str})."""
    parts = []
    for op in entry["operacje"]:
        if op[0] == "zachowaj":
            parts.append(texts[entry["oryginal"]][op[1]:op[2]])
        elif op[0] == "dopisz":
            parts.append(op[1])
        else:
            parts.append(texts[op[1]][op[2]:op[3]])
    return "".join(parts)


def course_states(recipe, kurs):
    """({recipe path: "oryginal" | "zainstalowany"}, {path: text of an
    original}, [problems]) of every file of the map "kurs"."""
    states, texts, problems = {}, {}, []
    for rel, digest in sorted(recipe["kurs"].items()):
        path = os.path.join(kurs, skill_path(rel))
        data = read_or_none(path)
        entry = recipe["pliki"].get(rel)
        if data is None:
            problems.append(f"{rel} ({path}): brak pliku kursu")
        elif sha256(data) == digest:
            try:
                texts[rel] = data.decode("utf-8")
            except UnicodeDecodeError:
                raise Broken(f"{path} ma skrót oryginału, ale nie jest UTF-8") from None
            states[rel] = "oryginal"
        elif entry is not None and sha256(data) == entry["sha256_wyniku"]:
            states[rel] = "zainstalowany"
        else:
            problems.append(f"{rel} ({path}): inny plik niż oryginał z upstream-10x w przepisie")
    return states, texts, problems


def recipe_results(recipe, states, texts, skills, backup_hint):
    """({recipe path: bytes} of every result, [problems])."""
    results, problems = {}, []
    for rel, entry in sorted(recipe["pliki"].items()):
        current = read_or_none(os.path.join(skills, skill_path(rel)))
        if current is not None and sha256(current) == entry["sha256_wyniku"]:
            results[rel] = current
            continue
        reads = [entry["oryginal"]] + [op[1] for op in entry["operacje"] if op[0] == "wez"]
        if any(r not in states for r in reads):
            continue  # a mismatch, already listed
        installed = [r for r in reads if states[r] == "zainstalowany"]
        if installed:
            problems.append(f"{rel}: częściowa instalacja — {', '.join(installed)} jest już po przepisie, "
                            f"a {rel} nie; przywróć pliki z kopii zapasowej ({backup_hint})")
            continue
        data = apply_entry(entry, texts).encode("utf-8")
        if sha256(data) != entry["sha256_wyniku"]:
            raise Broken(f"{RECIPE}: przepis {rel} nie daje pliku o skrócie sha256_wyniku")
        results[rel] = data
    return results, problems


def package_skill_files(package):
    """Sorted paths under skills/ of the package, without __pycache__ and *.pyc."""
    found = []
    root = os.path.join(package, "skills")

    def fail(exc):
        raise Broken(f"nie da się odczytać {root}: {exc}; paczka jest niepełna")

    for top, dirs, files in os.walk(root, onerror=fail):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in files:
            if not name.endswith(".pyc"):
                found.append(os.path.relpath(os.path.join(top, name), package).replace(os.sep, "/"))
    if not any(rel.endswith("/SKILL.md") for rel in found):
        raise Broken(f"{root}: brak skilli paczki; paczka jest niepełna")
    return sorted(found)


def load_settings(path):
    """(dict, its bytes or None, problem or None) of settings.json; {} when there is none."""
    if not os.path.exists(path):
        return {}, None, None
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, None, f"{path}: nie jest poprawnym JSON ({exc}); popraw plik albo go usuń"
    if not isinstance(data, dict):
        return None, None, f"{path}: nie jest obiektem JSON; popraw plik albo go usuń"
    return data, raw, None


def settings_additions(settings, package):
    """([(name, command)] of the entries still missing, problem or None)."""
    hooks = settings.get("hooks", {})
    sandbox = settings.get("sandbox", {})
    if not isinstance(hooks, dict) or not isinstance(hooks.get("SessionStart", []), list):
        return [], "settings.json: \"hooks\" albo \"hooks.SessionStart\" ma nieznaną postać; popraw plik"
    if not isinstance(sandbox, dict) or not isinstance(sandbox.get("excludedCommands", []), list):
        return [], "settings.json: \"sandbox\" albo \"sandbox.excludedCommands\" ma nieznaną postać; popraw plik"
    if any(isinstance(g, dict) and not isinstance(g.get("hooks", []), list) for g in hooks.get("SessionStart", [])):
        return [], "settings.json: grupa w \"hooks.SessionStart\" ma nieznaną postać; popraw plik"
    commands = [h.get("command") for group in hooks.get("SessionStart", []) if isinstance(group, dict)
                for h in group.get("hooks", []) if isinstance(h, dict)]
    missing = []
    if hook_command(package) not in commands:
        missing.append(("hooks.SessionStart", hook_command(package)))
    if autopilot_command(package) not in sandbox.get("excludedCommands", []):
        missing.append(("sandbox.excludedCommands", autopilot_command(package)))
    return missing, None


def add_entries(settings, missing):
    for name, command in missing:
        if name == "hooks.SessionStart":
            settings.setdefault("hooks", {}).setdefault("SessionStart", []).append(
                {"hooks": [{"type": "command", "command": command}]})
        else:
            settings.setdefault("sandbox", {}).setdefault("excludedCommands", []).append(command)


def write_bytes(dest, data, mode_from=None):
    """Write data to dest through a temporary file in its folder; a link
    stays a link and its target gets the data."""
    dest = os.path.realpath(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    keep = mode_from or (dest if os.path.exists(dest) else None)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest), prefix=".instaluj-")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        if keep is not None:
            shutil.copymode(keep, tmp)
        else:
            os.chmod(tmp, 0o644)
        os.replace(tmp, dest)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def plan_writes(package, recipe, results, kurs, skills):
    """[(relative path in the config folder, bytes, mode source or None)] of
    every file that is missing or has other content."""
    wanted = {}
    for rel, data in results.items():
        name = skill_path(rel)
        original = os.path.join(kurs, name)
        wanted[name] = (data, original if os.path.isfile(original) else None)
    pkg_files = package_skill_files(package)
    for rel in pkg_files:
        src = os.path.join(package, rel)
        with open(src, "rb") as fh:
            wanted[skill_path(rel)] = (fh.read(), src)
    if os.path.realpath(kurs) != os.path.realpath(skills):
        touched = {skill_path(r).split("/")[0] for r in list(recipe["pliki"]) + pkg_files}
        for skill in sorted(touched):
            for top, dirs, files in os.walk(os.path.join(kurs, skill)):
                dirs[:] = sorted(d for d in dirs if d != "__pycache__")
                for fname in files:
                    src = os.path.join(top, fname)
                    name = os.path.relpath(src, kurs).replace(os.sep, "/")
                    if name not in wanted and not fname.endswith(".pyc") and os.path.isfile(src):
                        with open(src, "rb") as fh:
                            wanted[name] = (fh.read(), src)
    writes = []
    for name in sorted(wanted):
        data, mode_from = wanted[name]
        if read_or_none(os.path.join(skills, name)) != data:
            writes.append(("skills/" + name, data, mode_from))
    return writes


def backup(config, writes, settings_path, settings_changes):
    """Backup folder with every file that will be overwritten; its path."""
    root = os.path.join(config, BACKUPS)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    folder, n = os.path.join(root, stamp), 1
    while os.path.exists(folder):
        folder, n = os.path.join(root, f"{stamp}-{n}"), n + 1
    os.makedirs(folder)
    new = []
    targets = [rel for rel, _, _ in writes] + (["settings.json"] if settings_changes else [])
    if os.path.isfile(settings_path) and "settings.json" not in targets:
        targets.append("settings.json")
    for rel in targets:
        src = os.path.join(config, rel)
        if os.path.isfile(src):
            dest = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
        else:
            new.append(rel)
    with open(os.path.join(folder, NEW_FILES), "w", encoding="utf-8") as fh:
        fh.write("".join(rel + "\n" for rel in new))
    return folder


def newest_backup(config):
    """The newest backup folder, or the folder of all backups without one."""
    root = os.path.join(config, BACKUPS)
    try:
        names = sorted(n for n in os.listdir(root) if os.path.isdir(os.path.join(root, n)))
    except OSError:
        names = []
    return os.path.join(root, names[-1]) if names else root


def check_installed(package, recipe, skills):
    """[problems] of --sprawdz."""
    problems, expected = [], {}
    for rel, entry in recipe["pliki"].items():
        expected[skill_path(rel)] = entry["sha256_wyniku"]
    for rel in package_skill_files(package):
        with open(os.path.join(package, rel), "rb") as fh:
            expected[skill_path(rel)] = sha256(fh.read())
    for name in sorted(expected):
        path = os.path.join(skills, name)
        data = read_or_none(path)
        if data is None:
            problems.append(f"skills/{name} ({path}): brak pliku")
        elif sha256(data) != expected[name]:
            problems.append(f"skills/{name} ({path}): inny skrót niż w paczce")
    return problems, len(expected)


def stop(problems, code=1):
    for problem in problems:
        print(f"PROBLEM: {problem}")
    print(f"Instalacja przerwana: {len(problems)} problem(ów); nic nie zapisane.")
    return code


def main(argv=None, package=PACKAGE):
    parser = argparse.ArgumentParser(description="Instalacja paczki fabryka w folderze konfiguracji Claude Code.")
    parser.add_argument("--kurs", help="folder ze skillami kursu z upstream-10x (domyślnie skills/ folderu "
                                       "konfiguracji)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--zapisz", action="store_true", help="zrób kopię zapasową i zainstaluj")
    mode.add_argument("--sprawdz", action="store_true", help="porównaj skróty zainstalowanych plików z paczką")
    args = parser.parse_args(argv)
    config = config_dir()
    skills = os.path.join(config, "skills")
    kurs = os.path.abspath(os.path.expanduser(args.kurs)) if args.kurs else skills
    print(f"Paczka: {package}")
    print(f"Folder konfiguracji: {config}")

    if args.sprawdz:
        try:
            recipe = load_recipe(package)
            problems, count = check_installed(package, recipe, skills)
        except Broken as exc:
            print(f"BŁĄD: {exc}", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"BŁĄD: nie da się odczytać plików: {exc}", file=sys.stderr)
            return 2
        for problem in problems:
            print(f"RÓŻNICA: {problem}")
        if problems:
            print(f"Sprawdzenie: {len(problems)} z {count} plików różni się od paczki.")
            return 1
        print(f"Sprawdzenie: {count} plików zgodnych z paczką.")
        return 0

    problems = []
    if shlex.quote(package) != package:
        problems.append(f"ścieżka paczki {package!r} ma spację, znak powłoki albo literę spoza ASCII "
                        "(np. ą, ó); przenieś paczkę do folderu bez takich znaków")
    version, problem = claude_version()
    print(f"Claude Code: {version or 'nieznana wersja'} (wymagane co najmniej "
          f"{'.'.join(map(str, MIN_VERSION))}: {'nie' if problem else 'tak'})")
    if problem:
        problems.append(problem)
    try:
        recipe = load_recipe(package)
        print(f"Kurs: {kurs}")
        states, texts, mismatches = course_states(recipe, kurs)
        problems.extend(mismatches)
        results, partial = recipe_results(recipe, states, texts, skills, newest_backup(config))
        problems.extend(partial)
    except (Broken, OSError) as exc:
        for problem in problems:
            print(f"PROBLEM: {problem}")
        reason = exc if isinstance(exc, Broken) else f"nie da się odczytać plików: {exc}"
        print(f"BŁĄD: {reason}", file=sys.stderr)
        return 2
    if not mismatches:
        originals = sum(1 for s in states.values() if s == "oryginal")
        print(f"Porównanie kursu: {len(states)} plików zgodnych z przepisem ({originals} oryginałów, "
              f"{len(states) - originals} już zainstalowanych)")
    settings_path = os.path.join(config, "settings.json")
    settings, settings_raw, problem = load_settings(settings_path)
    missing = []
    if problem:
        problems.append(problem)
    else:
        missing, problem = settings_additions(settings, package)
        if problem:
            problems.append(problem)
    if problems:
        return stop(problems)

    try:
        writes = plan_writes(package, recipe, results, kurs, skills)
    except Broken as exc:
        print(f"BŁĄD: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"BŁĄD: nie da się odczytać plików: {exc}", file=sys.stderr)
        return 2
    print(f"Pliki do zapisania w {skills} ({len(writes)}):")
    inside = os.path.join(os.path.realpath(config), "")
    for rel, _, _ in writes:
        real = os.path.realpath(os.path.join(config, rel))
        print(f"  {rel}" + ("" if real.startswith(inside) else f" (zapis przez dowiązanie do {real})"))
    print(f"Wpisy do dopisania w {os.path.realpath(settings_path)} ({len(missing)}):")
    for name, command in missing:
        print(f"  {name}: {command}")
    if not args.zapisz:
        print("Podgląd: nic nie zapisane. Instalacja: python3 scripts/instaluj.py --zapisz")
        return 0
    if not writes and not missing:
        print("Nic do zapisania: paczka jest już zainstalowana.")
        return 0

    folder = os.path.join(config, BACKUPS)
    try:
        folder = backup(config, writes, settings_path, bool(missing))
        print(f"Kopia zapasowa: {folder}")
        for rel, data, mode_from in writes:
            write_bytes(os.path.join(config, rel), data, mode_from)
            print(f"Zapisano: {rel}")
        if missing:
            if read_or_none(settings_path) != settings_raw:
                print(f"BŁĄD: {settings_path} zmienił się w trakcie instalacji; nie nadpisuję go. Skille są "
                      "zapisane; uruchom ponownie python3 scripts/instaluj.py --zapisz", file=sys.stderr)
                return 2
            add_entries(settings, missing)
            write_bytes(settings_path, (json.dumps(settings, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            for name, command in missing:
                print(f"Dopisano w settings.json: {name}: {command}")
    except OSError as exc:
        print(f"BŁĄD: zapis się nie udał: {exc}; kopia zapasowa jest w {folder}",
              file=sys.stderr)
        return 2
    print(f"Zainstalowano: {len(writes)} plików, {len(missing)} wpisów. Sprawdzenie: "
          "python3 scripts/instaluj.py --sprawdz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
