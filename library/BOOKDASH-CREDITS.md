# Book Dash licensed books — source and attribution

WonderNet bundles **five complete Book Dash picture-book editions** for offline reading
under **[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)**.

Original publisher: **[Book Dash](https://bookdash.org/)**, South Africa.
Original book art, text and book covers are preserved from the pinned
[Book Dash HTML-book repository](https://github.com/bookdash/bookdash-books)
at commit `54916310c5c06a5282e2d5d4add18d64f90e5fde` (2019-11-04).

Reproduction/adaptation changes: markdown/plain story text is rendered as
sanitized read-only HTML paragraphs; images and their order remain unchanged;
page navigation, reader controls and WonderNet layout are added. No artwork
is AI-generated, drawn by WonderNet, or remotely fetched at runtime. The five
books' original covers and each of their **twelve original image spreads**
are bundled at `frontend/assets/books/bookdash/`.

Book Dash publication/reuse guidance: [how to re-use its content](https://bookdash.org/re-using-the-book-dash-content/).
Include publisher, original writer, illustrator, designer, editor (where
credited), book source, license link and a note about formatting adaptations
whenever redistributing these editions. Book Dash's license **does not make
their books AGPL**; reader code remains AGPL-3.0-only.

## Individual books and credits

### A Beautiful Day

- Original publication: Book Dash, 2015; ISBN 978-1-928318-15-6
- Writer: **Elana Bregin**
- Illustrator: **Lindy Pelzl**
- Designer: **Raeesah Vawda**
- Editor: not named in the available original-book credits
- Original book: [https://bookdash.org/books/a-beautiful-day/](https://bookdash.org/books/a-beautiful-day/)
- Source text: `a-beautiful-day/en/index.md`, Git blob `00f1c85dae50c8366c90e8c93827f0adb161a54e`
- Images: 12 numbered original illustrations and original cover, listed by
  source Git blob SHA and exact byte count in `bookdash-books.json`
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Modifications: source-book images retained; narrative rendered as local,
  screen-readable text and page-layout reformatted

### A Tiny Seed: The Story of Wangari Maathai

- Original publication: Book Dash, 2014; ISBN 978-0-9946519-2-1
- Writer: **Nicola Rijsdijk**
- Illustrator: **Maya Marshak**
- Designer: **Tarryn-Anne Anderson**
- Editor: not named in the available original-book credits
- Original book: [https://bookdash.org/books/a-tiny-seed/](https://bookdash.org/books/a-tiny-seed/)
- Source text: `a-tiny-seed/en/index.md`, Git blob `0165547ce0984a18d36aebfc4e26cd60798c5c00`
- Images: 12 numbered original illustrations and original cover, listed by
  source Git blob SHA and exact byte count in `bookdash-books.json`
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Modifications: source-book images retained; narrative rendered as local,
  screen-readable text and page-layout reformatted

### A House for Mouse

- Original publication: Book Dash, 2014; ISBN 978-0-9922357-5-8
- Writer: **Michele Fry**
- Illustrator: **Amy Uzzell**
- Designer: **Jennifer Jacobs**
- Editor: not named in the available original-book credits
- Original book: [https://bookdash.org/books/a-house-for-mouse/](https://bookdash.org/books/a-house-for-mouse/)
- Source text: `a-house-for-mouse/en/index.md`, Git blob `19b7084a2bc36dd17138a1d40335bf2b7de093a7`
- Images: 12 numbered original illustrations and original cover, listed by
  source Git blob SHA and exact byte count in `bookdash-books.json`
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Modifications: source-book images retained; narrative rendered as local,
  screen-readable text and page-layout reformatted

### Come Back, Cat!

- Original publication: Book Dash, 2014; ISBN 978-0-9922358-2-6
- Writer: **Nicola Rijsdijk**
- Illustrator: **Karen Lilje**
- Designer: **Sam Scarborough**
- Editor: not named in the available original-book credits
- Original book: [https://bookdash.org/books/come-back-cat/](https://bookdash.org/books/come-back-cat/)
- Source text: `come-back-cat/en/index.md`, Git blob `868ecd40e5208f8b46d4b1e94b02dcfa8bf4a770`
- Images: 12 numbered original illustrations and original cover, listed by
  source Git blob SHA and exact byte count in `bookdash-books.json`
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Modifications: source-book images retained; narrative rendered as local,
  screen-readable text and page-layout reformatted

### Walking Together

- Original publication: Book Dash, 2015; ISBN 978-1-928318-28-6
- Writer: **Jade Mathieson**
- Illustrator: **Louwrisa Blaauw**
- Designer: **Bianca de Jong**
- Editor: Elise Varga
- Original book: [https://bookdash.org/books/walking-together/](https://bookdash.org/books/walking-together/)
- Source text: `walking-together/en/index.md`, Git blob `18c802bcb8f1b221aa5de9f95e435dd044eea8f8`
- Images: 12 numbered original illustrations and original cover, listed by
  source Git blob SHA and exact byte count in `bookdash-books.json`
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Modifications: source-book images retained; narrative rendered as local,
  screen-readable text and page-layout reformatted

## Verification and boundaries

`scripts/import_bookdash.py` pins each original image and text file to the
upstream Git commit, checks actual source bytes against their Git blob hash
and size, and records locally imported image SHA-256 fingerprints in
`bookdash-assets.sha256.json`. Run `python scripts/import_bookdash.py --verify-only`
to verify existing local files offline; network access is only needed for
the explicit developer-controlled import.

**Security:** no learner upload or fetch endpoint exists, images are fixed
first-party JPEG files, and pages are static HTML generated from text-only
markdown after stripping source markup. Raw third-party HTML is never executed.

**Content suitability:** these publications are promising for shared early
reading but are still **developer preview only**, with accessibility,
reading-level, educational suitability, and age/content review **pending**.
Do not describe this as approved for unsupervised child use.

**Offline definition:** when serving the static exported pages or local
FastAPI app on a local network, every picture and paragraph is local. GitHub
Pages itself is an internet-hosted developer preview; merely opening the
public preview without internet isn't guaranteed to work until browser
offline caching is separately implemented.
