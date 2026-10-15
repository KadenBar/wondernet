# WonderNet Licensing Decision — GNU AGPLv3

**Decision (October 2026):** WonderNet's original source code is licensed under the **GNU Affero General Public License, version 3 only** (SPDX identifier: `AGPL-3.0-only`). See the full [LICENSE](../LICENSE). Do not confuse this with `AGPL-3.0-or-later`; the project is choosing **version 3 only**.

## Why this license?

The goal is to let families, schools, libraries, nonprofits, volunteers and businesses use and improve WonderNet while generally ensuring covered modifications remain available as source code when distributed or made accessible to remote users over a network.

**The license permits commercial use** (including selling Pi kits or services) and does **not** require businesses to send their changes to this project's maintainers. Depending on the activity and AGPL conditions, they instead may need to offer corresponding source code to recipients or users interacting with a modified version over a network.

Not every private change triggers a publication obligation. Independent components, third-party dependencies and separately distributed materials raise compatibility and scope questions that must be evaluated individually.

## Previous licensing

Before this decision, the repository contained an MIT license during early private development. Replacing that file does not retroactively withdraw MIT permissions for any copies of those earlier versions legitimately received under MIT. The project should confirm copyright ownership and any existing third-party contributor rights before broad distribution.

## Separate asset and curriculum permissions

- **Project source code:** GNU AGPL-3.0-only, unless a source file says otherwise.
- **Third-party open-source code:** governed by its own license; check compatibility before integration.
- **Bundled lessons, books, PDFs, audio, images, graphics and game assets:** do **not** assume these are automatically covered by the code license. Identify each asset's rights explicitly; use permissions or an appropriate content license (e.g. a compatible Creative Commons license for original works).
- **Administrator-imported media:** not relicensed simply because an operator uses WonderNet.
- **WonderNet branding:** software licensing does not convey trademark ownership.

## Contributor expectations

Contributors should confirm they have the rights to submit code under AGPL-3.0-only, and clearly indicate when a proposed asset has a different redistribution license. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Reference

The complete license text is included in [LICENSE](../LICENSE), taken from the SPDX License List Data repository's `AGPL-3.0-only` text. For general guidance, see the [GNU AGPL page](https://www.gnu.org/licenses/agpl-3.0.html).

*This project note is not legal advice; have counsel review unusual integrations or significant commercial deployments.*
