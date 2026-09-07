# HKU Instagram collection

The reconciled collector uses ordinary public Instagram pages: the first visible grid of each departmental profile, plus up to four explicit post links in `hku_instagram_sources.json`. Existing manually discovered links are retained as additional seeds. Shared permalinks are fetched and counted once, including when they appear in both account grids. This is bounded discovery, not a complete feed, an authenticated API, or proof of inactivity elsewhere.

Use Python 3.11+ and install the requirements/browser described in [the ingestion guide](HKU_ACTIVITY_INGEST.md). A standalone refresh is:

```sh
.venv-ledger/bin/python scripts/ingest_hku_instagram.py
```

It preserves previously saved records still in the date window, updates the normalized Instagram sidecar and merges the verified source records into the main ledger. Existing faculty records retain their own retrieval timestamps. The earlier two-post supplement is now integrated into the shared report rather than loaded as a second, independently counted UI dataset.

For one combined review edition, run the social collector with `--collect-only`, then `scripts/ingest_hku_activity.py`. The manual GitHub review-artifact workflow runs that sequence. No scheduler or automatic publication is enabled. `--as-of YYYY-MM-DD` selects the reporting window only; it never backdates a source retrieval. The old metadata-only collector's custom-output/config/cache-reparse options are not part of this integrated CLI.

The public page must provide media data matching its permalink, an exact post timestamp, a caption and source account. A matching HTML time element or account/date metadata corroborates the timestamp. Dates are converted to Hong Kong time; comment timestamps and dates of advertised events are not substituted for posting dates. Caption evidence checks in `hku_instagram_curated.json` guard the reviewed summaries and staff links. Account association is not staff authorship, and a post about an award does not make a named supervisor its recipient.

Only concise paraphrases, reviewed roles, provenance and links are published. Raw HTML, full captions and comments remain in the ignored local cache. A failed attempt with no verified posts preserves the ledger, saved Instagram snapshot and editions, while exposing the failure separately. Partial attempts retain earlier verified records with their original timestamps.

See [the website handoff guide](HKU_ACTIVITY_WEBSITE.md) for testing and publishing the complete report, source sidecars and edition history together.
