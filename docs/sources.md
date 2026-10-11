# Sources

Every factual claim on the site cites one of these public pages. Each entry records
when it was last checked.

## Scene 1: Who's at the door?

| Claim | Source | Checked |
|---|---|---|
| ID tokens carry identity claims; access tokens carry scopes | [Cognito tokens](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html) | 2026-10-11 |
| Tokens are verified against the user pool's JWKS public keys | [Verifying a JWT](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html) | 2026-10-11 |
| Refresh tokens get new ID and access tokens | [Refresh tokens](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-refresh-token.html) | 2026-10-11 |
| MFA adds a "something you have" factor | [Adding MFA](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-mfa.html) | 2026-10-11 |
| Users confirm sign-up by verifying contact information | [Signing up and confirming](https://docs.aws.amazon.com/cognito/latest/developerguide/signing-up-users-in-your-app.html) | 2026-10-11 |
| Lite is a user pool feature plan | [Feature plans](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html) | 2026-10-11 |
| Passwords should be salted and hashed | [NIST SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) | 2026-10-11 |
| Token lifetime 3600 s, lockout after 5 wrong passwords, weak password rejected | Observed in a real run of lab/front_door.py on 2026-10-11 | 2026-10-11 |
| Amazon Cognito overview | [What is Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html) | 2026-10-11 |
| Keycloak is open-source identity and access management | [keycloak.org](https://www.keycloak.org/) | 2026-10-11 |
| Firebase Authentication | [Firebase docs](https://firebase.google.com/docs/auth) | 2026-10-11 |
| Microsoft Entra External ID | [Microsoft Learn](https://learn.microsoft.com/en-us/entra/external-id/external-identities-overview) | 2026-10-11 |
| Auth0, Clerk | [Auth0 docs](https://auth0.com/docs/get-started/auth0-overview), [Clerk docs](https://clerk.com/docs) | 2026-10-11 |

## Scene 2: Is that badge real?

| Claim | Source | Checked |
|---|---|---|
| Public certificates last at most 47 days from March 2029 (down from 398) | [CA/B Forum Ballot SC-081v3](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/) | 2026-10-11 |
| ACM certificates are valid for 198 days | [ACM certificate characteristics](https://docs.aws.amazon.com/acm/latest/userguide/acm-certificate-characteristics.html) | 2026-10-11 |
| ACM renews 198-day certificates 45 days before expiry if the DNS record is still in place | [ACM DNS renewal](https://docs.aws.amazon.com/acm/latest/userguide/dns-renewal-validation.html) | 2026-10-11 |
| DNS validation proves control of the name | [ACM DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html) | 2026-10-11 |
| Public certificates are logged to Certificate Transparency logs | [ACM best practices](https://docs.aws.amazon.com/acm/latest/userguide/acm-bestpractices.html) | 2026-10-11 |
| AWS Certificate Manager overview | [What is ACM](https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html) | 2026-10-11 |
| AWS Private CA runs a private certificate authority | [What is AWS Private CA](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html) | 2026-10-11 |
| Let's Encrypt is a free public certificate authority | [Let's Encrypt FAQ](https://letsencrypt.org/docs/faq/) | 2026-10-11 |
| The certificate chain shown for this site | Observed with openssl on 2026-10-11 | 2026-10-11 |
| A private CA hierarchy: a root CA with subordinate CAs below it | [AWS Private CA: CA hierarchy](https://docs.aws.amazon.com/privateca/latest/userguide/ca-hierarchy.html) | 2026-10-11 |
| AWS Private CA offers revocation via CRLs, managed OCSP, or both | [AWS Private CA: revocation](https://docs.aws.amazon.com/privateca/latest/userguide/revocation-setup.html) | 2026-10-11 |
| step-ca is an online certificate authority | [step-ca docs](https://smallstep.com/docs/step-ca/) | 2026-10-11 |
| HashiCorp Vault has a PKI secrets engine | [Vault PKI docs](https://developer.hashicorp.com/vault/docs/secrets/pki) | 2026-10-11 |
| Google Cloud Certificate Authority Service | [CA Service overview](https://cloud.google.com/certificate-authority-service/docs/ca-service-overview) | 2026-10-11 |
| Certificate and CRL format | [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.html) | 2026-10-11 |
| The private badge office replay | Real run of lab/badge_office.py on 2026-10-11 | 2026-10-11 |

## Scene 3: The locked box

| Claim | Source | Checked |
|---|---|---|
| Plaintext secrets in code should be moved to a secrets manager | [Move hardcoded secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/hardcoded.html) | 2026-10-11 |
| Code hosts scan for leaked secrets | [GitHub secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning) | 2026-10-11 |
| Secrets are protected with envelope encryption using KMS keys | [Secrets Manager encryption](https://docs.aws.amazon.com/secretsmanager/latest/userguide/security-encryption.html) | 2026-10-11 |
| API calls, including reads, are recorded by CloudTrail | [Secrets Manager and CloudTrail](https://docs.aws.amazon.com/secretsmanager/latest/userguide/monitoring-cloudtrail.html) | 2026-10-11 |
| Rotation has four steps: createSecret, setSecret, testSecret, finishSecret | [Rotation function steps](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html) | 2026-10-11 |
| Versions are labelled AWSCURRENT, AWSPENDING, AWSPREVIOUS | [Secrets Manager encryption](https://docs.aws.amazon.com/secretsmanager/latest/userguide/security-encryption.html) | 2026-10-11 |
| AWS Secrets Manager overview | [What is Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html) | 2026-10-11 |
| HashiCorp Vault key/value secrets | [Vault KV docs](https://developer.hashicorp.com/vault/docs/secrets/kv) | 2026-10-11 |
| Google Cloud Secret Manager | [Overview](https://cloud.google.com/secret-manager/docs/overview) | 2026-10-11 |
| Azure Key Vault stores secrets such as passwords | [About Key Vault secrets](https://learn.microsoft.com/en-us/azure/key-vault/secrets/about-secrets) | 2026-10-11 |
| Doppler | [Doppler docs](https://docs.doppler.com/docs) | 2026-10-11 |
| The locked box replay | Real run of lab/locked_box.py in a personal AWS account on 2026-10-11; all resources deleted | 2026-10-11 |

## Scene 4: The staff roster

| Claim | Source | Checked |
|---|---|---|
| AWS Directory Service offers ways to use Microsoft Active Directory with AWS | [What is AWS Directory Service](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/what_is.html) | 2026-10-11 |
| Managed Microsoft AD runs a highly available pair of domain controllers in different Availability Zones | [Managed Microsoft AD](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html) | 2026-10-11 |
| AD Connector forwards requests to an existing directory | [AD Connector](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_ad_connector.html) | 2026-10-11 |
| LDAP and Kerberos | [RFC 4511](https://www.rfc-editor.org/rfc/rfc4511.html), [RFC 4120](https://www.rfc-editor.org/rfc/rfc4120.html) | 2026-10-11 |
| Entra Domain Services offers domain join, LDAP and Kerberos as a managed domain | [Microsoft Learn](https://learn.microsoft.com/en-us/entra/identity/domain-services/overview) | 2026-10-11 |
| Google Cloud Managed Microsoft AD | [Overview](https://cloud.google.com/managed-microsoft-ad/docs/overview) | 2026-10-11 |
| OpenLDAP, FreeIPA | [openldap.org](https://www.openldap.org/), [freeipa.org](https://www.freeipa.org/) | 2026-10-11 |
| Microsoft Entra ID, Okta Universal Directory, JumpCloud | [Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/whatis), [Okta](https://www.okta.com/products/universal-directory/), [JumpCloud](https://jumpcloud.com/) | 2026-10-11 |
| The directory replay | Real anonymous LDAP searches of Forum Systems' public [test directory](https://www.forumsys.com/2022/05/10/online-ldap-test-server/) on 2026-10-11 | 2026-10-11 |

Ms. Rivera, Mr. Okafor, Ms. Chen, Trusty Stamps, Maple Hill Elementary, and the `.example` party sites are made up.
