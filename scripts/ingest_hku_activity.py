#!/usr/bin/env python3
"""Bounded, evidence-first public HKU activity ingestion; no productivity scoring."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import threading
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HK = ZoneInfo("Asia/Hong_Kong")
MONTHS = {m.lower(): i for i, m in enumerate(
    ["", "January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"]) if m}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
DATE_RE = re.compile(r"\b(\d{1,2})[\s-]+(" + "|".join(MONTHS) + r")[\s,-]+(20\d{2})\b", re.I)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def normalized(value):
    value = unicodedata.normalize("NFKD", value).casefold()
    return clean(re.sub(r"[^\w\s]", " ", value))


def canonical(url, base="https://www.arch.hku.hk/"):
    p = urlsplit(urljoin(base, url))
    path = re.sub(r"/+", "/", p.path)
    if not Path(path).suffix:
        path = path.rstrip("/") + "/"
    return urlunsplit(("https", p.netloc.lower(), path, "", ""))


def stable_id(prefix, value):
    return prefix + "-" + hashlib.sha256(value.encode()).hexdigest()[:14]


def parse_dates(text):
    """Only day-precision dates; a bare publication year is not window evidence."""
    text = clean(text).replace("–", "-").replace("—", "-")
    # Expand shared-month ranges, e.g. '20-24 July 2026'.
    text = re.sub(r"\b(\d{1,2})\s*-\s*(\d{1,2})\s+(\w+)\s+(20\d{2})",
                  r"\1 \3 \4 - \2 \3 \4", text)
    hits = []
    for m in DATE_RE.finditer(text):
        try:
            hits.append((m.start(), date(int(m[3]), MONTHS[m[2].lower()], int(m[1])).isoformat()))
        except ValueError:
            pass
    for m in re.finditer(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text):
        try:
            hits.append((m.start(), date.fromisoformat(m[0]).isoformat()))
        except ValueError:
            pass
    return list(dict.fromkeys(v for _, v in sorted(hits)))


def overlaps(start, end, window_start, as_of):
    return bool(start and start <= as_of and (end or start) >= window_start)


def content_root(soup, profile=False):
    if profile:
        return soup.select_one(".people-content-wrapper")
    # HKU puts a search-only .pageContent FIRST, then a stale sidebar, then the actual article.
    root = soup.select_one(".pageContent.right") or soup.select_one("main") or soup.select_one("article")
    return root or soup


def parse_directory(html, department):
    soup = BeautifulSoup(html, "html.parser")
    by_url = {}
    # Union BOTH alphabetical and title views; never filter to academics only.
    for a in soup.select("a.peopleItem[href]"):
        url = canonical(a["href"], department["url"])
        if "/staff/" not in urlsplit(url).path:
            continue
        name_node = a.select_one(".name")
        if not name_node:
            continue
        name = clean(name_node.get_text(" ", strip=True))
        # In the title-sorted view, .title.textGrey holds qualifications, not the job role.
        title = a.select_one(".title:not(.textGrey)")
        role = clean(title.get_text(" ", strip=True)) if title else ""
        entry = by_url.setdefault(url, {"name": name, "profileUrl": url, "roles": [], "directoryViews": []})
        if role and role not in entry["roles"]:
            entry["roles"].append(role)
        for c in a.get("class", []):
            if c.startswith("filter_sortBy") and c not in entry["directoryViews"]:
                entry["directoryViews"].append(c)
    return list(by_url.values())


def merge_people(rosters):
    people, by_url = [], {}
    for dept, roster in rosters:
        membership = {"id": dept["id"], "label": dept["label"], "directoryUrl": dept["url"]}
        for item in roster:
            # A shared canonical profile is identity evidence; similar names/initials are not.
            person = by_url.get(item["profileUrl"])
            if person is None:
                person = {"id": stable_id("person", item["profileUrl"]), "name": item["name"],
                          "profileUrl": item["profileUrl"], "profileUrls": [], "roles": [],
                          "departmentMemberships": [], "directoryEvidence": []}
                people.append(person)
            by_url[item["profileUrl"]] = person
            if item["profileUrl"] not in person["profileUrls"]:
                person["profileUrls"].append(item["profileUrl"])
            if membership not in person["departmentMemberships"]:
                person["departmentMemberships"].append(membership)
            person["roles"] = sorted(set(person["roles"] + item["roles"]))
            person["directoryEvidence"].append({"sourceUrl": dept["url"], "profileUrl": item["profileUrl"],
                                                  "roles": item["roles"], "views": item["directoryViews"]})
    return sorted(people, key=lambda p: p["name"].casefold())


def parse_index(html, base, kind):
    explicit_empty = False
    if html.lstrip().startswith("{"):
        obj = json.loads(html)
        # The site's JSON API uses a body-level 404 for an explicit exhausted result.
        if obj.get("code") == 404 and obj.get("max") == 0 and obj.get("next_page") is False and "No Event was found." in obj.get("content", ""):
            return []
        if obj.get("code") != 200 or "content" not in obj:
            raise ValueError("Unexpected official pagination response")
        html = obj["content"]
        explicit_empty = obj.get("post_count") in (0, "0")
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for card in soup.select(".eventItem"):
        title = card.select_one(".title")
        dates = card.select_one(".postdate")
        a = title.find_parent("a", href=True) if title else None
        if not a:
            continue
        url = canonical(a["href"], base)
        if urlsplit(url).netloc != "www.arch.hku.hk":
            continue
        parsed = parse_dates(dates.get_text(" ", strip=True) if dates else "")
        items.append({"title": clean(title.get_text(" ", strip=True)), "url": url,
                      "start": parsed[0] if parsed else None, "end": parsed[1] if len(parsed) > 1 else None,
                      "rawDate": clean(dates.get_text(" ", strip=True)) if dates else None, "kind": kind})
    if not items and not explicit_empty:
        raise ValueError("No parseable index cards; no explicit empty-page marker. Selector/source requires review")
    return list({i["url"]: i for i in items}.values())


def matching_people(root, people):
    text = normalized(root.get_text(" ", strip=True))
    linked = {canonical(a["href"]) for a in root.select("a[href]") if "/staff/" in a["href"]}
    result = []
    for p in people:
        if linked.intersection(p["profileUrls"]):
            result.append({"personId": p["id"], "matchMethod": "direct-profile-link",
                           "role": "Named/linked in source; individual role requires reading source"})
            continue
        names = [p["name"]]
        if "," in p["name"]:
            surname, rest = p["name"].split(",", 1)
            names.append(rest.strip() + " " + surname)
        if any(" " + normalized(n) + " " in " " + text + " " for n in names):
            result.append({"personId": p["id"], "matchMethod": "exact-full-name",
                           "role": "Name mentioned; role/identity require source review"})
    return result


class Fetcher:
    def __init__(self, cache_dir, timeout=15, reparse_cache=False):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.reparse_cache = reparse_cache
        self.records = []
        self.lock = threading.Lock()

    def fetch(self, url, source_id, kind):
        if not (urlsplit(url).hostname or "").endswith(".hku.hk"):
            raise ValueError("Only configured public HKU hosts are allowed")
        attempted = now()
        cache_key = hashlib.sha256(url.encode()).hexdigest()
        meta_path = self.cache_dir / (cache_key + ".json")
        body_path = self.cache_dir / (cache_key + ".html")
        if self.reparse_cache:
            record = json.loads(meta_path.read_text()) if meta_path.exists() else {
                "id": source_id, "url": url, "kind": kind, "lastAttemptAt": None,
                "lastSuccessfulFetchAt": None, "status": "failed", "itemsFound": 0,
                "error": "No saved response; --reparse-cache does not make network requests"}
            record.update({"id": source_id, "kind": kind, "fetchMode": "saved-response-reparse"})
            with self.lock:
                self.records.append(record)
            return (body_path.read_text() if record["status"] == "success" and body_path.exists() else None), record
        record = {"id": source_id, "url": url, "kind": kind, "lastAttemptAt": attempted,
                  "lastSuccessfulFetchAt": None, "status": "failed", "error": None, "itemsFound": 0}
        body = None
        for attempt in range(2):
            try:
                request = Request(url, headers={"User-Agent": "HKU-Public-Activity-Ledger/0.1 (bounded academic directory audit)",
                                               "Accept": "text/html,application/json"})
                with urlopen(request, timeout=self.timeout) as response:
                    final_url = response.geturl()
                    if not (urlsplit(final_url).hostname or "").endswith(".hku.hk"):
                        raise ValueError("Redirect outside public HKU allowlist")
                    raw = response.read(3_000_001)
                    if len(raw) > 3_000_000:
                        raise ValueError("Response exceeds 3 MB source bound")
                    body = raw.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
                    record.update({"status": "success", "lastSuccessfulFetchAt": now(), "httpStatus": response.status,
                                   "finalUrl": final_url, "sha256": hashlib.sha256(raw).hexdigest()})
                    body_path.write_bytes(raw)
                break
            except (HTTPError, URLError, OSError, ValueError) as exc:
                record["error"] = str(exc)[:350]
                if isinstance(exc, HTTPError) and exc.code in (401, 403, 404, 410, 429):
                    break  # No bypass of access blocks, no aggressive retries.
                if attempt == 0:
                    time.sleep(0.4)
        if body is not None:
            record["error"] = None
        meta_path.write_text(json.dumps(record, indent=2))
        with self.lock:
            self.records.append(record)
        return body, record


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def commit_snapshot(output, ledger, critical_ok):
    """Critical directory failure must never replace a prior committed snapshot."""
    if not critical_ok:
        return False
    atomic_json(output, ledger)
    return True


def activity_base(item, source, discovered, status="announced"):
    return {"id": stable_id("activity", item["url"]), "title": item["title"],
            "evidenceUrl": item["url"], "sourceUrl": item["url"], "sourceId": source,
            "eventDate": item.get("start"), "eventEndDate": item.get("end"),
            "eventDatePrecision": "day" if item.get("start") else "unknown",
            "dateBasis": "scheduled-event-date" if status == "announced" else "publication-date",
            "publicationDate": item.get("start") if status != "announced" else None,
            "discoveredAt": discovered, "kind": item["kind"], "status": status,
            "tentative": status == "announced", "personIds": [], "personEvidence": [],
            "evidenceExcerpt": "", "reviewState": "automated-candidate"}


def ingest(args):
    config = json.loads((ROOT / "scripts/hku_activity_sources.json").read_text())
    overrides = json.loads((ROOT / "scripts/hku_activity_curated.json").read_text())
    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(HK).date()
    window_start = as_of - timedelta(days=args.window_days - 1)
    as_of_s, start_s = as_of.isoformat(), window_start.isoformat()
    leads_path = ROOT / config["publicationLeadsFile"]
    leads_input = json.loads(leads_path.read_text()) if leads_path.exists() else {"leads": []}
    publication_leads = [lead for lead in leads_input.get("leads", [])
                         if overlaps(lead.get("suggestedOnlineDate"), None, start_s, as_of_s)]
    started = now()
    output = ROOT / "public/internal/hku-activity/ledger.json"
    previous = json.loads(output.read_text()) if output.exists() else {}
    if args.reparse_cache:
        # Preserve genuine failure provenance when replaying an earlier-version cache.
        for source in previous.get("sources", []):
            path = ROOT / "data/hku-activity/cache" / (hashlib.sha256(source["url"].encode()).hexdigest() + ".json")
            if source["status"] == "failed" and not path.exists():
                atomic_json(path, source)
    fetcher = Fetcher(ROOT / "data/hku-activity/cache", args.timeout, args.reparse_cache)
    rosters, critical_ok, errors = [], True, []
    for dept in config["directories"]:
        html, record = fetcher.fetch(dept["url"], "directory-" + dept["id"], "directory")
        roster = parse_directory(html, dept) if html else []
        record["itemsFound"] = len(roster)
        if len(roster) < dept["minimumPeople"]:
            critical_ok = False
            record["status"] = "failed"
            record["error"] = record["error"] or "Directory parser returned fewer than configured safety minimum"
        rosters.append((dept, roster))
    if not critical_ok:
        manifest = {"startedAt": started, "finishedAt": now(), "status": "aborted-critical-source-failure",
                    "snapshotReplaced": False, "sources": fetcher.records}
        atomic_json(ROOT / "data/hku-activity/last-attempt.json", manifest)
        print(json.dumps(manifest, indent=2))
        return 2
    people = merge_people(rosters)
    by_profile = {url: p for p in people for url in p["profileUrls"]}
    activities = {}

    def check_profile(person):
        html, rec = fetcher.fetch(person["profileUrl"], "profile-" + person["id"], "profile")
        root = content_root(BeautifulSoup(html, "html.parser"), profile=True) if html else None
        checked = {"status": "checked" if root else "failed", "checkedAt": rec["lastSuccessfulFetchAt"],
                   "sourceUrl": person["profileUrl"], "error": rec["error"],
                   "datedCandidatesInWindow": 0, "undatedOrYearOnlyReferences": 0,
                   "note": "Profile checked only; absence of recent dated items is not absence of activity."}
        candidates = []
        if root is None and html:
            checked["error"] = "Expected person-content container absent; parser review required"
            rec["status"], rec["error"] = "failed", checked["error"]
        if root:
            # Precise dates must occur within a self-contained paragraph/list item.
            for block in root.select("p,li"):
                text = clean(block.get_text(" ", strip=True))
                dates = parse_dates(text)
                if not dates and re.search(r"\b20\d{2}\b", text):
                    checked["undatedOrYearOnlyReferences"] += 1
                if dates and any(overlaps(d, d, start_s, as_of_s) for d in dates):
                    event_date = next(d for d in dates if start_s <= d <= as_of_s)
                    item = {"url": person["profileUrl"], "title": "Dated reference on " + person["name"] + "'s profile", "start": event_date,
                            "end": None, "kind": "dated profile reference"}
                    a = activity_base(item, rec["id"], rec["lastSuccessfulFetchAt"], "reference-needs-review")
                    a["id"] = stable_id("activity", item["url"] + text)
                    a.update({"personIds": [person["id"]], "personEvidence": [{"personId": person["id"],
                              "matchMethod": "own-profile", "role": "Dated profile reference; context requires review"}],
                              "dateBasis": "date-in-profile-text", "publicationDate": None, "evidenceExcerpt": ""})
                    candidates.append(a)
            checked["datedCandidatesInWindow"] = len(candidates)
            rec["itemsFound"] = len(candidates)
        person["profileCheck"] = checked
        person["publicationCoverage"] = {"status": "profile-only; repository checked separately",
                                          "note": "Year-only references cannot establish a rolling-60-day publication date."}
        query_name = person["name"]
        if "," in query_name:
            surname, rest = query_name.split(",", 1)
            query_name = clean(rest + " " + surname)
        q = '"' + query_name + '" HKU after:' + (window_start - timedelta(days=1)).isoformat() + ' before:' + (as_of + timedelta(days=1)).isoformat()
        person["followupSearchUrl"] = "https://www.google.com/search?" + urlencode({"q": q})
        person["followupSearchNote"] = "Suggested manual web query; results have NOT been searched by this ingestion."
        return candidates

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for candidates in pool.map(check_profile, people):
            for a in candidates:
                activities[a["id"]] = a
    print("Checked profiles:", len(people), flush=True)

    index_candidates = {}
    for index in config["indexes"]:
        for page in range(1, index["maxPages"] + 1):
            if index["pagination"] == "events-json":
                url = index["url"] if page == 1 else index["url"] + "?" + urlencode(
                    {"is_json": 1, "page_num": page, "event_year": "", "subcat": ""})
            else:
                url = index["url"] if page == 1 else index["url"] + "?" + urlencode({"paged": page})
            html, rec = fetcher.fetch(url, index["id"] + "-page-" + str(page), "index")
            if not html:
                break
            try:
                items = parse_index(html, url, index["kind"])
            except (ValueError, json.JSONDecodeError) as exc:
                rec["status"], rec["error"] = "failed", str(exc)
                break
            rec["itemsFound"] = len(items)
            rec["paginationBound"] = index["maxPages"]
            rec["windowBoundaryReached"] = bool(items) and all(i["start"] and (i["end"] or i["start"]) < start_s for i in items)
            for item in items:
                if overlaps(item["start"], item["end"], start_s, as_of_s):
                    item["indexSourceId"] = rec["id"]
                    index_candidates[item["url"]] = item
            if rec["windowBoundaryReached"] or not items:
                break
            if page == index["maxPages"]:
                rec["coverageNote"] = "Configured pagination bound reached; older or hidden items may remain."

    def check_item(item):
        html, rec = fetcher.fetch(item["url"], stable_id("detail", item["url"]), "activity-detail")
        if not html:
            return None
        root = content_root(BeautifulSoup(html, "html.parser"))
        matches = matching_people(root, people)
        rec["itemsFound"] = len(matches)
        if not matches:
            return None
        status = "announced" if item["kind"] == "event" else "reported-mention"
        a = activity_base(item, rec["id"], rec["lastSuccessfulFetchAt"], status)
        a.update({"personIds": [p["personId"] for p in matches], "personEvidence": matches,
                  "indexSourceId": item["indexSourceId"],
                  "evidenceExcerpt": "",
                  "caution": "An event listing does not establish attendance or completion; a name mention does not establish authorship."})
        return a

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for a in pool.map(check_item, list(index_candidates.values())[:config["maxActivityDetails"]]):
            if a:
                activities[a["id"]] = a

    # Finite publication gateway/repository checks. No claims of complete author-publication coverage.
    publication_sources = []
    for source in config["publicationSources"]:
        html, rec = fetcher.fetch(source["url"], source["id"], "publication-gateway")
        rec["coverageNote"] = "Gateway reachability and exposed links only; not a complete author bibliography."
        if html:
            soup = BeautifulSoup(html, "html.parser")
            rec["itemsFound"] = len({canonical(a["href"], source["url"]) for a in soup.select("a[href]")
                                      if "/handle/" in a["href"]})
        publication_sources.append(rec)

    # Curated evidence is separate input, re-fetched and source-substring validated every run.
    for override in overrides:
        if not overlaps(override["eventDate"], override.get("eventEndDate"), start_s, as_of_s):
            continue
        html, rec = fetcher.fetch(override["url"], stable_id("curated", override["url"]), "curated-evidence")
        if not html:
            continue
        root = content_root(BeautifulSoup(html, "html.parser"))
        page_text = normalized(root.get_text(" ", strip=True))
        evidence = override["evidenceText"]
        if normalized(evidence) not in page_text:
            rec["status"], rec["error"] = "failed", "Curated evidence text no longer present in fetched source"
            continue
        matches = []
        for assignment in override["people"]:
            p = by_profile.get(canonical(assignment["profileUrl"]))
            if not p or normalized(assignment["evidenceText"]) not in page_text:
                errors.append({"sourceUrl": override["url"], "error": "Curated person/evidence did not validate", "profileUrl": assignment["profileUrl"]})
                continue
            matches.append({"personId": p["id"], "matchMethod": "curated-primary-source",
                            "role": assignment["role"], "evidenceText": assignment["evidenceText"]})
        if not matches:
            continue
        item = {"url": canonical(override["url"]), "title": override["title"], "start": override["eventDate"],
                "end": override.get("eventEndDate"), "kind": override["kind"]}
        a = activity_base(item, rec["id"], rec["lastSuccessfulFetchAt"], override["status"])
        a.update({"personIds": [p["personId"] for p in matches], "personEvidence": matches,
                  "evidenceExcerpt": evidence, "reviewState": "curated-source-checked",
                  "publicationDate": override.get("publicationDate"),
                  "dateBasis": "scheduled-event-date" if override["status"] == "announced" else "reported-event-date",
                  "caution": override.get("caution", "Programme evidence is not proof of attendance or a new publication.")})
        activities[a["id"]] = a
        rec["itemsFound"] = len(matches)

    failed = [r for r in fetcher.records if r["status"] != "success"]
    finished = now()
    fully_successful = not failed and not errors
    fetched_at = max(r["lastSuccessfulFetchAt"] for r in fetcher.records if r["lastSuccessfulFetchAt"])
    for a in activities.values():
        old = next((x for x in previous.get("activities", []) if x["id"] == a["id"]), None)
        if old:
            a["discoveredAt"] = old["discoveredAt"]
    for p in people:
        p["activityIds"] = [a["id"] for a in activities.values() if p["id"] in a["personIds"]]
        p["activityCoverage"] = {"status": "evidence-found" if p["activityIds"] else (
            "profile-check-failed" if p["profileCheck"]["status"] == "failed" else "no-matching-dated-evidence-in-bounded-sources"),
            "note": "No matching evidence is not evidence of inactivity; external publications, practice and unannounced work are not exhaustively covered."}
    ledger = {"schemaVersion": "1.0.0", "scope": {"label": "HKU Architecture and Landscape Architecture public activity evidence",
        "asOf": as_of_s, "windowStart": start_s, "windowDays": args.window_days, "inclusive": True,
        "departments": config["directories"], "rosterBasis": "Current directory membership at retrieval, not historical affiliation throughout window"},
        "ingest": {"startedAt": started, "finishedAt": finished,
            "lastDayIngested": datetime.fromisoformat(fetched_at).astimezone(HK).date().isoformat(),
            "lastSuccessfulIngestAt": fetched_at if fully_successful else previous.get("ingest", {}).get("lastSuccessfulIngestAt"),
            "mode": "saved-response-reparse" if args.reparse_cache else "live-http",
            "status": "success" if fully_successful else "partial", "snapshotCommitted": True},
        "coverage": {"people": {"total": len(people), "profilesChecked": sum(p["profileCheck"]["status"] == "checked" for p in people),
                                    "profilesFailed": sum(p["profileCheck"]["status"] == "failed" for p in people)},
                     "sources": {"attempted": len(fetcher.records), "succeeded": len(fetcher.records) - len(failed), "failed": len(failed)},
                     "activityDetailsConsidered": len(index_candidates), "activityDetailLimit": config["maxActivityDetails"],
                     "publicationSources": publication_sources,
                     "limitations": ["Finite configured official sources; not an exhaustive internet search or publication database.",
                         "All roster roles are retained. Counts cannot rank productivity across different job roles.",
                         "Suggested per-person searches have not been executed. Year-only/undated references are excluded from date-window claims.",
                         "Announced events are not confirmed participation/outcomes, even when scheduled dates have passed.",
                         "Date window includes overlapping multi-day events; discovery time is stored separately.",
                         "Profile and news source failures are explicit; last fully successful ingest is not advanced on a partial run."]},
        "people": people, "activities": sorted(activities.values(), key=lambda a: (a["eventDate"] or "", a["title"]), reverse=True),
        "sources": sorted(fetcher.records, key=lambda s: s["id"]), "errors": errors}
    ledger["publicationLeads"] = publication_leads
    ledger["publicationLeadContext"] = {"status": "manual-follow-up-queue-not-refetched", "sourceFile": config["publicationLeadsFile"],
        "note": "Suggested dates only; not verified dated activities. Original verifiedAt/verificationScope are preserved; this run does not re-check metadata, identity or publication dates."}
    ledger["coverage"]["limitations"].append("Separate publication leads are a manually checked follow-up queue, not automatic publication ingestion or dated activity counts; their original verification timestamps are not refreshed.")
    commit_snapshot(output, ledger, True)
    atomic_json(ROOT / "data/hku-activity/last-attempt.json", {"startedAt": started, "finishedAt": finished,
        "status": ledger["ingest"]["status"], "snapshotReplaced": True, "sources": ledger["sources"], "errors": errors})
    print(json.dumps({"output": str(output), "status": ledger["ingest"]["status"],
                      "people": len(people), "activities": len(activities), "failedSources": len(failed), "errors": errors}, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", help="Inclusive window end YYYY-MM-DD; default actual Hong Kong date")
    parser.add_argument("--window-days", type=int, default=60)
    parser.add_argument("--workers", type=int, choices=range(1, 7), default=4)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--reparse-cache", action="store_true", help="Rebuild from saved response bytes without network or advancing retrieval dates")
    args = parser.parse_args()
    if not 1 <= args.window_days <= 366:
        parser.error("window-days must be between 1 and 366")
    return ingest(args)


if __name__ == "__main__":
    sys.exit(main())
