"""Deploy the static site to S3 + CloudFront with a free ACM certificate.

Chapter 2 of the story runs here for real: the HTTPS certificate on this site is
an ACM public certificate, validated by a DNS record at the domain's registrar.

Architecture (no servers, nothing public except through CloudFront):

    browser --HTTPS--> CloudFront (ACM cert, us-east-1)
                           |  Origin Access Control (SigV4-signed requests)
                           v
                       S3 bucket (private; Block Public Access on)

Steps, each safe to re-run:

    python3 scripts/deploy_site.py cert      # request the ACM cert, print the DNS validation record
    python3 scripts/deploy_site.py status    # is the cert issued? what is the CloudFront hostname?
    python3 scripts/deploy_site.py infra     # create the bucket, OAC, distribution, bucket policy
    python3 scripts/deploy_site.py upload    # build, sync dist/ to S3, invalidate the CloudFront cache
    python3 scripts/teardown.py              # delete everything this script created

Settings come from environment variables (defaults in brackets):
    ROBO_DOMAIN  [robo.qiaowei.wang]   ROBO_PROFILE [robo]

Resource IDs are kept in .deploy-state.json, which git ignores, so no account
details are ever committed. Cost: ACM public certificates are free; S3 and
CloudFront for a small static site fall within the free tier.
"""
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / ".deploy-state.json"
DIST_DIR = ROOT / "dist"   # built by scripts/build_site.py

DOMAIN = os.environ.get("ROBO_DOMAIN", "robo.qiaowei.wang")
PROFILE = os.environ.get("ROBO_PROFILE", "robo")
REGION = "us-east-1"  # CloudFront only accepts ACM certificates from us-east-1
TAGS = [{"Key": "project", "Value": "robo-pizza"}]

# AWS-managed CloudFront policies (public, fixed IDs from the CloudFront docs).
CACHE_POLICY_CACHING_OPTIMIZED = "658327ea-f89d-4fab-a63d-7e88639e58f6"
RESPONSE_HEADERS_SECURITY = "67f7725c-6f97-4210-82d7-5512b31e9d03"


def aws(*args, parse=True):
    """Run an AWS CLI command with this project's profile and region."""
    cmd = ["aws", *args, "--profile", PROFILE, "--region", REGION, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"aws {' '.join(args[:2])} failed:\n{result.stderr.strip()}")
    return json.loads(result.stdout) if parse and result.stdout.strip() else result.stdout


def load_state():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def cert():
    """Request (or reuse) a DNS-validated public certificate and show the validation record."""
    state = load_state()
    if "cert_arn" not in state:
        out = aws("acm", "request-certificate", "--domain-name", DOMAIN,
                  "--validation-method", "DNS", "--key-algorithm", "EC_prime256v1",
                  "--idempotency-token", "robopizza", "--tags", json.dumps(TAGS))
        state["cert_arn"] = out["CertificateArn"]
        save_state(state)
        time.sleep(5)  # ACM needs a moment to generate the validation record
    desc = aws("acm", "describe-certificate", "--certificate-arn", state["cert_arn"])["Certificate"]
    print(f"Certificate status: {desc['Status']}")
    for opt in desc.get("DomainValidationOptions", []):
        rr = opt.get("ResourceRecord")
        if rr:
            print("\nAdd this DNS record at your registrar (proves you control the domain):")
            print(f"  Type:  {rr['Type']}")
            print(f"  Host:  {rr['Name'].removesuffix('.')}")
            print(f"  Value: {rr['Value'].removesuffix('.')}")


def infra():
    """Create the private bucket, Origin Access Control, distribution and bucket policy."""
    state = load_state()
    if "cert_arn" not in state:
        sys.exit("Run 'cert' first.")
    status = aws("acm", "describe-certificate", "--certificate-arn",
                 state["cert_arn"])["Certificate"]["Status"]
    if status != "ISSUED":
        sys.exit(f"Certificate is {status}; wait until it is ISSUED (check with 'status').")

    # 1. Private bucket. A random suffix keeps the globally unique name free of account details.
    if "bucket" not in state:
        state["bucket"] = f"robo-pizza-site-{uuid.uuid4().hex[:10]}"
        aws("s3api", "create-bucket", "--bucket", state["bucket"], parse=False)
        aws("s3api", "put-public-access-block", "--bucket", state["bucket"],
            "--public-access-block-configuration",
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true",
            parse=False)
        aws("s3api", "put-bucket-tagging", "--bucket", state["bucket"],
            "--tagging", json.dumps({"TagSet": TAGS}), parse=False)
        save_state(state)

    # 2. Origin Access Control: CloudFront signs its requests to S3 with SigV4.
    if "oac_id" not in state:
        out = aws("cloudfront", "create-origin-access-control", "--origin-access-control-config",
                  json.dumps({"Name": "robo-pizza-oac", "SigningProtocol": "sigv4",
                              "SigningBehavior": "always", "OriginAccessControlOriginType": "s3"}))
        state["oac_id"] = out["OriginAccessControl"]["Id"]
        save_state(state)

    # 3. Distribution: HTTPS only, modern TLS, cheapest price class, security headers.
    if "distribution_id" not in state:
        origin_id = "robo-pizza-s3"
        config = {
            "CallerReference": f"robo-pizza-{uuid.uuid4().hex[:8]}",
            "Comment": "Robo Orders Pizza static site",
            "Enabled": True,
            "Aliases": {"Quantity": 1, "Items": [DOMAIN]},
            "DefaultRootObject": "index.html",
            "PriceClass": "PriceClass_100",
            "HttpVersion": "http2and3",
            "IsIPV6Enabled": True,
            "Origins": {"Quantity": 1, "Items": [{
                "Id": origin_id,
                "DomainName": f"{state['bucket']}.s3.{REGION}.amazonaws.com",
                "OriginAccessControlId": state["oac_id"],
                "S3OriginConfig": {"OriginAccessIdentity": ""},
            }]},
            "DefaultCacheBehavior": {
                "TargetOriginId": origin_id,
                "ViewerProtocolPolicy": "redirect-to-https",
                "Compress": True,
                "CachePolicyId": CACHE_POLICY_CACHING_OPTIMIZED,
                "ResponseHeadersPolicyId": RESPONSE_HEADERS_SECURITY,
                "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
            },
            "ViewerCertificate": {
                "ACMCertificateArn": state["cert_arn"],
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
            },
        }
        out = aws("cloudfront", "create-distribution", "--distribution-config", json.dumps(config))
        dist = out["Distribution"]
        state["distribution_id"] = dist["Id"]
        state["distribution_arn"] = dist["ARN"]
        state["distribution_domain"] = dist["DomainName"]
        save_state(state)

    # 4. Bucket policy: only this distribution may read objects.
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AllowCloudFrontRead",
            "Effect": "Allow",
            "Principal": {"Service": "cloudfront.amazonaws.com"},
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{state['bucket']}/*",
            "Condition": {"StringEquals": {"AWS:SourceArn": state["distribution_arn"]}},
        }],
    }
    aws("s3api", "put-bucket-policy", "--bucket", state["bucket"],
        "--policy", json.dumps(policy), parse=False)

    print("Infrastructure ready.")
    print(f"\nAdd this DNS record at your registrar so {DOMAIN} points at CloudFront:")
    print("  Type:  CNAME")
    print(f"  Host:  {DOMAIN.split('.')[0]}")
    print(f"  Value: {state['distribution_domain']}")


def upload():
    """Build the site, copy dist/ to the bucket, and clear CloudFront's cache."""
    state = load_state()
    if "bucket" not in state:
        sys.exit("Run 'infra' first.")
    build = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py")])
    if build.returncode != 0:
        sys.exit("Build failed; nothing uploaded.")
    aws("s3", "sync", str(DIST_DIR), f"s3://{state['bucket']}", "--delete",
        "--exclude", ".DS_Store", parse=False)
    aws("cloudfront", "create-invalidation", "--distribution-id", state["distribution_id"],
        "--paths", "/*")
    print(f"Uploaded. Live at https://{DOMAIN} once DNS points at CloudFront.")


def status():
    state = load_state()
    if "cert_arn" in state:
        c = aws("acm", "describe-certificate", "--certificate-arn", state["cert_arn"])["Certificate"]
        print(f"Certificate: {c['Status']}")
    if "distribution_id" in state:
        d = aws("cloudfront", "get-distribution", "--id", state["distribution_id"])["Distribution"]
        print(f"Distribution: {d['Status']}  ({state['distribution_domain']})")
    if not state:
        print("Nothing deployed yet.")


if __name__ == "__main__":
    steps = {"cert": cert, "infra": infra, "upload": upload, "status": status}
    if len(sys.argv) != 2 or sys.argv[1] not in steps:
        sys.exit(f"usage: python3 scripts/deploy_site.py {{{'|'.join(steps)}}}")
    steps[sys.argv[1]]()
