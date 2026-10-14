# WonderNet — Initial Threat Model (Draft)

**Priorities:** Children’s safety and privacy, platform availability, learning data, then game scores.

## Trust boundaries

1. Student browsers and API traffic are always untrusted.
2. Uploaded media and lessons are data, not automatically executable scripts.
3. Student coding environments must never access the host, credentials, other learners' data or privileged networks.
4. Student Wi-Fi must not route to home LAN, Internet or management interfaces.
5. Administrative access needs a separate protected path and appropriate authentication.
6. Offline updates must be verified and support recovery.

## Major threats and security requirements

| Threat | Control / verification |
|---|---|
| Manipulated student identifier | Server-side object authorization and cross-account tests |
| Runaway or malicious student code | Restricted browser workers or isolated dedicated lab hardware; resource/time limits |
| Script injection through uploaded content | Non-executable storage and vetted active-content isolation |
| Archive traversal or decompression bombs | Validate types, paths, sizes and decompressed limits |
| Unauthorized multiplayer access | Private rooms, server-side membership validation, rate limits, moderation |
| Reachability of home LAN from student network | Firewall segmentation and active reachability tests |
| Lost or stolen student data | Collect minimally, support deletion, storage access controls |
| Tampered offline update | Cryptographic signature verification and rollback |
| Compromised package/dependency | Reviewed and constrained dependencies with automated checks |

## Alpha 0.1 constraints

There is no login, upload system, multiplayer, code runner, or sandbox. Local HTTP development must bind to 127.0.0.1. Security headers alone cannot make it production-safe.

**Open design question:** Place intentionally vulnerable high-risk cyber labs on separate hardware, not the host serving children's data.
