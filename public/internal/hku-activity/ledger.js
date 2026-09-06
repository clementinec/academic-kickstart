'use strict';

const byId = (id) => document.getElementById(id);
const state = { ledger: null, visible: [], activities: [] };
const labels = {
  architecture: 'Department of Architecture', landscape: 'Division of Landscape Architecture',
  announcement: 'Announced activity', announced: 'Announced activity',
  reported_completed: 'Reported completed', 'reported-completed': 'Reported completed',
  confirmed: 'Source-checked', tentative: 'Tentative match', needs_review: 'Needs review',
  'reported-mention': 'Reported mention · review role', reported: 'Reported by source',
  'reference-needs-review': 'Profile reference · needs review',
  publication: 'Publication', exhibition: 'Exhibition', workshop: 'Workshop',
  recognition: 'Recognition', award: 'Award', project: 'Project', news: 'News',
  event: 'Event', programme: 'Programme', teaching: 'Teaching',
};
const readable = (value) => labels[value] || String(value || 'Unspecified').replaceAll('_', ' ').replaceAll('-', ' ');
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}
function safeLink(text, url, className) {
  const node = element('a', text, className);
  try {
    const parsed = new URL(url);
    if (!['https:', 'http:'].includes(parsed.protocol)) throw new Error('Unsafe link');
    node.href = parsed.href;
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
  } catch { node.removeAttribute('href'); }
  return node;
}
function day(value) {
  if (typeof value === 'object' && value) return value.start || value.date || null;
  return typeof value === 'string' ? value.slice(0, 10) : null;
}
function dateLabel(value) {
  const iso = day(value);
  if (!iso) return 'Date not established';
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return iso;
  const date = new Date(`${iso}T12:00:00Z`);
  return Number.isNaN(date.valueOf()) ? iso : new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(date);
}
function memberships(person) {
  return (person.departmentMemberships || []).map((item) => typeof item === 'string' ? { id: item, label: readable(item) } : item);
}
function activityStart(activity) { return day(activity.eventDate || activity.date || activity.publicationDate); }
function activityEnd(activity) { return day(activity.eventEndDate || activity.endDate || activity.eventDate?.end) || activityStart(activity); }
function windowStart() {
  const asOf = state.ledger.scope?.asOf || state.ledger.asOf;
  const date = new Date(`${asOf}T12:00:00Z`);
  date.setUTCDate(date.getUTCDate() - Number(byId('window').value) + 1);
  return date.toISOString().slice(0, 10);
}
function inWindow(activity) {
  const start = activityStart(activity), end = activityEnd(activity);
  const asOf = state.ledger.scope?.asOf || state.ledger.asOf;
  // Imprecise records never become this month's outcomes merely by being fetched.
  return /^\d{4}-\d{2}-\d{2}$/.test(start || '') && start <= asOf && end >= windowStart();
}
function personActivities(person) {
  return state.activities.filter((activity) => (activity.personIds || []).includes(person.id));
}
function publicationLeads() {
  const leads = state.ledger?.publicationLeads;
  return Array.isArray(leads) ? leads : leads?.leads || [];
}
function personLeads(person) {
  return publicationLeads().filter((lead) => (person.profileUrls || [person.profileUrl]).includes(lead.rosterProfileUrl));
}
function profileStatus(person) {
  const check = person.profileCheck || {};
  return typeof check === 'string' ? check : check.status || 'not_checked';
}
function checkPassed(status) { return ['ok', 'success', 'succeeded', 'checked', 'fetched'].includes(status); }
function renderActivity(activity, person) {
  const article = element('article', null, 'evidence');
  const top = element('div', null, 'evidence-top');
  top.append(element('span', readable(activity.kind), 'pill quiet'));
  const status = activity.status || 'tentative';
  top.append(element('span', readable(status), /announc|tentative|review/.test(status) ? 'pill warn' : 'pill'));
  if (activity.reviewState === 'automated-candidate') top.append(element('span', 'Automated candidate · not reviewed', 'pill warn'));
  const end = activityEnd(activity), start = activityStart(activity);
  top.append(element('span', `${dateLabel(start)}${end && end !== start ? ` – ${dateLabel(end)}` : ''}`));
  article.append(top, element('h3', activity.title));
  if (activity.summary || activity.evidenceExcerpt) article.append(element('p', activity.summary || activity.evidenceExcerpt));
  const roleEvidence = (activity.personEvidence || []).filter((item) => item.personId === person.id);
  roleEvidence.forEach((item) => article.append(element('p', `${person.name}: ${item.role}${item.matchMethod ? ` · Link basis: ${readable(item.matchMethod)}` : ''}`)));
  if (activity.personRoles) {
    const values = Array.isArray(activity.personRoles) ? activity.personRoles.map((r) => typeof r === 'string' ? r : `${r.name || r.personId}: ${r.role}`) : Object.values(activity.personRoles);
    article.append(element('p', values.join(' · ')));
  }
  if (activity.caution) article.append(element('p', activity.caution, 'uncertainty'));
  else if (/announc/.test(status)) article.append(element('p', 'The source announces this activity. Attendance, completion and final outcomes have not been independently established.', 'uncertainty'));
  if (activity.dateBasis || activity.eventDatePrecision) article.append(element('p', `Date basis: ${readable(activity.dateBasis || activity.eventDatePrecision)}${activity.publicationDate || activity.reportDate ? ` · Source publication: ${dateLabel(activity.publicationDate || activity.reportDate)}` : ''}`));
  const people = (activity.personIds || []).map((id) => state.ledger.people.find((p) => p.id === id)?.name).filter(Boolean);
  if (people.length > 1) article.append(element('p', `Other roster links are part of the same record: ${people.join('; ')}. Counted once in the overview.`));
  article.append(safeLink('Open primary source ↗', activity.evidenceUrl, 'citation'));
  return article;
}
function renderPerson(person, activities) {
  const details = element('details', null, 'person');
  details.dataset.personId = person.id;
  const summary = element('summary');
  const heading = element('div', null, 'person-heading');
  heading.append(element('span', person.name, 'person-name'));
  heading.append(element('span', (person.roles || []).join(' · ') || 'Role not specified in directory', 'person-role'));
  const meta = element('div', null, 'person-meta');
  meta.append(element('span', memberships(person).map((d) => d.label || readable(d.id)).join(' / '), 'department'));
  const checked = checkPassed(profileStatus(person));
  const status = activities.length ? `${activities.length} dated ${activities.length === 1 ? 'record' : 'records'}` : checked ? 'No matching dated record found' : 'Coverage incomplete';
  meta.append(element('span', status, `pill${activities.length ? '' : checked ? ' quiet' : ' warn'}`));
  const leads = personLeads(person);
  if (leads.length) meta.append(element('span', `${leads.length} publication ${leads.length === 1 ? 'lead' : 'leads'} · unverified date/identity`, 'pill warn'));
  summary.append(heading, meta);
  const body = element('div', null, 'person-body');
  const links = element('div', null, 'person-links');
  links.append(safeLink('Official profile ↗', person.profileUrl));
  for (const membership of memberships(person)) {
    if (membership.directoryUrl) links.append(safeLink(`${membership.id === 'landscape' ? 'Landscape' : 'Architecture'} roster ↗`, membership.directoryUrl));
  }
  const asOf = state.ledger.scope?.asOf || state.ledger.asOf;
  const nextDay = new Date(`${asOf}T12:00:00Z`); nextDay.setUTCDate(nextDay.getUTCDate() + 1);
  const parts = person.name.split(',');
  const searchName = parts.length === 2 ? `${parts[1].trim()} ${parts[0].trim()}` : person.name;
  const beforeStart = new Date(`${windowStart()}T12:00:00Z`); beforeStart.setUTCDate(beforeStart.getUTCDate() - 1);
  const query = `"${searchName}" HKU after:${beforeStart.toISOString().slice(0, 10)} before:${nextDay.toISOString().slice(0, 10)}`;
  links.append(safeLink('Broader web check (not yet ingested) ↗', `https://www.google.com/search?q=${encodeURIComponent(query)}`));
  body.append(links);
  if (activities.length) activities.forEach((activity) => body.append(renderActivity(activity, person)));
  else body.append(element('p', checked ? 'No matching dated public record in the selected window and record type was found in the sources checked. The profile was retrieved; journal, practice and wider-web coverage may still be incomplete. This is not a statement of inactivity.' : 'This person is on the official roster, but their profile or other source checks were incomplete. No conclusion about recent activity can be drawn.', 'no-record'));
  if (!checked && activities.length) body.append(element('p', 'Profile collection was incomplete; the linked activity evidence comes from other checked sources.', 'no-record'));
  for (const lead of leads) {
    const box = element('article', null, 'evidence');
    box.append(element('span', 'Publication lead · excluded from dated totals', 'pill warn'), element('h3', lead.title));
    box.append(element('p', lead.caveat), safeLink('Check publisher record ↗', lead.publisherUrl, 'citation'));
    body.append(box);
  }
  details.append(summary, body);
  return details;
}
function render() {
  const data = state.ledger;
  if (!data) return;
  const kind = byId('kind').value;
  const department = byId('department').value;
  const query = byId('search').value.trim().toLocaleLowerCase();
  state.activities = data.activities.filter((a) => inWindow(a) && (kind === 'all' || a.kind === kind));
  const openIds = new Set([...document.querySelectorAll('.person[open]')].map((p) => p.dataset.personId));
  state.visible = data.people.filter((person) => {
    const activities = personActivities(person);
    const unitMatch = department === 'all' || memberships(person).some((d) => d.id === department);
    const queryMatch = !query || [person.name, ...(person.roles || []), ...activities.map((a) => a.title), ...personLeads(person).map((lead) => lead.title)].join(' ').toLocaleLowerCase().includes(query);
    return unitMatch && queryMatch && (!byId('with-records').checked || activities.length > 0);
  }).sort((a, b) => a.name.localeCompare(b.name, 'en', { sensitivity: 'base' }));
  const fragment = document.createDocumentFragment();
  for (const person of state.visible) {
    const item = renderPerson(person, personActivities(person));
    item.open = openIds.has(person.id);
    fragment.append(item);
  }
  byId('person-list').replaceChildren(fragment);
  byId('empty').hidden = state.visible.length > 0;
  const visibleIds = new Set(state.visible.map((person) => person.id));
  const visibleActivities = state.activities.filter((a) => a.personIds?.some((id) => visibleIds.has(id)));
  byId('result-count').textContent = `${state.visible.length} of ${data.people.length} people · ${visibleActivities.length} distinct records in this view`;
  byId('count-people').textContent = state.visible.length;
  byId('count-matched').textContent = new Set(visibleActivities.flatMap((a) => a.personIds || []).filter((id) => visibleIds.has(id))).size;
  byId('count-records').textContent = visibleActivities.length;
  byId('window-label').textContent = `${dateLabel(windowStart())} – ${dateLabel(data.scope?.asOf || data.asOf)}`;
}
function csvCell(value) {
  let text = String(value ?? '');
  // Prevent spreadsheet formula injection from scraped titles/names.
  if (/^[\s]*[=+@-]/.test(text)) text = `'${text}`;
  return `"${text.replaceAll('"', '""')}"`;
}
function exportCsv() {
  const rows = [['Person', 'Department/division', 'Role', 'Profile', 'Profile check', 'Record', 'Type', 'Evidence status', 'Start date', 'End date', 'Evidence URL', 'Last day ingested']];
  for (const person of state.visible) {
    const activities = personActivities(person);
    for (const activity of activities.length ? activities : [null]) rows.push([
      person.name, memberships(person).map((d) => d.label).join('; '), (person.roles || []).join('; '), person.profileUrl,
      profileStatus(person), activity?.title || (checkPassed(profileStatus(person)) ? 'No matching dated record found in checked sources; not evidence of inactivity' : 'Coverage incomplete; no conclusion about activity'),
      activity?.kind, activity?.status, activity && activityStart(activity), activity && activityEnd(activity), activity?.evidenceUrl,
      state.ledger.ingest.lastDayIngested,
    ]);
  }
  const blob = new Blob(['\uFEFF', rows.map((row) => row.map(csvCell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a'); link.href = url; link.download = `hku-public-work-${state.ledger.scope?.asOf || state.ledger.asOf}.csv`;
  document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function initialize() {
  try {
    const response = await fetch('./ledger.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error(`Snapshot request returned ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data.people) || !Array.isArray(data.activities) || !(data.scope?.asOf || data.asOf) || !data.ingest?.lastDayIngested) throw new Error('Snapshot is incomplete or has an incompatible schema');
    for (const value of [data.scope?.asOf || data.asOf, data.ingest.lastDayIngested]) {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(new Date(`${value}T12:00:00Z`).valueOf())) throw new Error('Snapshot dates are invalid');
    }
    state.ledger = data;
    byId('ingested').textContent = dateLabel(data.ingest.lastDayIngested);
    const partial = data.ingest.status !== 'success' && data.ingest.status !== 'succeeded' && data.ingest.status !== 'complete';
    byId('ingest-note').textContent = `${partial ? 'Partial coverage · see source health below.' : 'Saved source snapshot · Hong Kong date.'} Refreshing this page does not refresh the evidence.`;
    const sources = data.sources || [];
    const successes = sources.filter((s) => checkPassed(s.status));
    byId('count-sources').textContent = `${successes.length}/${sources.length}`;
    const checked = data.people.filter((p) => checkPassed(profileStatus(p))).length;
    byId('coverage-summary').textContent = `${checked} of ${data.people.length} profile checks succeeded. ${successes.length} of ${sources.length} source fetches succeeded. ${data.errors?.length || 0} additional evidence-validation warnings. This bounded snapshot is not a complete publication or professional-output census.`;
    for (const source of sources) {
      const item = element('div', null, 'source-item');
      item.append(safeLink(source.label || source.id || source.url, source.url));
      item.append(element('span', `${readable(source.status)}${source.error ? ` · ${source.error}` : ''}`));
      if (source.coverageNote) item.append(element('span', source.coverageNote));
      if (source.paginationBound) item.append(element('span', `Pagination cap: ${source.paginationBound} pages${source.windowBoundaryReached ? ' · reporting-window boundary reached' : ''}`));
      byId('source-list').append(item);
    }
    for (const warning of data.errors || []) {
      const item = element('div', null, 'source-item');
      item.append(element('span', warning.error || 'Evidence requires review'));
      if (warning.sourceUrl) item.append(safeLink('Affected source ↗', warning.sourceUrl));
      byId('source-list').append(item);
    }
    const leads = publicationLeads();
    byId('publication-queue').hidden = !leads.length;
    for (const lead of leads) {
      const item = element('article', null, 'evidence');
      item.append(element('span', `${lead.personName} · not counted`, 'pill warn'), element('h3', lead.title));
      item.append(element('p', `Suggested first-online date: ${dateLabel(lead.suggestedOnlineDate)} · verification pending.`), element('p', lead.caveat));
      const links = element('div', null, 'person-links');
      links.append(safeLink('Publisher ↗', lead.publisherUrl), safeLink('Deposited metadata ↗', lead.metadataEvidenceUrl), safeLink('Provisional date source ↗', lead.dateEvidenceUrl));
      item.append(links); byId('publication-leads').append(item);
    }
    for (const kind of [...new Set(data.activities.map((a) => a.kind).filter(Boolean))].sort()) {
      const option = element('option', readable(kind)); option.value = kind; byId('kind').append(option);
    }
    byId('export').disabled = false;
    render();
  } catch (error) {
    state.ledger = null; state.visible = []; state.activities = [];
    byId('person-list').replaceChildren(); byId('source-list').replaceChildren();
    byId('publication-leads').replaceChildren(); byId('publication-queue').hidden = true;
    ['ingested', 'window-label', 'count-people', 'count-matched', 'count-records', 'count-sources'].forEach((id) => { byId(id).textContent = '—'; });
    byId('coverage-summary').textContent = ''; byId('export').disabled = true;
    byId('load-error').hidden = false;
    byId('load-error').textContent = `The saved ledger could not be loaded. No freshness or activity claims are being shown. ${error.message}`;
    byId('ingest-note').textContent = 'No valid snapshot loaded.';
    byId('result-count').textContent = 'Roster unavailable';
  }
}
byId('filters').addEventListener('submit', (event) => event.preventDefault());
byId('filters').addEventListener('input', render);
byId('export').addEventListener('click', exportCsv);
let printedDetails = [];
window.addEventListener('beforeprint', () => { printedDetails = [...document.querySelectorAll('details:not([open])')]; printedDetails.forEach((d) => { d.open = true; }); });
window.addEventListener('afterprint', () => { printedDetails.forEach((d) => { d.open = false; }); });
initialize();
