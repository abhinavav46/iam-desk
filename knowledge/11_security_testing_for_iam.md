# Security & QA Testing Notes for IAM Systems

Practical checklist material for testing IAM-adjacent features: login, SSO, access requests, provisioning and entitlement changes. Useful alongside UAT/functional testing work in tools like Micro Focus ALM or Selenium.

## Functional test areas for an IAM/IGA feature
- Identity lifecycle: new joiner creates correct birthright access; mover with a department/role change gains new access and loses access no longer justified; leaver is disabled/deleted per the defined timeline.
- Access request and approval: correct approver is routed to (manager, app owner, role owner); rejected requests do not provision anything; approved requests provision on the correct target system; requests for conflicting (SoD) entitlements are flagged or blocked as designed.
- Certification/access review: correct population and scope appears for each reviewer; revoke decisions actually remove access on the target system; "no response" escalation and auto-decision behavior matches the design.
- Provisioning: an approved change reaches the target application correctly (create/modify/delete account, add/remove entitlement); failures produce a visible, actionable error rather than a silent "stuck" state; manual/ticket-based provisioning is verified by SailPoint (or equivalent) after the ticket is marked complete.
- Correlation: new accounts on a source link to the correct identity; ambiguous or unmatched accounts are queued for manual review rather than silently mis-linked.

## Negative and edge-case testing (often missed)
- Duplicate identities (e.g. two HR records for the same person, or a rehire).
- Attribute values outside expected ranges (empty department, unexpected characters, extremely long names) breaking a rule or workflow.
- Race conditions: two changes to the same identity's access happening close together (e.g. a mover event and a certification revoke at the same time).
- Orphaned accounts: an account on a target system with no corresponding identity — should be surfaced, not silently ignored.
- Access requested for a role/entitlement that was disabled or deleted after the request was submitted but before it was approved.
- Time zone and daylight-saving edge cases in scheduled tasks (aggregation windows, certification deadlines, JIT access expiry).

## Security-focused testing questions to ask
- Can a user reach an approval, certification, or admin screen they should not have access to by guessing a URL or ID (broken access control / IDOR)?
- Does the system enforce SoD policy server-side, or only warn in the UI (which a direct API call could bypass)?
