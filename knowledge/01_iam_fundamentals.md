# IAM Fundamentals

## What IAM is
Identity and Access Management (IAM) is the set of processes, policies and tools that make sure the right identities (people, services, devices) have the right access to the right resources, at the right time, for the right reasons. It rests on four ideas: identification (who are you claiming to be), authentication (prove it), authorization (what are you allowed to do) and accountability (record what happened so it can be audited).

## Core vocabulary
- Identity: the digital representation of a person, service or device. One person usually has one identity but many accounts.
- Account: an identity's presence in one system, such as an Active Directory user or a Salesforce login.
- Credential: something used to prove identity, such as a password, certificate, key or token.
- Entitlement: a specific permission or group membership in a target system, for example membership of the AD group "Finance-Approvers".
- Role: a named bundle of access, usually tied to a job function.
- Policy: a rule that decides whether access is granted, requested, reviewed or blocked.
- Principal or subject: the identity making a request. Resource: the thing being accessed (application, file, API, database, cloud service).
- IdP (identity provider): the system that authenticates users and issues assertions or tokens, such as Entra ID, Okta or ADFS.
- SP or RP (service provider or relying party): the application that trusts the IdP.
- Directory: the store of identities and attributes, for example Active Directory or an LDAP server.
- Provisioning: creating, changing and removing accounts and entitlements in target systems.

## Authentication versus authorization
Authentication answers "who are you". Authorization answers "what may you do". Authentication happens first and produces a session or token. Authorization is evaluated on each request against roles, attributes or policies. Passing MFA does not mean a user should reach every resource.

## Identity types
- Workforce identities: employees and contractors.
- Customer identities (CIAM): consumers signing in to public applications. High volume, with focus on registration, consent and fraud.
- Machine or non-human identities: service accounts, API keys, certificates, bots, CI/CD pipelines and cloud workload identities. They often outnumber humans, tend to be over-privileged and are rarely reviewed.
- Third-party identities: vendors, partners and auditors who need time-boxed access.

## Guiding principles
- Least privilege: grant only the access needed for the task.
- Need to know: limit information to those whose job requires it.
- Separation of duties (SoD): no single person can complete a risky end-to-end process alone.
- Defense in depth: layer controls so one failure is not fatal.
- Zero standing privilege: elevated access is granted just in time and expires.
- Auditability: every access decision is enforced and logged.

## How IAM, IGA, PAM and CIAM differ
| Area | Focus | Example tools |
|---|---|---|
| Access management (AM) | Authentication, SSO, MFA and session or authorization at sign-in | Entra ID, Okta, Ping Identity |
| IGA (identity governance and administration) | Who should have what: lifecycle, requests, reviews, SoD, compliance | SailPoint, Saviynt, One Identity Manager, Omada |
| PAM (privileged access management) | Securing, controlling and recording privileged access | CyberArk, BeyondTrust, Delinea, One Identity Safeguard |
| CIAM (customer IAM) | Customer sign-up, login, consent and scale | Auth0, Okta Customer Identity, Entra External ID |
| ITDR (identity threat detection and response) | Detecting and responding to identity attacks | Microsoft Defender for Identity, CrowdStrike Identity Protection |

## Identity lifecycle: joiner, mover, leaver (JML)
- Joiner: a new hire or contractor appears in the authoritative source (usually HR). The identity is created and birthright access such as email, VPN and collaboration tools is provisioned automatically.
- Mover: a transfer, promotion or manager change. New access is added and access no longer needed must be removed. Movers are where privilege creep starts.
- Leaver: termination or contract end. Access is disabled promptly (the same day, or immediately for hostile exits). Accounts are deleted after a retention period, licences are reclaimed and owned objects are reassigned.
- Edge cases worth designing for: rehires, long leave, contractor extensions and conversions from contractor to employee.
