from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import hku_activity_service as service


def example():
    return {"scope": {"asOf": "2026-09-06", "windowStart": "2026-07-09"},
        "ingest": {"status": "partial", "mode": "saved-response-reparse", "startedAt": "2026-09-06T11:00:00+00:00",
                   "finishedAt": "2026-09-06T11:01:00+00:00", "lastDayIngested": "2026-09-06", "lastSuccessfulIngestAt": None},
        "sources": [{"id": "one", "url": "https://www.arch.hku.hk/people/arch_staff/", "status": "success", "lastAttemptAt": "2026-09-06T10:00:00+00:00", "lastSuccessfulFetchAt": "2026-09-06T10:00:01+00:00"}],
        "people": [{"id": "one"}], "activities": [{"id": "activity", "evidenceUrl": "https://www.arch.hku.hk/event_/example/"}],
        "publicationLeads": [{"doi": "example", "verifiedAt": "2026-09-05T10:00:00Z"}], "coverage": {"sources": {"failed": 0}}}


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        config = json.loads((ROOT / "scripts/hku_activity_service_config.json").read_text())
        service.atomic_json(self.root / "scripts/hku_activity_service_config.json", config)

    def tearDown(self):
        self.temp.cleanup()

    def test_channels_follow_evidence_host_and_leads_remain_separate(self):
        ledger = service.enrich_channels(example())
        self.assertEqual(ledger["activities"][0]["sourceChannel"], "faculty_web")
        self.assertEqual(ledger["publicationLeads"][0]["sourceChannel"], "publishers")
        self.assertEqual(ledger["publicationLeads"][0]["verifiedAt"], "2026-09-05T10:00:00Z")
        self.assertEqual(service.source_channel("https://www.usi.hku.hk/news/"), "university_news")
        self.assertEqual(service.source_channel("https://hub.hku.hk/handle/123"), "repositories")
        self.assertEqual(service.source_channel("https://notinstagram.com/"), "other")
        self.assertEqual(service.source_channel("https://instagram.com.evil.example/"), "other")
        self.assertEqual(service.source_channel("https://www.instagram.com/hkuarchitecture/"), "instagram")
        self.assertEqual(service.source_channel("https://arch.hku.hk/"), "faculty_web")
        self.assertEqual(service.source_channel("https://scholars.hku.hk/"), "repositories")
        self.assertEqual(service.source_channel("https://doi.org/10.1234/example"), "publishers")
        self.assertEqual(service.source_channel("https://api.crossref.org/works/example"), "publishers")
        self.assertEqual(service.source_channel("https://onlinelibrary.wiley.com/doi/example"), "publishers")
        self.assertEqual(service.source_channel("https://evilcrossref.org/"), "other")
        self.assertEqual(service.source_channel("javascript://arch.hku.hk/example"), "other")

    def test_bootstrap_once_preserves_genuine_time_and_no_fake_runs(self):
        ledger = example()
        first = service.record_commit(self.root, ledger, "saved-response-reparse", baseline=True)
        second = service.record_commit(self.root, ledger, "saved-response-reparse", baseline=True)
        self.assertEqual(len(second["editions"]), 1)
        self.assertEqual(len(second["runHistory"]), 1)
        self.assertEqual(first["latestEdition"]["retrievedAt"], "2026-09-06T10:00:01+00:00")
        self.assertEqual(first["latestEdition"]["origin"], "baseline-import")
        self.assertFalse(first["refresh"]["scheduleActive"])

    def test_reparse_records_operation_but_does_not_create_edition(self):
        ledger = example()
        service.record_commit(self.root, ledger, "saved-response-reparse", baseline=True)
        ledger["ingest"]["startedAt"] = "2026-10-01T10:00:00+00:00"
        latest = service.record_commit(self.root, ledger, "saved-response-reparse")
        self.assertEqual(len(latest["editions"]), 1)
        self.assertFalse(latest["runHistory"][0]["editionCreated"])
        self.assertEqual(latest["refresh"]["lastDayIngested"], "2026-09-06")

    def test_new_live_sweep_archives_real_new_edition(self):
        ledger = example()
        service.record_commit(self.root, ledger, "saved-response-reparse", baseline=True)
        ledger["ingest"].update({"startedAt": "2026-10-01T10:00:00+00:00", "lastDayIngested": "2026-10-01", "mode": "live-http"})
        ledger["scope"]["asOf"] = "2026-10-01"
        ledger["sources"][0]["lastSuccessfulFetchAt"] = "2026-10-01T10:00:01+00:00"
        latest = service.record_commit(self.root, ledger, "live-http")
        self.assertEqual(len(latest["editions"]), 2)
        self.assertEqual(latest["latestEdition"]["asOf"], "2026-10-01")
        self.assertTrue(latest["runHistory"][0]["editionCreated"])

    def test_failure_preserves_ledger_archive_and_freshness(self):
        ledger = example()
        report = self.root / service.REPORT_PATH
        service.atomic_json(report / "ledger.json", ledger)
        service.record_commit(self.root, ledger, "saved-response-reparse", baseline=True)
        before = (report / "ledger.json").read_bytes()
        archive_before = (report / "editions/index.json").read_bytes()
        manifest = {"startedAt": "2026-10-01T10:00:00+00:00", "finishedAt": "2026-10-01T10:01:00+00:00",
                    "status": "aborted-critical-source-failure", "mode": "live-http", "sources": [{"status": "failed"}]}
        latest = service.record_failure(self.root, manifest)
        self.assertEqual((report / "ledger.json").read_bytes(), before)
        self.assertEqual((report / "editions/index.json").read_bytes(), archive_before)
        self.assertEqual(latest["refresh"]["lastDayIngested"], "2026-09-06")
        self.assertFalse(latest["runHistory"][0]["committed"])

    def test_no_archive_without_actual_source_fetch_timestamp(self):
        ledger = example()
        ledger["sources"] = []
        with self.assertRaises(ValueError):
            service.register_edition(self.root, ledger)


if __name__ == "__main__":
    unittest.main()
