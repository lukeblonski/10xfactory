#!/usr/bin/env python3
"""PreToolUse guard: while .claude/locked-tests exists, block writes to the
test files it lists (one path per line, "#" comments allowed). Used by the
bug-fix mode of /10x-tdd: the failing repro test must not change.

On every run (PreToolUse and PostToolUse) it also mirrors the list into the
sandbox's denyWrite in .claude/settings.local.json, so the OS sandbox blocks
shell writes the Bash parsing cannot see. Claude Code applies that file on
its own schedule, so for a few seconds after a lock change every other shell
command waits ("lock-pending"); "touch -c <locked test>" is let through as
the probe that shows the sandbox has the lock (it fails there with
"Operation not permitted", and touch -c never changes content)."""

import os
import shlex
import sys

# No __pycache__/ next to the hook, also when it runs without -B.
sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import guardlib  # noqa: E402
except BaseException as exc:  # exit 1 would let the action through
    print("[guardrails] BLOCKED (guardrails-error)\n"
          f"Cannot load guardlib.py next to this hook: {type(exc).__name__}: {exc}\n"
          "Re-run the guardrails installer. Nothing was changed.", file=sys.stderr)
    sys.exit(2)

HOW_TO_ALLOW = (
    "Bug-fix mode: this test reproduces the bug and must not change. Fix the "
    "production code instead. If you think the test itself is wrong, stop and "
    "tell the user; do not remove the lock to edit it."
)


def locked_paths(pdir):
    locked = []
    for line in guardlib.read_locked_lines(pdir):
        locked += guardlib.rel_candidates(guardlib.absolute(line, pdir), pdir)
    return locked


PENDING_HOW = (
    "Wait a few seconds and run the command again. To check that the lock has "
    "reached the sandbox, run `touch -c <locked test>`: it must fail with "
    "\"Operation not permitted\"."
)


def is_lock_probe(command, locked, pdir):
    """Exactly "touch -c <locked test> ...": changes no content, creates
    nothing, and runs in the sandbox, so it shows whether the lock is there."""
    if any(c in command for c in ";&|<>$`()\n\\*?[{~#"):
        return False
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    if len(argv) < 3 or argv[:2] != ["touch", "-c"]:
        return False
    folded = {test.casefold() for test in locked}
    return all(any(rel.casefold() in folded for rel in guardlib.rel_candidates(guardlib.absolute(arg, pdir), pdir))
               for arg in argv[2:])


def check(data, pdir):
    guardlib.sync_locked_tests(pdir)
    if data.get("hook_event_name") == "PostToolUse":
        return  # after a tool ran: only keep the sandbox lock in sync
    locked = locked_paths(pdir)
    shell = data["tool_name"] == "Bash"
    if shell and is_lock_probe(guardlib.bash_command(data), locked, pdir):
        return
    targets = guardlib.tool_targets(data, pdir)
    for target, kind in targets:
        for rel in guardlib.rel_candidates(target, pdir, shell):
            for test in locked:
                if rel.casefold() == test.casefold() or (kind == "write" and guardlib.contains(rel, test)):
                    guardlib.block(
                        f"locked-test: {test}",
                        f"Target: {rel}\n{test} is listed in {guardlib.LOCKED_TESTS_REL}.",
                        HOW_TO_ALLOW,
                    )
    if shell and guardlib.lock_pending(pdir):
        guardlib.block(
            "lock-pending",
            f"The test lock in {guardlib.LOCKED_TESTS_REL} changed less than "
            f"{guardlib.LOCK_SETTLE_SECONDS} s ago and may not be in the sandbox yet.",
            PENDING_HOW,
        )


if __name__ == "__main__":
    guardlib.run_guard(check)
