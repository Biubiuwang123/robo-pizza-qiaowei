# Robo Orders Pizza

**A plain-language, hands-on tour of how identity, certificates, and secrets fit together on AWS — told through a robot ordering pizza.**

> I work at Amazon. This is a personal learning project built only from public AWS
> documentation and pricing. Views are my own and do not represent Amazon or AWS.
> Not affiliated with or endorsed by AWS.

## The story

Maple Hill Elementary is throwing a class party, and the teacher sends **Robo**, the
school's helper robot, to order pizza. Every step of Robo's errand is one AWS service,
and every step keeps four ideas apart that are easy to blur:
**who you are** (identity), **what you may do** (permission),
**how you prove it** (a credential), and **where secrets live** (secret storage).

| # | Story beat | Service | How you can see it |
|---|---|---|---|
| 1 | The teacher logs in to send Robo | Amazon Cognito | Live sign-in on the site |
| 2 | The party website has to be the real one | AWS Certificate Manager (ACM) | This site's own HTTPS certificate |
| 3 | The badge office signs Robo's badge | AWS Private Certificate Authority | Build a CA by hand with openssl, then see what a managed CA removes |
| 4 | Robo and the kitchen check each other's badges | Mutual TLS (mTLS) | Two tiny services shake hands |
| 5 | The key desk hands out a temporary key | AWS IAM, IAM Roles Anywhere, AWS STS | A long-lived key "before", short-lived credentials "after" |
| 6 | Robo opens the locked treasure box | AWS Secrets Manager | Store, read, and rotate a secret |
| 7 | Staff use their school logins | AWS Directory Service | Workforce directory vs. customer sign-in |

Each chapter has the same four cards: **Explain it three ways** (executive, product,
engineer) · **How it's priced** (public list prices, a worked example) ·
**Alternatives** (the wider market, cited) · **See it run** (a live demo or a redacted
replay of a real run).

## Status

Early build. Chapters arrive one at a time.

- [x] Landing page (local preview)
- [ ] Chapter 1 — Cognito
- [ ] Chapter 2 — ACM
- [ ] Chapter 3 — Private CA
- [ ] Chapter 4 — mTLS
- [ ] Chapter 5 — IAM Roles Anywhere + STS
- [ ] Chapter 6 — Secrets Manager
- [ ] Chapter 7 — Directory Service

## What's in this repo

```
site/      the static website (HTML/CSS/JS, no server)
lab/       small Python scripts you can run against your own AWS account
replays/   redacted transcripts of real lab runs, shown on the site
scripts/   deploy, teardown, and leak-check helpers
docs/      sources, cost ledger, and how this project stays public-only
tests/     tests for the helpers
```

## Public sources only

Every fact on the site links to a public source, listed in
[`docs/sources.md`](docs/sources.md). How the project keeps to that — including the
checks that run before every commit — is in [`docs/public-only.md`](docs/public-only.md).

## Cost

The whole project is designed to cost a few dollars at most. Every AWS resource it
creates, and what it cost, is tracked in [`docs/cost-ledger.md`](docs/cost-ledger.md).
Private CA and Directory Service are explained, not run, because running them is not cheap.

## License

Code is MIT licensed — see [`LICENSE`](LICENSE).
