"""Scene 2, part two, for real: a do-it-yourself private badge office.

Builds a small private certificate authority with openssl, then runs real
mutual-TLS handshakes between "Robo" (client) and "the kitchen" (server):

    1. Master stamp (root CA)   -> kept offline in real life
    2. Desk stamp (subordinate CA), signed by the master stamp
    3. Badges (leaf certificates) for Robo and the kitchen, signed by the desk stamp
    4. Handshake: Robo and the kitchen check each other's badges     -> accepted
    5. An outside drone with a badge from a different office knocks   -> rejected
    6. Robo's key is copied, so its badge is cancelled (CRL)          -> rejected

Everything runs on this laptop over 127.0.0.1. Keys and certificates are written
to lab/out/ (git-ignored). Nothing touches AWS and nothing costs money.

    python3 lab/badge_office.py              # prints the transcript
    python3 lab/badge_office.py --save       # also writes replays/badge-office.txt

This is the work a managed private CA takes off your plate: guarding the root
key, signing on time, and publishing the cancelled list where everyone can check it.
"""
import shutil
import socket
import ssl
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lab" / "out" / "badge-office"
REPLAY = ROOT / "replays" / "badge-office.txt"
OPENSSL = shutil.which("openssl") or "openssl"

lines = []


def say(text=""):
    print(text)
    lines.append(text)


def openssl(*args):
    subprocess.run([OPENSSL, *args], cwd=OUT, check=True, capture_output=True)


def subject_and_issuer(cert):
    out = subprocess.run([OPENSSL, "x509", "-in", cert, "-noout", "-subject", "-issuer"],
                         cwd=OUT, check=True, capture_output=True, text=True).stdout
    return [l.strip() for l in out.splitlines()]


# ---------- 1-3: build the badge office ----------

CA_CONFIG = """
[ ca ]
default_ca = desk
[ desk ]
database = desk-index.txt
new_certs_dir = .
certificate = desk.crt
private_key = desk.key
serial = desk-serial
crlnumber = desk-crlnumber
default_md = sha256
default_crl_days = 1
policy = anything
[ anything ]
commonName = supplied
"""


def build_office():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "ca.cnf").write_text(CA_CONFIG)
    (OUT / "desk-index.txt").write_text("")
    (OUT / "desk-serial").write_text("1000\n")
    (OUT / "desk-crlnumber").write_text("1000\n")

    ec = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256", "-nodes"]

    # Master stamp: self-signed root, long-lived, can only sign other stamps.
    openssl("req", "-x509", *ec, "-keyout", "master.key", "-out", "master.crt", "-days", "3650",
            "-subj", "/CN=Maple Hill Master Stamp",
            "-addext", "basicConstraints=critical,CA:TRUE,pathlen:1",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign")

    # Desk stamp: subordinate CA signed by the master stamp; does the daily signing.
    openssl("req", *ec, "-keyout", "desk.key", "-out", "desk.csr", "-subj", "/CN=Maple Hill Desk Stamp")
    (OUT / "desk.ext").write_text("basicConstraints=critical,CA:TRUE,pathlen:0\n"
                                  "keyUsage=critical,keyCertSign,cRLSign\n")
    openssl("x509", "-req", "-in", "desk.csr", "-CA", "master.crt", "-CAkey", "master.key",
            "-CAcreateserial", "-out", "desk.crt", "-days", "365", "-extfile", "desk.ext")

    # Badges: short-lived leaf certificates, signed by the desk stamp.
    def badge(name, cn, usage, san):
        openssl("req", *ec, "-keyout", f"{name}.key", "-out", f"{name}.csr", "-subj", f"/CN={cn}")
        (OUT / f"{name}.ext").write_text(f"basicConstraints=critical,CA:FALSE\n"
                                         f"keyUsage=critical,digitalSignature\n"
                                         f"extendedKeyUsage={usage}\nsubjectAltName={san}\n")
        openssl("ca", "-batch", "-config", "ca.cnf", "-in", f"{name}.csr", "-out", f"{name}.crt",
                "-days", "1", "-extfile", f"{name}.ext", "-notext")

    badge("robo", "robo.school.example", "clientAuth", "DNS:robo.school.example")
    badge("kitchen", "kitchen.school.example", "serverAuth", "DNS:kitchen.school.example,IP:127.0.0.1")

    # An outsider: a drone with a badge from a completely different office.
    openssl("req", "-x509", *ec, "-keyout", "other-master.key", "-out", "other-master.crt", "-days", "30",
            "-subj", "/CN=Somewhere Else Stamp Office",
            "-addext", "basicConstraints=critical,CA:TRUE")
    openssl("req", *ec, "-keyout", "drone.key", "-out", "drone.csr", "-subj", "/CN=drone.delivery.example")
    (OUT / "drone.ext").write_text("extendedKeyUsage=clientAuth\n")
    openssl("x509", "-req", "-in", "drone.csr", "-CA", "other-master.crt", "-CAkey", "other-master.key",
            "-CAcreateserial", "-out", "drone.crt", "-days", "1", "-extfile", "drone.ext")

    # Empty cancelled list to start with.
    openssl("ca", "-config", "ca.cnf", "-gencrl", "-out", "desk.crl")


# ---------- 4-6: knock on the kitchen door ----------

def kitchen_context(check_cancelled):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(OUT / "kitchen.crt", OUT / "kitchen.key")
    ctx.load_verify_locations(OUT / "master.crt")      # trust only our master stamp
    ctx.verify_mode = ssl.CERT_REQUIRED                 # mutual: the client must show a badge too
    if check_cancelled:
        ctx.load_verify_locations(OUT / "desk.crl")
        ctx.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF
    return ctx


def knock(client_cert, client_key, check_cancelled=False):
    """Run one real TLS handshake on 127.0.0.1. Returns (accepted, detail)."""
    server_ctx = kitchen_context(check_cancelled)
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    result = {}

    def serve():
        conn, _ = listener.accept()
        try:
            with server_ctx.wrap_socket(conn, server_side=True) as tls:
                peer = dict(x[0] for x in tls.getpeercert()["subject"])
                result["server"] = f"kitchen sees {peer['commonName']}, {tls.version()}, {tls.cipher()[0]}"
                tls.sendall(b"Come in.")
        except (ssl.SSLError, OSError) as err:
            result["server"] = f"kitchen refused: {getattr(err, 'reason', None) or err}"
        finally:
            listener.close()

    thread = threading.Thread(target=serve)
    thread.start()

    client_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client_ctx.load_verify_locations(OUT / "master.crt")
    client_ctx.load_cert_chain(OUT / client_cert, OUT / client_key)
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=5) as raw:
            with client_ctx.wrap_socket(raw, server_hostname="kitchen.school.example") as tls:
                reply = tls.recv(64).decode() or "(connection closed)"
                peer = dict(x[0] for x in tls.getpeercert()["subject"])
                result["client"] = f"robo sees {peer['commonName']}, reply: {reply}"
    except (ssl.SSLError, OSError) as err:
        result["client"] = f"handshake failed: {getattr(err, 'reason', None) or err}"
    thread.join()
    accepted = "Come in." in result.get("client", "")
    return accepted, result


def why(cert, check_cancelled=False):
    """The kitchen's verdict on a badge, in openssl's own words."""
    trust = OUT / "trust.pem"
    trust.write_text((OUT / "master.crt").read_text()
                     + ((OUT / "desk.crl").read_text() if check_cancelled else ""))
    args = [OPENSSL, "verify", "-CAfile", str(trust), "-untrusted", str(OUT / "desk.crt")]
    if check_cancelled:
        args.append("-crl_check")
    out = subprocess.run([*args, str(OUT / cert)], capture_output=True, text=True)
    text = (out.stdout + out.stderr).strip().splitlines()
    for line in text:
        if "lookup:" in line:
            return line.split("lookup:", 1)[1].strip()
    return text[-1].split(":", 1)[-1].strip() if text else "?"


def main():
    say("# Building the school's badge office (openssl, EC P-256)")
    build_office()
    for cert in ("master.crt", "desk.crt", "robo.crt", "kitchen.crt"):
        subj, issuer = subject_and_issuer(cert)
        say(f"{cert:<12} {subj}")
        say(f"{'':<12} {issuer}")
    say()

    # Leaf certificates must be presented with the desk stamp so the other side can
    # walk the chain up to the master stamp it trusts.
    for name in ("robo", "kitchen"):
        (OUT / f"{name}.crt").write_text((OUT / f"{name}.crt").read_text() + (OUT / "desk.crt").read_text())

    say("# 1. Robo knocks on the kitchen door (mutual TLS)")
    ok, r = knock("robo.crt", "robo.key")
    say(f"   {r['server']}")
    say(f"   {r['client']}")
    say(f"   -> {'ACCEPTED' if ok else 'REJECTED'}")
    say()

    say("# 2. An outside drone with a badge from another office knocks")
    ok, r = knock("drone.crt", "drone.key")
    say(f"   kitchen's check: {why('drone.crt')}")
    say(f"   -> {'ACCEPTED' if ok else 'REJECTED'}")
    say()

    say("# 3. Robo's key was copied: cancel its badge, publish the cancelled list")
    openssl("ca", "-config", "ca.cnf", "-revoke", "robo.crt", "-crl_reason", "keyCompromise")
    openssl("ca", "-config", "ca.cnf", "-gencrl", "-out", "desk.crl")
    crl = subprocess.run([OPENSSL, "crl", "-in", "desk.crl", "-noout", "-text"], cwd=OUT,
                         check=True, capture_output=True, text=True).stdout
    for l in crl.splitlines():
        if "Serial Number" in l or "Key Compromise" in l:
            say(f"   CRL: {l.strip()}")
    ok, r = knock("robo.crt", "robo.key", check_cancelled=True)
    say(f"   kitchen's check: {why('robo.crt', check_cancelled=True)}")
    say(f"   -> {'ACCEPTED' if ok else 'REJECTED'}")

    if "--save" in sys.argv:
        REPLAY.write_text("\n".join(lines) + "\n")
        print(f"\nSaved {REPLAY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
