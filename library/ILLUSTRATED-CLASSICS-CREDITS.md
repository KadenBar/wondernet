# Original illustrated classics — source, rights and review record

WonderNet's **Winnie-the-Pooh** and **The Velveteen Rabbit** use complete
public-domain-in-the-United-States original-era source editions, including
the historic illustrations, not modern copyrighted adaptations.

## Winnie-the-Pooh (1926)

- Writer: **A. A. Milne**; original illustrator: **E. H. Shepard**.
- Historical publication: 1926 (Canadian source edition).
- Reader: `/read/winnie-the-pooh`; introduction plus **all ten chapters**.
- Original art: historical cover, Hundred Acre Wood map, and **113** numbered
  E. H. Shepard illustrations (**115** local JPEG files total).
- Source ebook: [Project Gutenberg #67098](https://www.gutenberg.org/ebooks/67098).
- Source mirror: [GITenberg/Winnie-the-Pooh_67098](https://github.com/GITenberg/Winnie-the-Pooh_67098),
  pinned to commit `8e2945e548754afc55c919576e664979469d1c64`.

## The Velveteen Rabbit (1922)

- Writer: **Margery Williams**; original illustrator: **William Nicholson**.
- Original publication: 1922; this old illustrated edition retains period art.
- Reader: `/read/velveteen-rabbit`, the complete narrative divided into
  **15** manageable screen-reading sections.
- Artwork: **8** illustrations from the source including its title/first detail
  image, historical scene art and closing image. The local cover card uses
  `christmas.jpg` from the source edition rather than a modern cover.
- Source ebook: [Project Gutenberg #11757](https://www.gutenberg.org/ebooks/11757).
- Source mirror: [GITenberg/The-Velveteen-Rabbit_11757](https://github.com/GITenberg/The-Velveteen-Rabbit_11757),
  pinned to commit `4e0b5bda90a99e98cb1ace8572aac3196b1ce7e6`.

## Reuse, attribution, and constraints

The specific original narratives and historic illustrations are public domain
in the **United States** according to Project Gutenberg's edition records and
the age of their original publication. Copyright differs by country. WonderNet
does **not** import modern Disney Pooh characters, branded adaptations,
newer colorized or redrawn editions, narration/music, or updated translations.
Modern trademark issues may also apply to branding/packaging; WonderNet
presents the historic book titles as source identification, not as a Disney
product or endorsement.

Gutenberg's digitization/source license, trademark text and unrelated printer
advertisements are not included in the reading pages. The work itself has been
reformatted into a local first-party HTML reader, with historic illustrations
placed along the story (and two Pooh frontispiece/map images relocated to
their relevant opening chapters). Paragraph whitespace is normalized; the
original prose is **not abridged**. Pooh keeps an introduction and ten distinct
chapters, Velveteen keeps its full narrative and original eight illustrations.

The provenance in `illustrated-classics.json` lists the exact upstream commit,
ebook HTML SHA, every expected JPEG Git blob SHA, the expected byte size and
its relative local path. After import, the repository also records **123**
SHA-256 checksums in `illustrated-classics-assets.sha256.json` and a
section-count manifest. Run:

```bash
python scripts/import_illustrated_classics.py --verify-only
```

That verification command **does not fetch the internet**. The initial
download is a **maintainer-only** fixed-allowlist operation (source and output
are pinned), and the temporary elevated GitHub import workflow was removed
before merge. Static image assets and reader pages have no external network
requests at runtime. The public GitHub Pages preview itself is internet-hosted;
offline reading requires local serving of the exported site.

**Not yet approved for unsupervised child use:** check reading ages, period
cultural depictions and language, book-specific distressing themes, plus
manual screen-reader/alt-text/contrast/mobile review. In particular, the
historical Pooh images often lack meaningful source alt text, so they are
presented as decorative until a human can review and write good alternative
descriptions. *Velveteen Rabbit* has scarlet fever, fears of destruction and
separation. We make no claim of age/educator approval.

WonderNet reader software remains **AGPL-3.0-only**; these public-domain books
are not relicensed under the software license.
