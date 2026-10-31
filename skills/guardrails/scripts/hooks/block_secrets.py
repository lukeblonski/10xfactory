#!/usr/bin/env python3
"""PreToolUse guard: block writing secrets (private keys, AWS keys, sk- and
ghp_ tokens). Files matching "secret_allow" in .claude/guardrails.json are
exempt; Bash commands never are."""

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
    "Never write real secrets into files; read them from the environment. If this "
    "is test data, only a human can allow it: they add the file to \"secret_allow\" "
    "in .claude/guardrails.json themselves (outside Claude). Agent: stop and tell the user."
)


def check(data, pdir):
    cfg = guardlib.load_config(pdir)
    if data["tool_name"] == "Bash":
        texts = [guardlib.bash_command(data)]
        where = "the Bash command"
    elif data["tool_name"] in guardlib.FILE_TOOLS:
        cwd = guardlib.session_cwd(data, pdir)
        target = guardlib.file_targets(data, cwd)[0]
        rels = guardlib.rel_candidates(target, pdir)
        if any(guardlib.matches(p, rel) for p in cfg["secret_allow"] for rel in rels):
            return
        texts = guardlib.written_texts(data["tool_input"])
        where = f"content written to {rels[0]}"
    else:
        raise guardlib.GuardError(f"unsupported tool {data['tool_name']!r}")
    for text in texts:
        found = guardlib.find_secret(text)
        if found:
            name, masked = found
            guardlib.block(f"secret: {name}", f"Found {masked} ({name}) in {where}.", HOW_TO_ALLOW)


if __name__ == "__main__":
    guardlib.run_guard(check)
