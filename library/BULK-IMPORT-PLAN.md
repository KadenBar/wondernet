# Bulk book import staging policy

This directory holds **maintainer-only** staging tools and manifests. Nothing here enables learner uploads or network access on the Raspberry Pi.

## Import contract

1. Select an exact edition and verify US redistribution rights for text, translation, cover, and every illustration independently. Record the source URL, attribution, license, and jurisdiction.
2. Deduplicate against `library/complete-text-editions.json`, `library/illustrated-classics.json`, `library/bookdash-books.json`, `library/picture-books.json`, and `library/catalog.json` by normalized title and author, with manual edition review.
3. Pin source revision and SHA-256 checksums. Download only during a maintainer-initiated build, using allowlisted HTTPS hosts, bounded sizes, and no redirects to untrusted hosts.
4. Never serve imported EPUB HTML, JavaScript, SVG scripts, external images, embedded frames, or remote fonts directly. Convert to escaped text and vetted locally packaged raster images; preserve original chapter boundaries and illustration credits.
5. Generate static reader pages using existing WonderNet styles and routes. Preserve all 14 existing stories and existing reader behavior.
6. Require separate rights, editorial/age-suitability, accessibility, and package-security review gates before declaring any imported title approved for children.
7. Verify offline operation, chapter navigation, missing assets, alt text, checksums, and no external network requests with automated tests. Manual accessibility and editorial review remains mandatory.

## Expansion plan

Target **50 additional unique readable titles**, imported in five reviewable batches of ten. Favor original-edition Nancy Drew, Hardy Boys, House at Pooh Corner, The Little Engine That Could, Oz, Alice, and licensed contemporary picture books. Replace any duplicate or unverifiable edition before counting it toward 50. Historical stereotypes, violence, and outdated language require visible editorial review.

The initial branch establishes policy only; it does **not** import books or implement a generic importer. Follow-up PRs should add a constrained manifest schema, deterministic generator, fixture tests, and then the first ten complete editions.
