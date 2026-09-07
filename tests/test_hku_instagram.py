from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ingest_hku_instagram import parse_public_post, normalize_post, merge_instagram, post_code

URL = "https://www.instagram.com/hkulandscape/p/Example123/"
STAMP = 1787628059  # 2026-08-25 03:20:59 UTC


def html(code="Example123", caption="Project Alpha. Supervisor William Shivers.", times=True):
    media = {"code": code, "taken_at": STAMP, "user": {"username": "hkulandscape"}, "caption": {"text": caption}}
    times_html = '<time datetime="2026-09-01T00:00:00Z">comment</time><time datetime="2026-08-25T03:20:59Z">post</time>' if times else ""
    return '<script type="application/json">' + json.dumps({"nested": [media]}) + '</script>' + times_html


class InstagramTests(unittest.TestCase):
    def test_permalink_allowlist(self):
        self.assertEqual(post_code(URL), "Example123")
        self.assertEqual(post_code("https://www.instagram.com/reel/Example123/"), "Example123")
        self.assertIsNone(post_code("https://instagram.com.evil.test/p/Example123/"))
        self.assertIsNone(post_code("https://www.instagram.com/accounts/login/"))
        self.assertIsNone(post_code("javascript://www.instagram.com/p/Example123/"))

    def test_post_specific_timestamp_not_comment(self):
        post = parse_public_post(html(), URL)
        self.assertEqual(post["postingDate"], "2026-08-25")
        self.assertEqual(post["postedAt"], "2026-08-25T03:20:59+00:00")
        self.assertEqual(post["account"], "hkulandscape")

    def test_unrelated_media_is_not_post_evidence(self):
        with self.assertRaises(ValueError):
            parse_public_post(html(code="OtherPost"), URL)
        with self.assertRaises(ValueError):
            parse_public_post('<p>Please log in</p>', URL)

    def test_meta_corroboration_never_supplies_timestamp_alone(self):
        meta = '<meta property="og:description" content="12 likes - hkulandscape on August 24, 2026: Project Alpha">'
        self.assertEqual(parse_public_post(meta + html(times=False), URL)["postingDate"], "2026-08-25")
        with self.assertRaises(ValueError):
            parse_public_post(meta, URL)
        with self.assertRaises(ValueError):
            parse_public_post(html(times=False), URL)

    def test_hong_kong_boundary_and_conflicting_timestamps(self):
        source = html().replace(str(STAMP), str(STAMP - 4 * 3600)).replace("2026-08-25T03:20:59Z", "2026-08-24T23:20:59Z")
        self.assertEqual(parse_public_post(source, URL)["postingDate"], "2026-08-25")
        with self.assertRaises(ValueError):
            parse_public_post(html() + html().replace(str(STAMP), str(STAMP + 1)), URL)

    def test_future_event_is_separate_and_unmatched_posts_retained(self):
        parsed = parse_public_post(html(), URL)
        source = {"url": URL, "id": "post-source", "lastSuccessfulFetchAt": "2026-09-07T00:00:00Z"}
        record = normalize_post(parsed, source, ["hkuarchitecture", "hkulandscape"], [], [],
            {"Example123": {"captionContains": ["Project Alpha"], "advertisedEventDate": "2026-10-01"}})
        self.assertEqual(record["eventDate"], "2026-08-25")
        self.assertEqual(record["advertisedEventDate"], "2026-10-01")
        self.assertEqual(record["personIds"], [])
        self.assertEqual(record["departmentIds"], ["architecture", "landscape"])
        self.assertEqual(record["evidenceExcerpt"], "")
        with self.assertRaises(ValueError):
            normalize_post(parsed, source, ["hkulandscape"], [], [], {"Example123": {"captionContains": ["Different Project"]}})

    def test_merge_preserves_faculty_dates_and_source_record_identity(self):
        faculty = {"id": "faculty", "eventDate": "2026-08-25", "title": "Project Alpha", "sourceChannel": "faculty_web", "personIds": []}
        ledger = {"scope": {"windowStart": "2026-07-10", "asOf": "2026-09-07"}, "ingest": {"lastDayIngested": "2026-09-06"},
                  "activities": [faculty], "sources": [{"id": "faculty-source", "status": "success", "lastSuccessfulFetchAt": "2026-09-06T01:00:00Z"}], "people": []}
        source_before = deepcopy(ledger["sources"])
        post = {"id": "instagram-Example123", "sourceChannel": "instagram", "eventDate": "2026-08-25", "title": "Project post", "personIds": [], "discoveredAt": "2026-09-07T00:00:00Z", "relatedRecordIds": ["faculty"]}
        snapshot = {"activities": [post], "sources": [{"id": "post-source", "sourceChannel": "instagram", "status": "success"}]}
        merge_instagram(ledger, snapshot)
        self.assertEqual(len(ledger["activities"]), 2)
        self.assertEqual(ledger["ingest"]["lastDayIngested"], "2026-09-06")
        self.assertEqual(ledger["sources"][0], source_before[0])
        merge_instagram(ledger, snapshot)
        self.assertEqual(len(ledger["activities"]), 2)


if __name__ == "__main__":
    unittest.main()
