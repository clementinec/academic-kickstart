#!/usr/bin/env python3
"""Bounded public Instagram pages: no login, private API, scroll loop or block retry.

Collect the visible profile grid and verify each post's own timestamp and caption
from JSON served inside its ordinary public page. Raw responses stay local.
"""
import argparse
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from hku_activity_service import atomic_json, enrich_channels, record_commit, record_failure

ROOT = Path(__file__).resolve().parents[1]
REPORT = Path("public/internal/hku-activity")
ACCOUNTS = {"hkuarchitecture": "architecture", "hkulandscape": "landscape"}
HK = ZoneInfo("Asia/Hong_Kong")
MAX_GRID = 12
MAX_POSTS = 24
MAX_CURATED_POSTS = 4


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(value):
    return " ".join((value or "").split())


def post_code(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in {"instagram.com", "www.instagram.com"} or parts.username or parts.password or parts.port not in (None, 443):
        return None
    match = re.fullmatch(r"/(?:[A-Za-z0-9_.]+/)?(?:p|reel)/([A-Za-z0-9_-]+)/?", parts.path)
    return match[1] if match else None


def configured_posts(root):
    path = root / "scripts/hku_instagram_sources.json"
    posts = json.loads(path.read_text()).get("posts", []) if path.exists() else []
    if not isinstance(posts, list) or len(posts) > MAX_CURATED_POSTS:
        raise ValueError("At most four manually configured public post links are allowed")
    for item in posts:
        if not post_code(item.get("url", "")) or item.get("account") not in ACCOUNTS:
            raise ValueError("Configured posts need an allowed permalink and departmental account")
    return posts


class PublicHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts, self.times, self.meta = [], [], {}
        self.script = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") in {"application/json", "application/ld+json"}:
            self.script = []
        if tag == "time" and attrs.get("datetime"):
            self.times.append(attrs["datetime"])
        if tag == "meta":
            self.meta[attrs.get("property") or attrs.get("name")] = attrs.get("content", "")

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.scripts.append("".join(self.script))
            self.script = None


def walk(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            yield item
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def parse_public_post(html, url):
    """Never use a comment timestamp, image URL year, relative age or event date."""
    code = post_code(url)
    if not code:
        raise ValueError("Not an allowed public Instagram post permalink")
    parser = PublicHTML()
    parser.feed(html)
    if parser.meta.get("og:url") and post_code(parser.meta["og:url"]) != code:
        raise ValueError("Public page canonical URL does not match requested post")
    candidates = []
    for raw in parser.scripts:
        try:
            value = json.loads(raw)
        except (ValueError, TypeError):
            continue
        for obj in walk(value):
            if obj.get("code", obj.get("shortcode")) != code:
                continue
            stamp = obj.get("taken_at", obj.get("taken_at_timestamp"))
            caption = obj.get("caption")
            caption = caption.get("text") if isinstance(caption, dict) else caption
            if not caption:
                edges = obj.get("edge_media_to_caption", {}).get("edges", [])
                caption = edges[0].get("node", {}).get("text") if edges else None
            owner = (obj.get("user") or obj.get("owner") or {}).get("username")
            if isinstance(stamp, (int, float)) and not isinstance(stamp, bool) and caption and owner:
                candidates.append((int(stamp), clean(caption), owner))
    candidates = list(set(candidates))
    if len(candidates) != 1:
        raise ValueError("No unique post-specific timestamp, caption and account in public HTML")
    stamp, caption, owner = candidates[0]
    if not re.fullmatch(r"[A-Za-z0-9_.]+", owner):
        raise ValueError("Invalid source account")
    posted = datetime.fromtimestamp(stamp, timezone.utc)
    matching_time = False
    for value in parser.times:
        try:
            matching_time |= datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() == stamp
        except ValueError:
            pass
    meta_corroborated = False
    description = parser.meta.get("og:description", parser.meta.get("description", ""))
    header = re.search(r" - " + re.escape(owner) + r" on ([A-Za-z]+ \d{1,2}, \d{4}):", description)
    if header:
        try:
            displayed = datetime.strptime(header[1], "%B %d, %Y").date()
            # Public metadata may use the publisher's US-local date. The actual
            # record still uses permalink-matched taken_at converted to Hong Kong.
            meta_corroborated = abs((displayed - posted.date()).days) <= 1
        except ValueError:
            pass
    if not matching_time and not meta_corroborated:
        raise ValueError("Post timestamp lacks corroborating public time or account/date metadata")
    return {"code": code, "account": owner, "caption": caption,
            "postedAt": posted.isoformat(timespec="seconds"),
            "postingDate": posted.astimezone(HK).date().isoformat(),
            "dateEvidence": "Permalink-matched public media taken_at, corroborated by " + ("matching HTML time datetime" if matching_time else "account/date Open Graph metadata") + "; date converted to Asia/Hong_Kong."}


def normalize_post(parsed, source, discovered_accounts, people, existing, curated):
    code, caption = parsed["code"], parsed["caption"]
    if datetime.fromisoformat(parsed["postedAt"]) > datetime.fromisoformat(source["lastSuccessfulFetchAt"].replace("Z", "+00:00")) + timedelta(minutes=5):
        raise ValueError("Post timestamp is later than its actual retrieval")
    annotation = curated.get(code, {})
    for phrase in annotation.get("captionContains", []):
        if clean(phrase).casefold() not in caption.casefold():
            raise ValueError("Reviewed caption evidence changed for " + code)
    record = {"id": "instagram-" + code, "title": annotation.get("title", "Public post by @" + parsed["account"]),
        "summary": annotation.get("summary", "Public departmental post; classification and individual staff links await review."),
        "evidenceUrl": source["url"], "sourceUrl": source["url"], "sourceId": source["id"],
        "sourceChannel": "instagram", "sourceAccount": {"handle": parsed["account"], "url": "https://www.instagram.com/" + parsed["account"] + "/"},
        "discoveredAccounts": [{"handle": account, "url": "https://www.instagram.com/" + account + "/"} for account in sorted(discovered_accounts)],
        "departmentIds": sorted({ACCOUNTS[a] for a in discovered_accounts}),
        "eventDate": parsed["postingDate"], "eventEndDate": None, "eventDatePrecision": "day", "dateBasis": "publication-date",
        "publicationDate": parsed["postingDate"], "postedAt": parsed["postedAt"], "dateEvidence": parsed["dateEvidence"],
        "discoveredAt": source["lastSuccessfulFetchAt"], "lastVerifiedAt": source["lastSuccessfulFetchAt"],
        "kind": "social post", "status": "public-post", "reviewState": "source-checked", "tentative": True,
        "personIds": [], "personEvidence": [], "relatedRecordIds": [], "evidenceExcerpt": "",
        "caution": "The date is the post publication date, not proof that the work was completed then. Departmental account coverage is not individual staff authorship."}
    # Public summaries are paraphrases; do not republish full captions or comments.
    if annotation.get("advertisedEventDate"):
        date.fromisoformat(annotation["advertisedEventDate"])
        record["advertisedEventDate"] = annotation["advertisedEventDate"]
    for url in annotation.get("relatedUrls", []):
        linked = next((a for a in existing if a["evidenceUrl"].rstrip("/") == url.rstrip("/")), None)
        if linked:
            record["relatedRecordIds"].append(linked["id"])
    for related_code in annotation.get("relatedPostCodes", []):
        if re.fullmatch(r"[A-Za-z0-9_-]+", related_code) and related_code != code:
            record["relatedRecordIds"].append("instagram-" + related_code)
    for assignment in annotation.get("people", []):
        person = next((p for p in people if assignment["profileUrl"] in p.get("profileUrls", [p["profileUrl"]])), None)
        if not person:
            continue
        evidence_url = assignment.get("evidenceUrl", source["url"])
        if evidence_url == source["url"]:
            phrase = clean(assignment.get("evidenceText"))
            if not phrase or phrase.casefold() not in caption.casefold():
                raise ValueError("Named-person caption evidence did not validate for " + code)
            method = "named-in-post-caption"
        else:
            linked = next((a for a in existing if a["evidenceUrl"].rstrip("/") == evidence_url.rstrip("/") and a["id"] in record["relatedRecordIds"] and person["id"] in a.get("personIds", [])), None)
            if not linked:
                raise ValueError("Cross-source person link lacks reviewed related faculty record")
            method = "linked-faculty-coverage-not-caption-authorship"
        record["personIds"].append(person["id"])
        record["personEvidence"].append({"personId": person["id"], "role": assignment["role"], "matchMethod": method, "evidenceUrl": evidence_url})
    record["personIds"] = sorted(set(record["personIds"]))
    return record


def in_window(record, start, end):
    first = record.get("eventDate")
    return bool(first and first <= end and (record.get("eventEndDate") or first) >= start)


def merge_instagram(ledger, snapshot):
    """Merge saved source records without claiming the HKU sweep re-fetched them."""
    start, end = ledger["scope"]["windowStart"], ledger["scope"]["asOf"]
    original = {a["id"]: a for a in ledger.get("activities", [])}
    other = [a for a in original.values() if a.get("sourceChannel") != "instagram" and in_window(a, start, end)]
    social = [deepcopy(a) for a in snapshot.get("activities", []) if in_window(a, start, end)]
    for activity in social:
        if activity["id"] in original:
            activity["discoveredAt"] = original[activity["id"]]["discoveredAt"]
    ledger["activities"] = sorted(other + social, key=lambda a: (a.get("eventDate") or "", a["title"]), reverse=True)
    sources = [s for s in ledger.get("sources", []) if s.get("sourceChannel") != "instagram"] + deepcopy(snapshot.get("sources", []))
    ledger["sources"] = sorted({s["id"]: s for s in sources}.values(), key=lambda s: s["id"])
    failed = sum(s.get("status") != "success" for s in ledger["sources"])
    ledger.setdefault("coverage", {})["sources"] = {"attempted": len(ledger["sources"]), "failed": failed, "succeeded": len(ledger["sources"]) - failed}
    ledger["coverage"]["instagram"] = {"collectedAt": snapshot.get("finishedAt"), "status": snapshot.get("status"),
        "gridLimitPerAccount": MAX_GRID, "verifiedPostsThisRun": snapshot.get("verifiedPostCount", 0),
        "note": "Public visible profile grids only, not an exhaustive 60-day feed. Saved post timestamps are retained when another channel is refreshed. Source records are not unique accomplishments."}
    for person in ledger.get("people", []):
        person["activityIds"] = [a["id"] for a in ledger["activities"] if person["id"] in a.get("personIds", [])]
        if person["activityIds"]:
            person.setdefault("activityCoverage", {})["status"] = "evidence-found"
        else:
            person.setdefault("activityCoverage", {})["status"] = "no-matching-dated-evidence-in-bounded-sources" if person.get("profileCheck", {}).get("status") == "checked" else "profile-check-failed"
    return ledger


class AccessBlocked(Exception):
    pass


def collect(root, as_of, merge=True):
    from playwright.sync_api import sync_playwright
    report, cache = root / REPORT, root / "data/hku-activity/cache/instagram"
    cache.mkdir(parents=True, exist_ok=True)
    ledger = json.loads((report / "ledger.json").read_text())
    old = json.loads((report / "instagram.json").read_text()) if (report / "instagram.json").exists() else {}
    curated = json.loads((root / "scripts/hku_instagram_curated.json").read_text())
    seeds = configured_posts(root)
    started, sources, records, discovered = now(), [], [], {}
    start = (date.fromisoformat(as_of) - timedelta(days=59)).isoformat()

    def read_page(context, url, source_id, kind, callback):
        source = {"id": source_id, "url": url, "sourceChannel": "instagram", "kind": kind,
                  "lastAttemptAt": now(), "lastSuccessfulFetchAt": None, "status": "failed", "itemsFound": 0,
                  "fetchMode": "ordinary-public-browser-no-login"}
        sources.append(source)
        page = context.new_page()
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
            source.update({"httpStatus": response.status if response else None, "finalUrl": page.url})
            if response and response.status in (401, 403, 429):
                raise AccessBlocked("Public page access blocked; no retry or further requests in this run")
            if not response or response.status != 200 or urlsplit(page.url).hostname not in {"www.instagram.com", "instagram.com"}:
                raise ValueError("Public page did not return an allowed HTTP 200 response")
            if kind == "social-profile-grid" and urlsplit(page.url).path.rstrip("/") != urlsplit(url).path.rstrip("/"):
                raise ValueError("Profile redirected away from the configured account")
            page.wait_for_timeout(1500)
            html = page.content()
            if len(html.encode("utf-8")) > 8_000_000:
                raise ValueError("Rendered public page exceeds 8 MB bound")
            result = callback(page, html)
            source.update({"status": "success", "lastSuccessfulFetchAt": now(), "error": None,
                           "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest()})
            (cache / (source_id + ".html")).write_text(html, encoding="utf-8")
            return result, source
        except Exception as exc:
            source["error"] = str(exc)[:450]
            if isinstance(exc, AccessBlocked):
                raise
            return None, source
        finally:
            atomic_json(cache / (source_id + ".json"), source)
            page.close()

    with sync_playwright() as driver:
        browser = driver.webkit.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 900}, timezone_id="Asia/Hong_Kong")
        try:
            for account in ACCOUNTS:
                def grid(page, html):
                    links = page.locator('a[href*="/p/"],a[href*="/reel/"]').evaluate_all('(nodes) => [...new Set(nodes.map(n => n.href))]')
                    links = [url for url in links if post_code(url)][:MAX_GRID]
                    if not links:
                        raise ValueError("No public post grid visible; not evidence of an empty feed")
                    return links
                links, source = read_page(context, "https://www.instagram.com/" + account + "/", "instagram-profile-" + account, "social-profile-grid", grid)
                source["itemsFound"] = len(links or [])
                source["coverageNote"] = "At most 12 visible public grid links; no pagination, login or complete-feed claim."
                for url in links or []:
                    entry = discovered.setdefault(post_code(url), {"url": url, "accounts": []})
                    entry["accounts"].append(account)
            for item in seeds:
                discovered.setdefault(post_code(item["url"]), {"url": item["url"], "accounts": [], "configuredAccount": item["account"]})
            for code, entry in list(discovered.items())[:MAX_POSTS + MAX_CURATED_POSTS]:
                parsed, source = read_page(context, entry["url"], "instagram-source-" + code, "social-post", lambda page, html: parse_public_post(html, entry["url"]))
                if parsed:
                    try:
                        record = normalize_post(parsed, source, entry["accounts"], ledger["people"], ledger["activities"], curated)
                        if entry.get("configuredAccount"):
                            if parsed["account"] != entry["configuredAccount"]:
                                raise ValueError("Configured post account does not match the public post")
                            record["departmentIds"] = [ACCOUNTS[entry["configuredAccount"]]]
                            record["discoveryMethod"] = "curated-public-permalink"
                        records.append(record)
                        source["itemsFound"] = 1
                    except ValueError as exc:
                        source.update({"status": "failed", "error": str(exc)})
                print(json.dumps({"post": code, "status": source["status"], "date": parsed.get("postingDate") if parsed else None, "error": source.get("error")}), flush=True)
        except AccessBlocked:
            pass
        finally:
            context.close()
            browser.close()
    for source in sources:
        atomic_json(cache / (source["id"] + ".json"), source)
    finished = now()
    manifest = {"startedAt": started, "finishedAt": finished, "mode": "live-public-instagram", "channel": "instagram", "sources": sources,
                "status": "partial" if any(s["status"] != "success" for s in sources) else "success", "verifiedPostCount": len(records)}
    if not records:
        manifest["status"] = "blocked-public-instagram"
        atomic_json(report / "instagram-attempt.json", manifest)
        record_failure(root, manifest)
        print("No verified posts; previous snapshot and ingestion date preserved.")
        return 2
    previous = {a["id"]: a for a in old.get("activities", []) if in_window(a, start, as_of)}
    for record in records:
        if record["id"] in previous:
            record["discoveredAt"] = previous[record["id"]]["discoveredAt"]
        if in_window(record, start, as_of):
            previous[record["id"]] = record
    retained_sources = {s["id"]: s for s in old.get("sources", []) if s["id"] in {a["sourceId"] for a in previous.values()}}
    for source in sources:
        previous_source = retained_sources.get(source["id"], {})
        if source["status"] != "success" and previous_source.get("lastSuccessfulFetchAt"):
            source["lastSuccessfulFetchAt"] = previous_source["lastSuccessfulFetchAt"]
            source["sha256"] = previous_source.get("sha256")
        retained_sources[source["id"]] = source
    snapshot = {**manifest, "schemaVersion": "1.0.0", "asOf": as_of, "windowStart": start,
                "activities": list(previous.values()), "sources": list(retained_sources.values()),
                "coverageNote": "Visible public grids (12 links/account) plus at most four configured post links; shared permalinks count once. This is not exhaustive 60-day coverage or an authenticated/API feed."}
    atomic_json(report / "instagram.json", snapshot)
    atomic_json(report / "instagram-attempt.json", manifest)
    if merge:
        ledger["scope"].update({"asOf": as_of, "windowStart": start, "windowDays": 60})
        merge_instagram(ledger, snapshot)
        ledger["ingest"].update({"startedAt": started, "finishedAt": finished, "mode": "live-public-instagram",
            "lastDayIngested": datetime.fromisoformat(max(s["lastSuccessfulFetchAt"] for s in sources if s.get("lastSuccessfulFetchAt"))).astimezone(HK).date().isoformat(),
            "status": "partial", "snapshotCommitted": True,
            "note": "Instagram public posts refreshed; faculty and roster sources retain their earlier individual retrieval dates."})
        enrich_channels(ledger)
        atomic_json(report / "ledger.json", ledger)
        record_commit(root, ledger, "live-public-instagram")
    print(json.dumps({"verifiedPostsThisRun": len(records), "instagramRecordsInWindow": len(previous), "merged": merge, "asOf": as_of}), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", help="Reporting-window end only; never a fabricated retrieval date")
    parser.add_argument("--collect-only", action="store_true", help="Save the verified Instagram sidecar for the following full HKU collection")
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of).isoformat() if args.as_of else datetime.now(HK).date().isoformat()
    return collect(ROOT, as_of, not args.collect_only)


if __name__ == "__main__":
    raise SystemExit(main())
