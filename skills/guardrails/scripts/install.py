#!/usr/bin/env python3
"""Install guardrails into a project.

    python3 install.py <project> [--fast-check CMD] [--fast-check-include GLOB ...]
                                 [--allow-domain DOMAIN ...] [--allow-write PATH ...]

- copies the hooks to <project>/.claude/hooks/guardrails/
- creates <project>/.claude/guardrails.json (defaults + flags) if missing
- creates <project>/.claude/agents/verifier.md if missing
- adds .claude/settings.local.json and .claude/locked-tests.sandbox to the
  git exclude file (the test lock lives there while /10x-tdd bug-fix mode
  runs)
- adds the line __pycache__/ to <project>/.gitignore when it is missing
  (creates the file when there is none; other lines stay as they are)
- merges into <project>/.claude/settings.json, keeping every existing key and
  entry: the hook entries, and the Claude Code sandbox (enabled, no
  unsandboxed commands, refuse to start without it, denyWrite for the
  protected paths, allowedDomains and allowWrite from guardrails.json plus
  the flags). settings.json is written last, so a failed run never leaves
  hooks registered without their config.

Idempotent: a second run changes nothing. Exit codes: 0 ok; 1 settings.json
or guardrails.json unreadable (nothing written); 2 bad arguments, missing
templates, or the target is the skills repository itself; 3 a write failed
part way (the files already written are listed).
"""

import argparse
import json
import os
import subprocess
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_SRC = os.path.join(SKILL_DIR, "scripts", "hooks")
TEMPLATES = os.path.join(SKILL_DIR, "templates")

sys.dont_write_bytecode = True
sys.path.append(HOOKS_SRC)
import guardlib  # noqa: E402

HOOK_FILES = ["guardlib.py", "protect_paths.py", "block_secrets.py", "lock_tests.py", "post_edit_check.py"]
PRE_HOOKS = ["protect_paths.py", "block_secrets.py", "lock_tests.py"]
POST_HOOKS = ["post_edit_check.py"]
SYNC_HOOKS = ["lock_tests.py"]
PRE_MATCHER = "Edit|Write|MultiEdit|NotebookEdit|Bash"
POST_MATCHER = "Edit|Write|MultiEdit|NotebookEdit"
SYNC_MATCHER = "Edit|Write|MultiEdit|NotebookEdit|Bash"
HOOKS_REL = ".claude/hooks/guardrails"
CONFIG_REL = guardlib.CONFIG_REL
GITIGNORE_REL = ".gitignore"
PYCACHE_LINE = "__pycache__/"
# Sandbox switches the guardrails rely on: no shell command outside the
# sandbox, and no silent fallback when the sandbox cannot start.
SANDBOX_FLAGS = [("enabled", True), ("failIfUnavailable", True), ("allowUnsandboxedCommands", False)]


class InstallError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def hook_entry(script, timeout):
    return {
        "type": "command",
        "command": "python3",
        "args": ["-I", "-B", "${CLAUDE_PROJECT_DIR}/" + HOOKS_REL + "/" + script],
        "timeout": timeout,
        "onFailure": "block",
    }


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_installed(project, rel):
    """A file already in the project; unreadable → exit 1 before any write."""
    try:
        return read_text(os.path.join(project, rel))
    except (OSError, ValueError) as exc:
        raise InstallError(f"cannot read {rel} ({exc}); remove or fix it and re-run", 1)


def git_exclude_path(project):
    """info/exclude of the project's repository, also when .git is a file
    (worktree, submodule); None when it cannot be found."""
    if os.path.isdir(os.path.join(project, ".git")):
        return os.path.join(project, ".git", "info", "exclude")
    try:
        proc = subprocess.run(["git", "-C", project, "rev-parse", "--git-path", "info/exclude"],
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return os.path.normpath(os.path.join(project, proc.stdout.strip()))


def dump_json(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def is_installed(groups, script):
    marker = f"{HOOKS_REL}/{script}"
    for group in groups:
        for hook in group.get("hooks", []) if isinstance(group, dict) else []:
            if not isinstance(hook, dict):
                continue
            args = hook.get("args", []) or []
            if not isinstance(args, list):
                raise InstallError('a hook in .claude/settings.json has "args" that is not a list; '
                                   "fix it and re-run", 1)
            parts = [hook.get("command", "")] + args
            if any(isinstance(p, str) and marker in p for p in parts):
                return True
    return False


def _object(parent, key, where):
    value = parent.setdefault(key, {})
    if not isinstance(value, dict):
        raise InstallError(f'"{where}" in .claude/settings.json is not an object; fix it and re-run', 1)
    return value


def _union(parent, key, entries, where):
    """Append missing entries to parent[key]; True when something was added."""
    if not entries:
        return False
    current = parent.setdefault(key, [])
    if not isinstance(current, list):
        raise InstallError(f'"{where}" in .claude/settings.json is not a list; fix it and re-run', 1)
    missing = [e for e in entries if e not in current]
    current.extend(missing)
    return bool(missing)


def merged_settings(path, sandbox_lists):
    """(new_text or None when unchanged, existed, warnings)."""
    existed = os.path.exists(path)
    if existed:
        try:
            settings = json.loads(read_text(path))
        except (OSError, ValueError) as exc:
            raise InstallError(f"cannot read .claude/settings.json ({exc}); fix it and re-run", 1)
        if not isinstance(settings, dict):
            raise InstallError(".claude/settings.json is not a JSON object; fix it and re-run", 1)
    else:
        settings = {}
    original = dump_json(settings)
    warnings = []

    hooks = _object(settings, "hooks", "hooks")
    for event, matcher, scripts, timeout in (("PreToolUse", PRE_MATCHER, PRE_HOOKS, 10),
                                             ("PostToolUse", POST_MATCHER, POST_HOOKS, 45),
                                             ("PostToolUse", SYNC_MATCHER, SYNC_HOOKS, 10)):
        groups = hooks.setdefault(event, [])
        if not isinstance(groups, list):
            raise InstallError(f'"hooks.{event}" in .claude/settings.json is not a list; fix it and re-run', 1)
        missing = [s for s in scripts if not is_installed(groups, s)]
        if missing:
            groups.append({"matcher": matcher, "hooks": [hook_entry(s, timeout) for s in missing]})

    sandbox = _object(settings, "sandbox", "sandbox")
    for key, value in SANDBOX_FLAGS:
        if key not in sandbox:
            sandbox[key] = value
        elif sandbox[key] != value:
            # A value someone set on purpose is not overwritten (D18).
            warnings.append(f"sandbox.{key} is {json.dumps(sandbox[key])}, guardrails expect "
                            f"{json.dumps(value)}; a human decides whether to change it")
    deny, allow_write, domains = sandbox_lists
    _union(_object(sandbox, "filesystem", "sandbox.filesystem"), "denyWrite", deny, "sandbox.filesystem.denyWrite")
    _union(sandbox["filesystem"], "allowWrite", allow_write, "sandbox.filesystem.allowWrite")
    if domains:
        _union(_object(sandbox, "network", "sandbox.network"), "allowedDomains", domains,
               "sandbox.network.allowedDomains")

    new = dump_json(settings)
    return (None if existed and new == original else new), existed, warnings


def split_values(values):
    """Accept "--fast-check-include '*.ts' '*.tsx'" as well as one quoted
    "'*.ts *.tsx'" or "'*.ts,*.tsx'" argument; the same for the other lists."""
    return [p for value in values for p in value.replace(",", " ").split()]


include_patterns = split_values


def load_project_config(project):
    """The existing guardrails.json, validated like the hooks do, and its raw keys."""
    try:
        config = guardlib.load_config(project)
        raw = json.loads(read_text(os.path.join(project, CONFIG_REL)))
    except (guardlib.GuardError, OSError, ValueError) as exc:
        raise InstallError(f"{exc}", 1)
    return config, raw


def plan_install(project, fast_check, fast_check_include, allow_domains=(), allow_write=()):
    """([(rel_path, new_text or None, action)], warnings) — validated before
    any write; settings.json comes last."""
    if not os.path.isdir(project):
        raise InstallError(f"project directory not found: {project}", 2)
    if os.path.isfile(os.path.join(project, "skills", "guardrails", "SKILL.md")):
        raise InstallError("this is the skills repository itself; guardrails are not installed here", 2)
    for name in HOOK_FILES:
        if not os.path.isfile(os.path.join(HOOKS_SRC, name)):
            raise InstallError(f"missing hook source {name} in {HOOKS_SRC}", 2)
    for name in ("guardrails.json", "verifier.md"):
        if not os.path.isfile(os.path.join(TEMPLATES, name)):
            raise InstallError(f"missing template {name} in {TEMPLATES}", 2)
    allow_domains, allow_write = split_values(allow_domains), split_values(allow_write)

    steps = []
    for name in HOOK_FILES:
        rel = f"{HOOKS_REL}/{name}"
        new = read_text(os.path.join(HOOKS_SRC, name))
        dest = os.path.join(project, rel)
        if not os.path.exists(dest):
            steps.append((rel, new, "created"))
        elif read_installed(project, rel) != new:
            steps.append((rel, new, "updated"))
        else:
            steps.append((rel, None, "unchanged"))

    template = json.loads(read_text(os.path.join(TEMPLATES, "guardrails.json")))
    config_path = os.path.join(project, CONFIG_REL)
    if os.path.exists(config_path):
        config, raw = load_project_config(project)
        for key in ("allowed_domains", "allow_write"):
            if key not in raw:
                config[key] = template[key]  # a file from an older version
        suggested = {}
        if fast_check or fast_check_include:
            suggested["fast_check"] = fast_check
            suggested["fast_check_include"] = include_patterns(fast_check_include or [])
        for key, values in (("allowed_domains", allow_domains), ("allow_write", allow_write)):
            extra = [v for v in values if v not in config[key]]
            if extra:
                suggested[key] = config[key] + extra
        note = ""
        if suggested:
            note = (" (exists; not changed. A human can set "
                    + ", ".join(f'"{k}": {json.dumps(v)}' for k, v in suggested.items())
                    + " in it; the sandbox lists below use the flags already)")
        steps.append((CONFIG_REL, None, "kept" + note))
    else:
        config = dict(template)
        if fast_check:
            config["fast_check"] = fast_check
        if fast_check_include:
            config["fast_check_include"] = include_patterns(fast_check_include)
        config["allowed_domains"] = config["allowed_domains"] + [
            d for d in allow_domains if d not in config["allowed_domains"]]
        config["allow_write"] = config["allow_write"] + [
            p for p in allow_write if p not in config["allow_write"]]
        steps.append((CONFIG_REL, dump_json(config), "created"))

    verifier_rel = ".claude/agents/verifier.md"
    verifier_template = read_text(os.path.join(TEMPLATES, "verifier.md"))
    verifier = os.path.join(project, verifier_rel)
    if not os.path.exists(verifier):
        steps.append((verifier_rel, verifier_template, "created"))
    elif read_installed(project, verifier_rel) == verifier_template:
        steps.append((verifier_rel, None, "unchanged"))
    else:
        steps.append((verifier_rel, None, "kept (differs from the template; not overwritten)"))

    warnings = []
    lines = ["/" + guardlib.SETTINGS_LOCAL_REL, "/" + guardlib.LOCK_STATE_REL]
    if os.path.lexists(os.path.join(project, ".git")):
        exclude = git_exclude_path(project)
        if exclude is None:
            warnings.append("cannot find the git exclude file (git rev-parse --git-path info/exclude failed); "
                            "add " + " and ".join(lines) + " to it, or the test lock of /10x-tdd "
                            "bug-fix mode shows up as untracked files")
        else:
            exclude_rel = os.path.relpath(exclude, project)
            if exclude_rel.startswith(".."):
                exclude_rel = exclude
            text = read_installed(project, exclude) if os.path.exists(exclude) else ""
            missing = [line for line in lines if line not in text.splitlines()]
            if not missing:
                steps.append((exclude_rel, None, "unchanged"))
            else:
                sep = "" if not text or text.endswith("\n") else "\n"
                steps.append((exclude_rel, text + sep + "".join(f"{line}\n" for line in missing),
                              "updated" if text else "created"))

    # A hook run by hand without -B used to leave __pycache__/ in the project.
    gitignore = os.path.join(project, GITIGNORE_REL)
    text = read_installed(project, GITIGNORE_REL) if os.path.exists(gitignore) else None
    if text is not None and PYCACHE_LINE in (line.strip() for line in text.splitlines()):
        steps.append((GITIGNORE_REL, None, "unchanged"))
    else:
        sep = "" if not text or text.endswith("\n") else "\n"
        steps.append((GITIGNORE_REL, (text or "") + sep + PYCACHE_LINE + "\n",
                      "created" if text is None else "updated"))

    deny = guardlib.sandbox_deny_entries(config["protected"] + guardlib.BUILTIN_PROTECTED,
                                         guardlib.BUILTIN_PROTECTED_HOME)
    domains = config["allowed_domains"] + [d for d in allow_domains if d not in config["allowed_domains"]]
    writes = config["allow_write"] + [p for p in allow_write if p not in config["allow_write"]]
    settings_text, existed, settings_warnings = merged_settings(
        os.path.join(project, ".claude", "settings.json"), (deny, writes, domains))
    warnings += settings_warnings
    if settings_text is None:
        steps.append((".claude/settings.json", None, "unchanged"))
    else:
        steps.append((".claude/settings.json", settings_text, "updated" if existed else "created"))
    return steps, warnings


def write_atomic(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp-guardrails"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except OSError:
        if os.path.isfile(tmp):
            os.remove(tmp)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install guardrails into a project.")
    parser.add_argument("project")
    parser.add_argument("--fast-check", help='command run after each edit; "{file}" is the edited file')
    parser.add_argument("--fast-check-include", nargs="*", default=[], metavar="GLOB",
                        help="only run fast_check for files matching these patterns")
    parser.add_argument("--allow-domain", nargs="*", default=[], metavar="DOMAIN",
                        help="extra hosts sandboxed commands may reach (e.g. pypi.org)")
    parser.add_argument("--allow-write", nargs="*", default=[], metavar="PATH",
                        help="extra paths sandboxed commands may write (e.g. ~/.npm)")
    args = parser.parse_args(argv)
    project = os.path.abspath(args.project)
    try:
        steps, warnings = plan_install(project, args.fast_check, args.fast_check_include,
                                       args.allow_domain, args.allow_write)
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code
    written = []
    for rel, text, action in steps:
        if text is not None:
            try:
                write_atomic(os.path.join(project, rel), text)
            except OSError as exc:
                print(f"error: cannot write {rel} ({exc})", file=sys.stderr)
                print("written before the failure: " + (", ".join(written) or "nothing"), file=sys.stderr)
                print(".claude/settings.json is written last, so no new hook or sandbox setting is active. "
                      "Fix the cause and re-run.", file=sys.stderr)
                return 3
            written.append(rel)
        word = action.split(" ")[0]
        print(f"{word:9} {rel}{action[len(word):]}")
    for warning in warnings:
        print(f"WARN      {warning}")
    print("Nothing changed." if not written else f"Installed guardrails in {project}: {len(written)} file(s) written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
