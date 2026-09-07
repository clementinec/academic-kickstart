# Public-work ledger: site and monthly handoff

The report lives at **`/internal/hku-activity/`** in FORGE's existing Astro `public/` directory. The normal navigation, homepage and layout are unchanged. The snapshot is a tentative discovery aid, not an official HKU evaluation or a ranking of staff.

## Re-run each month

Follow [the collector setup and source policy](HKU_ACTIVITY_INGEST.md): Python 3.11+, both requirements files, and the Playwright WebKit browser are required for the combined refresh. The recommended monthly sequence is:

```sh
.venv-ledger/bin/python scripts/ingest_hku_instagram.py --collect-only
.venv-ledger/bin/python scripts/ingest_hku_activity.py
```

Both use the current Hong Kong day and an inclusive 60-day window; pass the same optional `--as-of` to both for a selected window. The second command incorporates the saved Instagram sidecar without claiming a second social fetch. If Instagram fails, review its attempt log; faculty collection may still proceed separately with previously verified social evidence and its original dates. Running the Instagram command alone **without** `--collect-only` commits a partial social refresh and a new edition while retaining faculty/roster retrieval dates. The UI can narrow the view to 30 days. A browser refresh does not run either collector.

Alternatively, open **GitHub → Actions → HKU public activity ledger (review artifact) → Run workflow**. It attempts the bounded public Instagram collection first, then the faculty collection, and stores a downloadable report for review without changing the live website. It installs Playwright 1.61.0 and WebKit with Linux dependencies. This is a manual workflow, not an activated monthly schedule or automatic publication. The optional `as_of` input sets the reporting window, never a fake retrieval timestamp.

The downloadable artifact contains the full report, including `ledger.json`, the saved `instagram.json` snapshot and `instagram-attempt.json` where created, `service.json`, real edition archive/index, `runs.json`, `editorial-log.json` and the faculty attempt manifest. Inspect `ingest.status`, source failures, channel-specific dates and person assignments before publishing. GitHub retains successful review artifacts for 31 days; durable editions are the normalized files under `public/internal/hku-activity/editions/` committed with their index and operation history. The initial September 6 baseline is genuine; subsequent editions must arise from actual committed collections, never invented earlier months.

## Publish a reviewed snapshot

1. Collect locally, or merge the workflow artifact's complete `public/internal/hku-activity/` report directory into the checkout, retaining existing edition files and history. Do not copy only `ledger.json`; preserve the Instagram sidecar/attempt diagnostics, service metadata, edition index and operation history. Check that earlier editions remain indexed.
2. Inspect failures and curated-source checks. Empty person entries are not findings of inactivity; automated exact-name matches remain candidates. Confirm post dates versus advertised event dates, actual source accounts versus discovery profiles, direct versus cross-source role evidence, and links to repeated coverage. Publication gateway reachability is not a full bibliography search.
3. Run `.venv-ledger/bin/python -m unittest discover -s tests -v`, `node tests/test_ledger_model.js`, `npm run build` with Node 22, and the browser checks below.
4. Commit only the reviewed normalized report and intentional source-configuration changes, then push through the existing GitHub/Netlify workflow. Raw HTML, full captions/comments, local caches and environments stay ignored and are not deployed.

No collection occurs during a site build. A failed critical directory refresh preserves the previous ledger. An Instagram attempt with no verified posts preserves the previous ledger, social snapshot, archive and ingestion date while exposing its failed attempt. Neither failure is a new successful collection. The page's **Last day ingested** field comes only from the actual committed source snapshot, never a build/render clock; a social-only refresh does not update faculty records' individual source dates.

`service.json` exposes the operating policy and actual channel coverage. The service remains manual and awaits the user's cadence/publication decision; no cron or automatic publication is active. Faculty pages are bounded, university news is curated-URL-only, publisher records are pending manual leads, Instagram uses bounded ordinary public pages, and repository coverage can be blocked. Instagram checks at most 12 visible links from each of two profile grids, deduplicating shared permalinks; it is not an exhaustive 60-day feed. No direct API calls, login, scrolling or block retry are used. Saved-response reparsing and merging an existing sidecar do not masquerade as a new social collection. See [the collector guide](HKU_ACTIVITY_INGEST.md) for edition and editorial-history commands.

The report has HTML robots metadata and route-scoped Netlify `X-Robots-Tag: noindex, nofollow, noarchive` headers. Do not add it to navigation, feeds or sitemaps. It is unlisted but **public, not password-protected**; no private personnel information belongs here. The repository may also be public, so authentication added to the page alone would not make committed data private.

## Report views and artwork

The default **Records pulled** view counts distinct dated source records, not people, HTTP requests or unique accomplishments. Shared Instagram permalinks count once; separate posts about the same studio or a faculty event remain separate source records linked by `relatedRecordIds`. Instagram cards use post publication dates, with any advertised event date shown separately. A recent announcement can therefore concern a future event without claiming completion. The actual posting account is distinct from the departmental profiles where it was discovered, and departmental posts need not name a staff member.

**People** retains the complete directory roster, while **Sources & service** separates channel coverage, collection health, manual publication leads and real edition history. Filters apply to dated records and linked people; collection-wide HTTP counts remain explicitly labelled. CSV exports follow the selected view. Public social cards show reviewed paraphrases, role attributions and source permalinks, not full captions or comments.

The self-hosted typography and credited, unaltered HKU event artwork give the report an exhibition-catalogue layout. `scripts/hku_activity_media.json` maps evidence URLs to local thumbnails and their attribution; `public/internal/hku-activity/media.json` is its public copy. After reviewing a new official thumbnail mapping, run `python scripts/fetch_hku_activity_media.py` to retrieve bounded promotional images. The helper does not discover or collect activity, and visual changes never advance the ingestion date. Keep font licences and media attribution with the report.

## Browser checks

With the pinned Playwright dependency and WebKit installed, serve `dist/` locally and run:

```sh
.venv-ledger/bin/python tests/check_ledger_ui.py http://127.0.0.1:8765/internal/hku-activity/
```

The smoke test checks records-first and keyboard-accessible tabs, roster totals, filtering, channel counts, source links, view-specific CSV downloads, mobile overflow, missing media/service fallbacks and failed-snapshot handling. Social fixtures also check unmatched department-only posts, actual/discovery account links, post versus future event dates, related faculty coverage and role-evidence links. The Python suite additionally checks permalink-specific timestamp extraction/corroboration and preserved faculty dates; the JavaScript model checks source-record deduplication and channel filtering. Screenshots are written to a temporary directory, not committed. Passing tests is not proof of complete feed coverage or approval to publish.
