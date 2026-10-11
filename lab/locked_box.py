"""Scene 3, for real: the locked box in AWS Secrets Manager.

    1. Put the pizza shop's password in the box (a secret, encrypted with a KMS key)
    2. Write the list: Robo may open it, the hall monitor may not (IAM policies),
       checked by AWS's own policy evaluator without anyone assuming a role
    3. Robo's way to read it: ask the box at the moment it's needed
    4. Change the combination: a new version becomes AWSCURRENT,
       the old one is kept as AWSPREVIOUS
    5. Clean up: delete the secret and the two roles

The password is random and never printed: the transcript shows only its first
character. Account IDs and ARNs are redacted before anything is saved.

    python3 lab/locked_box.py          # run, print transcript, clean up
    python3 lab/locked_box.py --save   # also write replays/locked-box.txt

Cost: one secret for a few minutes, a handful of API calls - well under one cent.
"""
import json
import os
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "replays" / "locked-box.txt"
PROFILE = os.environ.get("ROBO_PROFILE", "robo")
REGION = "us-east-1"
SECRET = "robo-pizza/pizza-shop-login"
ROLES = {"robo": "robo-pizza-robo", "hall": "robo-pizza-hall-monitor"}

lines = []


def redact(text):
    text = re.sub(r"\b\d{12}\b", "<account>", text)
    return re.sub(r"(secret:robo-pizza/pizza-shop-login)-[A-Za-z0-9]{6}", r"\1-<id>", text)


def say(text=""):
    text = redact(text)
    print(text)
    lines.append(text)


def aws(*args, check=True):
    cmd = ["aws", *args, "--profile", PROFILE, "--region", REGION, "--output", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"aws {' '.join(args[:2])} failed:\n{redact(r.stderr.strip())}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def masked(value):
    return value[0] + "•" * (len(value) - 1)


def cleanup():
    aws("secretsmanager", "delete-secret", "--secret-id", SECRET,
        "--force-delete-without-recovery", check=False)
    for role in ROLES.values():
        aws("iam", "delete-role-policy", "--role-name", role, "--policy-name", "open-the-box", check=False)
        aws("iam", "delete-role", "--role-name", role, check=False)


def main():
    account = aws("sts", "get-caller-identity")["Account"]
    cleanup()  # start from a clean slate if a previous run was interrupted
    time.sleep(2)

    say("# 1. Put the pizza shop's password in the box")
    first = secrets.token_urlsafe(12)
    created = aws("secretsmanager", "create-secret", "--name", SECRET,
                  "--description", "Robo Pizza demo - deleted after the run",
                  "--secret-string", json.dumps({"username": "maple-hill-party", "password": first}),
                  "--tags", json.dumps([{"Key": "project", "Value": "robo-pizza"}]))
    arn = created["ARN"]
    desc = aws("secretsmanager", "describe-secret", "--secret-id", SECRET)
    say(f"$ aws secretsmanager create-secret --name {SECRET}")
    say(f"   ARN: {arn}")
    say(f"   Encrypted with: {desc.get('KmsKeyId', 'aws/secretsmanager (AWS managed key)')}")
    say()

    say("# 2. The list: Robo may open the box, the hall monitor may not")
    trust = json.dumps({"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{account}:root"}, "Action": "sts:AssumeRole"}]})
    for key, role in ROLES.items():
        aws("iam", "create-role", "--role-name", role, "--assume-role-policy-document", trust,
            "--tags", "Key=project,Value=robo-pizza")
    aws("iam", "put-role-policy", "--role-name", ROLES["robo"], "--policy-name", "open-the-box",
        "--policy-document", json.dumps({"Version": "2012-10-17", "Statement": [{
            "Effect": "Allow", "Action": "secretsmanager:GetSecretValue", "Resource": arn}]}))
    for key, label in (("robo", "Robo"), ("hall", "Hall monitor")):
        role_arn = f"arn:aws:iam::{account}:role/{ROLES[key]}"
        result = aws("iam", "simulate-principal-policy", "--policy-source-arn", role_arn,
                     "--action-names", "secretsmanager:GetSecretValue", "--resource-arns", arn)
        decision = result["EvaluationResults"][0]["EvalDecision"]
        say(f"   {label:<13} GetSecretValue on the box -> {decision}")
    say("   (evaluated by IAM's policy simulator; anything not explicitly allowed is denied)")
    say()

    say("# 3. Ask the box at the moment the password is needed")
    got = aws("secretsmanager", "get-secret-value", "--secret-id", SECRET)
    value = json.loads(got["SecretString"])["password"]
    say(f"$ aws secretsmanager get-secret-value --secret-id {SECRET}")
    say(f"   password: {masked(value)}   version stages: {got['VersionStages']}")
    say()

    say("# 4. Change the combination")
    second = secrets.token_urlsafe(12)
    aws("secretsmanager", "put-secret-value", "--secret-id", SECRET,
        "--secret-string", json.dumps({"username": "maple-hill-party", "password": second}))
    versions = aws("secretsmanager", "list-secret-version-ids", "--secret-id", SECRET)["Versions"]
    for v in sorted(versions, key=lambda v: v.get("CreatedDate", 0)):
        say(f"   version {v['VersionId'][:8]}…  {', '.join(v.get('VersionStages', []))}")
    now = json.loads(aws("secretsmanager", "get-secret-value", "--secret-id", SECRET)["SecretString"])["password"]
    say(f"   Robo's next ask gets: {masked(now)}  (the new one: {now == second})")
    say()

    say("# 5. Clean up")
    cleanup()
    say(f"   deleted {SECRET} and roles {', '.join(ROLES.values())}")

    if "--save" in sys.argv:
        REPLAY.write_text("\n".join(lines) + "\n")
        print(f"\nSaved {REPLAY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
