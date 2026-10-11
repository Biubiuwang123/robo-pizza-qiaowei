# Cost ledger

Every AWS resource this project creates, what pricing tier it falls under, and what
it actually cost. Budget: under $5 for the whole project. A billing alert fires at $1.

| Date created | Resource | Chapter | Pricing basis | Deleted | Actual cost |
|---|---|---|---|---|---|
| 2026-10-11 | ACM public certificate (robo.qiaowei.wang) | 2 | Free for use with CloudFront | — | $0.00 |
| 2026-10-11 | S3 bucket (private, < 1 MB) | 2 | Free tier | — | $0.00 |
| 2026-10-11 | CloudFront distribution + Origin Access Control | 2 | Free tier | — | $0.00 |

**Running total: $0.00**

Never created on purpose: AWS Private CA (monthly fee per CA) and AWS Directory
Service (hourly per directory). Both are explained rather than run.
