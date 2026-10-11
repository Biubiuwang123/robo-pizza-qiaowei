"""Scene 4, for real: asking a directory "who is this?" and "who is in this group?"

AWS Managed Microsoft AD is real Microsoft Active Directory, and systems talk to
it in LDAP. Running one for a demo means a private network, two domain
controllers and a server inside that network to query them, so this lab instead
speaks the same LDAP to Forum Systems' public, read-only test directory
(https://www.forumsys.com/2022/05/10/online-ldap-test-server/):

    1. Look up one person
    2. List a group's members
    3. Ask the yes/no question a system really asks: is this person in this group?

Only anonymous, read-only searches. No sign-in, nothing is changed. Email
attributes are not requested. Uses the ldapsearch tool that ships with macOS.

    python3 lab/staff_roster.py          # print transcript
    python3 lab/staff_roster.py --save   # also write replays/staff-roster.txt
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "replays" / "staff-roster.txt"
SERVER = "ldap://ldap.forumsys.com"
BASE = "dc=example,dc=com"

lines = []


def say(text=""):
    print(text)
    lines.append(text)


def search(filter_, *attrs):
    cmd = ["ldapsearch", "-x", "-LLL", "-H", SERVER, "-b", BASE, filter_, *attrs]
    say("$ ldapsearch -x -LLL -H " + SERVER + f' -b "{BASE}" "{filter_}" ' + " ".join(attrs))
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if out.returncode != 0:
        sys.exit(out.stderr.strip())
    body = [l for l in out.stdout.splitlines() if l.strip()]
    for l in body:
        say("   " + l)
    if not body:
        say("   (no match)")
    return body


def main():
    say("# 1. Who is this? Look up one person")
    search("(uid=euler)", "cn", "objectClass")
    say()
    say("# 2. Who is in this group?")
    search("(ou=mathematicians)", "uniqueMember")
    say()
    say("# 3. The question a system asks: is this person in the group?")
    search(f"(&(ou=mathematicians)(uniqueMember=uid=euler,{BASE}))", "dn")
    search(f"(&(ou=mathematicians)(uniqueMember=uid=newton,{BASE}))", "dn")
    say("   -> euler: yes, newton: no. One list answers every system the same way.")

    if "--save" in sys.argv:
        REPLAY.write_text("\n".join(lines) + "\n")
        print(f"\nSaved {REPLAY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
