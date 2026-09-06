"""Optional browser smoke test: pip install playwright; playwright install webkit.

Serve the built website first, then run:
python tests/check_ledger_ui.py http://127.0.0.1:8765/internal/hku-activity/
"""
import json
import sys
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/internal/hku-activity/"
    data = json.load(urlopen(url + "ledger.json"))
    assert data["people"], "Live roster must not be empty"
    with sync_playwright() as driver:
        browser = driver.webkit.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1050})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url)
        page.wait_for_function("document.querySelectorAll('.person').length > 0")
        assert page.locator(".person").count() == len(data["people"])
        assert "Last day ingested" in page.locator("body").text_content()
        assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex, nofollow, noarchive"
        assert not page.locator("#load-error").is_visible()
        page.locator("#search").fill(data["people"][0]["name"])
        assert page.locator(".person").count() >= 1
        assert data["people"][0]["name"] in page.locator("#person-list").inner_text()
        page.locator("#search").fill("ZZZ_NONEXISTENT_9876")
        assert page.locator(".person").count() == 0
        assert page.locator("#empty").is_visible()
        assert page.locator("#count-people").inner_text() == "0"
        assert page.locator("#count-records").inner_text() == "0"
        page.locator("#search").fill("")
        if data.get("publicationLeads"):
            assert page.locator("#publication-queue").is_visible()
            page.locator("#search").fill(data["publicationLeads"][0]["title"])
            assert page.locator(".person").count() >= 1
            page.locator("#search").fill("")
        page.locator("#department").select_option("landscape")
        expected = sum(any((m.get("id") if isinstance(m, dict) else m) == "landscape" for m in person["departmentMemberships"]) for person in data["people"])
        assert page.locator(".person").count() == expected
        page.locator("#department").select_option("all")
        page.locator("#with-records").check()
        matched_count = page.locator(".person").count()
        assert matched_count <= len(data["people"])
        if matched_count:
            page.locator(".person > summary").first.click()
            assert page.locator(".person[open] .evidence").count() > 0
            assert page.locator(".person[open] .citation").first.get_attribute("href").startswith("https://")
        page.locator("#window").select_option("30")
        assert page.locator(".person").count() <= matched_count
        page.locator("#window").select_option("60")
        with page.expect_download() as download:
            page.locator("#export").click()
        assert download.value.suggested_filename.endswith(".csv")
        # Keep the overview complete for the visual check, then check narrow layout.
        page.locator("#with-records").uncheck()
        page.evaluate("window.scrollTo(0, 0)")
        page.screenshot(path="/tmp/hku-ledger-desktop.png", full_page=False)
        page.set_viewport_size({"width": 390, "height": 844})
        page.evaluate("window.scrollTo(0, 0)")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Horizontal overflow"
        page.screenshot(path="/tmp/hku-ledger-mobile.png", full_page=False)
        assert not errors, errors
        page.close()
        broken = browser.new_page()
        broken.route("**/ledger.json", lambda route: route.fulfill(status=503, body="unavailable"))
        broken.goto(url)
        broken.locator("#load-error").wait_for(state="visible")
        assert broken.locator("#ingested").inner_text() == "—"
        assert broken.locator(".person").count() == 0
        malformed = browser.new_page()
        bad_data = dict(data)
        bad_data["scope"] = dict(data["scope"], asOf="invalid-date")
        malformed.route("**/ledger.json", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(bad_data)))
        malformed.goto(url)
        malformed.locator("#load-error").wait_for(state="visible")
        assert malformed.locator("#ingested").inner_text() == "—"
        assert malformed.locator("#export").is_disabled()
        browser.close()
    print(json.dumps({"browser": "webkit", "people": len(data["people"]), "checks": "roster, search, departments, windows, evidence links, CSV, mobile overflow, source failure", "status": "passed"}))


if __name__ == "__main__":
    main()
