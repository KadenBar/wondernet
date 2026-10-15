# Public Repository Launch Checklist

Use this checklist **before changing repository visibility to public**. Publishing source code is different from certifying the software safe for real child use. Nothing here implies production approval.

## Ownership, identity and legal
- [ ] Confirm rights to publish code created on personal time/equipment under any applicable employer agreements
- [ ] Verify AGPL-3.0-only source-code licensing, copyright ownership, and compatibility with planned dependencies and contributors
- [ ] Check the provisional WonderNet name for conflicting brands/trademarks
- [ ] Confirm contributor guidance and separate third-party asset/content licenses

## Privacy and security
- [ ] Inspect **all commits**, not only current files, for tokens, keys, personally identifiable information and copied third-party code
- [ ] Review GitHub Actions workflows for least-privilege permissions
- [ ] Enable GitHub **private vulnerability reporting** and confirm a usable disclosure path
- [ ] Enable Dependabot/security alerts where available
- [ ] Configure branch protection/rulesets, code review and passing checks
- [ ] Verify `.gitignore` and scan tracked files for confidential material
- [ ] Keep sample screenshots/data fully synthetic and non-identifying
- [ ] Confirm README and documentation clearly say the prototype is **not ready for child use**
- [ ] No student data, secrets, private keys or unlicensed media in the repository

## Presentation and community
- [ ] Confirm README features are categorized as **current** vs **planned**
- [ ] Confirm current installation and test commands actually work
- [ ] Verify CI result on the target branch
- [ ] Add repository topics and a concise description in GitHub settings
- [ ] Decide whether to enable Discussions and post a welcoming first thread
- [ ] Review issue templates, contributing rules and code of conduct
- [ ] Add screenshots only after verifying they match the current prototype

## Future child-facing release gates (NOT required merely to publish code)
- [ ] Independently assessed host/network isolation and authentication/authorization
- [ ] Secure reviewed file import and game-package isolation
- [ ] Sandbox validation with adversarial tests
- [ ] Accessibility validation and privacy impact assessment
- [ ] Maintenance, incident handling and secure offline updates

## Visibility change

The GitHub owner can change visibility at **Settings → General → Danger Zone → Change repository visibility** after confirming these checks. Once public, forks and clones may persist even if the repository is made private later.

**Current decision:** Keep private until the owner approves publication.
