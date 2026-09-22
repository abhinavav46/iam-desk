# Identity-Based Attacks and Detection

## Credential-based attacks
- Password spraying: a small number of common passwords tried against many accounts, staying below per-account lockout thresholds. Detect through many accounts with a few failed logins from the same source in a short window; defend with MFA, breached-password screening and smarter lockout policies.
- Credential stuffing: credentials leaked from other breaches replayed at scale, betting on password reuse. Defend with MFA and monitoring for logins matching known-breached credential lists.
- Brute force: many attempts against one account. Defend with throttling, lockouts and MFA.
- Phishing and AiTM (adversary-in-the-middle): covered in the authentication notes; the defense is phishing-resistant MFA and conditional access.

## Windows and Active Directory attacks
- Pass-the-hash: an attacker reuses a captured NTLM password hash to authenticate without knowing the plaintext password.
- Pass-the-ticket / Kerberoasting: an attacker requests service tickets for accounts with a Service Principal Name (SPN) and cracks the ticket offline to recover the service account's password, since service accounts often have weak, never-changed passwords.
- Golden ticket / silver ticket: forging Kerberos tickets after compromising the krbtgt account (golden) or a service account (silver) to impersonate any user, sometimes long after the initial compromise.
- DCSync: abusing directory replication permissions to pull password hashes for any account, including krbtgt, directly from a domain controller.
- Defenses: tiered administration (no reuse of admin credentials across trust tiers), strong and rotated service account passwords or Group Managed Service Accounts (gMSA), monitoring for abnormal ticket requests and replication calls, and limiting who holds replication rights.

## Token and session attacks
- Token theft or replay: stealing an issued access, refresh or session token (from a browser, a compromised device or a proxy phishing kit) and reusing it to skip authentication entirely.
- Consent phishing: tricking a user into granting an OAuth application broad scopes; the attacker never needs the password.
- Defenses: short token lifetimes, token binding to device or session, conditional access requiring a compliant device, and admin restrictions on which OAuth apps users may consent to.

## Privilege escalation and lateral movement
Attackers who land on one low-privilege account look for misconfigured entitlements, excessive group memberships, cached credentials of higher-privilege users, or trust relationships between domains and cloud tenants. Reducing standing privilege, segmenting networks and monitoring for unusual access pattern changes all reduce this risk.

## Identity attack detection signals
- Impossible travel: sign-ins from two distant locations within a time window too short to travel between them.
- Unusual sign-in properties: new device, new country, anonymising proxy or Tor, atypical time of day.
- Abnormal access patterns: a service account suddenly making interactive sign-ins, or a user account suddenly authenticating like a script.
- Spikes in failed authentication, especially spread across many accounts (spraying) or many attempts on one account (brute force).
- Sudden entitlement or group membership changes outside a change window, especially additions to privileged groups.
- Use of legacy or basic authentication protocols that bypass MFA.

## Identity Threat Detection and Response (ITDR)
A newer category (Microsoft Defender for Identity, CrowdStrike Identity Protection and similar) focused specifically on identity infrastructure: monitoring directories, IdPs and PAM systems for the attack patterns above and responding in real time, complementing traditional endpoint and network detection.
