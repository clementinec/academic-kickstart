# HKU public activity evidence ingestion

This is a bounded public-source evidence ledger, not a performance ranking, exhaustive web search, or finding that anybody has been inactive. It retains all job roles listed in the current Architecture and Landscape directories, deduplicating both display orders and merging shared canonical profile URLs across departments. Names or initials alone never merge different profile identities. Directory membership is current at retrieval, not a historical affiliation claim for the whole window.

## Run manually or monthly

Use Python 3.11 or later. The Instagram collector uses the Python standard library plus Playwright 1.61.0 from `requirements-instagram.txt`; it needs no Instagram SDK, API token or login.

```sh
python3 -m venv .venv-ledger
.venv-ledger/bin/pip install -r requirements-ledger.txt -r requirements-instagram.txt
.venv-ledger/bin/python -m playwright install webkit
.venv-ledger/bin/python -m unittest discover -s tests -v
.venv-ledger/bin/python scripts/ingest_hku_instagram.py --collect-only
.venv-ledger/bin/python scripts/ingest_hku_activity.py
```

On Linux CI, install the browser with `python -m playwright install --with-deps webkit`. The recommended combined refresh collects Instagram first with `--collect-only`, then runs the faculty collector. The second command merges the saved `instagram.json` sidecar without claiming it fetched those posts again. If Instagram fails, inspect its exit status and attempt log; the faculty command can still run separately using previously verified social evidence and its original dates.

Both collectors default to a rolling 60-day inclusive window ending on the actual Asia/Hong_Kong date. Pass the same `--as-of YYYY-MM-DD` to both commands for a chosen reporting window; actual retrieval timestamps are never backdated. To refresh only Instagram, run `scripts/ingest_hku_instagram.py` without `--collect-only`: a successful collection merges a visibly partial refresh into the ledger and creates a live edition while retaining faculty and roster sources' individual retrieval dates.

For faculty parser/debug verification only, add `--reparse-cache` to `ingest_hku_activity.py` to use saved responses without network access; this preserves actual retrieval dates and labels the mode, and missing cached sources fail explicitly. It is not a new Instagram collection or a monthly refresh. The prototype does not install a scheduler automatically.

## Bounded source policy

`hku_activity_sources.json` contains the two critical directories, a maximum six pages of general events, two exhibition pages and two news pages, with at most 60 event/news detail pages. The official event AJAX endpoint is a read-only GET documented in the site's own `assets/js/main-prod.js`: `is_json=1`, `page_num`, `event_year`, `subcat`. The year filter is left empty so January/February windows can include previous-year events. A page wholly before the date window stops pagination. Pagination caps remain visible in source coverage records; reaching the cap is not declared exhaustive. An empty selector result is a parser failure unless the JSON endpoint explicitly reports zero posts. Profiles are checked once per deduplicated person. No recursively discovered off-site links are fetched. Requests use at most six workers, a 3 MB body cap, two attempts, and no retry of 401/403/404/410/429. Access-denied sources are reported, never bypassed.

The publications gateway and HKU Scholars Hub Architecture collection are checked and exposed in the manifest. Their reachability does not constitute a complete publication search. Profile references require explicit day dates to enter the 60-day ledger. Bare years, month-only dates, undated projects, employment titles, and upload-path years are not treated as new activity. The initial collection endpoint may return HTTP 403; this is a genuine coverage gap. Per-person Google query links are follow-up suggestions only; their results are not automatically searched or verified.

Curated entries in `hku_activity_curated.json` must cite primary public sources and exact evidence text. Every run re-fetches and checks the quoted identifying text. Curated person assignment still requires human judgement about identity and role; string presence is a regression guard, not automatic proof of the entire claim. Announcements remain announced even after their event date; only an explicit retrospective report may be marked reported. A design featured at an exhibition is not proof that the design was created in the reporting window.

## Bounded Instagram collection

`scripts/ingest_hku_instagram.py` opens the ordinary public profile grids of `@hkuarchitecture` and `@hkulandscape` in a fresh unauthenticated WebKit context. It takes at most 12 visible post/reel links from each grid and adds up to four explicit links from `scripts/hku_instagram_sources.json`, deduplicating shared shortcodes before checking at most 28 distinct public post pages. Explicit seeds are labelled separately from grid discoveries. There is no scrolling, pagination, login, credential reuse or direct/private API request. A 401, 403 or 429 stops further requests in that run without retry. Other inaccessible or unparseable pages are recorded as failures. An empty visible grid is not treated as an empty account.

Dates require a unique permalink-matched public media timestamp (`taken_at`) and caption/account in the ordinary page, corroborated by matching HTML time or account/date metadata. The timestamp is converted to Asia/Hong_Kong. A comment timestamp, relative age, search snippet, image filename or advertised event date cannot supply the post's date. The visible grids are **not an exhaustive 60-day feed**: posts beyond the cap, unindexed/private material, and inaccessible pages may be absent.

`scripts/hku_instagram_curated.json` supplies reviewed paraphrases, short caption checks, roles and links. The collector rechecks those caption phrases and direct person-name evidence; it does not infer staff authorship from a departmental account. A shared post retains its actual source account and the profile grids on which it was discovered. Department-only posts with no named roster member remain valid source records. Full captions, comments and rendered HTML stay in the ignored local cache; the public report contains paraphrased summaries, attributed roles, dates and permalinks, not a caption/comment republication.

The counting unit is a **source record**, not a completed piece of work. Instagram uses the post publication date; `advertisedEventDate`, when explicitly documented, is separate and can be in the future. `relatedRecordIds` links reviewed counterparts, including existing faculty-work coverage and paired studio posts. These relationships do not merge separate posts or turn repeated coverage into additional accomplishments. Earlier verified posts still inside the window are retained when the currently visible grid changes.

## Outputs, failure safety, schema

Public normalized output is `public/internal/hku-activity/ledger.json`. The report also carries the saved Instagram source snapshot (`instagram.json`), its latest attempt diagnostics (`instagram-attempt.json`), operating state (`service.json`), edition index/files, `runs.json` and `editorial-log.json`. Raw response bytes/full captions/HTTP provenance are cached under `data/hku-activity/cache/`, including the `instagram/` subdirectory; keep that cache and `.venv-ledger/` out of version control and deployment. The faculty collector's most recent attempt manifest is `data/hku-activity/last-attempt.json` (also ignored locally).

Schema version 1.0.0 has `scope`, `ingest`, `coverage`, `people`, `activities`, `sources`, and `errors`. For faculty event records, `eventDate` and optional `eventEndDate` represent the documented activity dates; `publicationDate` records an article/report date where available. For Instagram source records, `eventDate` and `publicationDate` both carry the Hong Kong posting date, `postedAt` preserves the timestamp, and `advertisedEventDate` is separate. `discoveredAt` is the first successful retrieval in this ledger and is preserved on later runs. Every record has an evidence URL and explicit date basis, precision, review state and status. Automated exact-name/direct-link matches are conservative candidates, not verified authorship. A faculty multi-day event enters if any day overlaps the window; an Instagram announcement enters by its posting date, not by treating an upcoming event as completed.

`ingest.lastDayIngested` is the real Hong Kong retrieval day of the committed snapshot; it is not render time or `asOf`. `lastSuccessfulIngestAt` only advances when all configured attempts and curated checks succeed. Partial source failures may commit a visibly partial snapshot. Either critical directory failing HTTP/parser safety checks aborts the faculty run, returns exit 2 and preserves the previous public ledger byte-for-byte. Profiles or news pages failing never become a claim of no activity. For the faculty collector, exit 0 means a snapshot was committed; inspect `ingest.status` for partial versus success.

If an Instagram attempt verifies no posts, it returns exit 2 and preserves the previous `ledger.json`, `instagram.json`, edition archive and ingestion date. The new `instagram-attempt.json` and failed-run/service diagnostics remain visible. A partial successful social refresh retains older verified records and their individual timestamps; it does not imply that faculty pages or all social posts were refreshed. With `--collect-only`, success saves the Instagram sidecar but does not itself commit the merged ledger or create an edition.

Manual verification remains necessary before using a candidate as an asserted accomplishment. Do not use activity counts to compare academic, honorary, administrative, technical and support roles, or to infer zero productivity.

The optional `publicationLeads` array is loaded from the separate manually reviewed `scripts/hku_publication_leads.json`, filtered by *suggested* online dates within the reporting window. It is never included in `activities` or counts. Original `verifiedAt` and `verificationScope` are preserved verbatim; neither live ingestion nor cache reparsing re-verifies these leads. See `HKU_PUBLICATION_LOOKUP.md` for promotion criteria. Missing first-online dates, fuzzy names, future issue dates and repository accession dates must not become fabricated publication dates.

## Operating state and channel connections

`scripts/hku_activity_service_config.json` is the explicit operating-policy configuration. `service.json` combines it with saved source health and real edition history. It distinguishes bounded faculty collection, curated university URLs, manual publisher leads, bounded public-page Instagram collection, and repository reachability. A channel's collection policy is not proof that its latest attempt succeeded; inspect actual source/attempt dates and failures. Activity `sourceChannel` comes from the evidence hostname; publisher follow-up leads remain separate from dated records and retain their original manual-review timestamps.

The initial operating state is `prototype-awaiting-refresh-policy`: manual collection and review artifacts are configured, `scheduleActive` and `autoPublish` are false, and the user's monthly-review versus automatic-publication choice is pending. A workflow URL is a configured retry destination, not proof that the workflow has been deployed or scheduled. No script activates a scheduler, pushes Git commits or deploys the site.

## Real editions and operation history

A successfully committed **live HTTP or live public Instagram** collection creates an immutable normalized JSON edition under `public/internal/hku-activity/editions/`, and appends its provenance to `editions/index.json`. A valid partial refresh also creates an edition, explicitly labelled `partial`. A faculty sweep requires the critical directory checks; an Instagram-only refresh does not repeat them and preserves their prior retrieval dates. Neither means every channel is complete or the edition has been editorially approved. Filename identity uses the actual last source retrieval timestamp, reporting-window end and content hash. Raw HTML stays outside the public archive.

The edition index's `sha256` field and filename digest are **deterministic-JSON content hashes, not hashes of the indented file bytes**. Exact algorithm: `sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(", ", ": ")).encode("utf-8")).hexdigest()`, with no trailing newline. This uses Python's sorted-key JSON serialization, not RFC 8785/JCS. Parse an archived JSON file and apply that serialization to reproduce its index digest; a plain `sha256sum` of the emitted file will differ. The original baseline archive is not rewritten when presentation/service code changes.

The initial September 6 edition was imported from the existing genuine snapshot with original source timestamps and `origin: baseline-import`. No earlier months or previous collection runs were invented. Running `scripts/hku_activity_service.py --bootstrap` imports a baseline only when no edition exists; repeating it never creates an extra historical edition. The ordinary command without flags rebuilds metadata only. Neither operation performs network requests.

`--reparse-cache` records a **reparse operation**, not a new source collection or edition, and does not advance retrieval dates. Critical directory failure appends a failed-attempt entry while preserving the current ledger, edition files and freshness. `runs.json` and `editorial-log.json` are append-only through the provided tools (not a cryptographic or tamper-proof audit trail). An attributed editorial note can be added without changing activity evidence or dates:

```sh
.venv-ledger/bin/python scripts/hku_activity_service.py --note "Describe the actual reviewed correction" --reviewer "Reviewer name or role" --record-id ACTIVITY_ID
```

This command records the supplied attribution; it does not certify a review, alter a source claim or create an edition. Corrections to curated evidence still require the source-backed review procedure. Preserve the full editions and history files when publishing a reviewed artifact; copying only `ledger.json` loses the service's continuity.

## Verification before handoff

Run the Python suite, `node tests/test_ledger_model.js`, the Node 22 site build and the browser smoke test described in `HKU_ACTIVITY_WEBSITE.md`. Instagram tests cover permalink allowlisting, post-specific versus comment timestamps, unrelated media, corroboration, Hong Kong date boundaries, conflicting timestamps, future advertised dates, unmatched departmental posts and preservation of faculty dates/source-record identity. Browser/model checks cover social-channel filters, source-account versus discovered-account links, related records, deduplication, date labels, empty-person states and failure fallbacks. Tests verify behaviour; they do not establish exhaustive source coverage or editorial approval.
