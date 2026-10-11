# Sources

Every factual claim on the site cites one of these public pages. Each entry records
when it was last checked, because prices and features change.

| Chapter | Claim | Source | Checked |
|---|---|---|---|
| 1 Cognito | User pools return an ID token (identity claims) and an access token (scopes) | [Tokens](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html) | 2026-10-11 |
| 1 Cognito | Tokens are verified against the user pool's JWKS signing keys | [Verifying a JWT](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html) | 2026-10-11 |
| 2 ACM | DNS validation proves domain control | [DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html) | 2026-10-11 |
| 2 ACM | DNS-validated certificates in use renew automatically | [Managed renewal](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html) | 2026-10-11 |
| 2 ACM | CloudFront needs the certificate in us-east-1 | [CloudFront HTTPS requirements](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-requirements.html) | 2026-10-11 |
| 3 Private CA | Managed private CA hierarchy | [What is AWS Private CA](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html) | 2026-10-11 |
| 3 Private CA | Revocation via OCSP, CRLs, or both | [Revocation](https://docs.aws.amazon.com/privateca/latest/userguide/revocation-setup.html) | 2026-10-11 |
| 4 mTLS | Handshake, certificate authentication, proof of key possession | [RFC 8446 (TLS 1.3)](https://www.rfc-editor.org/rfc/rfc8446) | 2026-10-11 |
| 5 Roles Anywhere | A CA registered as a trust anchor | [Roles Anywhere](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/introduction.html) | 2026-10-11 |
| 5 Roles Anywhere | CreateSession, signed with the certificate's key | [Authentication](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/authentication.html) | 2026-10-11 |
| 5 STS | Temporary credentials are short-term and stop working when they expire | [Temporary credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html) | 2026-10-11 |
| 5 IAM | Requests are implicitly denied unless allowed | [Policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html) | 2026-10-11 |
| 6 Secrets Manager | Secrets are encrypted with an AWS KMS key | [Encryption](https://docs.aws.amazon.com/secretsmanager/latest/userguide/security-encryption.html) | 2026-10-11 |
| 6 Secrets Manager | Rotation via a Lambda function or managed rotation | [Rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html) | 2026-10-11 |
| 7 Directory Service | Managed Microsoft AD: a highly available pair of domain controllers across AZs | [Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html) | 2026-10-11 |
| 7 Directory Service | AD Connector forwards to an existing directory | [AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_ad_connector.html) | 2026-10-11 |

## Chapter 2 page (ACM)

| Claim | Source | Checked |
|---|---|---|
| Non-exportable public certs: no cost; exportable $7.00/FQDN, $79.00/wildcard at issuance and renewal; ACME $1.00/$0.50/$0.25 per FQDN tiers, wildcards $5.00/$2.50, max 45 days | [ACM pricing](https://aws.amazon.com/certificate-manager/pricing/) | 2026-10-11 |
| ACM certificates are valid for 198 days | [Certificate characteristics](https://docs.aws.amazon.com/acm/latest/userguide/acm-certificate-characteristics.html) | 2026-10-11 |
| 198-day certificates renew 45 days before expiry if the CNAME resolves and the cert is in use | [DNS renewal](https://docs.aws.amazon.com/acm/latest/userguide/dns-renewal-validation.html) | 2026-10-11 |
| Public certificates are logged to Certificate Transparency logs | [ACM best practices](https://docs.aws.amazon.com/acm/latest/userguide/acm-bestpractices.html) | 2026-10-11 |
| Max public TLS validity falls from 398 to 47 days, March 2026 to March 2029 | [CA/B Forum Ballot SC-081v3](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/) | 2026-10-11 |
| Let's Encrypt: 90-day default, 6-day opt-in | [Let's Encrypt FAQ](https://letsencrypt.org/docs/faq/) | 2026-10-11 |
| cert-manager issues and renews certificates in Kubernetes | [cert-manager docs](https://cert-manager.io/docs/) | 2026-10-11 |
| Cloudflare Universal SSL: free edge certificates | [Cloudflare docs](https://developers.cloudflare.com/ssl/edge-certificates/universal-ssl/) | 2026-10-11 |
| Google-managed certificates for Google Cloud load balancers | [Certificate Manager overview](https://cloud.google.com/certificate-manager/docs/overview) | 2026-10-11 |
| Free App Service managed certificate | [Azure docs](https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate) | 2026-10-11 |
| Chain, key type, validity of this site's certificate | Observed with openssl on 2026-10-11 | 2026-10-11 |
