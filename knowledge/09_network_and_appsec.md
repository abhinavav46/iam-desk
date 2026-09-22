# Network Security and Application Security

## Network security fundamentals
- Firewall: filters traffic by rules (source/destination IP, port, protocol). Next-generation firewalls (NGFW) add application awareness, intrusion prevention and TLS inspection.
- Segmentation: dividing a network into zones (e.g. user, server, DMZ, OT) so a breach in one zone does not automatically reach another. Microsegmentation applies this at the workload level, often via identity-aware policies rather than just IP ranges.
- VPN: encrypts traffic between two points, commonly used for remote access or site-to-site links. Increasingly replaced or supplemented by ZTNA for remote access.
- ZTNA (zero trust network access): grants access to specific applications based on identity, device posture and policy, rather than placing a user on the network the way a VPN does. Reduces lateral movement risk versus flat VPN access.
- IDS/IPS: intrusion detection/prevention systems watch traffic for known attack signatures or anomalies; IPS can block in-line, IDS only alerts.
- DNS security: DNS filtering blocks known-malicious domains; DNSSEC adds cryptographic integrity to DNS responses to prevent spoofing.
- Network access control (NAC): checks a device's identity and posture before allowing it onto the network (e.g. 802.1X).

## Application security basics (OWASP-aligned)
- Injection (SQL, command, LDAP): untrusted input is concatenated into a command or query. Defense: parameterized queries/prepared statements, input validation, least-privileged database accounts.
- Broken access control: an application fails to enforce who can do what, e.g. one user reaching another's data by changing an ID in a URL (insecure direct object reference, IDOR). Defense: enforce authorization server-side on every request, never trust client-side checks alone.
- Cross-site scripting (XSS): untrusted input is rendered as HTML/JS in another user's browser. Defense: output encoding, a strict Content-Security-Policy, and frameworks that auto-escape by default.
- Cross-site request forgery (CSRF): a malicious site tricks a logged-in user's browser into submitting a request to a real site. Defense: anti-CSRF tokens, SameSite cookies.
- Security misconfiguration: default credentials, verbose error messages, unnecessary services or open admin panels left exposed.
- Vulnerable and outdated components: using libraries or frameworks with known CVEs. Defense: dependency scanning (SCA) and a patching cadence.
- Insecure deserialization: untrusted data is deserialized into objects, sometimes leading to remote code execution.
- SSRF (server-side request forgery): an attacker tricks a server into making requests on their behalf, often reaching internal-only services or cloud metadata endpoints (a common way to steal cloud credentials). Defense: allow-list outbound destinations, block link-local/metadata addresses from application code.
- Security logging and monitoring failures: without adequate, tamper-resistant logs, breaches go undetected for longer.

## Where IAM meets application security
Authentication and session handling (covered in the authentication notes) are themselves part of the OWASP Top 10 (broken authentication / identification and authentication failures). Access control decisions in an application are exactly what RBAC/ABAC models formalize. A pentest or code review of an app's login, session and authorization logic is IAM work as much as it is AppSec work.

## Security testing types
- SAST (static application security testing): scans source code without running it, catching issues like injection patterns or hardcoded secrets early in the pipeline.
- DAST (dynamic application security testing): tests a running application from the outside, similar to how an attacker would probe it, catching runtime issues SAST can miss.
- SCA (software composition analysis): scans dependencies for known-vulnerable versions.
- Penetration testing: manual, scenario-driven testing (often by a third party) simulating a real attacker within an agreed scope.
- Vulnerability scanning: automated, broad scanning for known weaknesses (missing patches, open ports, weak TLS config), usually run continuously or on a schedule rather than a point-in-time engagement.
- Red team vs blue team vs purple team: red team simulates an attacker end-to-end (often including social engineering), blue team is the defenders who detect and respond, purple team is a collaborative exercise where both sides share findings in real time to improve detection.
