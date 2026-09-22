# Authorization Models

## Access control models
- DAC (discretionary): the resource owner decides who gets access, as with file sharing permissions.
- MAC (mandatory): a central authority assigns labels such as Secret or Confidential and the system enforces them.
- RBAC (role-based): permissions are attached to roles and users are assigned roles.
- ABAC (attribute-based): decisions use attributes of the user, resource, action and environment, for example "department = Finance AND device = compliant AND time = business hours".
- PBAC (policy-based): access is evaluated from centrally written policies, commonly implemented with ABAC-style rules.
- ReBAC (relationship-based): access follows relationships such as "owner of" or "member of", as in document sharing systems.
- ACL (access control list): a list attached to a resource of who may do what.

## RBAC versus ABAC
| | RBAC | ABAC |
|---|---|---|
| Easy to explain and audit | Yes | Harder |
| Fine-grained and dynamic | Weak | Strong |
| Typical problem | Role explosion | Policy sprawl and difficulty testing |
| Best for | Stable job functions | Context-dependent access such as device, region or data classification |
Most organisations use both: roles for the baseline and attributes or policies to narrow them.

## Role explosion and role engineering
Role explosion happens when there are so many roles that they stop being manageable, usually because a new role is created for every exception. To avoid it: separate business roles (what a job function needs) from IT roles (technical bundles of entitlements), use attributes for variations, run role mining on real access data, give every role an owner, and review roles periodically.

## Role types often used in IGA
- Birthright role: given automatically to everyone or to a population, such as email and intranet.
- Business role: reflects a job function, such as "Accounts Payable Clerk".
- IT role: a technical grouping of entitlements across systems, such as "Oracle AP Read + Approver group".
- Assignable versus automatic: automatic roles are granted by rules on attributes, assignable roles are requested and approved.

## Least privilege in practice
Start with no access, grant by role, remove access at role change, use time-limited grants for elevated permissions, review regularly and remove unused entitlements based on usage data.

## Just-in-time (JIT) and just-enough-access (JEA)
JIT grants elevated access only for a defined time window after approval. JEA limits the scope to the specific task. Together they move an organisation toward zero standing privilege.

## Separation of duties (SoD)
A control that stops one person holding conflicting access, such as creating a vendor and approving payments to it. Preventive SoD blocks a request that would create a conflict. Detective SoD finds conflicts in existing access. When a conflict is unavoidable, use a compensating control such as extra approval, monitoring or periodic review with documented risk acceptance.
