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
