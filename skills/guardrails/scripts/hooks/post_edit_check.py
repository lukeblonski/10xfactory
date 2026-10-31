#!/usr/bin/env python3
"""PostToolUse hook: after a file edit, run "fast_check" from
.claude/guardrails.json on the edited file (e.g. lint it) with a 30 s limit.
On failure, exit 2 so Claude sees the tail of the output. The edit itself is
not undone. Without "fast_check" the hook does nothing."""

import os
import shlex
import subprocess
import sys

# No __pycache__/ next to the hook, also when it runs without -B.
sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import guardlib  # noqa: E402
except BaseException as exc:  # exit 1 would hide the failure from Claude
    print("[guardrails] post-edit check could not run: cannot load guardlib.py "
          f"({type(exc).__name__}: {exc}). Re-run the guardrails installer.", file=sys.stderr)
    sys.exit(2)

TIMEOUT = 30
TAIL_LINES = 40
TAIL_CHARS = 4000


def build_command(command, rel):
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        raise guardlib.GuardError(f'cannot parse "fast_check" ({exc})')
    if not parts:
        raise guardlib.GuardError('"fast_check" is empty')
    if rel.startswith("-"):
        rel = "./" + rel  # a file named "--fix.ts" is not an option
    if any("{file}" in p for p in parts):
        return [p.replace("{file}", rel) for p in parts]
    return parts + [rel]


def _text(value):
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def run_fast_check(argv, cwd, timeout=TIMEOUT):
    """(ok, reason, output). Timeout and a missing program count as failure."""
    try:
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        return False, f"command not found: {argv[0]}", ""
    except subprocess.TimeoutExpired as exc:
        return False, f"timed out after {timeout}s", _text(exc.stdout) + _text(exc.stderr)
    return proc.returncode == 0, f"exit {proc.returncode}", proc.stdout + proc.stderr


def tail(output):
    text = "\n".join(output.rstrip().splitlines()[-TAIL_LINES:])
    return text[-TAIL_CHARS:]


def main():
    try:
        data = guardlib.read_input()
        pdir = guardlib.project_dir(data)
        if data["tool_name"] not in guardlib.FILE_TOOLS:
            return 0
        cfg = guardlib.load_config(pdir)
        if not cfg["fast_check"]:
            return 0
        target = guardlib.file_targets(data, guardlib.session_cwd(data, pdir))[0]
        rels = guardlib.rel_candidates(target, pdir)
        rel = rels[0] if rels else "/"
        if rel.startswith("/") or not os.path.isfile(target):
            return 0
        include = cfg["fast_check_include"]
        if include and not any(guardlib.matches(p, rel) for p in include):
            return 0
        argv = build_command(cfg["fast_check"], rel)
    except guardlib.GuardError as exc:
        print(f"[guardrails] post-edit check could not run: {exc}", file=sys.stderr)
        return guardlib.BLOCK
    ok, reason, output = run_fast_check(argv, pdir)
    if ok:
        return 0
    print(f"[guardrails] fast_check failed for {rel} ({reason})", file=sys.stderr)
    print(f"$ {shlex.join(argv)}", file=sys.stderr)
    if output.strip():
        print(tail(output), file=sys.stderr)
    print("Fix the problem in this file before moving on.", file=sys.stderr)
    return guardlib.BLOCK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # surface bugs to Claude instead of hiding them
        print(f"[guardrails] post-edit check crashed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(guardlib.BLOCK)
