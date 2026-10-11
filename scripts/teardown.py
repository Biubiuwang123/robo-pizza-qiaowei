"""Delete everything scripts/deploy_site.py created, in dependency order.

    python3 scripts/teardown.py

CloudFront must be disabled and finish deploying before it can be deleted, so
this can take several minutes. Safe to re-run if interrupted.
"""
import json
import subprocess
import sys
import time

sys.path.insert(0, __import__("os").path.dirname(__file__))
from deploy_site import STATE_FILE, aws, load_state, save_state  # noqa: E402


def main():
    state = load_state()
    if not state:
        print("Nothing to tear down.")
        return

    if "distribution_id" in state:
        dist_id = state["distribution_id"]
        got = aws("cloudfront", "get-distribution-config", "--id", dist_id)
        config, etag = got["DistributionConfig"], got["ETag"]
        if config["Enabled"]:
            config["Enabled"] = False
            aws("cloudfront", "update-distribution", "--id", dist_id, "--if-match", etag,
                "--distribution-config", json.dumps(config))
            print("Disabling the distribution (takes a few minutes)...")
        while aws("cloudfront", "get-distribution", "--id", dist_id)["Distribution"]["Status"] != "Deployed":
            time.sleep(30)
        etag = aws("cloudfront", "get-distribution", "--id", dist_id)["ETag"]
        aws("cloudfront", "delete-distribution", "--id", dist_id, "--if-match", etag, parse=False)
        for key in ("distribution_id", "distribution_arn", "distribution_domain"):
            state.pop(key, None)
        save_state(state)
        print("Distribution deleted.")

    if "oac_id" in state:
        etag = aws("cloudfront", "get-origin-access-control", "--id", state["oac_id"])["ETag"]
        aws("cloudfront", "delete-origin-access-control", "--id", state["oac_id"],
            "--if-match", etag, parse=False)
        state.pop("oac_id")
        save_state(state)
        print("Origin Access Control deleted.")

    if "bucket" in state:
        aws("s3", "rb", f"s3://{state['bucket']}", "--force", parse=False)
        state.pop("bucket")
        save_state(state)
        print("Bucket deleted.")

    if "cert_arn" in state:
        aws("acm", "delete-certificate", "--certificate-arn", state["cert_arn"], parse=False)
        state.pop("cert_arn")
        save_state(state)
        print("Certificate deleted.")

    STATE_FILE.unlink(missing_ok=True)
    print("Teardown complete. Remove the two DNS records at your registrar too.")


if __name__ == "__main__":
    main()
