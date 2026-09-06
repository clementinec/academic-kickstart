import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts/ingest_hku_activity.py"
spec = importlib.util.spec_from_file_location("ledger", MODULE)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class LedgerTests(unittest.TestCase):
    def test_day_precision_and_invalid_dates(self):
        self.assertEqual(ledger.parse_dates("20–24 July 2026"), ["2026-07-20", "2026-07-24"])
        self.assertEqual(ledger.parse_dates("2026-09-06; 31-Feb-2026; publication 2026"), ["2026-09-06"])
        self.assertEqual(ledger.parse_dates("July 2026"), [])

    def test_window_overlap_and_future_exclusion(self):
        self.assertTrue(ledger.overlaps("2026-07-08", "2026-07-14", "2026-07-09", "2026-09-06"))
        self.assertFalse(ledger.overlaps("2026-07-08", None, "2026-07-09", "2026-09-06"))
        self.assertFalse(ledger.overlaps("2026-09-07", None, "2026-07-09", "2026-09-06"))

    def test_directory_union_duplicate_and_all_roles(self):
        html = (Path(__file__).parent / "fixtures/directory.html").read_text()
        dept = {"id": "architecture", "label": "Architecture", "url": "https://www.arch.hku.hk/people/arch_staff/"}
        people = ledger.parse_directory(html, dept)
        self.assertEqual(len(people), 3)
        self.assertNotIn("BA HKU; MArch Harvard", [r for p in people for r in p["roles"]])
        self.assertIn("Office Attendant", [r for p in people for r in p["roles"]])
        self.assertTrue(any(not p["roles"] for p in people))
        second = dict(dept, id="landscape", label="Landscape")
        merged = ledger.merge_people([(dept, people), (second, people[:1])])
        self.assertEqual(len(merged), 3)
        self.assertEqual(len(next(p for p in merged if "Professor" in p["roles"])["departmentMemberships"]), 2)

    def test_event_json_parser_canonicalizes_page_tracking(self):
        html = (Path(__file__).parent / "fixtures/events.html").read_text()
        parsed = ledger.parse_index(json.dumps({"code": 200, "content": html}), "https://www.arch.hku.hk/", "event")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["start"], "2026-09-04")
        self.assertEqual(parsed[0]["end"], "2026-09-28")
        self.assertEqual(parsed[0]["url"], "https://www.arch.hku.hk/event_/example/")

    def test_index_selector_failure_not_reported_as_empty_success(self):
        with self.assertRaises(ValueError):
            ledger.parse_index("<html>Temporarily unavailable</html>", "https://www.arch.hku.hk/", "event")
        self.assertEqual(ledger.parse_index('{"code":200,"post_count":0,"content":""}', "https://www.arch.hku.hk/", "event"), [])
        self.assertEqual(ledger.parse_index('{"code":404,"max":0,"next_page":false,"content":"No Event was found."}', "https://www.arch.hku.hk/", "event"), [])

    def test_article_body_ignores_search_panel_and_stale_sidebar(self):
        soup = ledger.BeautifulSoup('<div class="pageContent search">Search</div><div class="pageContent left">Other people</div><div class="pageContent right">Article evidence</div>', "html.parser")
        self.assertEqual(ledger.content_root(soup).get_text(), "Article evidence")

    def test_failed_critical_source_preserves_prior_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            path.write_text('{"ingest":{"lastDayIngested":"2026-08-01"}}')
            before = path.read_bytes()
            self.assertFalse(ledger.commit_snapshot(path, {"fake": "fresh"}, False))
            self.assertEqual(path.read_bytes(), before)

    def test_identical_names_with_distinct_profiles_not_automatically_merged(self):
        dept = {"id": "architecture", "label": "Architecture", "url": "https://www.arch.hku.hk/people/arch_staff/"}
        entries = [{"name": "Lee, K.", "profileUrl": "https://www.arch.hku.hk/staff/arch/lee-one/", "roles": [], "directoryViews": []},
                   {"name": "Lee, K.", "profileUrl": "https://www.arch.hku.hk/staff/dla/lee-two/", "roles": [], "directoryViews": []}]
        self.assertEqual(len(ledger.merge_people([(dept, entries)])), 2)

    def test_cache_reparse_preserves_actual_fetch_time(self):
        with tempfile.TemporaryDirectory() as temp:
            url = "https://www.arch.hku.hk/example/"
            key = ledger.hashlib.sha256(url.encode()).hexdigest()
            record = {"id": "old", "url": url, "kind": "profile", "status": "success", "itemsFound": 0,
                      "lastAttemptAt": "2026-08-01T01:00:00+00:00", "lastSuccessfulFetchAt": "2026-08-01T01:00:01+00:00", "error": None}
            (Path(temp) / (key + ".json")).write_text(json.dumps(record))
            (Path(temp) / (key + ".html")).write_text("<html>Saved source</html>")
            body, checked = ledger.Fetcher(temp, reparse_cache=True).fetch(url, "current", "profile")
            self.assertEqual(checked["lastSuccessfulFetchAt"], "2026-08-01T01:00:01+00:00")
            self.assertEqual(checked["fetchMode"], "saved-response-reparse")
            self.assertIn("Saved source", body)

    def test_announcement_never_auto_promoted_after_date(self):
        item = {"title": "Event", "url": "https://www.arch.hku.hk/event_/example/", "start": "2020-01-01", "kind": "event"}
        activity = ledger.activity_base(item, "source", "2026-09-06T00:00:00+00:00")
        self.assertEqual(activity["status"], "announced")
        self.assertTrue(activity["tentative"])


if __name__ == "__main__":
    unittest.main()
