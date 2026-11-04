"""Shared helpers for the guardrails hooks.

Each hook reads one Claude Code hook-input JSON object from stdin and exits
0 (allow) or 2 (block; the reason on stderr is shown to Claude). A guard that
cannot read its input or its config blocks: it must never report "allowed"
when it did not check anything. Exit code 1 is never used, because Claude
Code treats it as a non-blocking error and lets the action through.

Standard library only.
"""

import fnmatch
import json
import os
import re
import shlex
import sys
import tempfile
import time

BLOCK = 2
FILE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
CONFIG_REL = ".claude/guardrails.json"
LOCKED_TESTS_REL = ".claude/locked-tests"
# What the test-lock hook added to settings.local.json (see sync_locked_tests).
LOCK_STATE_REL = ".claude/locked-tests.sandbox"
# Claude Code reloads settings.local.json on its own schedule: for this long
# after a lock change, shell commands wait (see lock_pending).
LOCK_SETTLE_SECONDS = 5

# Always protected, whatever guardrails.json says: an agent that could edit
# these could switch the guardrails off.
BUILTIN_PROTECTED = [
    ".claude/guardrails.json",
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/hooks/guardrails/**",
    ".claude/agents/verifier.md",
]
# Relative to the user's home: "disableAllHooks" there switches every
# project's hooks off.
BUILTIN_PROTECTED_HOME = [
    ".claude/settings.json",
    ".claude/settings.local.json",
]

SECRET_PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("sk-token", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}")),
    ("github-token", re.compile(r"ghp_[A-Za-z0-9]{36,}")),
]

FIX_CONFIG = (
    "Restore .claude/guardrails.json or re-run the guardrails installer. "
    "Only a human can change this file."
)

GLOB_CHARS = set("*?[")
# Command prefixes that run the next word as the command, with the options
# that take a separate value.
SHELL_PREFIXES = {
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-r", "-t", "-T", "-U"},
    "doas": {"-u", "-C"},
    "env": {"-u", "-C", "-S", "-P"},
    "command": set(),
    "exec": {"-a"},
    "nohup": set(),
    "time": {"-f", "-o"},
    "nice": {"-n"},
    "ionice": {"-c", "-n", "-p"},
    "stdbuf": {"-i", "-o", "-e"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
}
SHELLS = {"bash", "sh", "zsh", "dash"}
SHELL_VALUE_OPTIONS = {"-o", "+o", "-O", "+O"}
INTERPRETERS = {"python", "node", "ruby", "perl", "deno", "bun"}
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
PATCH_VALUE_OPTIONS = {"-p", "-i", "-d", "-o", "-r", "-B", "-F", "-V", "-z", "-D", "-Y", "-g"}
WRITE_ALL_ARGS = {
    "rm", "rmdir", "unlink", "shred", "truncate", "touch", "ln",
    "chmod", "chown", "tee",
}
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&", "<>"}
HEREDOC_RE = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
PATHLIKE_RE = re.compile(r"[A-Za-z0-9_./~-]+")
KNOWN_VARS_RE = re.compile(
    r"\$(?:\{(CLAUDE_PROJECT_DIR|PWD|HOME)\}|(CLAUDE_PROJECT_DIR|PWD|HOME)(?![A-Za-z0-9_]))")
# Stands in for a command substitution whose output is unknown.
UNKNOWN_SUBST = "$__SUBST"


class GuardError(Exception):
    """The guard could not check the action; it must block."""


# ---------------------------------------------------------------- input


def read_input(stream=None):
    raw = (stream or sys.stdin).read()
    if not raw.strip():
        raise GuardError("empty hook input on stdin")
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise GuardError(f"hook input is not valid JSON ({exc})")
    if not isinstance(data, dict):
        raise GuardError("hook input is not a JSON object")
    if not isinstance(data.get("tool_name"), str) or not data["tool_name"]:
        raise GuardError("hook input has no tool_name")
    if not isinstance(data.get("tool_input"), dict):
        raise GuardError("hook input has no tool_input object")
    return data


def project_dir(data):
    pdir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd")
    if not isinstance(pdir, str) or not os.path.isdir(pdir):
        raise GuardError("cannot determine the project directory")
    return os.path.normpath(pdir)


def session_cwd(data, pdir):
    cwd = data.get("cwd")
    return os.path.normpath(cwd) if isinstance(cwd, str) and cwd else pdir


def _string_list(cfg, key, required):
    if key not in cfg:
        if required:
            raise GuardError(f'{CONFIG_REL} has no "{key}" list. {FIX_CONFIG}')
        return []
    value = cfg[key]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise GuardError(f'"{key}" in {CONFIG_REL} must be a list of strings. {FIX_CONFIG}')
    return value


def load_config(pdir):
    path = os.path.join(pdir, CONFIG_REL)
    if not os.path.isfile(path):
        raise GuardError(f"{CONFIG_REL} is missing. {FIX_CONFIG}")
    try:
        with open(path, encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as exc:
        raise GuardError(f"cannot read {CONFIG_REL} ({exc}). {FIX_CONFIG}")
    if not isinstance(cfg, dict):
        raise GuardError(f"{CONFIG_REL} is not a JSON object. {FIX_CONFIG}")
    # The post-edit check is gone: no hook runs a program of the project. An
    # old copy of that hook in a project still reads these two keys, so they
    # are always empty, whatever the file says, and that hook exits 0.
    return {
        "protected": _string_list(cfg, "protected", required=True),
        "secret_allow": _string_list(cfg, "secret_allow", required=False),
        "fast_check": None,
        "fast_check_include": [],
        "allowed_domains": _string_list(cfg, "allowed_domains", required=False),
        "allow_write": _string_list(cfg, "allow_write", required=False),
    }


def file_targets(data, cwd):
    tool_input = data["tool_input"]
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        raise GuardError(f"{data['tool_name']} input has no file_path")
    return [absolute(path, cwd)]


def bash_command(data):
    command = data["tool_input"].get("command")
    if not isinstance(command, str):
        raise GuardError("Bash input has no command")
    return command


def written_texts(value, skip=("old_string", "file_path", "notebook_path")):
    """Every string in tool_input except removed text and paths."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [t for item in value for t in written_texts(item, skip)]
    if isinstance(value, dict):
        return [t for k, v in value.items() if k not in skip for t in written_texts(v, skip)]
    return []


# ---------------------------------------------------------------- paths


def absolute(path, base):
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(base, path)
    return os.path.normpath(path)


def expand(word, base, pdir):
    """Expand what a hook can know for sure: $CLAUDE_PROJECT_DIR, $PWD,
    $HOME (also as ${...}) and a leading ~+. Other variables stay as they are."""
    if word == "~+" or word.startswith("~+/"):
        word = base + word[2:]
    values = {"CLAUDE_PROJECT_DIR": pdir, "PWD": base, "HOME": os.path.expanduser("~")}
    return KNOWN_VARS_RE.sub(lambda m: values[m.group(1) or m.group(2)], word)


def dynamic_tails(path):
    """For a path with an unknown variable, every tail after the last
    unknown segment: "$X/.claude/settings.json" may be the project's own
    .claude/settings.json, so it is checked as that, and as "settings.json"."""
    segments = path.replace(os.sep, "/").split("/")
    last = max(i for i, seg in enumerate(segments) if "$" in seg or "`" in seg)
    rest = [seg for seg in segments[last + 1:] if seg]
    return ["/".join(rest[i:]) for i in range(len(rest))]


def rel_candidates(path, pdir, shell=False):
    """The path relative to the project ("." for the root), as given and
    after resolving symlinks; absolute when outside the project. With
    shell=True (a path from a Bash command), a path with an unknown variable
    gives its tails (see dynamic_tails); in a file tool's path "$" is just a
    character, as in Remix's "routes/$id.tsx"."""
    if shell and ("$" in path or "`" in path):
        return dynamic_tails(path)
    roots = [os.path.normpath(pdir), os.path.realpath(pdir)]
    out = []
    for variant in (os.path.normpath(path), os.path.realpath(path)):
        rel = None
        for root in roots:
            if variant == root:
                rel = "."
            elif variant.startswith(root.rstrip(os.sep) + os.sep):
                rel = os.path.relpath(variant, root)
            if rel:
                break
        rel = (rel or variant).replace(os.sep, "/")
        if rel not in out:
            out.append(rel)
    return out


def _match_segments(pattern, segments):
    if not pattern:
        return not segments
    if pattern[0] == "**":
        return any(_match_segments(pattern[1:], segments[i:]) for i in range(len(segments) + 1))
    return (
        bool(segments)
        and fnmatch.fnmatchcase(segments[0], pattern[0])
        and _match_segments(pattern[1:], segments[1:])
    )


def matches(pattern, rel):
    """gitignore-like: a pattern without "/" matches any path segment at any
    depth; a pattern with "/" matches the project-relative path, where "**"
    stands for any number of segments. Case-insensitive, because the default
    macOS file system is: ".ENV" is the same file as ".env"."""
    pattern, rel = pattern.strip().casefold(), rel.casefold()
    if pattern.startswith("./"):
        pattern = pattern[2:]
    if not pattern:
        return False
    if "/" not in pattern.rstrip("/"):
        return any(fnmatch.fnmatchcase(seg, pattern.rstrip("/")) for seg in rel.split("/") if seg)
    if rel.startswith("/"):
        return False
    return _match_segments(pattern.strip("/").split("/"), rel.split("/"))


def example_file(rel):
    """True when the last segment of rel ends with ".example" (any case):
    a sample file such as ".env.example" holds no secrets."""
    last = rel.replace(os.sep, "/").rstrip("/").rsplit("/", 1)[-1]
    return last.casefold().endswith(".example")


def literal_prefix(pattern):
    """Leading glob-free directory of an anchored pattern ("" if none)."""
    pattern = pattern.strip()
    if pattern.startswith("./"):
        pattern = pattern[2:]
    if "/" not in pattern.rstrip("/"):
        return ""
    prefix = []
    for seg in pattern.strip("/").split("/"):
        if GLOB_CHARS & set(seg):
            break
        prefix.append(seg)
    return "/".join(prefix)


def contains(rel_dir, anchor):
    """True when writing to rel_dir (a directory) can change anchor."""
    if not anchor or rel_dir.startswith("/"):
        return False
    rel_dir, anchor = rel_dir.casefold(), anchor.casefold()
    return rel_dir == "." or anchor == rel_dir or anchor.startswith(rel_dir.rstrip("/") + "/")


# ---------------------------------------------------------------- bash


def strip_heredocs(command):
    """(command without heredoc bodies, [bodies]); the opener line stays
    (it may hold a redirect)."""
    out, pending, bodies = [], [], []
    for line in command.split("\n"):
        if pending:
            dash, word = pending[0]
            if (line.lstrip("\t") if dash else line) == word:
                pending.pop(0)
            else:
                bodies.append(line)
            continue
        out.append(line)
        pending.extend((bool(m.group(1)), m.group(3)) for m in HEREDOC_RE.finditer(line))
    return "\n".join(out), ["\n".join(bodies)] if bodies else []


def strip_comments(text):
    """Drop "#" comments. As in the shell, "#" starts a comment only at the
    start of a word and outside quotes: "s#a#b#" and "a#b" are not comments."""
    out, quote, i = [], None, 0
    while i < len(text):
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                out.append(text[i + 1])
                i += 1
            elif ch == quote:
                quote = None
        elif ch == "\\" and i + 1 < len(text):
            out.append(text[i:i + 2])
            i += 1
        elif ch in "'\"":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or text[i - 1] in " \t\n;&|()"):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _closing_paren(text, start):
    depth, quote, i = 1, None, start
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\" and quote == '"':
                i += 1
            elif ch == quote:
                quote = None
        elif ch == "\\":
            i += 1
        elif ch in "'\"":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text)


def extract_substitutions(text):
    """(text, [inner commands]). Each $(...) and `...` outside single quotes
    is replaced: $(pwd) and `pwd` by $PWD, anything else by UNKNOWN_SUBST,
    so a path like "$(git rev-parse --show-toplevel)/.env" stays one word.
    The inner commands are checked on their own."""
    out, inner, quote, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if quote == "'":
            out.append(ch)
            if ch == "'":
                quote = None
            i += 1
            continue
        if ch == "\\" and i + 1 < len(text):
            out.append(text[i:i + 2])
            i += 2
            continue
        if text.startswith("$(", i):
            end = _closing_paren(text, i + 2)
            body = text[i + 2:end]
        elif ch == "`":
            end = text.find("`", i + 1)
            end = len(text) if end < 0 else end
            body = text[i + 1:end]
        else:
            if ch == "'" and quote is None:
                quote = "'"
            elif ch == '"':
                quote = None if quote == '"' else '"'
            out.append(ch)
            i += 1
            continue
        i = end + 1
        if body.strip() in ("pwd", "pwd -P", "pwd -L"):
            out.append("$PWD")
        else:
            inner.append(body)
            out.append(UNKNOWN_SUBST)
    return "".join(out), inner


def split_commands(text):
    """Split on newline ; && || | & ( ) outside quotes; keep >& and &> intact."""
    parts, buf, quote, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if quote:
            buf.append(ch)
            if ch == "\\" and quote == '"' and i + 1 < len(text):
                buf.append(text[i + 1])
                i += 1
            elif ch == quote:
                quote = None
        elif ch == "\\" and i + 1 < len(text):
            buf.append(text[i:i + 2])
            i += 1
        elif ch in "'\"":
            quote = ch
            buf.append(ch)
        elif ch in "\n;()" or (ch == "|" and text[i - 1:i] != ">"):
            parts.append("".join(buf))
            buf = []
            if text[i:i + 2] == "||":
                i += 1
        elif ch == "&":
            prev, nxt = text[i - 1:i], text[i + 1:i + 2]
            if prev == ">" or nxt == ">":
                buf.append(ch)
            else:
                parts.append("".join(buf))
                buf = []
                if nxt == "&":
                    i += 1
        else:
            buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return [p.strip() for p in parts if p.strip()]


def tokenize(simple):
    try:
        lexer = shlex.shlex(simple, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""  # comments are already gone (strip_comments)
        return list(lexer)
    except ValueError:
        return simple.split()


def _options_split(args):
    """Non-option arguments (everything after "--" counts as non-option)."""
    out, after_dashes = [], False
    for arg in args:
        if after_dashes:
            out.append(arg)
        elif arg == "--":
            after_dashes = True
        elif not arg.startswith("-") or arg == "-":
            out.append(arg)
    return out


def _option_values(args, shorts, longs):
    """Values of the given options: "-o F", "-oF", "-sSo F", "--output F",
    "--output=F"."""
    out, i = [], 0
    while i < len(args):
        arg = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else None
        if arg.startswith("--"):
            key, eq, value = arg.partition("=")
            if key in longs:
                if eq:
                    out.append(value)
                elif nxt is not None:
                    out.append(nxt)
                    i += 1
        elif arg.startswith("-") and len(arg) > 1:
            for j, letter in enumerate(arg[1:], 1):
                if letter in shorts:
                    if arg[j + 1:]:
                        out.append(arg[j + 1:])
                    elif nxt is not None:
                        out.append(nxt)
                        i += 1
                    break
        i += 1
    return out


def _has_inplace(args):
    for arg in args:
        if arg == "--in-place" or arg.startswith("--in-place="):
            return True
        if arg.startswith("-") and not arg.startswith("--") and "i" in arg[1:]:
            return True
    return False


def _awk_inplace(args):
    for i, arg in enumerate(args):
        if arg in ("-i", "--include") and args[i + 1:i + 2] == ["inplace"]:
            return True
        if arg in ("-iinplace", "--include=inplace"):
            return True
    return False


def _strip_prefixes(argv):
    """Drop VAR=value words and wrappers such as sudo, env, timeout 5, nice -n 5."""
    while argv:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0]):
            argv.pop(0)
            continue
        name = os.path.basename(argv[0])
        if name not in SHELL_PREFIXES:
            break
        argv.pop(0)
        while argv and (argv[0].startswith("-") or "=" in argv[0]):
            opt = argv.pop(0)
            if opt == "--":
                break
            if opt in SHELL_PREFIXES[name] and argv:
                argv.pop(0)
        if name == "timeout" and argv:
            argv.pop(0)  # the duration
    return argv


def _shell_code(args):
    """The command string of "bash -c CMD", also "-lc", "-ec", "-o x -c"."""
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in SHELL_VALUE_OPTIONS:
            i += 2
            continue
        if re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", arg):
            rest = [a for a in args[i + 1:] if not a.startswith(("-", "+"))]
            return rest[0] if rest else None
        if not arg.startswith(("-", "+")):
            return None  # a script file
        i += 1
    return None


def _inline_code(name, args, has_heredoc, bodies):
    """The code an interpreter gets on the command line or from a heredoc,
    or None. Arguments after a script or "-m module" belong to that program,
    so "python3 -m pytest -p no:cacheprovider x" runs no inline code."""
    kind = re.sub(r"[0-9.]+$", "", name)
    if kind not in INTERPRETERS:
        return None
    codes, i = [], 0
    while i < len(args):
        arg = args[i]
        nxt = args[i + 1] if i + 1 < len(args) else ""
        if arg == "-":
            codes += bodies  # code from stdin
            break
        if not arg.startswith("-"):
            if kind == "deno" and arg == "eval":
                codes.append(nxt)
            break  # a script or subcommand
        if kind == "python":
            if arg == "-m":
                break
            if arg in ("-W", "-X"):
                i += 2
                continue
            if re.fullmatch(r"-[A-Za-z]*c", arg):
                codes.append(nxt)
                break
        elif kind in ("node", "bun", "deno"):
            key, eq, value = arg.partition("=")
            if key in ("-e", "-p", "--eval", "--print"):
                codes.append(value if eq else nxt)
                break
        elif re.fullmatch(r"-[A-Za-z.]*[eE]", arg):  # perl, ruby: -e, -pe, -ne, -E
            codes.append(nxt)
            break
        i += 1
    if has_heredoc and not codes:
        codes += bodies
    return codes or None


def _copy_targets(args, base, moving):
    dest_dir, rest, i = None, [], 0
    while i < len(args):
        arg = args[i]
        if arg in ("-t", "--target-directory") and i + 1 < len(args):
            dest_dir = args[i + 1]
            i += 1
        elif arg.startswith("--target-directory="):
            dest_dir = arg.split("=", 1)[1]
        else:
            rest.append(arg)
        i += 1
    paths = _options_split(rest)
    if dest_dir is None:
        if len(paths) < 2:
            return []
        dest, sources = paths[-1], paths[:-1]
    else:
        dest, sources = dest_dir, paths
    dest_abs = absolute(dest, base)
    if dest_dir is not None or dest.endswith("/") or os.path.isdir(dest_abs):
        targets = [os.path.join(dest_abs, os.path.basename(s.rstrip("/"))) for s in sources]
    else:
        targets = [dest_abs]
    if moving:
        targets += [absolute(s, base) for s in sources]
    return targets


def _rsync_targets(args, base):
    paths = _options_split(args)
    if len(paths) < 2:
        return []
    dest = absolute(paths[-1], base)
    names = [os.path.basename(s.rstrip("/")) for s in paths[:-1]]
    return [dest] + [os.path.join(dest, n) for n in names if n]


def _patch_targets(args, base):
    """The file "patch FILE [PATCH]" changes and "-o OUT". Files named only
    inside the diff ("patch -p1 < x.diff") are a known limit."""
    targets, positional, i = [], [], 0
    while i < len(args):
        arg = args[i]
        if arg in PATCH_VALUE_OPTIONS and i + 1 < len(args):
            if arg == "-o":
                targets.append(absolute(args[i + 1], base))
            elif arg == "-d":
                base = absolute(args[i + 1], base)
            i += 2
            continue
        if arg.startswith("--output="):
            targets.append(absolute(arg.split("=", 1)[1], base))
        elif not arg.startswith("-"):
            positional.append(arg)
        i += 1
    if positional:
        targets.append(absolute(positional[0], base))
    return targets


def _restores_index_only(args):
    """"git restore --staged" without --worktree only unstages."""
    flags = set()
    for arg in args:
        if arg == "--":
            break
        if arg.startswith("--"):
            flags.add(arg)
        elif arg.startswith("-") and len(arg) > 1:
            flags.update("-" + ch for ch in arg[1:])
    return bool(flags & {"--staged", "-S"}) and not flags & {"--worktree", "-W"}


def _git_targets(args, base, pdir):
    """(targets, new_base) for a git invocation."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        if args[i] in GIT_VALUE_OPTIONS and i + 1 < len(args):
            if args[i] == "-C":
                base = absolute(args[i + 1], base)
            i += 1
        i += 1
    if i >= len(args):
        return [], base
    sub, rest = args[i], args[i + 1:]
    if sub == "restore" and _restores_index_only(rest):
        return [], base
    if sub in ("rm", "mv"):
        return [absolute(a, base) for a in _options_split(rest)], base
    if sub in ("checkout", "restore"):
        if "--" in rest:
            k = rest.index("--")
            revision, paths = _options_split(rest[:k]), rest[k + 1:]
        else:
            revision, paths = [], _options_split(rest)
            if sub == "checkout" and len(paths) > 1:
                revision, paths = paths[:1], paths[1:]
        if any(a in ("-s", "--source") or a.startswith("--source=") for a in rest):
            revision = revision or ["--source"]
        found = [absolute(a, base) for a in paths]
        # Restoring the whole project from the index or HEAD only brings back
        # tracked content; from another revision it can roll back anything.
        return [p for p in found if revision or p != os.path.normpath(pdir)], base
    return [], base


def bash_write_targets(command, cwd, pdir=None):
    """[(absolute_path, kind)] the command may write; kind is "write" or
    "mention" (a path named inside inline interpreter code). A path that
    still holds an unknown variable is checked by its tails (rel_candidates)."""
    pdir = pdir or cwd
    targets = []
    base, previous, stack = cwd, cwd, []
    text, bodies = strip_heredocs(command)
    text, inner = extract_substitutions(strip_comments(text))
    for sub in inner:
        targets += bash_write_targets(sub, cwd, pdir)
    for simple in split_commands(text):
        tokens = [expand(t, base, pdir) for t in tokenize(simple)]
        argv, i = [], 0
        while i < len(tokens):
            tok = tokens[i]
            if tok in REDIRECTS and i + 1 < len(tokens):
                dest = tokens[i + 1]
                if not (tok == ">&" and dest.isdigit()) and dest != "/dev/null":
                    targets.append((absolute(dest, base), "write"))
                i += 2
                continue
            if tok in ("<", "<<", "<<<", "<<-") :
                if tok == "<" and i + 1 < len(tokens):
                    i += 2
                    continue
                argv.append(tok)
                i += 1
                continue
            argv.append(tok)
            i += 1
        argv = _strip_prefixes(argv)
        if not argv:
            continue
        name, args = os.path.basename(argv[0]), [a for a in argv[1:] if a not in ("<<", "<<<", "<<-")]
        has_heredoc = any(a in ("<<", "<<<", "<<-") for a in argv[1:])
        if name in ("cd", "pushd"):
            dest = _options_split(args)
            if name == "pushd":
                stack.append(base)
            if not dest:
                new = os.path.expanduser("~") if name == "cd" else base
            elif dest[0] == "-":
                new = previous
            else:
                new = absolute(dest[0], base)
            previous, base = base, new
        elif name == "popd":
            if stack:
                previous, base = base, stack.pop()
        elif name in SHELLS:
            code = _shell_code(args)
            if code is not None:
                targets += bash_write_targets(code, base, pdir)
        elif name == "eval":
            targets += bash_write_targets(" ".join(args), base, pdir)
        elif name in WRITE_ALL_ARGS:
            targets += [(absolute(a, base), "write") for a in _options_split(args) if a]
        elif name in ("sed", "perl", "ruby") and _has_inplace(args):
            targets += [(absolute(a, base), "write") for a in _options_split(args) if a]
        elif name in ("awk", "gawk") and _awk_inplace(args):
            targets += [(absolute(a, base), "write") for a in _options_split(args) if a and a != "inplace"]
        elif name in ("cp", "install"):
            targets += [(t, "write") for t in _copy_targets(args, base, moving=False)]
        elif name == "mv":
            targets += [(t, "write") for t in _copy_targets(args, base, moving=True)]
        elif name == "rsync":
            targets += [(t, "write") for t in _rsync_targets(args, base)]
        elif name == "patch":
            targets += [(t, "write") for t in _patch_targets(args, base)]
        elif name == "curl":
            targets += [(absolute(v, base), "write") for v in _option_values(args, "o", {"--output"})]
        elif name == "wget":
            longs = {"--output-document", "--output-file", "--append-output"}
            targets += [(absolute(v, base), "write") for v in _option_values(args, "Ooa", longs)]
        elif name == "dd":
            targets += [(absolute(a[3:], base), "write") for a in args if a.startswith("of=")]
        elif name == "git":
            found, base = _git_targets(args, base, pdir)
            targets += [(t, "write") for t in found]
        # Code run by an interpreter can write anywhere; treat every path it
        # names as a possible target. Reading a protected file this way is
        # blocked too, which is the cautious side.
        # Only words that look like paths (a "/" or a leading dot) count, so
        # "import secrets" is not the protected directory "secrets".
        for code in _inline_code(name, args, has_heredoc, bodies) or []:
            for token in PATHLIKE_RE.findall(code):
                if token.strip("./~-") and ("/" in token or token.startswith(".")):
                    targets.append((absolute(token, base), "mention"))
    return targets


# ---------------------------------------------------------------- sandbox
# The Claude Code sandbox enforces writes for every shell command at the OS
# level; the Bash parsing above is only an extra, earlier layer. Paths in
# sandbox.filesystem lists: "./<path>" is project-relative, "~/<path>"
# home-relative, "//<path>" absolute.

SETTINGS_LOCAL_REL = ".claude/settings.local.json"


def sandbox_deny_entries(patterns, home_patterns=()):
    """sandbox.filesystem.denyWrite entries for gitignore-like patterns: a
    pattern without "/" matches at any depth ("./.env" and "./**/.env"); a
    trailing "/**" covers the directory. A pattern with "**" segments also
    gets each entry without some of them ("./secrets" before "./**/secrets",
    "./config/x.key" before "./config/**/x.key"), as the sandbox docs do not
    say whether "**" matches zero directories.
    Wildcards work on macOS; on Linux the sandbox skips entries with "*",
    "?" or "[" (SKILL.md, Known limits)."""
    out = []
    for pattern in patterns:
        p = pattern.strip()
        if p.startswith("./"):
            p = p[2:]
        anchored = "/" in p.rstrip("/")  # the same rule as matches()
        while p.endswith("/**"):
            p = p[:-3]
        p = p.strip("/")
        if not p:
            continue
        if anchored:
            forms = [[]]
            for seg in p.split("/"):
                forms = (forms if seg == "**" else []) + [f + [seg] for f in forms]
            entries = [f"./{'/'.join(f)}" for f in forms if f]
        else:
            entries = [f"./{p}", f"./**/{p}"]
        out += [e for e in entries if e not in out]
    for pattern in home_patterns:
        entry = "~/" + pattern.strip("/")
        if entry not in out:
            out.append(entry)
    return out


def _lock_entries(line, pdir):
    """The path as written and its symlink target: a shell command must not
    repoint a locked link either."""
    path = absolute(line, pdir)
    out = []
    for p in (path, os.path.realpath(path)):
        entry = "//" + p.lstrip("/")
        if entry not in out:
            out.append(entry)
    return out


def _write_json_atomic(path, value):
    """Write through a unique temp file: hooks of parallel tool calls run at
    the same time."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _read_lock_state(path):
    """(entries the hook added to settings.local.json, whether it created the
    file, when it last changed the lock). A missing or unreadable state owns
    nothing, so nothing a human wrote is ever removed (a stale lock entry is
    the safe side)."""
    try:
        with open(path, encoding="utf-8") as fh:
            state = json.load(fh)
        entries = state["entries"]
        changed_at = state.get("changed_at", 0)
        if (isinstance(entries, list) and all(isinstance(e, str) for e in entries)
                and isinstance(changed_at, (int, float))):
            return entries, state.get("created_file") is True, changed_at
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        pass
    return [], False, 0


def lock_pending(pdir):
    """True while a lock added in the last LOCK_SETTLE_SECONDS may not have
    reached the sandbox yet."""
    entries, _, changed_at = _read_lock_state(os.path.join(pdir, LOCK_STATE_REL))
    return bool(entries) and abs(time.time() - changed_at) < LOCK_SETTLE_SECONDS


def read_locked_lines(pdir):
    """Entries of .claude/locked-tests ([] when the file is absent)."""
    path = os.path.join(pdir, LOCKED_TESTS_REL)
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise GuardError(f"cannot read {LOCKED_TESTS_REL} ({exc})")
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def sync_locked_tests(pdir):
    """Mirror .claude/locked-tests into sandbox.filesystem.denyWrite of
    .claude/settings.local.json, so the sandbox blocks shell writes to a
    locked test too. Claude Code reloads the file and applies it to the next
    sandboxed command. The entries the hook added are recorded in
    .claude/locked-tests.sandbox and only those are removed when the lock is
    lifted; every other entry and key is left alone, and the file is deleted
    only when the hook created it. Returns True when settings were written."""
    wanted = []
    for line in read_locked_lines(pdir):
        wanted += [e for e in _lock_entries(line, pdir) if e not in wanted]
    path = os.path.join(pdir, SETTINGS_LOCAL_REL)
    state_path = os.path.join(pdir, LOCK_STATE_REL)
    if not wanted and not os.path.exists(state_path):
        return False  # no lock now and nothing of ours from an earlier one
    owned, created_before, changed_before = _read_lock_state(state_path)
    exists = os.path.exists(path)
    settings, current = {}, []
    if exists:
        try:
            with open(path, encoding="utf-8") as fh:
                settings = json.load(fh)
            if not isinstance(settings, dict):
                raise ValueError("not a JSON object")
            fs = settings.get("sandbox", {}).get("filesystem", {})
            current = fs.get("denyWrite", [])
            if not isinstance(current, list):
                raise ValueError("sandbox.filesystem.denyWrite is not a list")
        except (OSError, ValueError, AttributeError) as exc:
            if not wanted:
                return False  # nothing to lock; leave the user's file (and our record) alone
            raise GuardError(f"cannot add the test lock to {SETTINGS_LOCAL_REL} ({exc}); "
                             "fix that file so the sandbox can lock the test")
    created = created_before if owned else not exists
    user = [e for e in current if e not in owned]
    added = [e for e in wanted if e not in user]
    new = user + added
    changed_at = time.time() if new != current else changed_before
    try:
        recorded = (owned, created_before, changed_before)
        claim = owned + [e for e in added if e not in owned]
        if claim != owned:  # record ownership before the entries appear
            recorded = (claim, created, changed_at)
            _write_json_atomic(state_path, {"entries": claim, "created_file": created, "changed_at": changed_at})
        if new != current:
            sandbox = settings.setdefault("sandbox", {})
            fs = sandbox.setdefault("filesystem", {})
            if new:
                fs["denyWrite"] = new
            else:
                fs.pop("denyWrite", None)
                if not fs:
                    sandbox.pop("filesystem")
                if not sandbox:
                    settings.pop("sandbox")
            if not settings and created:
                os.remove(path)
            else:
                _write_json_atomic(path, settings)
        if not added:
            if os.path.exists(state_path):
                os.remove(state_path)
        elif (added, created, changed_at) != recorded:
            _write_json_atomic(state_path, {"entries": added, "created_file": created, "changed_at": changed_at})
    except OSError as exc:
        raise GuardError(f"cannot write {SETTINGS_LOCAL_REL} or {LOCK_STATE_REL} ({exc})")
    return new != current


# ---------------------------------------------------------------- output


def mask(secret):
    return secret[:4] + "…"


def find_secret(text):
    for name, pattern in SECRET_PATTERNS:
        found = pattern.search(text)
        if found:
            return name, mask(found.group(0))
    return None


def block(rule, detail, how_to_allow):
    print(f"[guardrails] BLOCKED ({rule})", file=sys.stderr)
    print(detail, file=sys.stderr)
    print(how_to_allow, file=sys.stderr)
    sys.exit(BLOCK)


def tool_targets(data, pdir):
    """[(absolute_path, kind)] for a file tool or a Bash call."""
    cwd = session_cwd(data, pdir)
    tool = data["tool_name"]
    if tool in FILE_TOOLS:
        return [(p, "write") for p in file_targets(data, cwd)]
    if tool == "Bash":
        return bash_write_targets(bash_command(data), cwd, pdir)
    raise GuardError(f"unsupported tool {tool!r}; update the guardrails hooks to handle it")


def run_guard(check):
    """Run check(data, project_dir); any failure to check blocks."""
    try:
        data = read_input()
        check(data, project_dir(data))
    except SystemExit:
        raise
    except GuardError as exc:
        block("guardrails-error", f"The guard could not check this action: {exc}", FIX_CONFIG
              if "guardrails.json" in str(exc) else
              "Nothing was changed. Report this to the user instead of working around it.")
    except Exception as exc:  # fail closed on bugs too
        block("guardrails-error", f"Internal error in the guard: {type(exc).__name__}: {exc}",
              "Nothing was changed. Report this to the user instead of working around it.")
    sys.exit(0)
