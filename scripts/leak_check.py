"""Leak check: blocks a commit or push that contains anything that should not be public.

Two layers of rules:

1. Built-in patterns (in this file, safe to publish): AWS access keys, private keys,
   JSON Web Tokens, AWS account IDs, ARNs, email addresses and IP addresses.
   Documentation examples (AWS's ...EXAMPLE keys, example.com, RFC 5737 IPs) are allowed.

2. A personal denylist kept OUTSIDE this repo, because the list itself is private.
   Default location: ~/.config/robo-pizza-qiaowei/denylist.txt
   Override with the ROBO_DENYLIST environment variable.
   One term per line, matched case-insensitively as a whole word.
   A line starting with "re:" is a regular expression. "#" starts a comment.
   If the denylist is missing, the check FAILS - it never silently passes.

Usage:
    python3 scripts/leak_check.py --staged          # pre-commit: staged changes
    python3 scripts/leak_check.py --all             # every tracked/untracked file
    python3 scripts/leak_check.py --message FILE    # commit-msg: the message text
    python3 scripts/leak_check.py --history         # pre-push: every commit, author, message
    python3 scripts/leak_check.py PATH [PATH ...]   # specific files

Exit code 0 = clean, 1 = findings, 2 = setup problem.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_DENYLIST = Path.home() / ".config" / "robo-pizza-qiaowei" / "denylist.txt"
NOREPLY_SUFFIX = "@users.noreply.github.com"

# This file describes the patterns, so it is exempt from the built-in pattern scan.
# It is still scanned against the personal denylist.
SELF = "scripts/leak_check.py"

BUILTIN = [
    ("AWS access key ID", re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA)[A-Z0-9]{16}\b")),
    ("AWS secret key", re.compile(r"(?i)aws.{0,20}secret.{0,20}[=:]\s*['\"]?[A-Za-z0-9/+]{40}\b")),
    ("private key block", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("JSON Web Token", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+")),
    ("AWS ARN", re.compile(r"\barn:aws[a-z-]*:[a-z0-9-]+:[a-z0-9-]*:\d{12}:")),
    ("12-digit account ID", re.compile(r"(?<![\d.])\d{12}(?![\d.])")),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("IPv4 address", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
]

# Values that look sensitive but are published documentation placeholders.
ALLOWED_VALUES = [
    re.compile(r"EXAMPLE"),                                   # AWS docs keys
    re.compile(r"@(?:example\.(?:com|org|net)|[a-z0-9.-]+\.test)\b"),
    re.compile(re.escape(NOREPLY_SUFFIX)),
    re.compile(r"noreply@anthropic\.com"),                   # commit co-author trailer
    re.compile(r"\b111122223333\b|\b123456789012\b"),         # AWS docs account IDs
    re.compile(r"\b(?:127\.0\.0\.1|0\.0\.0\.0|192\.0\.2\.\d+|198\.51\.100\.\d+|203\.0\.113\.\d+)\b"),
]


def load_denylist():
    path = Path(os.environ.get("ROBO_DENYLIST", DEFAULT_DENYLIST)).expanduser()
    if not path.exists():
        print(f"leak-check: denylist not found at {path}", file=sys.stderr)
        print("leak-check: refusing to pass without it (set ROBO_DENYLIST or create the file).",
              file=sys.stderr)
        sys.exit(2)
    rules = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            pattern = line[3:]
        else:
            pattern = r"(?<![\w])" + re.escape(line) + r"(?![\w])"
        try:
            rules.append(re.compile(pattern, re.IGNORECASE))
        except re.error as err:
            print(f"leak-check: bad denylist regex {line!r}: {err}", file=sys.stderr)
            sys.exit(2)
    return rules


def is_allowed(value):
    return any(p.search(value) for p in ALLOWED_VALUES)


def scan_text(name, text, denylist, builtin=True):
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for rule in denylist:
            if rule.search(line):
                # Show the line number only: the term itself is private and
                # terminal output can end up in screenshots or logs.
                findings.append(f"{name}:{lineno}: matches a private denylist term")
                break
        if not builtin:
            continue
        for label, rule in BUILTIN:
            for match in rule.finditer(line):
                if not is_allowed(match.group(0)) and not is_allowed(line):
                    findings.append(f"{name}:{lineno}: looks like an {label}")
    return findings


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def read_file(path):
    data = Path(path).read_bytes()
    if b"\0" in data[:8000]:
        return None  # binary; images are reviewed by eye
    return data.decode("utf-8", errors="replace")


def check_author():
    email = git("config", "user.email").strip()
    if not email.endswith(NOREPLY_SUFFIX):
        return [f"git user.email is {email or '(unset)'}; use your GitHub "
                f"...{NOREPLY_SUFFIX} address so no personal or work email is published"]
    return []


def main(argv):
    denylist = load_denylist()
    findings = []

    if argv and argv[0] == "--message":
        text = Path(argv[1]).read_text(encoding="utf-8")
        text = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
        findings += scan_text("commit message", text, denylist)
    elif argv and argv[0] == "--history":
        # pre-push: every commit about to become public, not just the latest files.
        for sha in git("rev-list", "HEAD").split():
            short = sha[:8]
            author = git("show", "-s", "--format=%ae", sha).strip()
            if not author.endswith(NOREPLY_SUFFIX):
                findings.append(f"commit {short}: author email is not a GitHub noreply address")
            message = git("show", "-s", "--format=%B", sha)
            findings += scan_text(f"commit {short} message", message, denylist)
            for name in git("show", "--format=", "--name-only", sha).split():
                findings += scan_text(f"commit {short} {name} (file name)", name, denylist,
                                      builtin=False)
                try:
                    text = git("show", f"{sha}:{name}")
                except subprocess.CalledProcessError:
                    continue  # file deleted in this commit
                if "\0" in text[:8000]:
                    continue
                findings += scan_text(f"commit {short} {name}", text, denylist,
                                      builtin=(name != SELF))
    elif argv and argv[0] == "--staged":
        findings += check_author()
        names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").split()
        for name in names:
            text = git("show", f":{name}")
            if "\0" in text[:8000]:
                continue
            findings += scan_text(name, text, denylist, builtin=(name != SELF))
            findings += scan_text(f"{name} (file name)", name, denylist, builtin=False)
    else:
        if argv and argv[0] == "--all":
            names = git("ls-files", "--cached", "--others", "--exclude-standard").split("\n")
            names = [n for n in names if n]
        else:
            names = argv
        for name in names:
            text = read_file(name)
            if text is None:
                continue
            findings += scan_text(name, text, denylist, builtin=(name != SELF))
            findings += scan_text(f"{name} (file name)", name, denylist, builtin=False)

    if findings:
        print("leak-check: BLOCKED - fix these before anything leaves this laptop:", file=sys.stderr)
        for f in findings:
            print("  " + f, file=sys.stderr)
        return 1
    if not denylist:
        print("leak-check: note - your private denylist is empty; only built-in patterns ran.")
    print(f"leak-check: clean ({len(denylist)} private terms + built-in patterns)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
