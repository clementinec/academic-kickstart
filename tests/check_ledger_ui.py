"""Browser checks against the non-empty manual-refresh observatory baseline.

Requires Playwright + WebKit. Record/channel/lead counts come from the snapshot,
but this scenario expects Instagram disconnected and one blocked repository.
Empty editions or a changed connection/refresh policy need a scenario update.

python tests/check_ledger_ui.py http://127.0.0.1:8765/internal/hku-activity/
"""
import csv
import io
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from playwright.sync_api import sync_playwright


def download_rows(download):
    with tempfile.TemporaryDirectory() as tmp:
        destination = Path(tmp) / 'export.csv'
        download.save_as(destination)
        return list(csv.reader(io.StringIO(destination.read_text(encoding='utf-8-sig'))))


def publisher_key(value):
    parts = urlsplit(value or '')
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not k.lower().startswith('utm_') and k.lower() not in ('fbclid', 'igshid')])
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip('/'), query, ''))


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/internal/hku-activity/'
    data = json.load(urlopen(url + 'ledger.json'))
    end = date.fromisoformat(data['scope']['asOf'])
    start = end - timedelta(days=59)
    expected = [a for a in data['activities'] if a.get('eventDate') and a['eventDate'] <= end.isoformat()
                and (a.get('eventEndDate') or a['eventDate']) >= start.isoformat()]
    leads = data.get('publicationLeads', [])
    if isinstance(leads, dict):
        leads = leads.get('leads', [])
    lead_count = len({publisher_key(lead.get('publisherUrl')) or lead.get('doi') or lead['title'] for lead in leads})
    university_count = sum(a.get('sourceChannel') == 'university_news' for a in expected)
    with sync_playwright() as driver:
        browser = driver.webkit.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1050})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url)
        page.wait_for_function("document.querySelectorAll('#record-list .record-card').length > 0")
        assert page.locator('#panel-records').is_visible()
        assert not page.locator('#panel-people').is_visible()
        assert page.locator('#record-list .record-card').count() == len(expected)
        assert page.locator('#count-records').inner_text() == str(len(expected))
        assert page.locator('#person-list .person').count() == len(data['people'])
        assert not page.locator('#load-error').is_visible()
        assert page.locator('meta[name="robots"]').get_attribute('content') == 'noindex, nofollow, noarchive'
        ids = page.locator('#record-list .record-card').evaluate_all('(nodes) => nodes.map(n => n.dataset.recordId)')
        assert len(ids) == len(set(ids)), 'Shared records must appear only once'
        page.locator('#view-records').focus()
        page.keyboard.press('ArrowRight')
        assert page.locator('#view-people').get_attribute('aria-selected') == 'true'
        assert page.locator('#panel-people').is_visible()
        assert page.locator('#view-people').evaluate('(node) => document.activeElement === node')
        page.keyboard.press('End')
        assert page.locator('#panel-sources').is_visible()
        page.locator('#service-summary').get_by_text('No automatic refresh schedule is active.', exact=False).wait_for()
        assert page.locator('#channels-list').get_by_text('Not connected', exact=True).count() == 1
        assert page.locator('#channels-list').get_by_text('Blocked', exact=True).count() == 1
        assert page.locator('#publication-leads .publication-group').count() == lead_count
        page.locator('#view-records').click()
        # Source-total activation replaces the buttons; focus must survive rendering.
        source_button = page.locator('.source-total[data-channel="faculty_web"]')
        source_button.focus()
        page.keyboard.press('Space')
        assert page.locator('#channel').input_value() == 'faculty_web'
        assert source_button.evaluate('(node) => document.activeElement === node')
        page.keyboard.press('Space')
        assert page.locator('#channel').input_value() == 'all'
        assert source_button.evaluate('(node) => document.activeElement === node')
        assert 'collection-wide' in page.locator('.source-total[data-channel="publishers"]').inner_text()
        page.locator('#channel').select_option('university_news')
        assert page.locator('#record-list .record-card').count() == university_count
        assert page.locator('#count-records').inner_text() == str(university_count)
        page.locator('#channel').select_option('publishers')
        publisher_count = sum(a.get('sourceChannel') == 'publishers' for a in expected)
        assert page.locator('#record-list .record-card').count() == publisher_count
        assert page.locator('#empty').is_visible() == (publisher_count == 0)
        assert page.locator('#count-records').inner_text() == str(publisher_count)
        page.locator('#channel').select_option('instagram')
        assert page.locator('#record-list .record-card').count() == sum(a.get('sourceChannel') == 'instagram' for a in expected)
        page.locator('#channel').select_option('all')
        page.locator('#department').select_option('landscape')
        landscape_ids = {p['id'] for p in data['people'] if any(m['id'] == 'landscape' for m in p['departmentMemberships'])}
        count_la = sum(bool(landscape_ids.intersection(a['personIds'])) for a in expected)
        assert page.locator('#record-list .record-card').count() == count_la
        page.locator('#department').select_option('all')
        page.locator('#window').select_option('30')
        count_30 = sum((a.get('eventEndDate') or a['eventDate']) >= (end - timedelta(days=29)).isoformat() for a in expected)
        assert page.locator('#record-list .record-card').count() == count_30
        page.locator('#window').select_option('60')
        page.locator('#search').fill('ZZZ_NO_MATCH_9876')
        assert page.locator('#record-list .record-card').count() == 0
        page.locator('#search').fill('')
        person_name = page.locator('#record-list .person-chip').first.inner_text()
        page.locator('#record-list .person-chip').first.click()
        assert page.locator('#panel-people').is_visible()
        assert page.locator('#search').input_value() == person_name
        assert page.locator('#person-list .person[open]').count() == 1
        page.locator('#search').fill('')
        page.locator('#with-records').check()
        assert page.locator('#person-list .person').count() <= len(data['people'])
        page.locator('#with-records').uncheck()
        page.locator('#view-records').click()
        with page.expect_download() as pending:
            page.locator('#export').click()
        download = pending.value
        assert 'records-' in download.suggested_filename
        rows = download_rows(download)
        assert len(rows) - 1 == len(expected)
        assert rows[0][0] == 'Record ID'
        for view, first_heading in [('people', 'Person'), ('sources', 'Row type')]:
            page.locator('#view-' + view).click()
            with page.expect_download() as pending:
                page.locator('#export').click()
            saved = pending.value
            assert view + '-' in saved.suggested_filename
            exported = download_rows(saved)
            assert exported[0][0] == first_heading
            if view == 'sources':
                channels = [r for r in exported[1:] if r[0] == 'Channel']
                fetches = [r for r in exported[1:] if r[0] == 'HTTP fetch']
                leads = [r for r in exported[1:] if r[0] == 'Manual lead']
                assert sum(int(r[5]) for r in channels) == len(expected)
                assert len(fetches) == len(data['sources'])
                assert sum(int(r[6]) for r in fetches) == sum(s['status'] == 'success' for s in data['sources'])
                assert len(leads) == lead_count and all(not r[5] and not r[6] and not r[7] for r in leads)
        page.locator('#view-records').click()
        page.evaluate('document.fonts.ready')
        page.screenshot(path='/private/tmp/hku-observatory-desktop.png', full_page=False)
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path='/private/tmp/hku-observatory-top-desktop.png', full_page=False)
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal overflow'
        page.screenshot(path='/private/tmp/hku-observatory-mobile.png', full_page=False)
        page.evaluate('document.fonts.ready')
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path='/private/tmp/hku-observatory-top-mobile.png', full_page=False)
        assert not errors, errors

        # Optional files failing must preserve all mandatory dated records.
        optional = browser.new_page()
        optional.route('**/service.json', lambda route: route.fulfill(status=503, body='unavailable'))
        optional.route('**/media.json', lambda route: route.fulfill(status=503, body='unavailable'))
        optional.goto(url)
        optional.wait_for_function("document.querySelector('#quick-read-status').textContent.includes('unavailable')")
        assert optional.locator('#quick-read-status').is_visible()
        assert optional.locator('#record-list .record-card').count() == len(expected)
        assert optional.locator('#record-list .record-fallback').count() == len(expected)
        assert not optional.locator('#load-error').is_visible()
        optional.close()

        # Image errors must replace the image with a real typographic fallback.
        media = browser.new_page()
        media.route('**/media.json', lambda route: route.fulfill(content_type='application/json', body=json.dumps({expected[0]['evidenceUrl']: {'src': './media/missing-test.jpg', 'alt': 'Test image'}})))
        media.route('**/media/missing-test.jpg', lambda route: route.fulfill(status=404, body='missing'))
        media.goto(url)
        media.get_by_text('Source image unavailable', exact=True).first.wait_for()
        assert media.locator('#record-list .record-card').count() == len(expected)
        media.close()

        # Mandatory failure and malformed dates must not leak freshness/count claims.
        for payload in [None, {**data, 'scope': {**data['scope'], 'asOf': '2026-02-30'}}]:
            broken = browser.new_page()
            broken.route('**/ledger.json', lambda route, request, body=payload: route.fulfill(status=503 if body is None else 200, content_type='application/json', body='unavailable' if body is None else json.dumps(body)))
            broken.goto(url)
            broken.locator('#load-error').wait_for(state='visible')
            assert broken.locator('#ingested').inner_text() == '—'
            assert broken.locator('#record-list .record-card').count() == 0
            assert broken.locator('#export').is_disabled()
            broken.close()
        browser.close()
    print(json.dumps({'status': 'passed', 'records': len(expected), 'checks': 'records-first, deduplication, keyboard tabs, channels, filters, separate leads, service state, CSV, mobile, optional failures, image fallback, mandatory failure'}))


if __name__ == '__main__':
    main()
