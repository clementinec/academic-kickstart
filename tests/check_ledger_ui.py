"""Browser checks against the non-empty manual-refresh observatory baseline.

Requires Playwright + WebKit. Record/channel/lead counts and channel states come
from the saved snapshot/service metadata. This scenario expects a non-empty
manual-refresh edition; empty editions or automatic refresh need an update.

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


def check_title_arrow(page):
    arrow = page.locator('#title svg.title-mark')
    assert arrow.count() == 1, 'Title arrow must use a fixed SVG, not an OS-dependent glyph'
    assert arrow.get_attribute('aria-hidden') == 'true'
    assert arrow.get_attribute('focusable') == 'false'
    assert '↗' not in page.locator('#title').text_content()
    assert arrow.evaluate('''(node) => {
        const arrow = node.getBoundingClientRect();
        const title = node.closest('.hero-title').getBoundingClientRect();
        const text = document.createRange();
        text.selectNodeContents(node.parentNode.firstChild);
        const works = text.getBoundingClientRect();
        return arrow.width > 0 && arrow.height > 0 &&
            arrow.left >= works.right - 1 && arrow.right <= title.right + 1 &&
            arrow.top < works.bottom && arrow.bottom > works.top &&
            getComputedStyle(node).stroke === getComputedStyle(node.parentNode).color;
    }'''), 'Title arrow must remain red and beside WORKS within the hero column'


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/internal/hku-activity/'
    data = json.load(urlopen(url + 'ledger.json'))
    service = json.load(urlopen(url + 'service.json'))
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
        page.evaluate('document.fonts.ready')
        for width in (320, 390, 541, 820, 1440):
            page.set_viewport_size({'width': width, 'height': 1050})
            check_title_arrow(page)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), f'Horizontal overflow at {width}px'
        assert page.locator('#panel-records').is_visible()
        assert not page.locator('#panel-people').is_visible()
        assert page.locator('#record-list .record-card').count() == len(expected)
        assert page.locator('#count-records').inner_text() == str(len(expected))
        assert page.locator('#person-list .person').count() == len(data['people'])
        assert not page.locator('#load-error').is_visible()
        if data['ingest'].get('note'):
            assert data['ingest']['note'] in page.locator('#ingest-note').inner_text()
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
        state_labels = {'configured-bounded': 'Configured · bounded coverage', 'manual-leads-only': 'Manual leads only', 'not-connected': 'Not connected', 'blocked': 'Blocked'}
        for channel in service.get('channels', []):
            if channel['id'] in ['faculty_web', 'university_news', 'publishers', 'instagram', 'repositories', 'other']:
                expected_label = state_labels.get(channel['state'], channel['state'].replace('-', ' ').replace('_', ' '))
                assert page.locator(f'.channel-card[data-channel="{channel["id"]}"] .pill').first.inner_text() == expected_label
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
        count_la = sum('landscape' in a.get('departmentIds', []) or bool(landscape_ids.intersection(a['personIds'])) for a in expected)
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
        assert page.locator('#record-list').evaluate('(node) => getComputedStyle(node).gridTemplateColumns.split(" ").length') == 1, 'Mobile evidence cards should use one readable column'
        assert page.locator('#record-list .record-card p:not(.record-dates)').first.evaluate('(node) => parseFloat(getComputedStyle(node).fontSize)') >= 12
        assert page.locator('#record-list .record-dates').first.evaluate('(node) => parseFloat(getComputedStyle(node).fontSize)') >= 10
        page.set_viewport_size({'width': 320, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Narrow-mobile horizontal overflow'
        page.set_viewport_size({'width': 390, 'height': 844})
        page.screenshot(path='/private/tmp/hku-observatory-mobile.png', full_page=False)
        page.evaluate('document.fonts.ready')
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path='/private/tmp/hku-observatory-top-mobile.png', full_page=False)
        if any(a.get('sourceChannel') == 'instagram' for a in expected):
            page.locator('#channel').select_option('instagram')
            page.locator('#record-list .record-card').first.scroll_into_view_if_needed()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Social-post mobile overflow'
            page.screenshot(path='/private/tmp/hku-instagram-records-mobile.png', full_page=False)
            page.set_viewport_size({'width': 1440, 'height': 1050})
            page.locator('#record-list .record-card').first.scroll_into_view_if_needed()
            page.screenshot(path='/private/tmp/hku-instagram-records-desktop.png', full_page=False)
            role_record = next((a for a in expected if a.get('sourceChannel') == 'instagram' and any(item.get('evidenceUrl') and item['evidenceUrl'] != a['evidenceUrl'] for item in a.get('personEvidence', []))), None)
            if role_record:
                page.locator('#search').fill(role_record['title'])
                page.locator('#record-list .record-role-details summary').first.click()
                page.locator('#record-list .record-card').first.scroll_into_view_if_needed()
                page.screenshot(path='/private/tmp/hku-instagram-role-evidence.png', full_page=False)
                page.locator('#search').fill('')
            page.locator('#view-sources').click()
            page.locator('.channel-card[data-channel="instagram"]').scroll_into_view_if_needed()
            page.screenshot(path='/private/tmp/hku-instagram-sources-desktop.png', full_page=False)
            page.locator('#channel').select_option('all')
            page.evaluate('window.scrollTo(0, 0)')
            page.screenshot(path='/private/tmp/hku-instagram-sources-all-desktop.png', full_page=False)
            page.locator('#view-records').click()
        assert not errors, errors

        # Synthetic public-post fixtures exercise semantics without adding published data.
        faculty_record = next(a for a in expected if a.get('personIds'))
        post_date = (end - timedelta(days=3)).isoformat()
        event_date = (end + timedelta(days=20)).isoformat()
        social_post = {'id': 'fixture-ig-unmatched', 'title': 'Fixture department-only public post', 'kind': 'social post', 'status': 'public-post', 'reviewState': 'source-checked', 'dateBasis': 'publication-date', 'publicationDate': post_date, 'eventDate': event_date, 'advertisedEventDate': event_date, 'evidenceUrl': 'https://www.instagram.com/p/FIXTURE1/', 'sourceChannel': 'instagram', 'departmentIds': ['landscape'], 'personIds': [], 'personEvidence': [], 'sourceAccount': {'handle': 'hkulandscape', 'url': 'https://www.instagram.com/hkulandscape/'}, 'discoveredAccounts': [{'handle': 'hkulandscape', 'url': 'https://www.instagram.com/hkulandscape/'}], 'relatedRecordIds': [faculty_record['id']], 'discoveredAt': data['ingest']['lastDayIngested']}
        linked_post = {**social_post, 'id': 'fixture-ig-linked', 'title': 'Fixture public post with linked role evidence', 'evidenceUrl': 'https://www.instagram.com/p/FIXTURE2/', 'personIds': faculty_record['personIds'][:1], 'personEvidence': [{'personId': faculty_record['personIds'][0], 'role': 'Role documented in linked faculty coverage', 'evidenceUrl': faculty_record['evidenceUrl'], 'matchMethod': 'reviewed-related-coverage'}]}
        partial_note = 'Instagram public posts refreshed; faculty and roster sources retain their earlier individual retrieval dates.'
        fixture_data = {**data, 'activities': [*data['activities'], social_post, linked_post], 'ingest': {**data['ingest'], 'status': 'partial', 'note': partial_note}}
        attempt_error = {'url': 'https://www.instagram.com/hkulandscape/', 'httpStatus': 403, 'error': 'Public access blocked <img src=x onerror=alert(1)>; no retry.'}
        blocked_attempt = {'attemptAt': '2026-09-06T16:05:00+00:00', 'status': 'blocked-public-instagram', 'committed': False, 'checksAttempted': 1, 'failedChecks': 1, 'sources': [attempt_error], 'note': 'Previous saved evidence retained.'}
        fixture_service = {**service, 'refresh': {**service['refresh'], 'lastAttemptAt': blocked_attempt['attemptAt'], 'lastAttemptStatus': blocked_attempt['status']}, 'channels': [{**channel, 'state': 'blocked', 'latestAttempt': blocked_attempt, 'latestAttemptErrors': [attempt_error]} if channel['id'] == 'instagram' else channel for channel in service['channels']]}
        fixture = browser.new_page(viewport={'width': 1440, 'height': 1050})
        fixture.route('**/ledger.json', lambda route: route.fulfill(content_type='application/json', body=json.dumps(fixture_data)))
        fixture.route('**/service.json', lambda route: route.fulfill(content_type='application/json', body=json.dumps(fixture_service)))
        fixture.goto(url + '?channel=not-a-channel')
        fixture.wait_for_function("document.querySelectorAll('#record-list .record-card').length > 0")
        assert fixture.locator('#channel').input_value() == 'all', 'Unknown deep-link channels must be ignored'
        assert fixture.locator('#record-list .record-card').count() == len(expected) + 2
        assert partial_note in fixture.locator('#ingest-note').inner_text()
        post_card = fixture.locator('.record-card[data-record-id="fixture-ig-unmatched"]')
        assert 'Post published:' in post_card.locator('.record-dates').inner_text()
        assert 'Advertised event:' in post_card.locator('.record-dates').inner_text()
        assert post_card.locator('.person-chip').count() == 0
        assert 'no individual staff attribution established' in post_card.inner_text()
        assert 'Caption/date checked · staff links separate' in post_card.inner_text()
        assert post_card.locator('.record-accounts a').first.get_attribute('href') == 'https://www.instagram.com/hkulandscape/'
        assert 'not another accomplishment' in post_card.locator('.related-coverage').inner_text()
        assert post_card.locator('.related-coverage a').first.get_attribute('href') == faculty_record['evidenceUrl']
        fixture.locator('#department').select_option('landscape')
        assert post_card.count() == 1, 'Unmatched social post must survive its department filter'
        fixture.locator('#department').select_option('all')
        linked_card = fixture.locator('.record-card[data-record-id="fixture-ig-linked"]')
        linked_card.locator('.record-role-details summary').click()
        assert 'Role evidence from linked coverage, not the post caption' in linked_card.inner_text()
        assert linked_card.locator('.record-role-details a').get_attribute('href') == faculty_record['evidenceUrl']
        fixture.locator('#channel').select_option('instagram')
        assert fixture.locator('#record-list .record-card').count() == sum(a.get('sourceChannel') == 'instagram' for a in expected) + 2
        with fixture.expect_download() as pending:
            fixture.locator('#export').click()
        fixture_rows = download_rows(pending.value)
        exported_post = next(row for row in fixture_rows[1:] if row[0] == social_post['id'])
        assert exported_post[6] == post_date and exported_post[7] == post_date
        assert event_date in exported_post and faculty_record['evidenceUrl'] in exported_post
        fixture.locator('#view-sources').click()
        attempt_card = fixture.locator('.channel-card[data-channel="instagram"]')
        assert 'no snapshot committed' in attempt_card.locator('.channel-attempt').inner_text()
        assert '1/1 source checks failed' in attempt_card.locator('.channel-attempt').inner_text()
        assert 'separate from saved-snapshot counts' in attempt_card.locator('.channel-attempt').inner_text()
        attempt_card.locator('.channel-attempt-errors summary').click()
        assert attempt_error['error'] in attempt_card.locator('.channel-attempt-errors').inner_text()
        assert attempt_card.locator('.channel-attempt-errors img').count() == 0
        assert attempt_card.locator('.channel-attempt-errors a').get_attribute('href') == attempt_error['url']
        assert 'blocked public instagram' in fixture.locator('#service-summary').inner_text()
        assert fixture.locator('#ingested').inner_text() == page.locator('#ingested').inner_text(), 'A failed attempt must not advance the saved ingestion date'
        fixture.goto(url + '?channel=instagram')
        fixture.wait_for_function("document.querySelector('#channel').value === 'instagram'")
        assert fixture.locator('#record-list .record-card').count() == sum(a.get('sourceChannel') == 'instagram' for a in expected) + 2
        fixture.close()

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
    print(json.dumps({'status': 'passed', 'records': len(expected), 'checks': 'records-first, deduplication, keyboard tabs, channels, filters, separate leads, service state, partial-refresh note, social-post dates and account attribution, related coverage, CSV, mobile, optional failures, image fallback, mandatory failure'}))


if __name__ == '__main__':
    main()
