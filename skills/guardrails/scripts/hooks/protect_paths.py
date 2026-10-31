#!/usr/bin/env python3
"""PreToolUse guard: block writes to protected paths.

Protected: the "protected" patterns in .claude/guardrails.json plus the
built-in guardrails config files. Handles the file tools; a shell command
passes, because sandbox.filesystem.denyWrite stops its writes.
"""

import os
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
    "Only a human can allow this: they edit .claude/guardrails.json themselves "
    "(outside Claude) and narrow or remove the rule. Agent: do not try another "
    "way to change this path; stop and tell the user what you wanted to change and why."
)


def example_exempt(pattern, rel):
    """A "protected" wildcard pattern without "/" (e.g. ".env.*") does not
    cover a sample file such as ".env.example", as long as the pattern hits
    only the last segment of rel. A hit in a directory (".env.d/x.example"),
    a pattern with "/", an exact pattern, a pattern that names "example"
    itself (such as "*.example") and the built-in list protect "*.example"
    files as before."""
    pattern = pattern.strip()
    if ("/" in pattern or not guardlib.GLOB_CHARS & set(pattern) or "example" in pattern.lower()
            or not guardlib.example_file(rel)):
        return False
    parents = "/".join(seg for seg in rel.split("/")[:-1] if seg)
    return not (parents and guardlib.matches(pattern, parents))


def check(data, pdir):
    cfg = guardlib.load_config(pdir)
    if data["tool_name"] == "Bash":
        return  # a shell write to a protected path is stopped by sandbox.filesystem.denyWrite
    rules = [(p, f"protected: '{p}'", "in \"protected\" of .claude/guardrails.json", True)
             for p in cfg["protected"]]
    rules += [(p, f"built-in: '{p}'", "in the built-in list of guardrails config files", False)
              for p in guardlib.BUILTIN_PROTECTED]
    home = os.path.expanduser("~")
    for target, _ in guardlib.tool_targets(data, pdir):
        for rel in guardlib.rel_candidates(target, home):
            if rel.startswith("/"):
                continue
            for pattern in guardlib.BUILTIN_PROTECTED_HOME:
                if guardlib.matches(pattern, rel) or guardlib.contains(rel, pattern):
                    guardlib.block(
                        f"built-in: '~/{pattern}'",
                        f"Target: ~/{rel}\nThe user's Claude Code settings can switch every hook off.",
                        HOW_TO_ALLOW,
                    )
        for rel in guardlib.rel_candidates(target, pdir):
            for pattern, rule, where, user in rules:
                if user and example_exempt(pattern, rel):
                    continue
                hit = guardlib.matches(pattern, rel)
                if not hit:
                    hit = guardlib.contains(rel, guardlib.literal_prefix(pattern))
                if hit:
                    guardlib.block(
                        rule,
                        f"Target: {rel}\nThe target matches pattern '{pattern}' {where}.",
                        HOW_TO_ALLOW,
                    )


if __name__ == "__main__":
    guardlib.run_guard(check)
