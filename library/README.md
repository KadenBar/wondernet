# WonderNet Library: First Curation Queue

**Status: one original reader demonstration plus eleven research candidates.** The original story is bundled in the static frontend. No third-party ebooks have been imported; there is no book upload endpoint, generalized EPUB/PDF reader, secure import pipeline, or approved children's shelf.

## One original sample story you can actually read

`reader-demos.json` tracks **The Lantern That Kept the Stars**, an original five-chapter story created for WonderNet. Its content is embedded in `frontend/pages/book-lantern.html`, served only through the `/read/lantern` allowlist. It does not require network access, user accounts, databases or external assets once the local page is loaded. Readers can use the table of contents, previous/next chapter buttons, adjustable text size and three color themes. A chapter can be referenced by a URL fragment; no reading history is stored.

This **original demo is not an approved child-facing book**. The story and interface still need editorial, accessibility and rights review. Original sample content is included in the AGPL-3.0-only repository and includes no third-party text, images or imports. Do not use its static format as permission to accept arbitrary user-provided HTML.

## What we have started

`catalog.json` is the source-of-truth inventory for **11 candidate editions**:
nine older English-language books from Standard Ebooks and two contemporary
illustrated books from Pratham Books' StoryWeaver. Each candidate records:

- Exact title, author, illustrator (where known), subject and *tentative*
  reading audience (not a validated reading level).
- Source provider and the specific edition/reference URL.
- Rights classification **and jurisdiction**, a link to the relevant legal
  dedication/license, and edition-specific attribution requirements.
- Independent checks for rights, editorial/content suitability, accessibility
  and package security.
- Current package status (`not-imported`), future local file and checksum.
- Editorial flags that reviewers must consider, including historical
  stereotypes, difficult themes and cultural context.

**All entries have four review gates pending and no local files.** Publication,
availability and suitability must not be implied by inclusion in this list.
URLs exist only for adult curators; the learner-facing page does not link out
to any external book provider.

## Verified discovery sources (not automatic import approval)

### [Standard Ebooks](https://standardebooks.org/)

- Carefully produced digital editions of public-domain literature.
- Listed book pages state the books are *believed* free from US copyright
  restrictions, but may remain copyrighted in other countries.
- Standard Ebooks' original editorial contributions to editions are dedicated
  CC0, but the underlying work and included art need their own rights review.
- Check each **exact edition**, especially illustrations, translation,
  transcription, adaptations, and title/cover art, before redistribution.
- Catalog entries are jurisdiction-scoped to **US-PD**, not "copyright-free
  worldwide". Do not bulk-import automatically.

### [Pratham Books StoryWeaver](https://storyweaver.org.in/en/open-content)

- Modern and multilingual children's picture books. Story text and
  illustrations are generally **CC BY 4.0**.
- StoryWeaver requires attribution to creators, translators when applicable,
  Pratham Books / publisher, and donor/funder. Retain existing notices,
  source URL, license URL and any change notices when redistributing.
- **Audio, readalongs and videos are licensed differently** (StoryWeaver states
  CC BY-NC-ND 4.0 for its readalongs/video), so do NOT treat all media there as
  downloadable and remixable under CC BY.
- We have cataloged text/illustrated editions only. Their exact package
  files, credits and edition details still need curator verification.

### Additional collections to evaluate next

- [Global Digital Library](https://digitallibrary.io/about/license/):
  early-grade reading resources with per-item licenses, including CC BY
  and CC BY-SA; verify each item and its credits before adding.
- [OpenStax](https://help.openstax.org/s/article/Openstax-textbook-licensing-and-customization):
  science and mathematics textbooks are promising for older learners,
  **but current publisher guidance includes noncommercial/share-alike terms**.
  Do not auto-tag the entire catalog as CC BY or unrestricted. Validate the
  license printed in the exact work and the allowed distribution model first.
- Museum and government-media collections require item-by-item rights,
  accuracy, and accessibility review; public visibility alone isn't permission.

We should expand beyond English classics toward short illustrated beginner
books, multilingual stories, science, math, everyday skills, disability
representation and authors from varied cultural backgrounds. Historical works
need contextual and age-appropriate editorial screening.

## Review checklist before allowing local distribution

1. **Provenance:** identify the original, edition, author, illustrator,
   translator, asset variants, publisher and canonical source.
2. **Rights:** record the exact work, text, images, cover and format licenses;
   jurisdiction, attribution, and allowed modifications. Obtain permission
   when uncertain. CC BY is not the same as CC0 or public domain.
3. **Content:** review the actual complete item for age suitability, harmful
   stereotypes, factual accuracy (especially science), accessibility and
   educational quality. Curate rather than ingest everything.
4. **Download safely (future admin-only workflow):** stage downloads outside
   the app origin; restrict size/type, validate signatures and container
   entries, block unsafe embedded content and scripts, scan and quarantine
   before conversion, prevent path traversal and zip bombs.
5. **Package:** prefer open offline formats with secure, sandboxed viewers.
   Preserve attribution and license notices; generate hashes and local
   relative paths; support captions/transcripts where relevant.
6. **Approve:** only explicitly reviewed packages can move into the local
   learner catalog. Require all four review gates and a verified file
   checksum before display as readable.

No background downloader, arbitrary URL fetcher, third-party ebook renderer
or unreviewed upload endpoint is included in this phase. The original reader sample has not changed the status of any of the eleven unreviewed third-party candidates.

## Code vs. book rights

WonderNet's **software** is AGPL-3.0-only. Books and media retain their own
copyright, public-domain status and Creative Commons obligations. Do not
relicense third-party stories as AGPL simply because their metadata lives
in this repository.

## Next implementation milestone

Build a **secure general-purpose reader and importer for individually reviewed third-party content**, with attribution and a restricted rendering pipeline. The original short story is a static proof of the reading experience, not a general ebook importer. The Raspberry Pi private Wi-Fi service remains unimplemented.
