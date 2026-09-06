# Public-work ledger: site and monthly handoff

The report lives at **`/internal/hku-activity/`** in FORGE's existing Astro `public/` directory. The normal navigation, homepage and layout are unchanged. The snapshot is a tentative discovery aid, not an official HKU evaluation or a ranking of staff.

## Re-run each month

Follow [the collector setup and source policy](HKU_ACTIVITY_INGEST.md). After setup, the refresh command is:

```sh
.venv-ledger/bin/python scripts/ingest_hku_activity.py
```

It uses the current Hong Kong day and an inclusive 60-day window. The UI can narrow this to 30 days. A browser refresh does not run the collector.

Alternatively, open **GitHub → Actions → HKU public activity ledger (review artifact) → Run workflow**. It collects and stores a downloadable report for review, without changing the live website. This is a manual workflow, not an activated monthly schedule. The optional `as_of` input sets the reporting window, never a fake retrieval timestamp.

The downloadable artifact contains the report, service metadata, real edition archive/history and attempt manifest. Inspect `ingest.status`, source failures, dates and person assignments before publishing. GitHub retains successful review artifacts for 31 days; durable editions are the normalized files under `public/internal/hku-activity/editions/` committed with their index and operation history. The initial archive contains only the genuine September 6 baseline, not invented earlier months.

## Publish a reviewed snapshot

1. Collect locally, or merge the workflow artifact's complete `public/internal/hku-activity/` report directory into the checkout, retaining existing edition files and history. Do not copy only `ledger.json`; check that `editions/index.json` still contains earlier editions before publishing.
2. Inspect failures and curated-source checks. Empty person entries are not findings of inactivity; automated exact-name matches remain candidates. Publication gateway reachability is not a full bibliography search.
3. Run `.venv-ledger/bin/python -m unittest discover -s tests -v`, `node tests/test_ledger_model.js` and `npm run build` with Node 22.
4. Commit the normalized JSON and intentional source-configuration changes, then push through the existing GitHub/Netlify workflow. Raw page caches and local environments are ignored.

No scraping occurs during a site build. A failed critical directory refresh preserves the previous snapshot; it must not be presented as newly ingested. The page's **Last day ingested** field comes only from the actual saved source snapshot, never a build/render clock.

`service.json` exposes the operating policy and actual channel coverage. The service remains manual and awaits the user's cadence/publication decision; no cron or automatic publication is active. Faculty pages are bounded, university news is curated-URL-only, publisher records are pending manual leads, Instagram is not connected, and repository coverage can be blocked. Saved-response reparsing is shown as maintenance, never a newly collected edition. See [the collector guide](HKU_ACTIVITY_INGEST.md) for edition and editorial-history commands.

The report has HTML robots metadata and route-scoped Netlify `X-Robots-Tag: noindex, nofollow, noarchive` headers. Do not add it to navigation, feeds or sitemaps. It is unlisted but **public, not password-protected**; no private personnel information belongs here. The repository may also be public, so authentication added to the page alone would not make committed data private.

## Report views and artwork

The default **Records pulled** view counts distinct dated source records, not people or HTTP requests. Records shared by multiple people count once. **People** retains the complete directory roster, while **Sources & service** separates channel coverage, collection health, manual publication leads and real edition history. Filters apply to dated records and linked people; collection-wide HTTP counts remain explicitly labelled. CSV exports follow the selected view.

The self-hosted typography and credited, unaltered HKU event artwork give the report an exhibition-catalogue layout. `scripts/hku_activity_media.json` maps evidence URLs to local thumbnails and their attribution; `public/internal/hku-activity/media.json` is its public copy. After reviewing a new official thumbnail mapping, run `python scripts/fetch_hku_activity_media.py` to retrieve bounded promotional images. The helper does not discover or collect activity, and visual changes never advance the ingestion date. Keep font licences and media attribution with the report.

## Browser checks

With Playwright and its WebKit browser installed, serve `dist/` locally and run:

```sh
python tests/check_ledger_ui.py http://127.0.0.1:8765/internal/hku-activity/
```

The smoke test checks records-first and keyboard-accessible tabs, roster totals, filtering, channel counts, source links, view-specific CSV downloads, mobile overflow, missing media/service fallbacks and failed-snapshot handling. Screenshots are written to a temporary directory, not committed.
