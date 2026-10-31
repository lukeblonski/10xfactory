#!/usr/bin/env python3
"""Ensure an npm project has one `verify` script (lint + typecheck + tests).

    python3 setup_verify.py <project>

If package.json already has "verify", nothing changes. Otherwise "verify" is
built from the existing lint, typecheck and test scripts, in that order;
missing parts are reported as WARN lines. Exit codes: 0 ok; 1 none of lint,
typecheck, test exists (a verify that checks nothing is not created);
2 package.json unreadable; 3 no package.json (not an npm project).
"""

import json
import os
import sys

LINT = ["lint"]
TYPECHECK = ["typecheck", "type-check", "check-types", "tsc", "types"]
TEST = ["test"]
NPM_PLACEHOLDER = "no test specified"


def find(scripts, names):
    for name in names:
        value = scripts.get(name)
        if isinstance(value, str) and value.strip() and NPM_PLACEHOLDER not in value:
            return name
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: setup_verify.py <project>", file=sys.stderr)
        return 2
    path = os.path.join(argv[0], "package.json")
    if not os.path.isfile(path):
        print("no package.json: not an npm project; create an equivalent verify command by hand",
              file=sys.stderr)
        return 3
    try:
        with open(path, encoding="utf-8") as fh:
            package = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"cannot read package.json ({exc})", file=sys.stderr)
        return 2
    if not isinstance(package, dict) or not isinstance(package.get("scripts", {}), dict):
        print("package.json has no usable \"scripts\" object", file=sys.stderr)
        return 2
    scripts = package.setdefault("scripts", {})
    if isinstance(scripts.get("verify"), str) and scripts["verify"].strip():
        print(f"verify exists: {scripts['verify']}")
        return 0

    parts, missing = [], []
    for label, names in (("lint", LINT), ("typecheck", TYPECHECK), ("test", TEST)):
        name = find(scripts, names)
        if name is None:
            missing.append(label)
        else:
            parts.append("npm test" if name == "test" else f"npm run {name}")
    if not parts:
        print("no lint, typecheck or test script found; verify was not created", file=sys.stderr)
        return 1
    scripts["verify"] = " && ".join(parts)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(package, indent=2, ensure_ascii=False) + "\n")
    print(f"created verify: {scripts['verify']}")
    for label in missing:
        print(f"WARN missing: {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
