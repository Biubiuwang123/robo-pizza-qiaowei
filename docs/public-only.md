# How this project stays public-only

This is a personal learning project. It uses public information only, and a few
rules keep it that way.

## Sources

- **Allowed:** AWS product, pricing, and documentation pages; AWS public blogs and
  announcements; public conference talks; other vendors' public pages; open standards
  (RFCs, SPIFFE, CA/Browser Forum).
- Every factual claim links to a source in [`sources.md`](sources.md). No link, no claim.
- Only generally available, publicly announced features are covered.

## What the site does not do

- Speculate about roadmaps, strategy, or why anything is priced the way it is.
- Use non-public numbers. Pricing examples use public list prices and made-up workloads.
- Mention people, teams, or customers.
- Use AWS logos or imitate official AWS design.

## Checks before anything leaves the laptop

Git hooks (enable with `scripts/setup_hooks.sh`) run `scripts/leak_check.py`:

- **Before each commit:** staged files and file names are scanned for secrets
  (access keys, private keys, tokens), account IDs, ARNs, email and IP addresses,
  and the commit author must be a GitHub `noreply` address.
- **On each commit message**, with the same rules.
- **Before each push:** every commit in history, its author, and its message.
- A personal list of terms that must never appear is kept outside the repo and
  checked too. If that list is missing, the check fails rather than passing.

Lab output (keys, certificates, tokens) is written to `lab/out/`, which git ignores.
Replays are redacted before they are saved, then scanned like everything else.
