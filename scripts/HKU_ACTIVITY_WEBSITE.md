# Public-work ledger: site and monthly handoff

The report lives at **`/internal/hku-activity/`** in FORGE's existing Astro `public/` directory. The normal navigation, homepage and layout are unchanged. The snapshot is a tentative discovery aid, not an official HKU evaluation or a ranking of staff.

## Re-run each month

Follow [the collector setup and source policy](HKU_ACTIVITY_INGEST.md). After setup, the refresh command is:

```sh
.venv-ledger/bin/python scripts/ingest_hku_activity.py
```

It uses the current Hong Kong day and an inclusive 60-day window. The UI can narrow this to 30 days. A browser refresh does not run the collector.

Alternatively, open **GitHub → Actions → HKU public activity ledger (review artifact) → Run workflow**. It collects and stores a downloadable report for review, without changing the live website. This is a manual workflow, not an activated monthly schedule. The optional `as_of` input sets the reporting window, never a fake retrieval timestamp.

The downloadable artifact contains the report and attempt manifest. Inspect `ingest.status`, source failures, dates and person assignments before publishing. GitHub retains successful review artifacts for 31 days; long-term saved editions are the committed JSON snapshots in repository history.

## Publish a reviewed snapshot

1. Collect locally, or copy the workflow artifact's `ledger.json` into `public/internal/hku-activity/`.
2. Inspect failures and curated-source checks. Empty person entries are not findings of inactivity; automated exact-name matches remain candidates. Publication gateway reachability is not a full bibliography search.
3. Run `.venv-ledger/bin/python -m unittest discover -s tests -v` and `npm run build` with Node 22.
4. Commit the normalized JSON and intentional source-configuration changes, then push through the existing GitHub/Netlify workflow. Raw page caches and local environments are ignored.

No scraping occurs during a site build. A failed critical directory refresh preserves the previous snapshot; it must not be presented as newly ingested. The page's **Last day ingested** field comes only from the actual saved source snapshot, never a build/render clock.

The report has HTML robots metadata and route-scoped Netlify `X-Robots-Tag: noindex, nofollow, noarchive` headers. Do not add it to navigation, feeds or sitemaps. It is unlisted but **public, not password-protected**; no private personnel information belongs here. The repository may also be public, so authentication added to the page alone would not make committed data private.

## Browser checks

With Playwright and its WebKit browser installed, serve `dist/` locally and run:

```sh
python tests/check_ledger_ui.py http://127.0.0.1:8765/internal/hku-activity/
```

The smoke test checks roster totals, search, department/window filtering, source links, CSV download, mobile overflow and failed-snapshot handling. Screenshots are written to a temporary directory, not committed.
