'use strict';

const byId = (id) => document.getElementById(id);
const state = { ledger: null, service: null, media: {}, optionalErrors: [], view: 'records', records: [], activities: [], visible: [], baseActivities: [] };
const CHANNELS = ['faculty_web', 'university_news', 'publishers', 'instagram', 'repositories', 'other'];
const labels = {
  architecture: 'Department of Architecture', landscape: 'Division of Landscape Architecture',
  faculty_web: 'Faculty website', university_news: 'University news & institutes', publishers: 'Publishers',
  instagram: 'Instagram', repositories: 'Repositories', other: 'Other / unclassified',
  announced: 'Announced activity', announcement: 'Announced activity', reported: 'Reported by source',
  'reported-mention': 'Reported mention · review role', 'reference-needs-review': 'Profile reference · needs review',
  'reported-completed': 'Reported completed', reported_completed: 'Reported completed',
  'automated-candidate': 'Automated candidate · not reviewed', 'curated-source-checked': 'Curated · source checked',
  'configured-bounded': 'Configured · bounded coverage', 'manual-leads-only': 'Manual leads only',
  'not-connected': 'Not connected', blocked: 'Blocked', unknown: 'State unavailable',
  tentative: 'Tentative match', confirmed: 'Source checked', publication: 'Publication', event: 'Event',
  teaching: 'Teaching', exhibition: 'Exhibition', workshop: 'Workshop', conference: 'Conference',
  'social post': 'Social post', 'public-post': 'Public post · not an outcome', 'source-checked': 'Source checked',
};
const readable = (value) => labels[value] || String(value || 'Unspecified').replaceAll('_', ' ').replaceAll('-', ' ');
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}
function setText(id, text) { if (byId(id)) byId(id).textContent = text; }
function replace(id, ...nodes) { if (byId(id)) byId(id).replaceChildren(...nodes); }
function httpUrl(value) {
  try { const url = new URL(value); return ['http:', 'https:'].includes(url.protocol) ? url : null; } catch { return null; }
}
function canonicalUrl(value) {
  const url = httpUrl(value);
  if (!url) return '';
  url.hash = ''; url.hostname = url.hostname.toLowerCase();
  for (const key of [...url.searchParams.keys()]) if (/^(utm_|fbclid$|igshid$)/i.test(key)) url.searchParams.delete(key);
  return url.href.replace(/\/$/, '');
}
function safeLink(text, url, className, local = false) {
  const node = element('a', text, className), parsed = httpUrl(url);
  if (parsed) { node.href = parsed.href; node.target = '_blank'; node.rel = 'noopener noreferrer'; }
  else if (local && typeof url === 'string' && /^\.\/(?:[a-zA-Z0-9_-]+\/)*[a-zA-Z0-9_.-]+\.json$/.test(url) && !url.includes('..')) node.href = url;
  return node;
}
function sourceChannel(value) {
  const url = httpUrl(value); if (!url) return 'other';
  const host = url.hostname.toLowerCase();
  if (host === 'instagram.com' || host.endsWith('.instagram.com')) return 'instagram';
  if (['hub.hku.hk', 'repository.hku.hk', 'scholars.hku.hk'].includes(host)) return 'repositories';
  if (host === 'arch.hku.hk' || host.endsWith('.arch.hku.hk')) return 'faculty_web';
  if (host === 'hku.hk' || host.endsWith('.hku.hk')) return 'university_news';
  const publishers = ['sciencedirect.com', 'elsevier.com', 'wiley.com', 'tandfonline.com', 'springer.com', 'springerlink.com', 'nature.com', 'sagepub.com', 'taylorfrancis.com', 'cambridge.org', 'academic.oup.com', 'mitpress.mit.edu', 'doi.org', 'crossref.org'];
  return publishers.some((domain) => host === domain || host.endsWith(`.${domain}`)) ? 'publishers' : 'other';
}
function day(value) {
  if (typeof value === 'object' && value) return day(value.start || value.date);
  return typeof value === 'string' ? value.slice(0, 10) : null;
}
function validDay(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return false;
  const date = new Date(`${value}T12:00:00Z`);
  return Number.isFinite(date.valueOf()) && date.toISOString().slice(0, 10) === value;
}
function dateLabel(value) {
  const iso = day(value);
  if (!validDay(iso)) return 'Date not established';
  const timestamp = typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T.+(?:Z|[+-]\d{2}:\d{2})$/.test(value);
  const date = new Date(timestamp ? value : `${iso}T12:00:00Z`);
  return Number.isFinite(date.valueOf()) ? new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Asia/Hong_Kong' }).format(date) : 'Date not established';
}
function shiftedDay(value, offset) { const date = new Date(`${value}T12:00:00Z`); date.setUTCDate(date.getUTCDate() + offset); return date.toISOString().slice(0, 10); }
function memberships(person) { return (person.departmentMemberships || []).map((m) => typeof m === 'string' ? { id: m, label: readable(m) } : m); }
function isSocialPost(a) { return a.kind === 'social post' || a.status === 'public-post'; }
function activityStart(a) { return day(isSocialPost(a) ? a.publicationDate || a.eventDate || a.date : a.eventDate || a.date || a.publicationDate); }
function activityEnd(a) { return isSocialPost(a) ? activityStart(a) : day(a.eventEndDate || a.endDate || a.eventDate?.end) || activityStart(a); }
function activityDateLabel(a) {
  if (isSocialPost(a)) return 'Post published';
  if (a.kind === 'dated profile reference' || a.dateBasis === 'date-in-profile-text') return 'Profile reference dated';
  if (a.dateBasis === 'publication-date') return 'Source publication';
  return /announc/.test(a.status || '') ? 'Scheduled' : 'Event';
}
function asOf() { return state.ledger.scope?.asOf || state.ledger.asOf; }
function windowStart() { return shiftedDay(asOf(), -Number(byId('window').value) + 1); }
function inWindow(a) {
  const start = activityStart(a), end = activityEnd(a);
  return validDay(start) && validDay(end) && end >= start && start <= asOf() && end >= windowStart();
}
function deduplicate(records) {
  const seen = new Map(), keysById = new Map();
  for (const record of records) {
    const profileReference = record.kind === 'dated profile reference' || record.dateBasis === 'date-in-profile-text';
    const key = keysById.get(record.id) || (profileReference ? record.id : canonicalUrl(record.evidenceUrl)) || record.id; if (!key) continue;
    if (record.id) keysById.set(record.id, key);
    if (!seen.has(key)) seen.set(key, { ...record, personIds: [...new Set(record.personIds || [])], personEvidence: [...(record.personEvidence || [])] });
    else {
      const previous = seen.get(key); previous.personIds = [...new Set([...previous.personIds, ...(record.personIds || [])])];
      for (const field of ['departmentIds', 'relatedRecordIds']) previous[field] = [...new Set([...(previous[field] || []), ...(record[field] || [])])];
      previous.discoveredAccounts = [...(previous.discoveredAccounts || []), ...(record.discoveredAccounts || [])];
      for (const evidence of record.personEvidence || []) if (!previous.personEvidence.some((p) => p.personId === evidence.personId && p.role === evidence.role && p.evidenceUrl === evidence.evidenceUrl)) previous.personEvidence.push(evidence);
    }
  }
  return [...seen.values()].sort((a, b) => (activityStart(b) || '').localeCompare(activityStart(a) || '') || a.title.localeCompare(b.title));
}
function linkedPeople(a) { return (a.personIds || []).map((id) => state.ledger.people.find((p) => p.id === id)).filter(Boolean); }
function recordDepartmentIds(a) { return [...new Set((a.departmentIds || []).filter((id) => ['architecture', 'landscape'].includes(id)))]; }
function accountReference(value) {
  const raw = typeof value === 'string' ? value : value?.url || value?.accountUrl || value?.handle || value?.username;
  if (typeof raw !== 'string') return null;
  const normalized = /^@?[a-zA-Z0-9_.]{1,30}$/.test(raw) ? `https://www.instagram.com/${raw.replace(/^@/, '')}/` : raw;
  const parsed = httpUrl(normalized);
  if (!parsed || sourceChannel(parsed.href) !== 'instagram' || !/^\/[a-zA-Z0-9_.]{1,30}\/?$/.test(parsed.pathname)) return null;
  const handle = parsed.pathname.replaceAll('/', '');
  if (['p', 'reel', 'reels', 'stories', 'accounts', 'explore'].includes(handle.toLowerCase())) return null;
  return { label: `@${handle}`, url: `https://www.instagram.com/${handle}/` };
}
function accountReferences(values) {
  const seen = new Map();
  for (const value of values) { const account = accountReference(value); if (account) seen.set(canonicalUrl(account.url).toLowerCase(), account); }
  return [...seen.values()];
}
function associatedAccounts(a) { return accountReferences([a.sourceAccount, ...(a.discoveredAccounts || [])]); }
function relatedRecords(a) { return [...new Set(a.relatedRecordIds || [])].filter((id) => id !== a.id).map((id) => state.records.find((r) => r.id === id)).filter(Boolean); }
function profileStatus(p) { return typeof p.profileCheck === 'string' ? p.profileCheck : p.profileCheck?.status || 'not_checked'; }
function checkPassed(status) { return ['ok', 'success', 'succeeded', 'checked', 'fetched'].includes(status); }
function publicationLeads() { const leads = state.ledger?.publicationLeads; return Array.isArray(leads) ? leads : leads?.leads || []; }
function leadPeople(lead) { return state.ledger.people.filter((p) => (p.profileUrls || [p.profileUrl]).some((url) => canonicalUrl(url) && canonicalUrl(url) === canonicalUrl(lead.rosterProfileUrl))); }
function personLeads(p) { return publicationLeads().filter((lead) => leadPeople(lead).some((person) => person.id === p.id)); }
function personActivities(p) { return state.activities.filter((a) => a.personIds.includes(p.id)); }
function personSearch(p) { return [p.name, ...(p.roles || [])].join(' '); }
function matchesDepartment(p, department) { return department === 'all' || memberships(p).some((m) => m.id === department); }
function filters() { return { department: byId('department').value, kind: byId('kind').value, channel: byId('channel').value, query: byId('search').value.trim().toLocaleLowerCase() }; }
function activityMatches(a, selected, ignoreChannel = false) {
  const people = linkedPeople(a);
  return inWindow(a) && (selected.kind === 'all' || a.kind === selected.kind)
    && (ignoreChannel || selected.channel === 'all' || sourceChannel(a.evidenceUrl) === selected.channel)
    && (selected.department === 'all' || recordDepartmentIds(a).includes(selected.department) || people.some((p) => matchesDepartment(p, selected.department)))
    && (!selected.query || [a.title, a.summary || '', ...people.map(personSearch), ...associatedAccounts(a).map((account) => account.label), ...recordDepartmentIds(a).map(readable)].join(' ').toLocaleLowerCase().includes(selected.query));
}
function filteredLeads() {
  const selected = filters();
  if (!['all', 'publishers'].includes(selected.channel) || !['all', 'publication'].includes(selected.kind)) return [];
  return publicationLeads().filter((lead) => (selected.department === 'all' || leadPeople(lead).some((p) => matchesDepartment(p, selected.department)))
    && (!selected.query || [lead.title, lead.personName, ...leadPeople(lead).map(personSearch)].join(' ').toLocaleLowerCase().includes(selected.query)));
}
function groupedLeads(leads) {
  const groups = new Map();
  for (const lead of leads) { const key = canonicalUrl(lead.publisherUrl) || lead.doi || lead.title; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(lead); }
  return [...groups.values()];
}
function warningText(a) {
  if (isSocialPost(a)) return `Public-post evidence, not a verified outcome. Account association does not establish individual authorship, attendance or completion.${a.caution ? ` ${a.caution}` : ''}`;
  if (/announc/.test(a.status || '')) return 'Announced role or event; attendance, completion and outcomes are not independently established.';
  if (a.reviewState === 'automated-candidate') return 'Automated source match; the person’s role and identity link require review.';
  return a.caution || 'Source-linked evidence; this record is not a productivity or impact assessment.';
}
function showPerson(person) {
  if (!matchesDepartment(person, byId('department').value)) byId('department').value = 'all';
  byId('search').value = person.name; setView('people');
  const details = [...document.querySelectorAll('.person')].find((node) => node.dataset.personId === person.id);
  if (details) { details.open = true; details.querySelector('summary').focus(); }
}
function mediaFallback(activity, index) {
  const tile = element('div', null, 'record-fallback'); tile.setAttribute('aria-hidden', 'true');
  tile.append(element('span', 'Source record', 'record-kicker'), element('span', String(index + 1).padStart(2, '0'), 'record-number'), element('strong', dateLabel(activityStart(activity))), element('span', readable(activity.kind))); return tile;
}
function recordMedia(activity, index) {
  const wrap = element('div', null, 'record-media');
  const manifest = state.media[activity.evidenceUrl] || Object.entries(state.media).find(([url]) => canonicalUrl(url) === canonicalUrl(activity.evidenceUrl))?.[1];
  // Only explicit local media files are allowed; never load arbitrary scraped image URLs.
  if (!manifest || typeof manifest.src !== 'string' || !/^\.\/media\/[a-zA-Z0-9_.-]+$/.test(manifest.src) || manifest.src.includes('..')) { wrap.append(mediaFallback(activity, index)); return wrap; }
  const image = element('img'); image.src = manifest.src; image.alt = String(manifest.alt || 'Source illustration'); image.loading = 'lazy'; image.decoding = 'async';
  image.addEventListener('error', () => { wrap.replaceChildren(mediaFallback(activity, index)); wrap.append(element('span', 'Source image unavailable', 'media-credit')); }, { once: true }); wrap.append(image);
  if (manifest.credit) wrap.append(safeLink(manifest.credit, manifest.sourceUrl || activity.evidenceUrl, 'media-credit')); return wrap;
}
function renderActivity(activity, index = 0, person = null) {
  const article = element('article', null, person ? 'evidence' : 'record-card'); article.dataset.recordId = activity.id; article.dataset.channel = sourceChannel(activity.evidenceUrl);
  if (!person) article.append(recordMedia(activity, index));
  const body = element('div', null, 'record-content'), top = element('div', null, 'record-top');
  top.append(element('span', readable(activity.kind), 'record-type'), element('span', readable(sourceChannel(activity.evidenceUrl)), 'record-channel')); body.append(top, element('h3', activity.title));
  const start = activityStart(activity), end = activityEnd(activity);
  const dateName = activityDateLabel(activity);
  const dates = element('p', `${dateName}: ${dateLabel(start)}${end !== start ? ` – ${dateLabel(end)}` : ''}`, 'record-dates');
  if (activity.publicationDate && activity.dateBasis !== 'publication-date') dates.append(element('span', ` · Report published ${dateLabel(activity.publicationDate)}`));
  if (validDay(day(activity.advertisedEventDate))) {
    const advertisedEnd = day(activity.advertisedEventEndDate || activity.advertisedEventDate?.end);
    dates.append(element('span', ` · Advertised event: ${dateLabel(activity.advertisedEventDate)}${validDay(advertisedEnd) && advertisedEnd !== day(activity.advertisedEventDate) ? ` – ${dateLabel(advertisedEnd)}` : ''} (scheduled, not established as completed)`));
  }
  dates.append(element('span', ` · First ingested ${dateLabel(activity.discoveredAt || state.ledger.ingest.lastDayIngested)}`)); body.append(dates);
  const statuses = element('div', null, 'record-status'); statuses.append(element('span', readable(activity.status || 'tentative'), 'pill warn'));
  if (activity.reviewState) statuses.append(element('span', isSocialPost(activity) && activity.reviewState === 'source-checked' ? 'Caption/date checked · staff links separate' : readable(activity.reviewState), activity.reviewState === 'automated-candidate' ? 'pill warn' : 'pill quiet')); body.append(statuses);
  if (activity.summary || activity.evidenceExcerpt) body.append(element('p', activity.summary || activity.evidenceExcerpt, 'record-excerpt'));
  const people = linkedPeople(activity), links = element('div', null, 'record-people');
  for (const p of people) { const button = element('button', p.name, 'person-chip'); button.type = 'button'; button.addEventListener('click', () => showPerson(p)); links.append(button); } if (people.length) body.append(links);
  if (isSocialPost(activity)) {
    if (!people.length) body.append(element('p', 'Department/account source record; no individual staff attribution established.', 'no-record'));
    const departments = recordDepartmentIds(activity);
    if (departments.length) body.append(element('p', `Record associated with: ${departments.map(readable).join(' / ')}. This is not staff authorship.`, 'record-departments'));
    for (const [label, accounts] of [['Account shown on post', accountReferences([activity.sourceAccount])], ['Found via public account grid(s)', accountReferences(activity.discoveredAccounts || [])]]) {
      if (!accounts.length) continue;
      const row = element('p', `${label}: `, 'record-accounts');
      accounts.forEach((account, i) => { if (i) row.append(element('span', ' · ')); row.append(safeLink(account.label, account.url)); }); body.append(row);
    }
  }
  const roleItems = (activity.personEvidence || []).filter((item) => !person || item.personId === person.id);
  if (roleItems.length) {
    const details = element('details', null, 'record-role-details'); details.append(element('summary', `Person linkage${roleItems.length > 1 ? `s (${roleItems.length})` : ''} & source evidence`));
    for (const item of roleItems) {
      const name = people.find((p) => p.id === item.personId)?.name || 'Roster match'; details.append(element('p', `${name}: ${item.role || 'Role not established'}${item.matchMethod ? ` · ${readable(item.matchMethod)}` : ''}`));
      if (item.evidenceText) details.append(element('p', item.evidenceText, 'source-excerpt'));
      if (httpUrl(item.evidenceUrl)) {
        const crossSource = canonicalUrl(item.evidenceUrl) !== canonicalUrl(activity.evidenceUrl), evidence = element('p', crossSource ? 'Role evidence from linked coverage, not the post caption: ' : 'Person-link evidence: ');
        evidence.append(safeLink('Open supporting source ↗', item.evidenceUrl)); details.append(evidence);
      }
    } body.append(details);
  }
  const related = relatedRecords(activity);
  if (related.length) {
    const coverage = element('div', null, 'related-coverage'); coverage.append(element('p', 'Related coverage of the same work; not another accomplishment:'));
    for (const record of related) { const row = element('p'); row.append(safeLink(`${record.title} (${readable(sourceChannel(record.evidenceUrl))}) ↗`, record.evidenceUrl)); coverage.append(row); } body.append(coverage);
  }
  body.append(element('p', warningText(activity), 'uncertainty'));
  const url = httpUrl(activity.evidenceUrl), provenance = element('p', null, 'record-provenance'); provenance.append(safeLink(url ? `Source: ${url.hostname} ↗` : 'Source URL unavailable', activity.evidenceUrl, 'citation'));
  body.append(provenance); article.append(body); return article;
}
function renderPerson(person, activities) {
  const details = element('details', null, 'person'); details.dataset.personId = person.id;
  const summary = element('summary'), heading = element('div', null, 'person-heading'); heading.append(element('span', person.name, 'person-name'), element('span', (person.roles || []).join(' · '), 'person-role'));
  const meta = element('div', null, 'person-meta'); meta.append(element('span', memberships(person).map((m) => m.label || readable(m.id)).join(' / '), 'department'));
  const checked = checkPassed(profileStatus(person)); meta.append(element('span', activities.length ? `${activities.length} dated record${activities.length === 1 ? '' : 's'}` : checked ? 'No matching dated record found' : 'Coverage incomplete', activities.length ? 'pill' : 'pill quiet'));
  summary.append(heading, meta); details.append(summary);
  const body = element('div', null, 'person-body'), links = element('div', null, 'person-links'); links.append(safeLink('Official profile ↗', person.profileUrl));
  for (const m of memberships(person)) if (m.directoryUrl) links.append(safeLink(`${readable(m.id)} roster ↗`, m.directoryUrl)); body.append(links);
  if (activities.length) activities.forEach((a, i) => body.append(renderActivity(a, i, person)));
  else body.append(element('p', checked ? 'No matching dated record in the selected filters was found in checked sources. Journal, practice and wider-web coverage remain incomplete. This is not evidence of inactivity.' : 'Source coverage is incomplete; no conclusion about recent activity can be drawn.', 'no-record'));
  if (!checked && activities.length) body.append(element('p', 'Profile collection was incomplete; these activity links come from other checked sources.', 'no-record'));
  for (const lead of filteredLeads().filter((l) => leadPeople(l).some((p) => p.id === person.id))) { const item = element('p', 'Manual publication lead — not a dated record: ', 'publication-lead'); item.append(safeLink(lead.title, lead.publisherUrl)); body.append(item); }
  details.append(body); return details;
}
function channelInfo(id) { return state.service?.channels?.find((c) => c.id === id) || { id, label: readable(id), state: state.service ? 'not-configured' : 'unknown', coverageNote: state.service ? 'No dedicated collector is configured for unclassified sources. Unrecognized or missing URLs stay in this category.' : 'Service metadata unavailable; connection status is not inferred from zero records.' }; }
function channelCounts(id) {
  const fetches = (state.ledger.sources || []).filter((s) => sourceChannel(s.url) === id);
  return { records: state.baseActivities.filter((a) => sourceChannel(a.evidenceUrl) === id).length, fetches: fetches.length, successes: fetches.filter((s) => checkPassed(s.status)).length };
}
function renderChannels() {
  const totals = document.createDocumentFragment(), details = document.createDocumentFragment();
  for (const id of CHANNELS) {
    const info = channelInfo(id), count = channelCounts(id), button = element('button', null, 'source-total'); button.type = 'button'; button.dataset.channel = id; button.setAttribute('aria-pressed', String(byId('channel').value === id));
    button.append(element('strong', count.records), element('span', readable(id)), element('small', id === 'publishers' ? `${groupedLeads(publicationLeads()).length} manual leads · collection-wide, not counted` : readable(info.state)));
    button.addEventListener('click', () => {
      byId('channel').value = byId('channel').value === id ? 'all' : id; render();
      // Rendering replaces the count buttons: keep keyboard users on the same control.
      byId('source-totals')?.querySelector(`[data-channel="${id}"]`)?.focus({ preventScroll: true });
    }); totals.append(button);
    if (byId('channel').value !== 'all' && byId('channel').value !== id) continue;
    const card = element('article', null, 'channel-card'); card.dataset.channel = id; card.append(element('h3', info.label || readable(id)), element('span', readable(info.state), 'pill quiet'));
    card.append(element('p', `${count.records} distinct dated records matching department, search, type and window. ${count.successes}/${count.fetches} saved-snapshot HTTP fetches succeeded; fetches are not activity records.`));
    if (info.coverageNote) card.append(element('p', info.coverageNote));
    const attempt = info.latestAttempt;
    if (attempt && typeof attempt === 'object') {
      card.append(element('p', `Latest channel attempt: ${dateLabel(attempt.attemptAt)} (Hong Kong) · ${readable(attempt.status)} · ${attempt.failedChecks ?? 'Unknown'}/${attempt.checksAttempted ?? 'unknown'} source checks failed · ${attempt.committed ? 'snapshot committed' : 'no snapshot committed'}. These attempt checks are separate from saved-snapshot counts.`, 'channel-attempt'));
      if (attempt.note) card.append(element('p', attempt.note));
      const errors = Array.isArray(info.latestAttemptErrors) ? info.latestAttemptErrors : (attempt.sources || []).filter((source) => source.error);
      if (errors.length) {
        const failures = element('details', null, 'record-role-details channel-attempt-errors'); failures.append(element('summary', `Latest-attempt source errors (${errors.length})`));
        for (const failure of errors) {
          const row = element('p'); row.append(safeLink(failure.url || 'Source URL unavailable', failure.url), element('span', `${failure.httpStatus ? ` · HTTP ${failure.httpStatus}` : ''} · ${failure.error || 'Check failed; no detail supplied'}`)); failures.append(row);
        }
        card.append(failures);
      }
    }
    if (Array.isArray(info.suggestedAccounts) && info.suggestedAccounts.length) {
      const accounts = element('details', null, 'record-role-details'); accounts.append(element('summary', info.state === 'not-connected' ? 'Suggested account identities · not connected' : 'Account identities & collection scope'));
      for (const account of info.suggestedAccounts.filter((a) => a && typeof a === 'object')) {
        const item = element('p'); item.append(safeLink(httpUrl(account.url)?.pathname || 'Suggested account', account.url), element('span', ` · ${readable(account.identityStatus)} · ${readable(account.collectionStatus)}`));
        if (account.identityEvidenceUrl) item.append(element('span', ' · '), safeLink('Identity evidence ↗', account.identityEvidenceUrl)); accounts.append(item);
      }
      card.append(accounts);
    }
    if (id === 'publishers') card.append(element('p', `${groupedLeads(publicationLeads()).length} manual publication leads across the full collection are held separately. This collection-wide total does not change with person or date filters; dates and identity remain subject to verification.`)); details.append(card);
  }
  replace('source-totals', totals); replace('channels-list', details);
}
function renderLeads() {
  const groups = groupedLeads(filteredLeads()), fragment = document.createDocumentFragment();
  for (const group of groups) {
    const lead = group[0], article = element('article', null, 'publication-group'); article.append(element('span', 'Manual lead · excluded from dated totals', 'pill warn'), element('h3', lead.title));
    article.append(element('p', [...new Set(group.map((l) => l.personName))].join(' · ')), element('p', `Suggested online date: ${dateLabel(lead.suggestedOnlineDate)} · not verified for the selected date window.`), element('p', lead.caveat));
    const links = element('div', null, 'person-links'); links.append(safeLink('Publisher record ↗', lead.publisherUrl), safeLink('Deposited metadata ↗', lead.metadataEvidenceUrl), safeLink('Provisional date evidence ↗', lead.dateEvidenceUrl)); article.append(links); fragment.append(article);
  }
  replace('publication-leads', fragment); if (byId('publication-queue')) byId('publication-queue').hidden = !groups.length;
}
function renderService() {
  const summary = document.createDocumentFragment(), history = document.createDocumentFragment(), runs = document.createDocumentFragment();
  if (!state.service) summary.append(element('p', 'Service status unavailable. No refresh schedule, automatic collection or next run is being claimed.', 'notice'));
  else {
    const refresh = state.service.refresh || {}, active = refresh.scheduleActive === true;
    summary.append(element('p', `Collection mode: ${readable(refresh.mode || 'unknown')}. ${active ? 'A collection schedule is marked active.' : 'No automatic refresh schedule is active.'}`, 'service-line'));
    summary.append(element('p', `Last retrieval attempt: ${dateLabel(refresh.lastAttemptAt)} · ${readable(refresh.lastAttemptStatus || 'unknown')}. Last committed retrieval: ${dateLabel(refresh.lastCommittedRetrievalAt)}. Attempt status does not replace saved-snapshot evidence.`, 'service-line'));
    summary.append(element('p', active && refresh.nextScheduledAt ? `Next scheduled retrieval: ${dateLabel(refresh.nextScheduledAt)}.` : 'Next scheduled retrieval: none established.', 'service-line'));
    summary.append(element('p', state.service.review?.autoPublish === true ? 'Automatic publication is enabled in service metadata.' : 'Automatic publication is not enabled. Review policy: manual review before publication.', 'service-line'));
    if (refresh.workflowUrl) summary.append(safeLink('Collection workflow ↗', refresh.workflowUrl));
    for (const edition of state.service.editions || []) { const item = element('article', null, 'history-item'); item.append(element('strong', `Edition as of ${dateLabel(edition.asOf)}`), element('p', `Retrieved ${dateLabel(edition.retrievedAt)} · ${edition.recordCount ?? 'Unknown'} records · ${edition.peopleCount ?? 'Unknown'} people · ${readable(edition.status)}`), safeLink('Open archived snapshot ↗', edition.href, '', true)); history.append(item); }
    if (!(state.service.editions || []).length) history.append(element('p', 'No archived editions are listed in service metadata.'));
    for (const run of state.service.runHistory || []) runs.append(element('p', `${dateLabel(run.attemptAt)} · ${readable(run.mode)} · ${readable(run.status)} · ${run.committed ? 'snapshot committed' : 'no snapshot committed'} · ${Array.isArray(run.sourceFailures) ? run.sourceFailures.length : run.sourceFailures ?? 'Unknown'} source failures`, 'history-item'));
    if (!(state.service.runHistory || []).length) runs.append(element('p', 'No run history is available.'));
  }
  for (const error of state.optionalErrors) summary.append(element('p', error, 'notice'));
  replace('service-summary', summary); replace('collection-history', history); replace('service-run-list', runs);
  setText('quick-read-status', state.optionalErrors.length ? state.optionalErrors.join(' ') : 'Saved, bounded source evidence. Announcements and unreviewed matches are labelled; manual leads are not dated records.');
  if (byId('quick-read-status')) byId('quick-read-status').hidden = !state.optionalErrors.length;
}
function renderSources() {
  const selected = byId('channel').value, sources = (state.ledger.sources || []).filter((s) => selected === 'all' || sourceChannel(s.url) === selected), fragment = document.createDocumentFragment();
  for (const source of sources) { const item = element('div', null, 'source-item'); item.append(safeLink(source.label || source.url || source.id, source.url), element('span', `${readable(source.status)} · ${readable(sourceChannel(source.url))}${source.error ? ` · ${source.error}` : ''}`)); if (source.coverageNote) item.append(element('span', source.coverageNote)); fragment.append(item); }
  for (const warning of state.ledger.errors || []) { const item = element('div', null, 'source-item'); item.append(element('span', warning.error || 'Evidence requires review')); if (warning.sourceUrl) item.append(safeLink('Affected source ↗', warning.sourceUrl)); fragment.append(item); } replace('source-list', fragment);
  const checked = state.ledger.people.filter((p) => checkPassed(profileStatus(p))).length;
  setText('coverage-summary', `${checked}/${state.ledger.people.length} profiles retrieved. ${sources.filter((s) => checkPassed(s.status)).length}/${sources.length} saved-snapshot HTTP fetches succeeded in the selected channel. Fetch health is collection-level, not restricted by person or event-date filters; latest-attempt results are shown separately. No complete publication or professional-output census is claimed.`);
  renderChannels(); renderLeads(); renderService();
}
function setView(view, focusTab = false) {
  state.view = ['records', 'people', 'sources'].includes(view) ? view : 'records';
  for (const name of ['records', 'people', 'sources']) { const tab = byId(`view-${name}`), panel = byId(`panel-${name}`), active = name === state.view; if (tab) { tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1; if (active && focusTab) tab.focus(); } if (panel) panel.hidden = !active; } render();
}
function render() {
  if (!state.ledger) return;
  const selected = filters(); state.baseActivities = state.records.filter((a) => activityMatches(a, selected, true)); state.activities = state.records.filter((a) => activityMatches(a, selected));
  state.visible = state.ledger.people.filter((person) => matchesDepartment(person, selected.department)
    && (!selected.query || [personSearch(person), ...personActivities(person).map((a) => a.title), ...personLeads(person).map((l) => l.title)].join(' ').toLocaleLowerCase().includes(selected.query))
    && (!byId('with-records').checked || personActivities(person).length)).sort((a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'base' }));
  const openIds = new Set([...document.querySelectorAll('.person[open]')].map((p) => p.dataset.personId)), records = document.createDocumentFragment(); state.activities.forEach((a, index) => records.append(renderActivity(a, index))); replace('record-list', records);
  const people = document.createDocumentFragment(); for (const person of state.visible) { const item = renderPerson(person, personActivities(person)); item.open = openIds.has(person.id); people.append(item); } replace('person-list', people);
  const visibleIds = new Set(state.visible.map((p) => p.id)); setText('count-people', state.visible.length); setText('count-matched', new Set(state.activities.flatMap((a) => a.personIds).filter((id) => visibleIds.has(id))).size); setText('count-records', state.activities.length);
  const sources = state.ledger.sources || []; setText('count-sources', `${sources.filter((s) => checkPassed(s.status)).length}/${sources.length}`); setText('window-label', `${dateLabel(windowStart())} – ${dateLabel(asOf())}`);
  const countLabel = `${state.activities.length} distinct dated records · ${state.visible.length} of ${state.ledger.people.length} roster people`;
  setText('result-count', state.view === 'records' ? `${countLabel} · newest record first` : state.view === 'people' ? `${countLabel} · alphabetical, no ranking` : 'Collection health is not an activity count. Channel cards separate records, manual leads and HTTP fetches.');
  const empty = byId('empty'); empty.hidden = state.view === 'sources' || (state.view === 'records' ? state.activities.length > 0 : state.visible.length > 0); empty.textContent = state.view === 'records' ? 'No dated records match these filters. This does not establish inactivity; try another channel or view collection coverage.' : 'No roster people match these filters.';
  renderSources();
}
function csvCell(value) { let text = String(value ?? ''); if (/^[\s]*[=+@-]/.test(text)) text = `'${text}`; return `"${text.replaceAll('"', '""')}"`; }
function csvRows(view = state.view) {
  if (view === 'sources') {
    const rows = [['Row type', 'Channel', 'Title', 'Source URL', 'Collection / review state', 'Dated records matching filters', 'HTTP fetches succeeded', 'HTTP fetches attempted', 'Manual leads (channel rows: collection-wide; never dated records)']];
    for (const id of CHANNELS.filter((id) => byId('channel').value === 'all' || byId('channel').value === id)) { const c = channelCounts(id); rows.push(['Channel', readable(id), '', '', channelInfo(id).state, c.records, c.successes, c.fetches, id === 'publishers' ? groupedLeads(publicationLeads()).length : 0]); }
    for (const source of (state.ledger.sources || []).filter((s) => byId('channel').value === 'all' || sourceChannel(s.url) === byId('channel').value)) rows.push(['HTTP fetch', readable(sourceChannel(source.url)), source.label || source.id, source.url, source.status, '', checkPassed(source.status) ? 1 : 0, 1, '']);
    for (const group of groupedLeads(filteredLeads())) rows.push(['Manual lead', 'Publishers', group[0].title, group[0].publisherUrl, 'Verification pending; excluded from dated totals', '', '', '', 1]); return rows;
  }
  const headers = ['Record ID', 'Title', 'Channel', 'Type', 'Evidence status', 'Review state', 'Event / source date', 'End date', 'Report publication date', 'First ingested', 'People (source links, not sole authorship)', 'Evidence URL', 'Associated units (not staff authorship)', 'Account shown on post', 'Discovered account grids', 'Advertised event date (not completion)', 'Related source record IDs (not additional accomplishments)', 'Related coverage URLs'];
  const activityRow = (a) => [a.id, a.title, readable(sourceChannel(a.evidenceUrl)), a.kind, a.status, a.reviewState, activityStart(a), activityEnd(a), a.publicationDate, day(a.discoveredAt), linkedPeople(a).map((p) => p.name).join('; '), a.evidenceUrl, recordDepartmentIds(a).map(readable).join('; '), accountReference(a.sourceAccount)?.url || '', accountReferences(a.discoveredAccounts || []).map((account) => account.url).join('; '), day(a.advertisedEventDate), (a.relatedRecordIds || []).join('; '), relatedRecords(a).map((r) => r.evidenceUrl).join('; ')];
  if (view === 'records') return [headers, ...state.activities.map(activityRow)];
  const rows = [['Person', 'Department / division', 'Roster role', 'Profile URL', 'Profile check', 'Coverage note', ...headers]];
  for (const person of state.visible) for (const activity of personActivities(person).length ? personActivities(person) : [null]) rows.push([person.name, memberships(person).map((m) => m.label || readable(m.id)).join('; '), (person.roles || []).join('; '), person.profileUrl, profileStatus(person), activity ? 'Person-record row; shared records repeat in this export' : checkPassed(profileStatus(person)) ? 'No matching record in checked sources; not evidence of inactivity' : 'Coverage incomplete; no conclusion about activity', ...(activity ? activityRow(activity) : headers.map(() => ''))]); return rows;
}
function exportCsv() {
  if (!state.ledger) return;
  const blob = new Blob(['\uFEFF', csvRows().map((row) => row.map(csvCell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob), link = element('a'); link.href = url; link.download = `hku-${state.view}-${asOf()}.csv`; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function loadJson(url) {
  const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 12000);
  try { const response = await fetch(url, { cache: 'no-cache', signal: controller.signal }); if (!response.ok) throw new Error(`HTTP ${response.status}`); return await response.json(); }
  finally { clearTimeout(timer); }
}
async function optionalJson(name, validator) {
  try { const data = await loadJson(`./${name}.json`); if (!validator(data)) throw new Error('incompatible format'); return data; }
  catch { state.optionalErrors.push(`${name === 'service' ? 'Collection-service metadata' : 'Source-image manifest'} unavailable; ${name === 'service' ? 'refresh state is unknown' : 'typographic record tiles are shown'}.`); return null; }
}
function resetAfterFailure(error) {
  state.ledger = null; state.records = []; state.activities = []; state.visible = [];
  ['record-list', 'person-list', 'source-list', 'publication-leads', 'source-totals', 'channels-list', 'service-summary', 'collection-history', 'service-run-list'].forEach((id) => replace(id));
  ['ingested', 'window-label', 'count-people', 'count-matched', 'count-records', 'count-sources'].forEach((id) => setText(id, '—')); setText('coverage-summary', ''); byId('export').disabled = true; byId('load-error').hidden = false;
  setText('load-error', `The mandatory ledger snapshot could not be loaded. No freshness or activity claims are shown. ${error.message}`); setText('ingest-note', 'No valid snapshot loaded.'); setText('result-count', 'Ledger unavailable'); if (byId('publication-queue')) byId('publication-queue').hidden = true;
}
async function initialize() {
  try {
    const data = await loadJson('./ledger.json');
    if (!Array.isArray(data.people) || !Array.isArray(data.activities) || !Array.isArray(data.sources || []) || !validDay(data.scope?.asOf || data.asOf) || !validDay(data.ingest?.lastDayIngested)) throw new Error('Invalid snapshot schema or dates');
    if (data.people.some((p) => !p.id || typeof p.name !== 'string') || data.activities.some((a) => !a.id || typeof a.title !== 'string')) throw new Error('Invalid person or record schema'); state.ledger = data; state.records = deduplicate(data.activities);
    const requestedChannel = new URL(window.location.href).searchParams.get('channel');
    if (['all', ...CHANNELS].includes(requestedChannel)) byId('channel').value = requestedChannel;
    setText('ingested', dateLabel(data.ingest.lastDayIngested)); setText('ingest-note', [checkPassed(data.ingest.status) ? 'Saved source snapshot.' : 'Partial source coverage.', typeof data.ingest.note === 'string' ? data.ingest.note.trim() : '', 'Reloading this page does not collect new evidence.'].filter(Boolean).join(' '));
    for (const kind of [...new Set(state.records.map((a) => a.kind).filter(Boolean))].sort()) { const option = element('option', readable(kind)); option.value = kind; byId('kind').append(option); } byId('export').disabled = false; setView('records');
    const [service, media] = await Promise.all([optionalJson('service', (d) => d && typeof d === 'object' && !Array.isArray(d) && Array.isArray(d.channels) && d.channels.every((c) => c && typeof c.id === 'string') && (!d.editions || (Array.isArray(d.editions) && d.editions.every((e) => e && typeof e === 'object'))) && (!d.runHistory || (Array.isArray(d.runHistory) && d.runHistory.every((r) => r && typeof r === 'object')))), optionalJson('media', (d) => d && typeof d === 'object' && !Array.isArray(d))]);
    if (!state.ledger) return; state.service = service; state.media = media || {}; render();
  } catch (error) { resetAfterFailure(error); }
}
byId('filters').addEventListener('submit', (event) => event.preventDefault()); byId('filters').addEventListener('input', render); byId('export').addEventListener('click', exportCsv);
for (const tab of document.querySelectorAll('[data-view]')) {
  tab.addEventListener('click', () => setView(tab.dataset.view));
  tab.addEventListener('keydown', (event) => { const views = ['records', 'people', 'sources'], index = views.indexOf(tab.dataset.view), next = event.key === 'ArrowRight' ? (index + 1) % 3 : event.key === 'ArrowLeft' ? (index + 2) % 3 : event.key === 'Home' ? 0 : event.key === 'End' ? 2 : null; if (next !== null) { event.preventDefault(); setView(views[next], true); } });
}
let printedDetails = [];
window.addEventListener('beforeprint', () => { printedDetails = [...document.querySelectorAll('details:not([open])')]; printedDetails.forEach((d) => { d.open = true; }); });
window.addEventListener('afterprint', () => { printedDetails.forEach((d) => { d.open = false; }); });
initialize();
