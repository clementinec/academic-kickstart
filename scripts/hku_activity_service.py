#!/usr/bin/env python3
"""Operational metadata and real edition history; never invent collection freshness."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = Path("public/internal/hku-activity")
LIVE_COLLECTION_MODES = {"live-http", "live-public-instagram"}
PUBLISHER_DOMAINS = (
    "sciencedirect.com", "elsevier.com", "wiley.com", "tandfonline.com", "springer.com",
    "springerlink.com", "nature.com", "sagepub.com", "taylorfrancis.com", "cambridge.org",
    "academic.oup.com", "mitpress.mit.edu", "doi.org", "crossref.org",
)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path, default):
    return json.loads(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else deepcopy(default)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def source_channel(url):
    try:
        parsed = urlsplit(url or "")
        host = (parsed.hostname or "").lower()
    except ValueError:
        return "other"
    if parsed.scheme not in {"http", "https"}:
        return "other"
    if host == "arch.hku.hk" or host.endswith(".arch.hku.hk"):
        return "faculty_web"
    if host in {"hub.hku.hk", "repository.hku.hk", "scholars.hku.hk"}:
        return "repositories"
    if host == "hku.hk" or host.endswith(".hku.hk"):
        return "university_news"
    if host == "instagram.com" or host.endswith(".instagram.com"):
        return "instagram"
    if any(host == domain or host.endswith("." + domain) for domain in PUBLISHER_DOMAINS):
        return "publishers"
    return "other"


def enrich_channels(ledger):
    for activity in ledger.get("activities", []):
        activity["sourceChannel"] = source_channel(activity.get("evidenceUrl"))
    for source in ledger.get("sources", []):
        source["sourceChannel"] = source_channel(source.get("url"))
    for lead in ledger.get("publicationLeads", []):
        lead["sourceChannel"] = "publishers"
        lead["channelStatus"] = "manual-follow-up-not-dated-activity"
    return ledger


def valid_times(values):
    result = []
    for value in values:
        if not value:
            continue
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                continue
            result.append(parsed.astimezone(timezone.utc).isoformat(timespec="seconds"))
        except (ValueError, TypeError):
            continue
    return result


def retrieval_time(ledger):
    # A reparse/build timestamp is never source retrieval evidence.
    values = valid_times(s.get("lastSuccessfulFetchAt") for s in ledger.get("sources", []))
    return max(values) if values else None


def append_unique(path, key, item):
    data = read_json(path, {"schemaVersion": "1.0.0", key: []})
    if not any(entry["id"] == item["id"] for entry in data[key]):
        data[key].append(item)
        atomic_json(path, data)
    return data


def run_source_details(sources, started_at, channel=None, keep_undated=False):
    """Record this attempt only; carried-forward source checks never become fresh."""
    start = valid_times([started_at])
    details = []
    for source in sources:
        source_id = source_channel(source.get("url"))
        if channel and source_id != channel:
            continue
        attempted = valid_times([source.get("lastAttemptAt")])
        if not attempted and not keep_undated:
            continue
        if attempted and start and attempted[0] < start[0]:
            continue
        details.append({"id": source.get("id"), "url": source.get("url"), "channel": source_id,
                        "status": source.get("status", "failed"), "httpStatus": source.get("httpStatus"),
                        "error": source.get("error"), "attemptAt": attempted[0] if attempted else None,
                        "lastSuccessfulFetchAt": source.get("lastSuccessfulFetchAt")})
    return details


def register_edition(root, ledger, origin="live-ingest"):
    """Only new live collections (or a single honest baseline import) create editions."""
    report = Path(root) / REPORT_PATH
    index_path = report / "editions/index.json"
    index = read_json(index_path, {"schemaVersion": "1.0.0", "editions": []})
    if origin == "baseline-import" and index["editions"]:
        return index["editions"][-1], False
    if origin not in {"baseline-import", "live-ingest"}:
        return (index["editions"][-1] if index["editions"] else None), False
    if ledger.get("ingest", {}).get("status") not in {"success", "partial"}:
        raise ValueError("Only successfully committed snapshots may become editions")
    retrieved_at = retrieval_time(ledger)
    if not retrieved_at:
        raise ValueError("Cannot archive an edition without genuine source retrieval timestamps")
    as_of = ledger["scope"]["asOf"]
    # Validate dates before constructing any output path.
    datetime.strptime(as_of, "%Y-%m-%d")
    stamp = datetime.fromisoformat(retrieved_at).strftime("%Y%m%dT%H%M%SZ")
    # This hashes deterministic JSON serialization, NOT the indented on-disk file bytes.
    # The exact algorithm is documented in HKU_ACTIVITY_INGEST.md; no JCS claim is made.
    digest = hashlib.sha256(json.dumps(ledger, sort_keys=True, ensure_ascii=False, separators=(", ", ": ")).encode("utf-8")).hexdigest()
    edition_id = stamp + "_asof-" + as_of + "_" + digest[:12]
    existing = next((e for e in index["editions"] if e["id"] == edition_id), None)
    if existing:
        return existing, False
    entry = {"id": edition_id, "asOf": as_of, "windowStart": ledger["scope"].get("windowStart"),
             "retrievedAt": retrieved_at, "registeredAt": utc_now(), "origin": origin,
             "collectionMode": ledger["ingest"].get("mode"),
             "status": ledger["ingest"]["status"], "peopleCount": len(ledger.get("people", [])),
             "recordCount": len(ledger.get("activities", [])), "publicationLeadCount": len(ledger.get("publicationLeads", [])),
             "href": "./editions/" + edition_id + ".json", "sha256": digest,
             "note": "Imported existing source snapshot; not a new collection run." if origin == "baseline-import" else (
                 "Bounded public Instagram collection; other channels retain their earlier check timestamps. Review before publication."
                 if ledger["ingest"].get("mode") == "live-public-instagram" else "Collected snapshot; publication still requires manual review.")}
    edition_path = report / "editions" / (edition_id + ".json")
    if edition_path.exists():
        # Never silently overwrite an immutable archived edition.
        if read_json(edition_path, None) != ledger:
            raise ValueError("Archive identity collision; existing edition was not overwritten")
    else:
        atomic_json(edition_path, ledger)
    index["editions"].append(entry)
    atomic_json(index_path, index)
    return entry, True


def build_service(root, ledger):
    root = Path(root)
    report = root / REPORT_PATH
    config = read_json(root / "scripts/hku_activity_service_config.json", None)
    if not config:
        raise ValueError("Service configuration missing")
    editions = read_json(report / "editions/index.json", {"editions": []})["editions"]
    runs = read_json(report / "runs.json", {"runs": []})["runs"]
    editorial = read_json(report / "editorial-log.json", {"changes": []})["changes"]
    source_attempts = valid_times(s.get("lastAttemptAt") for s in ledger.get("sources", []))
    live_runs = [r for r in runs if r["mode"] in LIVE_COLLECTION_MODES]
    # --collect-only has real channel evidence but deliberately creates no run
    # or edition. Consult its manifest without inventing either history entry.
    social_attempt = read_json(report / "instagram-attempt.json", {})
    social_start = valid_times([social_attempt.get("startedAt")])
    if social_attempt.get("mode") == "live-public-instagram" and social_start:
        matching = next((r for r in live_runs if r.get("channel") == "instagram"
                         and valid_times([r["attemptAt"]]) == social_start), None)
        live_runs.append({"attemptAt": social_start[0], "finishedAt": social_attempt.get("finishedAt"),
            "mode": "live-public-instagram", "status": social_attempt.get("status", "unknown"),
            "channel": "instagram", "channels": ["instagram"],
            "committed": bool(matching and matching.get("committed")),
            "sourceOutcomes": run_source_details(social_attempt.get("sources", []), social_start[0], "instagram", keep_undated=True),
            "note": "Actual saved Instagram attempt; collect-only evidence does not itself create a ledger edition."})
    live_runs.sort(key=lambda r: (valid_times([r["attemptAt"]]) or [""])[0])
    live_attempts = valid_times(r["attemptAt"] for r in live_runs)
    last_attempt = max(source_attempts + live_attempts) if source_attempts or live_attempts else None
    refresh = deepcopy(config["refresh"])
    refresh.update({"lastAttemptAt": last_attempt, "lastCommittedRetrievalAt": retrieval_time(ledger),
                    "lastDayIngested": ledger.get("ingest", {}).get("lastDayIngested"),
                    "lastSuccessfulIngestAt": ledger.get("ingest", {}).get("lastSuccessfulIngestAt"),
                    "lastAttemptStatus": live_runs[-1]["status"] if live_runs else ledger.get("ingest", {}).get("status"),
                    "lastOperationStatus": runs[-1]["status"] if runs else None,
                    "lastOperationMode": runs[-1]["mode"] if runs else None})
    channels = deepcopy(config["channels"])
    for channel in channels:
        channel["configuredState"] = channel["state"]
        sources = [s for s in ledger.get("sources", []) if source_channel(s.get("url")) == channel["id"]]
        channel["sourceIds"] = [s["id"] for s in sources]
        channel["checksInSavedSnapshot"] = len(sources)
        channel["failedChecksInSavedSnapshot"] = sum(s.get("status") != "success" for s in sources)
        channel["savedCheckErrors"] = list(dict.fromkeys(s["error"] for s in sources if s.get("error")))
        successes = valid_times(s.get("lastSuccessfulFetchAt") for s in sources)
        channel["lastSuccessfulFetchAt"] = max(successes) if successes else None
        channel_runs = [r for r in live_runs if r.get("channel") == channel["id"] or channel["id"] in r.get("channels", [])]
        channel["latestAttempt"] = None
        channel["latestAttemptAt"] = None
        channel["latestAttemptStatus"] = None
        channel["latestAttemptErrors"] = []
        if channel_runs:
            latest = channel_runs[-1]
            outcomes = [s for s in latest.get("sourceOutcomes", []) if s["channel"] == channel["id"]]
            channel["latestAttempt"] = {"attemptAt": latest["attemptAt"], "finishedAt": latest.get("finishedAt"),
                "mode": latest["mode"], "status": latest["status"], "committed": latest["committed"],
                "checksAttempted": len(outcomes), "failedChecks": sum(s["status"] != "success" for s in outcomes),
                "sources": outcomes, "note": latest.get("note")}
            channel["latestAttemptAt"] = latest["attemptAt"]
            channel["latestAttemptStatus"] = latest["status"]
            channel["latestAttemptErrors"] = [{"url": s["url"], "error": s["error"], "httpStatus": s["httpStatus"]}
                                               for s in outcomes if s["error"]]
            if not latest["committed"] and (latest["status"].startswith("blocked") or any(s.get("httpStatus") in {401, 403, 429} for s in outcomes)):
                channel["state"] = "blocked"
        if channel["id"] == "repositories" and sources and all(s.get("status") != "success" for s in sources):
            channel["state"] = "blocked"
        if channel["id"] == "publishers":
            channel["pendingLeadCount"] = len(ledger.get("publicationLeads", []))
            checked = valid_times(l.get("verifiedAt") for l in ledger.get("publicationLeads", []))
            channel["lastManualLeadCheckAt"] = max(checked) if checked else None
    result = {"schemaVersion": "1.0.0", "service": {"name": config["name"], "operatingState": config["operatingState"],
        "publicAccess": config["publicAccess"], "reviewPolicy": config["review"]["currentPolicy"],
        "stateBasis": "Literal operating configuration plus real saved source/edition history; not a promise of connected channels."},
        "refresh": refresh, "channels": channels, "review": config["review"],
        "latestEdition": editions[-1] if editions else None, "editions": list(reversed(editions)),
        "runHistory": list(reversed(runs)), "editorialChanges": list(reversed(editorial)),
        "historyLinks": {"editions": "./editions/index.json", "runs": "./runs.json", "editorial": "./editorial-log.json"}}
    atomic_json(report / "service.json", result)
    return result


def record_commit(root, ledger, mode, baseline=False):
    report = Path(root) / REPORT_PATH
    enrich_channels(ledger)
    edition, created = register_edition(root, ledger, "baseline-import" if baseline else (
        "live-ingest" if mode in LIVE_COLLECTION_MODES else "cache-reparse"))
    if baseline and not created:
        return build_service(root, ledger)
    if baseline:
        # Idempotent import; repeated service builds never fabricate previous runs.
        run_id = "baseline-import-" + edition["id"]
        attempt_at = edition["registeredAt"]
    else:
        attempt_at = ledger["ingest"]["startedAt"]
        run_id = hashlib.sha256((mode + attempt_at).encode()).hexdigest()[:20]
    channel = "instagram" if mode == "live-public-instagram" else ledger["ingest"].get("channel")
    outcomes = run_source_details(ledger.get("sources", []), attempt_at, channel) if mode in LIVE_COLLECTION_MODES and not baseline else []
    channels = sorted(set([s["channel"] for s in outcomes] + ([channel] if channel else [])))
    append_unique(report / "runs.json", "runs", {"id": run_id, "attemptAt": attempt_at,
        "finishedAt": ledger["ingest"].get("finishedAt") if not baseline else attempt_at,
        "mode": "baseline-import" if baseline else mode, "status": ledger["ingest"]["status"], "committed": True,
        "networkCollection": mode in LIVE_COLLECTION_MODES and not baseline, "editionCreated": created,
        "channel": channel, "channels": channels, "sourceOutcomes": outcomes,
        "editionId": edition["id"] if edition else None,
        "sourceFailures": ledger.get("coverage", {}).get("sources", {}).get("failed", 0) if baseline else sum(s["status"] != "success" for s in outcomes),
        "note": "Registered the existing saved source snapshot; no new requests were made." if baseline else (
            "Reparsed saved responses; no new edition or retrieval date." if mode not in LIVE_COLLECTION_MODES else (
                "Bounded public Instagram collection; earlier checks from other channels were not repeated." if mode == "live-public-instagram" else "New source collection; review before publishing."))})
    if not (report / "editorial-log.json").exists():
        atomic_json(report / "editorial-log.json", {"schemaVersion": "1.0.0", "changes": []})
    return build_service(root, ledger)


def record_failure(root, manifest):
    """Failure changes only operation history/service state, never ledger or editions."""
    report = Path(root) / REPORT_PATH
    ledger = read_json(report / "ledger.json", None)
    if ledger is None:
        return None
    mode = manifest.get("mode", "live-http")
    channel = manifest.get("channel") or ("instagram" if mode == "live-public-instagram" else None)
    outcomes = run_source_details(manifest.get("sources", []), manifest["startedAt"], channel, keep_undated=True)
    channels = sorted(set([s["channel"] for s in outcomes] + ([channel] if channel else [])))
    run_id = hashlib.sha256((mode + manifest["startedAt"]).encode()).hexdigest()[:20]
    append_unique(report / "runs.json", "runs", {"id": run_id, "attemptAt": manifest["startedAt"],
        "finishedAt": manifest["finishedAt"], "mode": mode, "status": manifest["status"], "committed": False,
        "networkCollection": mode in LIVE_COLLECTION_MODES, "editionCreated": False, "editionId": None,
        "channel": channel, "channels": channels, "sourceOutcomes": outcomes,
        "sourceFailures": sum(s["status"] != "success" for s in outcomes),
        "note": manifest.get("note") or "Collection attempt was not committed; previous snapshot, editions and retrieval dates were preserved."})
    return build_service(root, ledger)


def editorial_note(root, text, reviewer, record_ids):
    if not text.strip() or not reviewer.strip():
        raise ValueError("An editorial note requires text and an attributed reviewer")
    stamp = utc_now()
    item = {"id": hashlib.sha256((stamp + reviewer + text).encode()).hexdigest()[:20], "recordedAt": stamp,
            "reportedBy": reviewer, "note": text.strip(), "recordIds": record_ids,
            "kind": "editorial-note-not-new-ingestion"}
    append_unique(Path(root) / REPORT_PATH / "editorial-log.json", "changes", item)
    return build_service(root, read_json(Path(root) / REPORT_PATH / "ledger.json", {}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", action="store_true", help="Import the existing real baseline once; no network")
    parser.add_argument("--note", help="Append an attributed editorial note, without altering activity claims")
    parser.add_argument("--reviewer", help="Name/role supplied by the person recording an editorial note")
    parser.add_argument("--record-id", action="append", default=[])
    args = parser.parse_args()
    ledger_path = ROOT / REPORT_PATH / "ledger.json"
    ledger = read_json(ledger_path, None)
    if not ledger:
        parser.error("A genuine saved ledger is required")
    if args.note:
        if not args.reviewer:
            parser.error("--note requires --reviewer")
        service = editorial_note(ROOT, args.note, args.reviewer, args.record_id)
    elif args.bootstrap:
        enrich_channels(ledger)
        atomic_json(ledger_path, ledger)
        service = record_commit(ROOT, ledger, ledger["ingest"].get("mode", "unknown"), baseline=True)
    else:
        service = build_service(ROOT, ledger)
    print(json.dumps({"operatingState": service["service"]["operatingState"], "editions": len(service["editions"]),
                      "lastDayIngested": service["refresh"]["lastDayIngested"], "scheduleActive": service["refresh"]["scheduleActive"]}, indent=2))


if __name__ == "__main__":
    main()
