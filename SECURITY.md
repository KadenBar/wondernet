# Security Policy

WonderNet is being designed for learners, including children. **No production version is currently supported.** The Alpha 0.1 preview must not host student accounts, run untrusted student code, accept untrusted uploads or be exposed to shared/public networks.

## Report vulnerabilities privately

**Do not create public issues, discussions, pull requests or comments containing vulnerability details.**

Before publicly releasing the repository, the maintainer intends to enable GitHub's **Private Vulnerability Reporting** (Repository → Settings → Code security and analysis → Private vulnerability reporting). When enabled, use **Security → Report a vulnerability** in this repository.

**At present a private vulnerability intake route is not yet verified.** Please wait for that channel rather than publishing sensitive exploit details. We will update this document when available.

Provide impact, affected version, minimal reproduction using synthetic data, and any suggested fixes. Never send real student data or credentials.

## Responsible testing

- Only test an instance you own or are explicitly authorized to test.
- Use fictional accounts and sample data.
- Do not target production systems, other users' accounts or third-party deployments.
- Keep intentionally vulnerable cyber exercises separate from the host and future learner data.

## Current security scope

Current: read-only catalog/health endpoints, a static homepage and some defensive HTTP headers. There is **no authentication, hardened server deployment, uploaded-content processing or code sandbox**. That is by design at this early stage, not an assertion that the prototype is secure for use by children.

## Release blockers

Before introducing learner-facing data or execution features:

- Threat model and application permissions reviewed, including access to other users' resources.
- No learner-supplied code executing on the Raspberry Pi host.
- Browser/cyber labs isolated and bounded; high-risk exercises on separate hardware where appropriate.
- Uploaded content served inertly, reviewed, and strictly isolated from privileged origins.
- Wi-Fi/firewall segmentation prevents access to the home network and admin interfaces.
- Private multiplayer validates room membership server-side; moderation and rate limits.
- Clear data minimization/deletion and child privacy decisions.
- Offline updates authenticate packages and include rollback/recovery.
- Automated and manual accessibility/security reviews.

See [the threat model](security/THREAT_MODEL.md) and [public launch checklist](docs/public-launch-checklist.md).
