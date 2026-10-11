# Final audit — 2026-10-11

Run after all four scenes went live. Re-run the same checks before any future launch.

## Public-only

| Check | Result |
|---|---|
| Leak check over every commit, author, message and file (`leak_check.py --history`, `--all`) | Clean |
| Commit authors | One: the GitHub no-reply address |
| GitHub secret scanning, both repos | 0 alerts |
| Wording scan of full history for internal, roadmap, unreleased, team or colleague references | None; the only hit is this project's own rule against speculating about roadmaps |
| Job references | Only the disclaimer: "I work at Amazon… personal learning project… public sources only" |
| Names | Ms. Rivera, Mr. Okafor, Ms. Chen, Maple Hill and Trusty Stamps are made up; party sites use `.example` |

## Site quality

| Check | Result |
|---|---|
| External links on every page | 34 of 34 working |
| Internal links, shared pieces, scene wiring (`tests/`) | 12 tests passing |
| Each page: language, one `h1`, title, description, image alt text, named buttons | Pass, all 5 pages |
| Phone width (375 px), no sideways scroll | Pass, all 5 pages |
| Dark mode | Pass |

## AWS

| Check | Result |
|---|---|
| Still running | One S3 bucket, one CloudFront distribution, one ACM certificate (issued, in use, auto-renewal eligible) |
| Lab leftovers (secrets, user pools, IAM roles, directories, private CAs) | None |
| Bucket | All four public-access blocks on; policy allows only this CloudFront distribution |
| Live site | HTTPS only, HSTS and security headers on, TLS 1.1 refused, direct S3 access 403 |
| Spend | $0.00 actual on the $1 budget; ledger total under $0.01 |
