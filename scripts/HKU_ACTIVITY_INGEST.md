# HKU public activity evidence ingestion

This is a bounded public-source evidence ledger, not a performance ranking, exhaustive web search, or finding that anybody has been inactive. It retains all job roles listed in the current Architecture and Landscape directories, deduplicating both display orders and merging shared canonical profile URLs across departments. Names or initials alone never merge different profile identities. Directory membership is current at retrieval, not a historical affiliation claim for the whole window.

## Run manually or monthly

```sh
python3 -m venv .venv-ledger
.venv-ledger/bin/pip install -r requirements-ledger.txt
.venv-ledger/bin/python -m unittest discover -s tests -v
.venv-ledger/bin/python scripts/ingest_hku_activity.py
```

The default is a rolling 60-day inclusive window ending on the actual Asia/Hong_Kong date. Reproduce the initial reporting window with `--as-of 2026-09-06`; actual HTTP retrieval timestamps remain real and are never backdated. For parser/debug verification, add `--reparse-cache` to use saved responses without any network; this preserves actual retrieval dates and labels the mode, and missing cached sources fail explicitly. Never use this flag for the monthly refresh. A scheduler can run the normal command monthly. The prototype does not install a scheduler automatically.

## Bounded source policy

`hku_activity_sources.json` contains the two critical directories, a maximum six pages of general events, two exhibition pages and two news pages, with at most 60 event/news detail pages. The official event AJAX endpoint is a read-only GET documented in the site's own `assets/js/main-prod.js`: `is_json=1`, `page_num`, `event_year`, `subcat`. The year filter is left empty so January/February windows can include previous-year events. A page wholly before the date window stops pagination. Pagination caps remain visible in source coverage records; reaching the cap is not declared exhaustive. An empty selector result is a parser failure unless the JSON endpoint explicitly reports zero posts. Profiles are checked once per deduplicated person. No recursively discovered off-site links are fetched. Requests use at most six workers, a 3 MB body cap, two attempts, and no retry of 401/403/404/410/429. Access-denied sources are reported, never bypassed.

The publications gateway and HKU Scholars Hub Architecture collection are checked and exposed in the manifest. Their reachability does not constitute a complete publication search. Profile references require explicit day dates to enter the 60-day ledger. Bare years, month-only dates, undated projects, employment titles, and upload-path years are not treated as new activity. The initial collection endpoint may return HTTP 403; this is a genuine coverage gap. Per-person Google query links are follow-up suggestions only; their results are not automatically searched or verified.

Curated entries in `hku_activity_curated.json` must cite primary public sources and exact evidence text. Every run re-fetches and checks the quoted identifying text. Curated person assignment still requires human judgement about identity and role; string presence is a regression guard, not automatic proof of the entire claim. Announcements remain announced even after their event date; only an explicit retrospective report may be marked reported. A design featured at an exhibition is not proof that the design was created in the reporting window.

## Outputs, failure safety, schema

Public normalized output is `public/internal/hku-activity/ledger.json`. Raw response bytes/HTTP provenance are cached under `data/hku-activity/cache/`; keep that cache and `.venv-ledger/` out of version control and deployment. The most recent attempt manifest is `data/hku-activity/last-attempt.json` (also ignored locally).

Schema version 1.0.0 has `scope`, `ingest`, `coverage`, `people`, `activities`, `sources`, and `errors`. `eventDate` and optional `eventEndDate` represent the evidence's activity date; `publicationDate` records an article/report date where available. `discoveredAt` is the first successful retrieval in this ledger and is preserved on later runs. Every activity has an evidence URL and explicit date basis, precision, review state, status, and per-person role evidence. Automated exact-name/direct-link matches are conservative candidates, not verified authorship. A multi-day event enters if any day overlaps the window. Dates in the future do not enter merely because a page is already published.

`ingest.lastDayIngested` is the real Hong Kong retrieval day of the committed snapshot; it is not render time or `asOf`. `lastSuccessfulIngestAt` only advances when all configured attempts and curated checks succeed. Partial source failures may commit a visibly partial snapshot. Either critical directory failing HTTP/parser safety checks aborts the run, returns exit 2 and preserves the previous public ledger byte-for-byte. Profiles or news pages failing never become a claim of no activity. Exit 0 means a snapshot was committed; inspect `ingest.status` for partial versus success.

Manual verification remains necessary before using a candidate as an asserted accomplishment. Do not use activity counts to compare academic, honorary, administrative, technical and support roles, or to infer zero productivity.

The optional `publicationLeads` array is loaded from the separate manually reviewed `scripts/hku_publication_leads.json`, filtered by *suggested* online dates within the reporting window. It is never included in `activities` or counts. Original `verifiedAt` and `verificationScope` are preserved verbatim; neither live ingestion nor cache reparsing re-verifies these leads. See `HKU_PUBLICATION_LOOKUP.md` for promotion criteria. Missing first-online dates, fuzzy names, future issue dates and repository accession dates must not become fabricated publication dates.

## Operating state and channel connections

`scripts/hku_activity_service_config.json` is the explicit operating-policy configuration. `service.json` combines it with saved source health and real edition history. It distinguishes bounded faculty collection, curated university URLs, manual publisher leads, an unconnected Instagram channel, and repository reachability. A named channel is not a promise that it is connected. Activity `sourceChannel` comes from the evidence hostname; publisher follow-up leads remain separate from dated records and retain their original manual-review timestamps.

The initial operating state is `prototype-awaiting-refresh-policy`: manual collection and review artifacts are configured, `scheduleActive` and `autoPublish` are false, and the user's monthly-review versus automatic-publication choice is pending. A workflow URL is a configured retry destination, not proof that the workflow has been deployed or scheduled. No script activates a scheduler, pushes Git commits or deploys the site.

## Real editions and operation history

A successfully committed **live HTTP** sweep automatically creates an immutable normalized JSON edition under `public/internal/hku-activity/editions/`, and appends its provenance to `editions/index.json`. A valid partial sweep also creates an edition, explicitly labelled `partial`; this means the directory safety checks passed, not that all channels are complete or that the edition has been editorially approved. Filename identity uses the actual last source retrieval timestamp, reporting-window end and content hash. Raw HTML stays outside the public archive.

The edition index's `sha256` field and filename digest are **deterministic-JSON content hashes, not hashes of the indented file bytes**. Exact algorithm: `sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(", ", ": ")).encode("utf-8")).hexdigest()`, with no trailing newline. This uses Python's sorted-key JSON serialization, not RFC 8785/JCS. Parse an archived JSON file and apply that serialization to reproduce its index digest; a plain `sha256sum` of the emitted file will differ. The original baseline archive is not rewritten when presentation/service code changes.

The initial September 6 edition was imported from the existing genuine snapshot with original source timestamps and `origin: baseline-import`. No earlier months or previous collection runs were invented. Running `scripts/hku_activity_service.py --bootstrap` imports a baseline only when no edition exists; repeating it never creates an extra historical edition. The ordinary command without flags rebuilds metadata only. Neither operation performs network requests.

`--reparse-cache` records a **reparse operation**, not a new source collection or edition, and does not advance retrieval dates. Critical directory failure appends a failed-attempt entry while preserving the current ledger, edition files and freshness. `runs.json` and `editorial-log.json` are append-only through the provided tools (not a cryptographic or tamper-proof audit trail). An attributed editorial note can be added without changing activity evidence or dates:

```sh
.venv-ledger/bin/python scripts/hku_activity_service.py --note "Describe the actual reviewed correction" --reviewer "Reviewer name or role" --record-id ACTIVITY_ID
```

This command records the supplied attribution; it does not certify a review, alter a source claim or create an edition. Corrections to curated evidence still require the source-backed review procedure. Preserve the full editions and history files when publishing a reviewed artifact; copying only `ledger.json` loses the service's continuity.
