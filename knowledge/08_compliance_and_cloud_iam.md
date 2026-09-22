# Compliance, Frameworks and Cloud IAM

## Frameworks and regulations that shape IAM
- SOX (Sarbanes-Oxley): requires internal controls over financial reporting, which drives SoD controls and access certifications for finance-related systems in public companies.
- SOC 2: an auditor's report on a service organisation's controls, commonly covering access provisioning, deprovisioning and review as part of the Security trust criterion.
- ISO/IEC 27001: an information security management standard; Annex A includes access control requirements.
- NIST SP 800-53 and 800-63: US government control catalog and digital identity guidelines respectively; 800-63B covers authenticator and password requirements.
- GDPR: EU data protection law; relevant to IAM through data minimisation, access limitation to personal data and breach notification.
- HIPAA: US healthcare privacy and security rule; requires access controls and audit logs for systems holding patient data.
- PCI DSS: payment card security standard with explicit requirements for unique IDs, least privilege, MFA for access to the cardholder data environment, and periodic access review.

## Access certification (recertification)
A periodic (commonly quarterly for high-risk, annually for low-risk) review where a manager, application owner or entitlement owner confirms that a user's access is still needed. Certifications are a primary control auditors test. Good practice: certify against risk (more frequent for privileged and financial-system access), give reviewers enough context (entitlement descriptions, last usage) to make a real decision rather than rubber-stamping, and track revocation to completion.

## Audit evidence IAM teams are commonly asked for
- Joiner, mover and leaver process evidence: timestamps showing access granted or removed against HR events.
- Certification campaigns: who reviewed what, when, and evidence that revocations were completed.
- SoD policy definitions and violation reports, with sign-off on any accepted risk.
- Privileged access logs: who elevated, when, what they did, and session recordings where required.
- Segregation between who requests, approves and provisions access.

## Cloud IAM concepts
- Cloud providers use policy-based, largely ABAC-flavoured authorization: AWS IAM policies (JSON, evaluated with explicit deny beating allow), Azure/Entra RBAC role assignments, and Google Cloud IAM bindings.
- Federated access: workforce users sign in through the corporate IdP (SAML or OIDC) rather than provider-native passwords wherever possible.
- Workload identity: cloud-native ways for one service to authenticate to another without long-lived keys, such as AWS IAM roles for EC2 or Lambda, GCP workload identity federation and Entra managed identities. Preferred over embedding access keys in code or config.
- Common cloud IAM mistakes: public S3 buckets or storage accounts through overly broad policies, wildcard `*` actions or resources in policies, long-lived access keys instead of roles, and console users left with standing admin instead of using JIT elevation (for example Entra PIM or AWS IAM Identity Center permission sets).
- CIEM (cloud infrastructure entitlement management): tools that analyse the gap between granted cloud permissions and actually used permissions across AWS, Azure and GCP, and recommend right-sizing.

## Zero trust and IAM
Zero trust assumes no implicit trust from network location alone. Every request is authenticated, authorized against current context (device compliance, risk, location) and logged, continuously rather than once at login. Identity is often called the new perimeter because, in cloud and remote-work environments, identity and device posture are the main signals available.
