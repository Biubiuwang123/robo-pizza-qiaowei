"""Scene 1, for real: the sign-in desk in Amazon Cognito.

    1. Open a sign-in desk (a user pool, Lite plan) and register the teacher
    2. She signs in and gets wristbands: ID, access and refresh tokens
    3. Any room can check the seal on its own: fetch the desk's public keys
       (JWKS) and verify the RS256 signature locally, no call back to the desk
    4. Edit the wristband -> the seal breaks
    5. A quiet renewal with the refresh token, no password typed
    6. Someone guesses passwords -> the desk starts refusing
    7. Close the desk: delete the user pool

Tokens are never printed whole: only decoded claims and the first few
characters of the signature. Pool IDs and account IDs are redacted.
The teacher's email uses the reserved .example domain; no email is sent.

    python3 lab/front_door.py          # run, print transcript, clean up
    python3 lab/front_door.py --save   # also write replays/front-door.txt

Cost: one user pool for about a minute, one user - inside the free tier.
"""
import base64
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "replays" / "front-door.txt"
PROFILE = os.environ.get("ROBO_PROFILE", "robo")
REGION = "us-east-1"
POOL_NAME = "robo-pizza-front-door"
TEACHER = "ms.rivera@maplehill.example"

lines = []
pool_ids = set()


def redact(text):
    for pid in pool_ids:
        text = text.replace(pid, "us-east-1_<pool>")
    return re.sub(r"\b\d{12}\b", "<account>", text)


def say(text=""):
    text = redact(text)
    print(text)
    lines.append(text)


def aws(*args, check=True):
    cmd = ["aws", "cognito-idp", *args, "--profile", PROFILE, "--region", REGION, "--output", "json"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"cognito-idp {args[0]} failed:\n{redact(r.stderr.strip())}")
    return (json.loads(r.stdout) if r.stdout.strip() else {}), r


def b64url_decode(part):
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


def b64url_int(part):
    return int.from_bytes(b64url_decode(part), "big")


def decode(token):
    header, payload, sig = token.split(".")
    return json.loads(b64url_decode(header)), json.loads(b64url_decode(payload)), sig


def rs256_valid(token, jwks):
    """Verify an RS256 JWT signature with only the standard library (PKCS#1 v1.5, SHA-256)."""
    header_b64, payload_b64, sig_b64 = token.split(".")
    header = json.loads(b64url_decode(header_b64))
    key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
    if key is None:
        return False
    n, e = b64url_int(key["n"]), b64url_int(key["e"])
    k_len = (n.bit_length() + 7) // 8
    signed = pow(int.from_bytes(b64url_decode(sig_b64), "big"), e, n).to_bytes(k_len, "big")
    digest_info = bytes.fromhex("3031300d060960864801650304020105000420")
    expected = digest_info + hashlib.sha256(f"{header_b64}.{payload_b64}".encode()).digest()
    padding = b"\x00\x01" + b"\xff" * (k_len - len(expected) - 3) + b"\x00"
    return signed == padding + expected


def delete_pools():
    pools, _ = aws("list-user-pools", "--max-results", "60")
    for p in pools.get("UserPools", []):
        if p["Name"] == POOL_NAME:
            pool_ids.add(p["Id"])
            aws("delete-user-pool", "--user-pool-id", p["Id"], check=False)
            return p["Id"]
    return None


def main():
    delete_pools()  # clean slate if an earlier run was interrupted

    say("# 1. Open a sign-in desk and register the teacher")
    pool, _ = aws("create-user-pool", "--pool-name", POOL_NAME, "--user-pool-tier", "LITE",
                  "--policies", json.dumps({"PasswordPolicy": {"MinimumLength": 12, "RequireNumbers": True}}),
                  "--username-attributes", "email",
                  "--user-pool-tags", "project=robo-pizza")
    pool_id = pool["UserPool"]["Id"]
    pool_ids.add(pool_id)
    client, _ = aws("create-user-pool-client", "--user-pool-id", pool_id, "--client-name", "party-site",
                    "--explicit-auth-flows", "ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH")
    client_id = client["UserPoolClient"]["ClientId"]
    password = secrets.token_urlsafe(12) + "7"
    aws("admin-create-user", "--user-pool-id", pool_id, "--username", TEACHER,
        "--message-action", "SUPPRESS", "--user-attributes", "Name=email,Value=" + TEACHER,
        "Name=email_verified,Value=true")
    aws("admin-set-user-password", "--user-pool-id", pool_id, "--username", TEACHER,
        "--password", password, "--permanent")
    say(f"   user pool {pool_id} (Lite plan), app client 'party-site'")
    say(f"   teacher {TEACHER} registered")
    _, weak = aws("admin-set-user-password", "--user-pool-id", pool_id, "--username", TEACHER,
                  "--password", "pizza1", "--permanent", check=False)
    say(f"   try a weak password 'pizza1' -> {'rejected: ' + weak.stderr.split(':')[-1].strip() if weak.returncode else 'accepted'}")
    say()

    say("# 2. She signs in and gets wristbands")
    auth, _ = aws("initiate-auth", "--client-id", client_id, "--auth-flow", "USER_PASSWORD_AUTH",
                  "--auth-parameters", f"USERNAME={TEACHER},PASSWORD={password}")
    res = auth["AuthenticationResult"]
    id_token, access_token, refresh = res["IdToken"], res["AccessToken"], res["RefreshToken"]
    for name, tok in (("ID token", id_token), ("access token", access_token)):
        h, p, sig = decode(tok)
        keep = {k: p[k] for k in ("token_use", "email", "scope", "iss") if k in p}
        say(f"   {name}: header {json.dumps({'alg': h['alg'], 'kid': h['kid'][:6] + '…'}, ensure_ascii=False)}")
        say(f"      claims {json.dumps(keep)}")
        say(f"      lifetime {p['exp'] - p['iat']} seconds   signature {sig[:10]}…")
    say(f"   refresh token: {len(refresh)} characters, opaque (kept out of sight)")
    say()

    say("# 3. A room checks the seal on its own")
    jwks_url = f"https://cognito-idp.{REGION}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    jwks = json.loads(urllib.request.urlopen(jwks_url, timeout=10).read())
    say(f"$ curl {jwks_url}")
    say(f"   {len(jwks['keys'])} public keys: " + ", ".join(f"{k['alg']} kid {k['kid'][:6]}…" for k in jwks["keys"]))
    say(f"   RS256 signature on the ID token, checked locally -> {'VALID' if rs256_valid(id_token, jwks) else 'INVALID'}")
    say()

    say("# 4. Edit the wristband")
    h64, p64, s64 = id_token.split(".")
    claims = json.loads(b64url_decode(p64))
    claims["email"] = "principal@maplehill.example"
    forged = h64 + "." + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=") + "." + s64
    say(f"   email changed to {claims['email']} -> signature {'VALID' if rs256_valid(forged, jwks) else 'INVALID'}")
    say()

    say("# 5. Quiet renewal with the refresh token")
    renewed, _ = aws("initiate-auth", "--client-id", client_id, "--auth-flow", "REFRESH_TOKEN_AUTH",
                     "--auth-parameters", f"REFRESH_TOKEN={refresh}")
    new_id = renewed["AuthenticationResult"]["IdToken"]
    say(f"   new ID token issued, no password typed -> signature {'VALID' if rs256_valid(new_id, jwks) else 'INVALID'}")
    say()

    say("# 6. Someone guesses passwords")
    for attempt in range(1, 9):
        _, r = aws("initiate-auth", "--client-id", client_id, "--auth-flow", "USER_PASSWORD_AUTH",
                   "--auth-parameters", f"USERNAME={TEACHER},PASSWORD=guess-{attempt}-pepperoni", check=False)
        reason = r.stderr.strip().split(":")[-1].strip() if r.returncode else "signed in?!"
        say(f"   guess {attempt}: {reason}")
        time.sleep(0.5)
    _, r = aws("initiate-auth", "--client-id", client_id, "--auth-flow", "USER_PASSWORD_AUTH",
               "--auth-parameters", f"USERNAME={TEACHER},PASSWORD={password}", check=False)
    say(f"   right after, even the real password: {'signed in' if r.returncode == 0 else r.stderr.strip().split(':')[-1].strip()}")
    say()

    say("# 7. Close the desk")
    aws("delete-user-pool", "--user-pool-id", pool_id)
    say(f"   deleted user pool {pool_id}")

    if "--save" in sys.argv:
        REPLAY.write_text("\n".join(lines) + "\n")
        print(f"\nSaved {REPLAY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
