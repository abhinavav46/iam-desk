# Federation, SSO and Token Protocols

## Single sign-on (SSO) and federation
SSO lets a user authenticate once and reach many applications. Federation extends that trust across organisational or domain boundaries: an identity provider (IdP) vouches for the user and a service provider (SP) accepts the result without holding the user's password.

## SAML 2.0
An XML-based standard mostly used for enterprise web SSO.
- Parties: the IdP issues signed assertions, the SP consumes them. The user's browser carries the messages.
- SP-initiated flow: the user opens the application, the SP redirects the browser to the IdP with an AuthnRequest, the IdP authenticates the user, then returns a signed SAML Response containing an Assertion to the SP's Assertion Consumer Service (ACS) URL, and the SP creates a session.
- IdP-initiated flow: the user starts at the IdP portal and the IdP sends an unsolicited Response to the SP. It is easier to abuse because there is no request to tie the response to, so many teams disable it.
- Assertion contents: issuer, subject (NameID), conditions such as audience and validity window, and attributes.
- Metadata: XML files that exchange entity IDs, endpoints and signing certificates between IdP and SP.
- Things that go wrong: expired signing certificates, wrong ACS URL or audience, clock skew, NameID format mismatch, missing attribute mappings, and XML signature wrapping attacks against poor validators.

## OAuth 2.0
An authorization framework for delegated access. It is not an authentication protocol on its own.
- Roles: resource owner (user), client (application), authorization server, resource server (API).
- Authorization code flow with PKCE is the recommended flow for web, mobile and single-page apps. The client gets a one-time code and exchanges it for tokens, with PKCE proving the same client started the flow.
- Client credentials: machine-to-machine access with no user.
- Device code: for input-constrained devices such as TVs.
- Implicit flow and resource owner password credentials are deprecated and should not be used.
- Tokens: access tokens (short-lived, sent to APIs) and refresh tokens (longer-lived, used to get new access tokens, must be protected and ideally rotated).
- Scopes describe what the client may do. Consent is where the user or admin approves scopes.

## OpenID Connect (OIDC)
An identity layer on top of OAuth 2.0. It adds an ID token (a JWT describing the authentication event and the user), the `openid` scope, a UserInfo endpoint and a discovery document at `/.well-known/openid-configuration`. Use OIDC when an application needs to know who the user is.

## SAML versus OIDC
SAML is XML, older and dominant in enterprise and legacy web apps. OIDC is JSON and REST-friendly, better for modern web, mobile and APIs. Both provide SSO. OAuth 2.0 alone gives delegated API access rather than login.

## JWT (JSON Web Token)
Three base64url parts: header, payload (claims) and signature. Validators must check the signature against a trusted key, pin the accepted algorithms, and verify `iss`, `aud`, `exp` and `nbf`. Never accept `alg: none`. A JWT is signed, not encrypted, so anyone can read the payload. Do not put secrets in it.

## Common OAuth and OIDC misconfigurations
- Wildcard or loosely matched redirect URIs, which enable code and token theft.
- Missing `state` (CSRF) or `nonce` (replay) checks.
- No PKCE for public clients.
- Tokens in URLs or local storage in single-page apps without extra protection.
- Over-broad scopes and users who can consent to risky apps (consent phishing).
- Refresh tokens that never expire or are not revoked on password change.

## SCIM
System for Cross-domain Identity Management is a REST and JSON standard for provisioning. It defines resources such as `/Users` and `/Groups` and operations to create, read, update, patch and delete them. IdPs and IGA tools use SCIM to push lifecycle changes to SaaS applications.

## LDAP and Active Directory basics
LDAP is a directory access protocol. Entries live in a tree identified by distinguished names such as `CN=Jane Doe,OU=Finance,DC=corp,DC=example`. Active Directory combines LDAP, Kerberos and DNS. Group membership and OU placement drive much of enterprise access.
