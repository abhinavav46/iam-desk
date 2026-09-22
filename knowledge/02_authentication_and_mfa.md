# Authentication and MFA

## Authentication factors
- Something you know: password, PIN.
- Something you have: phone, hardware key, smart card, authenticator app.
- Something you are: fingerprint, face.
Multi-factor authentication (MFA) combines at least two different categories. Two passwords are not MFA.

## MFA methods ranked by strength
- Phishing-resistant: FIDO2/WebAuthn security keys and passkeys, and smart cards with PKI. The credential is bound to the real website origin, so a fake login page cannot capture something reusable.
- Strong but phishable: authenticator app codes (TOTP) and push approvals with number matching.
- Weak: SMS and voice codes, which can be lost through SIM swapping and interception, and simple push approvals that can be accepted by mistake.
- Email codes are only as safe as the mailbox.
Recommended direction: passkeys or FIDO2 keys for admins and high-risk users, number-matching push or TOTP as the baseline, SMS only as a last resort.

## MFA fatigue (push bombing)
An attacker who already has a password repeatedly triggers push prompts until the user approves one out of annoyance or by mistake. Defenses: number matching or additional context in the prompt, limits on the number of prompts, alerts on repeated denials, phishing-resistant methods for privileged users, and user training that unexpected prompts must be denied and reported.

## Adversary-in-the-middle (AiTM) phishing
Proxy kits relay the real login page, capture the password and MFA result, and then steal the session cookie. TOTP and push do not stop this. Phishing-resistant MFA, token binding, short session lifetimes, conditional access requiring compliant devices, and detection of impossible travel or new-device sessions do.

## Password guidance (NIST SP 800-63B)
- Length matters more than complexity rules. Allow long passphrases and all characters.
- Check new passwords against breached and common password lists.
- Do not force periodic rotation without evidence of compromise.
- Do not use knowledge-based questions or password hints.
- Rate-limit attempts and use throttling rather than only hard lockouts, which enable denial of service.
- Store with a slow, salted hash such as Argon2id, bcrypt or scrypt.

## Adaptive and risk-based authentication
The sign-in decision uses context: device posture, location, IP reputation, time, behaviour and the sensitivity of the resource. Low risk can proceed silently, medium risk asks for MFA and high risk is blocked or requires stronger proof.

## Sessions
After authentication the application issues a session cookie or token. Protect it with Secure, HttpOnly and SameSite cookie flags, short idle and absolute timeouts, rotation at privilege change and server-side revocation on logout or password reset.

## Protocols you will meet
- Kerberos: ticket-based authentication in Active Directory. The client gets a Ticket Granting Ticket (TGT) from the KDC, then service tickets for each service.
- NTLM: older challenge-response protocol, vulnerable to relay and pass-the-hash. Reduce and eventually disable it.
- LDAP: protocol to query and modify directories. Use LDAPS or StartTLS and never simple binds over plain text.
- RADIUS and TACACS+: network device authentication.
