# CV / direction 01

A terminal-inspired academic layout: IBM Plex Sans for reading, IBM Plex Mono
for section labels and dates, a muted green accent, and a small vector cursor
after the name. White A4 pages remain suitable for printing. The broad visual
reference is [Awesome CV](https://github.com/posquit0/Awesome-CV); this layout
uses custom LaTeX rather than the Awesome CV class.

## Content and builds

- `cv.tex`: full CV, including the expanded bibliography and patent applications.
- `cv-profile.tex`: a two-page academic profile using the same opening content.
- `cv/profile.tex`: research areas, appointments, education, funding, honors,
  supervision, teaching, and service. Update both documents here.
- `cv/publications.tex`: citations, statuses, and patent applications. The source
  ledger is `data/publication-refresh-2026-09-29.md`.
- `cv/style.tex`: fonts, color, spacing, header/footer, and layout helpers. Future
  visual directions can change this file without rewriting the record.

From the repository root:

```sh
sh scripts/build-cv.sh
```

Requires `latexmk`, pdfLaTeX, Python 3, and the TeX packages used in
`cv/style.tex`, including `plex`. With Poppler's `pdftoppm`, the build also
renders `public/images/cv-preview.png`. All fonts are embedded; the text and
DOI links remain selectable/clickable. Intermediates use a temporary directory.

The build updates `cv.pdf`, `public/cv.pdf`, `static/files/cv.pdf`, and
`public/cv-profile.pdf`. Rebuild Astro to refresh `dist/`. Review page breaks
after adding content; the short profile currently fits two pages at 11 pt.
The footer date is maintained in `cv/style.tex`.

## Editorial choices

The first page presents three overlapping research areas with linked
representative papers: **People — thermal protection and human variability**,
**Systems — integration and energy uncertainty**, and **Climate — future
weather and resilience**. The selected work connects these contributions:

- People: human heat defaults (J10), contextual drivers (J07), and thermal sensation probabilities (J06).
- Systems: co-simulation (J09), model benchmarking (A02), and HVAC supervision using sensation probabilities (A01).
- Climate: the paired sAMY studies of weather generation (J03) and input fidelity (J05), plus cooling and ageing (A03).

J10 revisits metabolic heat assumptions, while J07 examines sensitivity to
contextual thermal-comfort drivers. J09 links human-response models to building
control, connecting People and Systems. A02 compares learned thermal-sensation
models with PMV across climates; A01 connects ordinal and tail risk with HVAC
supervision. J03 and J05 address complementary aspects of the sAMY research
thread, and A03 connects Climate with human thermal outcomes and ageing.
Each area has three representative papers; these placements show contributions
and interactions rather than exclusive research-area assignments.
The opening explains thermal protection through the likelihood and consequences
of unacceptable discomfort. Selected-work labels describe the predicted quantity
(thermal sensation probabilities) and its use in HVAC supervision. Ordinal
learning and tail risk remain technical descriptions in the underlying record;
the opening does not equate sensation votes with measured health risk or claim
that financial costs or protective outcomes have been established.
Every selected-work link includes its reference ID and jumps to
the full citation within the CV, regardless of publication status. Selected
bibliography IDs are bold and link back to the programme heading; other IDs
use the same neutral ink in regular weight. Selection is registered by
`\pubref`, so no separate list of bold IDs needs maintaining. DOI links remain
beside the full citations. In the short profile, selected-work links open the
named citation destination in the website's full CV; visible IDs also allow
manual lookup in PDF readers that do not support named-destination URLs.
Appointments, education, and the external research award follow the research overview.
Teaching grants, honors, supervision, courses, and service follow on page two.
The full CV adds conventional citations with separate accepted/in-press,
published, conference/workshop, and under-review categories.

Own-name emphasis does not imply corresponding authorship. Student or
corresponding-author symbols have not been added without verification.
Grant roles and amounts are retained from the existing record; the unspecified
startup-package entry and unverified claims of direct standards adoption have
been removed. Patent application numbers retain their published/filed status,
without implying grant or current pending status.

The newly confirmed ENB sole authorship, EAAI two-author list, Energy in-press
status, and IAQVEC award date/recipients are preserved. MArch supervision is
dated 2026 without asserting that the students have graduated.

## Website connections

The Research page follows the same programme-to-evidence sequence. Its nine
highlights are defined in `src/data/research.ts` and resolve stable CV reference
IDs against the publication records in `src/data/site.ts`. Titles, authors,
status, and DOI links are shared with the publication catalogue. Update the
selections in both `cv/profile.tex` and `src/data/research.ts` when curating a
new set of highlights; reference IDs should remain stable.

Research links use `#paper-j10`-style destinations; catalogue entries use
`#publication-j10`. A catalogue deep link reveals its paper even if URL filters
would otherwise hide it. Programme and catalogue entries link in both
directions. The catalogue remains the selected output since joining HKU;
the full career bibliography is in the CV.
