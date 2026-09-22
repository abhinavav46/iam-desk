# Privileged Access Management (PAM)

## Why privileged accounts are high risk
Privileged accounts (domain admins, root, database admins, service accounts, cloud IAM admins) can change security controls, read all data or move laterally across the environment. Most serious breaches involve privilege escalation or misuse of standing privileged access.

## Core PAM capabilities
- Vaulting: privileged credentials are stored encrypted in a vault rather than known to humans, with checkout on demand.
- Password rotation: credentials are automatically rotated after use or on a schedule, breaking reuse by attackers who captured an old value.
- Session management and recording: privileged sessions (RDP, SSH, database, web console) are proxied so no direct credential is exposed to the user's endpoint, and the session can be recorded and, in some tools, watched live.
- Just-in-time (JIT) elevation: standing admin rights are removed; a user requests temporary elevation, approved automatically or by a human, that expires after a set window.
- Least privilege on endpoints: application allow-listing and controlled local admin rights instead of permanent local admin for everyone.
- Secrets management: API keys, certificates and service account credentials for applications and pipelines, with rotation and short-lived dynamic secrets where possible.

## Common PAM vendors and pieces
- CyberArk: Vault, Privileged Session Manager (PSM), Central Policy Manager (CPM) for rotation, Conjur or Secrets Manager for application secrets.
- BeyondTrust: Password Safe, Privilege Management for endpoints.
- Delinea (formerly Thycotic): Secret Server, Privilege Manager.
- One Identity Safeguard, Microsoft's built-in Privileged Identity Management (PIM) for Entra ID roles.

## Zero standing privilege (ZSP)
Instead of always-on admin rights, access is granted only for the duration of an approved task and automatically revoked afterward. This shrinks the time window an attacker can exploit a compromised privileged account and forces every elevation to be requested, approved and logged.

## Break-glass accounts
Emergency accounts kept outside normal MFA or federation flows for use when the primary identity system is unavailable. They must be tightly controlled: vaulted, monitored with real-time alerting on any use, and periodically tested, since they are also an attractive target.

## PAM and IGA together
IGA governs who is entitled to request privileged access and certifies that entitlement periodically; PAM enforces how that access is actually vaulted, elevated, used and recorded. Mature programs feed PAM session and usage data back into IGA certifications so reviewers see actual use, not just entitlement.
