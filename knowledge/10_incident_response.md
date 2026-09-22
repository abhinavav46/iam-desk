# Incident Response

## The standard lifecycle (NIST-aligned)
1. Preparation: playbooks, contact lists, tooling and access ready before an incident happens. For identity incidents this includes knowing how to disable an account, revoke sessions/tokens, and force a password/credential reset quickly.
2. Detection and analysis: an alert or report is triaged to confirm whether it is a real incident, and its scope is assessed (which accounts, systems, data).
3. Containment: short-term containment stops the bleeding (disable the compromised account, isolate the host, revoke the token); long-term containment addresses the root cause without disrupting the business more than necessary.
4. Eradication: remove the attacker's foothold — malware, backdoor accounts, malicious OAuth grants, persistence mechanisms (e.g. scheduled tasks, new admin accounts, forwarding rules in mailboxes).
5. Recovery: restore systems to normal operation, re-enable accounts with new credentials, monitor closely for re-compromise.
6. Lessons learned (post-incident review): what happened, what worked, what to fix — feeding back into detection rules, playbooks and control gaps.

## Identity-specific incident response
- Compromised account: disable sign-in, revoke all active sessions and refresh tokens (not just resetting the password, since existing sessions can survive a reset), review recently granted permissions and OAuth app consents, check for new mail rules or forwarding, and review the account's recent activity for lateral movement.
- Compromised privileged account: treat as high severity; also rotate any credentials the account could have accessed (vault secrets, service account passwords, API keys) and review PAM session logs for what was actually done during the compromise window.
- Suspicious OAuth app consent: revoke the app's access at the tenant level, review what scopes it had and what data it could reach, and check whether it was used to create persistence (mail rules, additional app registrations).
- Insider risk: requires closer coordination with HR/legal; focus on evidence preservation and least-disruptive containment until authorized to act further.

## Evidence and logging for identity incidents
Useful sources: authentication logs (successful/failed sign-ins, MFA results, device/location), directory change logs (group membership, role assignments), IGA logs (who requested/approved/provisioned what), PAM session recordings, and application audit logs. Centralizing these in a SIEM makes correlation across systems possible; without it, incident responders end up chasing logs across many consoles.

## Tabletop exercises
Structured walkthroughs of a hypothetical incident scenario with the actual responders, without touching production systems. They surface gaps in playbooks, unclear ownership, and missing access (e.g. discovering during the exercise that no one currently has the access needed to actually disable an account quickly).
