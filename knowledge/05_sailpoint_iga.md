# SailPoint IGA

## Product family
- IdentityIQ (IIQ): on-premises or self-hosted Java application, deployed by the customer, highly customisable with rules, workflows and a plugin framework.
- Identity Security Cloud (ISC), formerly IdentityNow: SaaS platform. Configuration is done through the UI and REST APIs rather than server-side Java rules; extensibility uses Cloud Rules (limited, sandboxed) and event-driven workflows.

## Core concepts common to both
- Source (application): a connected system such as Active Directory, SAP, Workday or a database, read through a connector.
- Account: an identity's presence on a source, linked to a single SailPoint identity through correlation.
- Entitlement: a specific permission on a source, such as an AD group or SAP role, aggregated into SailPoint's catalog.
- Identity cube (IIQ) or identity profile (ISC): the consolidated view of one person built from a designated authoritative source (usually HR) plus linked accounts.
- Aggregation: importing accounts and entitlements from a source into SailPoint.
- Correlation: matching an account to the right identity, typically by employee ID or a matching rule.
- Certification (access review): periodic manager, application-owner or entitlement-owner review confirming that access is still needed. Certifications can target managers, application owners, roles or entitlements, and unrevoked or revoked decisions trigger workflows.
- Access request and approval: end users request access from a catalog; approvals route to managers or owners with configurable workflows.
- Policy and SoD: SailPoint evaluates policies (including SoD policies) during requests and in scheduled scans, and raises policy violations that need justification or remediation.
- Role: business or IT roles assembled from entitlements, used to simplify requests and certifications.
- Provisioning: pushing approved changes to the source, either directly (a connector applies the change) or manually (a ticket is generated for someone else to action, then SailPoint verifies it landed).
- Workflow: automated sequences (approvals, notifications, provisioning steps) triggered by lifecycle events.
- Lifecycle state: attribute-driven status such as Active, Leave of Absence or Terminated that can trigger enable, disable or access-change workflows automatically.

## Typical joiner-mover-leaver flow in SailPoint
1. HR system (the authoritative source) creates or updates a worker record.
2. Aggregation brings the change into SailPoint; correlation matches it to an identity, or a new identity cube or profile is created.
3. Lifecycle state changes (for example Pre-hire to Active) trigger birthright role assignment and account creation on target sources.
4. For movers, role and entitlement changes are computed against the new attributes; access no longer justified is flagged for removal.
5. For leavers, the Terminated lifecycle state disables or deletes accounts on a schedule, often immediately for involuntary terminations.
6. Certifications periodically confirm that current access is still appropriate, independent of lifecycle events.

## Rules and workflows
- IdentityIQ Rules: server-side BeanShell (Java-like) scripts run at defined extension points such as build map, correlation, provisioning and workflow steps. Powerful but require code review since they run with full application privilege.
- IdentityIQ Workflows: BPEL-like XML processes wiring together approvals, provisioning and notifications.
- ISC Workflows: event-triggered, built visually or as JSON, calling out to actions and optionally to external services through connectors or a webhook.
- ISC Cloud Rules: a small, sandboxed set of rule types (for example attribute generation) for logic that configuration alone cannot express.

## Reporting and testing notes relevant to UAT
- Common IIQ test areas: aggregation results (accounts and entitlements landed correctly), correlation accuracy, certification generation and sign-off, request and approval routing, provisioning to test connectors, SoD policy triggering, and rule or workflow behaviour on edge-case attribute values.
- Common defects: mis-correlated accounts (duplicate identities), certifications not including scope they should, provisioning showing "pending" indefinitely because of a broken connector, entitlement descriptions missing so reviewers cannot judge risk, and lifecycle triggers firing on the wrong attribute change.
- Good defect reports include the identity or account tested, the source, the exact steps, the expected versus actual entitlement or workflow state, and relevant task or workflow logs.

## SailPoint versus other IGA tools
| | SailPoint IIQ/ISC | Saviynt | One Identity Manager |
|---|---|---|---|
| Deployment | IIQ self-hosted, ISC SaaS | SaaS-first (EIC) | On-prem or hosted |
| Customisation | IIQ: Java rules; ISC: workflows and Cloud Rules | Low-code control panels | .NET and web services |
| Notable strength | Large connector ecosystem, market leader in enterprises | Strong cloud entitlement and PAM-adjacent governance | Deep AD and legacy on-prem integration |
