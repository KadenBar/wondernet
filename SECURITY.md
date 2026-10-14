# Security Policy

WonderNet is intended for learners, including children. Security reports deserve particular care.

## Supported versions

**No supported production release yet.** Alpha 0.1 is a local development prototype and must not be used to store student information or expose services to untrusted networks.

## How to report a vulnerability

1. **Do not post vulnerability details in a public GitHub issue or discussion.**
2. When the repository is published, use the repository's **Security → Report a vulnerability** feature, after the maintainer enables GitHub private vulnerability reporting.
3. Until a private reporting channel is configured, contact the maintainer privately through a channel they designate. **Do not send secrets, student records, or exploit payloads to public threads.**
4. Provide a concise impact statement, affected version, reproduction steps using only synthetic data, and proposed remediation if known.

If private vulnerability reporting is not enabled, **do not assume a private disclosure channel exists**. Maintainers must set one up before the project invites reports.

## Authorized testing

- Security testing is welcome in your **own isolated local installation** using dummy data.
- Do not scan, exploit, or test installations owned by other people without permission.
- Do not access, alter, or expose other users' information.
- Do not deploy intentionally vulnerable exercises on the production WonderNet service.

## Nonnegotiable release gates

- Threat model and trusted/untrusted boundaries reviewed.
- No server-side execution of user-submitted code on the Pi host.
- Authentication, authorization, and session handling validated before user profiles go live.
- Uploaded files are never made executable by the server; active packages require separate review and sandboxing.
- Wi-Fi clients cannot reach the home network or administrator services.
- Local multiplayer room authorization, abuse prevention, and rate limits tested.
- Child privacy and accessibility tests pass.
- A documented method exists for installing authenticated offline security updates.

See [`security/THREAT_MODEL.md`](security/THREAT_MODEL.md).
