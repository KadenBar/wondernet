# WonderNet Library: First Curation Queue

**Status: twelve locally readable stories in an adult developer preview, plus eleven separate research candidates.** Five professionally illustrated CC BY 4.0 Book Dash books now have all original covers, full story text and twelve original illustration spreads bundled locally, joining five complete US-public-domain narrative texts and two WonderNet story experiments. This is not an approved children's shelf: human editorial and accessibility reviews, image attribution, and international copyright checks remain open. No arbitrary EPUB/PDF importer, upload endpoint, or Pi-hosted child-facing service exists.

## Five complete real Book Dash picture books

We've locally imported the original illustrated English editions of *A Beautiful Day*, *A Tiny Seed*, *A House for Mouse*, *Come Back, Cat!* and *Walking Together*. Each contains twelve complete source story-image spreads and its original cover, with page text faithfully rendered from Book Dash's original markdown. Unlike our previous original SVG experiment, these are **professionally illustrated, published books**.

The [Book Dash publisher](https://bookdash.org/) licenses them under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The original authors, illustrators, designers, and named editors appear on each local reader page, with detailed clickable source/attribution details in [`BOOKDASH-CREDITS.md`](BOOKDASH-CREDITS.md).

The exact source commit and 65 image blob hashes/expected sizes are in `bookdash-books.json`. Downloaded media SHA-256 digests live in `bookdash-assets.sha256.json`. `scripts/import_bookdash.py` is a developer-only fixed allowlist importer; `--verify-only` checks all assets without internet. No arbitrary student downloads or general book import endpoints were introduced. The temporary privileged GitHub import action was removed after import.

**Still pending:** educator/content, age appropriateness, reading-level and manual accessibility review. These are adult developer previews, **not approved for unsupervised child use**. GitHub Pages is publicly internet-hosted; the actual static pages can be served on a local offline device, but browser service-worker caching and the Pi hotspot are not yet built.

## Five complete classic story texts in the reader

`complete-text-editions.json` lists five **complete narrative texts** by Beatrix Potter, not five previews or summaries:

| Story | First published | Gutenberg ebook number | Approximate words |
| --- | --- | --- | ---: |
| The Tale of Peter Rabbit | 1902 | 14838 | 948 |
| The Tale of Benjamin Bunny | 1904 | 14407 | 1,120 |
| The Tale of Tom Kitten | 1907 | 14837 | 691 |
| The Tale of Jemima Puddle-Duck | 1908 | 14814 | 1,245 |
| The Tale of Mr. Jeremy Fisher | 1906 | 15077 | 794 |

These were sourced from the corresponding **GITenberg** mirrors of Project Gutenberg, with Git blob SHA and original ebook number recorded in the manifest. Source pages:

- https://www.gutenberg.org/ebooks/14838
- https://www.gutenberg.org/ebooks/14407
- https://www.gutenberg.org/ebooks/14837
- https://www.gutenberg.org/ebooks/14814
- https://www.gutenberg.org/ebooks/15077

Project Gutenberg lists each underlying work as public domain in the **United States**, not necessarily in other countries. The HTML source ebooks include the Gutenberg trademark and license terms, which are **not copied into these newly reformatted story pages**. The new pages include the public-domain narrative content only: original Gutenberg preambles, license, publication front matter, and historical scanned illustrations are omitted. Original prose has its whitespace normalized and is divided into screen-reading segments with no textual abridgment of the narrative. See [Project Gutenberg's licensing explanation](https://www.gutenberg.org/policy/license) for why unprotected US text can be reproduced independently of the original trademarked ebook.

**Illustrations:** the original Potter illustrations **were not imported** because the connected import interface cannot transfer binary picture files. The book pages display simple **new WonderNet-authored decorative SVGs**, not historical book artwork. This is an intentionally partial picture-book reproduction: the complete story text is available, but it is not a faithful illustration-preserving reproduction of the printed picture book.

**Audience review:** Potter stories can contain frightening animal situations, historical corporal punishment, and loss of eggs. The developer preview can be read by adult testers, but every book is flagged as **not approved for unsupervised child use**, with editorial and manual accessibility review still pending. There is no validation of educational reading levels.

**Security:** five statically generated first-party HTML files are hardcoded into `READABLE_BOOKS` and the Pages exporter. The book source material was flattened to text paragraphs; no untrusted scripts, file embeds, arbitrary links, uploaded HTML, embedded PDFs, external images, or network fetches are allowed. This is not a general-purpose ebook renderer.

The prior eleven-item `catalog.json` research queue remains entirely unchanged and pending. Some candidate titles and editions may represent the same underlying work as future imports, but an approved status must apply to the **exact edition**, not just the author or title.

## First illustrated bilingual picture book

**Mara's Moving Garden / El jardín viajero de Mara** is an original eight-spread story developed for WonderNet, not a Creative Commons import from another publisher. Each spread has a distinct first-party local SVG illustration. Its book page includes both English and draft Spanish text, switched in place by a local language control, including corresponding accessible image descriptions. The reader uses no remote media, online dictionary, fonts, login, telemetry or saved student data.

See `picture-books.json` for provenance, eight artwork file paths, language metadata, and explicit pending reviews. See `PICTURE-BOOK-LICENSE.md` for the **CC BY 4.0** creative-content attribution offer, separate from the **AGPL-3.0-only** application code. The repo owner must agree to the content licensing terms on merge; copyright applicability to AI-assisted material depends on jurisdiction.

**Still required before child use:** a fluent Spanish translation review, age suitability and cultural relevance review, manual screen-reader/keyboard/mobile/contrast checks, and assessment of appropriate reading level. This is an adult developer preview.

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
or unreviewed upload endpoint is included in this phase. The two original samples, five US-public-domain full-text demonstrations and five separate Book Dash source editions have not changed the status of any of the eleven other research candidates.

## Code vs. book rights

WonderNet's **software** is AGPL-3.0-only. Books and media retain their own
copyright, public-domain status and Creative Commons obligations. Do not
relicense third-party stories as AGPL simply because their metadata lives
in this repository.

## Next implementation milestone

Build a **secure general-purpose reader and importer for individually reviewed third-party content**, with attribution and a restricted rendering pipeline. The two original stories, five static public-domain text editions and five Book Dash illustrated source editions demonstrate a local reading experience, not a secure general ebook importer. The Raspberry Pi private Wi-Fi service remains unimplemented.
