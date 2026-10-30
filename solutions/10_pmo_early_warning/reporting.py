"""Create a reviewable PMO evidence bundle without a server or external assets.

The HTML dashboard is a local, read-only report. Deterministic metrics and agent
narratives are deliberately labeled separately. HTML escaping is applied at every
untrusted-text boundary; JavaScript receives no interpolated project data.
"""

import html  # Escape markup characters before inserting any data into HTML.
import json  # Serialize the complete evidence bundle for independent review.
import re  # Escape Markdown punctuation in user/model text.
from decimal import Decimal, InvalidOperation
from pathlib import Path  # Work with Windows and Unix paths using one interface.


ROLES = ('cost', 'schedule', 'risk', 'executive')
ROLE_LABELS = {'cost': 'Cost analysis', 'schedule': 'Schedule analysis',
               'risk': 'Risk synthesis', 'executive': 'Executive briefing'}
ASSUMPTIONS = [
    'Synthetic pilot data; outputs require project manager review.',
    'EAC = actual cost + estimate to complete. Remaining commitments are already inside ETC.',
    'Finish dates come from project-team inputs; SPI is not used to predict a finish date.',
    'Green means no configured warning triggered. It does not establish safety, completeness, or compliance.',
    'Undefined ratios are shown as N/A; unavailable comparisons are not invented.',
    'Agent text is an unverified draft. Evidence references establish traceability, not factual correctness.',
]


def _h(value):
    """Always escape text, including quotes used inside HTML attributes."""
    return html.escape(str(value), quote=True)


def _md(value):
    """Keep supplied prose readable while preventing raw HTML/Markdown injection."""
    escaped = html.escape(str(value), quote=False)
    return re.sub(r'([\\`*_{}\[\]()#+.!|])', r'\\\1', escaped)


def _money(value):
    """Format trusted decimal money strings without changing stored evidence."""
    try:
        number = Decimal(str(value))
        if number.is_finite():
            return f'${number:,.2f}'
    except (InvalidOperation, ValueError):
        pass
    return str(value)


def _ratio(value):
    return 'N/A' if value is None else str(value)


def _role_output(agent_result, role):
    return (agent_result or {}).get('roles', {}).get(role, {})


def _observation(agent_result, role, project_id):
    """Look up a checked role result for this project, never an arbitrary index."""
    for item in _role_output(agent_result, role).get('observations', []):
        if item.get('project_id') == project_id:
            return item
    return None


def _narrative_label(agent_result, failure):
    if failure is not None:
        return 'FAILED — agent narrative unavailable; baseline metrics retained'
    if not agent_result:
        return 'No agent narrative available'
    if agent_result.get('mode') == 'ai':
        return 'AI draft — unverified; requires project manager review'
    return 'Offline templates — no AI model was called'


def _brief(analysis, agent_result, provenance, failure):
    """Render a concise, source-linked briefing as portable Markdown."""
    p = analysis['portfolio']
    lines = ['# PMO early-warning executive brief', '',
             '**SYNTHETIC PILOT — REQUIRES PROJECT MANAGER REVIEW**', '',
             f"As of: {_md(analysis['as_of'])}",
             f"Previous snapshot: {_md(analysis.get('previous_as_of') or 'Not supplied')}",
             f"Narrative status: {_md(_narrative_label(agent_result, failure))}", '',
             '## Portfolio evidence', '',
             f"- Projects: {p['project_count']}; red: {p['red_count']}; amber: {p['amber_count']}; green: {p['green_count']}",
             f"- Approved budget: {_money(p['budget'])}",
             f"- Estimate at completion: {_money(p['eac'])}",
             f"- Sum of positive project overruns: {_money(p['overrun_amount'])}",
             f"- Weighted CPI: {_ratio(p['cpi'])}; weighted SPI: {_ratio(p['spi'])}", '']
    if p.get('net_variance_at_completion') is not None:
        lines.extend([f"Net variance at completion (budget minus EAC): {_money(p['net_variance_at_completion'])}. Positive project overruns above do not net out savings.", ''])
    if failure is not None:
        lines.extend(['## Agent execution failed', '',
                      'The agent chain did not complete. No partial agent output is presented as a completed briefing.',
                      f"Failure type: {_md(failure.get('error_type', 'Unknown'))}", ''])
    for project in analysis['projects']:
        pid = project['id']
        lines.extend([f"## {_md(pid)} — {_md(project['name'])}", '',
                      f"Manager: {_md(project['manager'])}; configured status: {project['rag'].upper()}",
                      f"EAC: {_money(project['eac'])}; budget: {_money(project['budget'])}; overrun: {_money(project['overrun_amount'])}",
                      f"Maximum finish slippage: {project['max_finish_slip_days']} days; overdue milestones: {project['overdue_milestones']}",
                      f"Open high-severity issues: {project['open_high_issues']}; overdue open issues: {project['overdue_issues']}", ''])
        for flag in project['flags']:
            lines.append(f"- {flag['severity'].upper()}: {_md(flag['message'])} [evidence: {_md(', '.join(flag['evidence_ids']))}]")
        if not project['flags']:
            lines.append('- No configured warning triggered. Review data completeness before relying on the status.')
        if project.get('trend'):
            trend = project['trend']
            lines.extend(['', f"Change in EAC: {_money(trend['eac_delta'])}; change in maximum slip: {trend['finish_slip_delta_days']} days.",
                          f"Budget changed: {trend['budget_changed']}; baseline changed: {trend['baseline_changed']}."])
        if project.get('milestone_details'):
            lines.extend(['', '### Milestone source details', '',
                          '| Milestone | Baseline finish | Forecast finish | Actual finish | Progress | Dependencies |',
                          '| --- | --- | --- | --- | --- | --- |'])
            for task in project['milestone_details']:
                values = [task['id'] + ' — ' + task['name'], task['baseline_finish'],
                          task['forecast_finish'], task['actual_finish'] or 'Not complete',
                          str(task['progress_percent']) + '%', ', '.join(task['depends_on']) or 'None']
                lines.append('| ' + ' | '.join(_md(value) for value in values) + ' |')
        if project.get('open_issue_details'):
            lines.extend(['', '### Open issue source details', '',
                          '| Issue | Owner | Due date | Severity | Category |',
                          '| --- | --- | --- | --- | --- |'])
            for issue in project['open_issue_details']:
                values = [issue['id'] + ' — ' + issue['title'], issue['owner'], issue['due_date'],
                          issue['severity'], issue['category']]
                lines.append('| ' + ' | '.join(_md(value) for value in values) + ' |')
        for role in ROLES:
            item = _observation(agent_result, role, pid)
            if item:
                lines.extend(['', f'### {ROLE_LABELS[role]} — draft', '',
                              _md(item['summary']), '',
                              '**Suggested action for review:** ' + _md(item['recommended_action']), '',
                              'Evidence: ' + _md(', '.join(item['evidence_ids']))])
        lines.append('')
    lines.extend(['## Data quality and comparison warnings', ''])
    lines.extend('- ' + _md(warning) for warning in analysis.get('quality_warnings', []))
    if not analysis.get('quality_warnings'):
        lines.append('- No configured data-quality warning. This is not a completeness certification.')
    lines.extend(['', '## Assumptions and limits', ''])
    lines.extend('- ' + _md(item) for item in ASSUMPTIONS)
    for role in ROLES:
        for limitation in _role_output(agent_result, role).get('limitations', []):
            lines.append(f'- {ROLE_LABELS[role]}: {_md(limitation)}')
    lines.extend(['', '## Evidence index', '',
                  '| Evidence ID | Project | Metric | Value | Source |',
                  '| --- | --- | --- | --- | --- |'])
    for eid, evidence in analysis['evidence'].items():
        lines.append('| ' + ' | '.join(_md(value) for value in [eid, evidence['project_id'],
                    evidence['metric'], _ratio(evidence['value']), evidence['source']]) + ' |')
    lines.extend(['', '## Run provenance', ''])
    for key, value in provenance.items():
        lines.append(f'- {_md(key)}: {_md(value if value is not None else "Not supplied")}')
    return '\n'.join(lines) + '\n'


CSS = """
:root{--ink:#182c3b;--muted:#5c6e7b;--navy:#132d3e;--teal:#006d72;--pale:#edf5f5;--line:#dce5e8;--bg:#f4f7f8;--red:#a92938;--amber:#8b5700;--green:#22633b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);font:15px/1.55 system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:var(--ink)}
a{color:var(--teal)}header{background:var(--navy);color:#fff;padding:36px max(24px,calc((100vw - 1200px)/2));border-bottom:5px solid #40bdb6}header .eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.16em;color:#a8dfdb}h1{font-size:clamp(27px,4vw,40px);line-height:1.2;margin:9px 0 12px;letter-spacing:-.035em}header p{color:#c8dce4;max-width:850px;margin:0}.meta{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px;font-size:13px}.meta span{border:1px solid #365468;border-radius:6px;padding:5px 10px}main{max-width:1248px;margin:0 auto;padding:24px}.notice{border-left:4px solid var(--teal);padding:14px 18px;background:#e7f3f1;border-radius:4px;margin-bottom:24px}.failure{background:#fff0f1;border-color:var(--red)}.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-bottom:24px}.kpi{background:white;border:1px solid var(--line);padding:20px;border-radius:10px}.kpi .label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.07em}.kpi .value{font-size:clamp(23px,3vw,30px);font-weight:700;margin:8px 0 3px;letter-spacing:-.025em}.kpi small{color:var(--muted)}section.panel,.project-card{background:#fff;border:1px solid var(--line);border-radius:10px;margin-bottom:22px;overflow:hidden}.panel-heading{padding:20px 22px;border-bottom:1px solid var(--line);display:flex;gap:12px;align-items:center;justify-content:space-between}.panel-heading h2{margin:0;font-size:19px}.body{padding:20px 22px}.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;padding:16px 22px;background:#fbfdfd}.toolbar label{font-size:13px;font-weight:600}input,select,button{font:inherit;border:1px solid #b5c7ce;padding:8px 11px;border-radius:6px;background:white;color:var(--ink)}input{min-width:240px}button{cursor:pointer}button:hover{background:var(--pale)}.count{margin-left:auto;color:var(--muted);font-size:13px}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th{text-align:left;background:#f4f8f9;color:var(--muted);font-weight:600}th,td{padding:13px 16px;border-bottom:1px solid var(--line);vertical-align:top}td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}.badge{display:inline-block;border-radius:100px;font-size:11px;letter-spacing:.05em;font-weight:750;padding:4px 9px}.red{background:#fbe5e8;color:var(--red)}.amber{background:#fff0cc;color:var(--amber)}.green{background:#e6f4eb;color:var(--green)}.project-top{padding:20px 22px;display:flex;align-items:start;justify-content:space-between;gap:16px;background:#fbfdfd;border-bottom:1px solid var(--line)}.project-top h3{margin:0 0 4px;font-size:20px}.project-top p{margin:0;color:var(--muted);font-size:13px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;padding:18px 22px;background:#fff}.metric span{display:block;font-size:12px;color:var(--muted)}.metric strong{font-size:18px;font-variant-numeric:tabular-nums}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}.subhead{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin:0 0 12px}.flags{list-style:none;padding:0;margin:0}.flags li{padding:10px 12px;background:#f7f9fa;border-radius:6px;margin-bottom:9px;border-left:3px solid #b7c9d0}.flags li.flag-red{border-color:var(--red)}.flags li.flag-amber{border-color:#c28b24}.evidence-ref{font-size:11px;color:var(--muted);overflow-wrap:anywhere}.trend{background:var(--pale);border-radius:6px;padding:12px;font-size:13px}.narrative{margin-top:18px;padding:16px;background:#f4f8f8;border:1px solid #d7e7e6;border-radius:7px}.narrative h4{margin:0 0 8px;font-size:14px}.narrative p{margin:7px 0;white-space:pre-wrap;overflow-wrap:anywhere}details{border-top:1px solid var(--line)}summary{cursor:pointer;font-weight:650;padding:14px 22px;background:#fbfdfd}details .body{font-size:13px}.muted{color:var(--muted)}.small{font-size:12px}.warnings{margin:0;padding-left:20px}.warnings li{margin:7px 0}.provenance{overflow-wrap:anywhere;font-size:12px;color:var(--muted)}.empty{padding:28px;text-align:center;color:var(--muted)}[hidden]{display:none!important}footer{max-width:1248px;margin:0 auto;padding:0 24px 32px;font-size:12px;color:var(--muted)}
@media(max-width:850px){.cards,.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.two-col{grid-template-columns:1fr}main{padding:16px}.count{margin-left:0}}
@media(max-width:460px){.cards{grid-template-columns:1fr}.toolbar{align-items:stretch}.toolbar input{min-width:0;width:100%}.project-top{flex-direction:column}.panel-heading{align-items:start;flex-direction:column}}
@media print{body{background:white;font-size:11px}header{background:white;color:#152d3d;padding:12px;border-bottom:2px solid #152d3d}header p,header .eyebrow{color:#345}.meta span{border:1px solid #ccc}.toolbar,button{display:none}main{max-width:none;padding:10px}.cards{gap:8px}.kpi{padding:10px}.kpi .value{font-size:21px}.project-card,.panel{break-inside:avoid;box-shadow:none}.project-card{page-break-inside:auto}.badge{-webkit-print-color-adjust:exact;print-color-adjust:exact}footer{padding:10px}details[open]{break-inside:auto}}
"""

SCRIPT = """
'use strict';
// Read plain text from escaped HTML attributes; never inject project data as HTML.
const search = document.getElementById('search');
const rag = document.getElementById('rag');
const cards = Array.from(document.querySelectorAll('.project-card'));
function filterProjects() {
  const query = search.value.toLocaleLowerCase().trim();
  let visible = 0;
  cards.forEach(card => {
    const match = (!rag.value || card.dataset.rag === rag.value) && card.dataset.search.includes(query);
    card.hidden = !match;
    const row = document.getElementById(card.dataset.row);
    row.hidden = !match;
    if (match) visible += 1;
  });
  document.getElementById('visible-count').textContent = visible + ' of ' + cards.length + ' projects';
  document.getElementById('empty').hidden = visible !== 0;
}
search.addEventListener('input', filterProjects);
rag.addEventListener('change', filterProjects);
document.getElementById('print').addEventListener('click', () => window.print());
filterProjects();
"""


def _evidence_table(evidence, project_id):
    rows = []
    for eid, item in evidence.items():
        if item['project_id'] != project_id:
            continue
        cells = [_h(eid), _h(item['metric']), _h(_ratio(item['value'])),
                 _h(_ratio(item.get('raw_value', item['value']))),
                 _h(item['unit']), _h(item['source'])]
        rows.append('<tr>' + ''.join('<td>' + cell + '</td>' for cell in cells) + '</tr>')
    return ('<div class="table-wrap"><table><thead><tr><th>Evidence ID</th><th>Metric</th>'
            '<th>Display value</th><th>Calculation precision</th><th>Unit</th><th>Source / formula</th></tr></thead><tbody>' +
            ''.join(rows) + '</tbody></table></div>')


def _source_details(project):
    """Render original milestone/issue rows as escaped, actionable source evidence."""
    parts = []
    tasks = project.get('milestone_details', [])
    if tasks:
        rows = []
        for task in tasks:
            values = [task['id'] + ' — ' + task['name'], task['baseline_finish'],
                      task['forecast_finish'], task['actual_finish'] or 'Not complete',
                      str(task['progress_percent']) + '%', ', '.join(task['depends_on']) or 'None']
            rows.append('<tr>' + ''.join('<td>' + _h(value) + '</td>' for value in values) + '</tr>')
        parts.append('<h4 class="subhead">Milestone source rows</h4><div class="table-wrap"><table><thead><tr>'
                     '<th>Milestone</th><th>Baseline finish</th><th>Forecast finish</th><th>Actual finish</th><th>Progress</th><th>Dependencies</th>'
                     '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
    issues = project.get('open_issue_details', [])
    if issues:
        rows = []
        for issue in issues:
            values = [issue['id'] + ' — ' + issue['title'], issue['owner'], issue['due_date'],
                      issue['severity'], issue['category']]
            rows.append('<tr>' + ''.join('<td>' + _h(value) + '</td>' for value in values) + '</tr>')
        parts.append('<h4 class="subhead" style="margin-top:20px">Open issue source rows</h4><div class="table-wrap"><table><thead><tr>'
                     '<th>Issue</th><th>Owner</th><th>Due date</th><th>Severity</th><th>Category</th>'
                     '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
    if not issues:
        parts.append('<p class="muted">No open issues were supplied for this project.</p>')
    return '<details><summary>Review milestone and open issue source rows</summary><div class="body">' + ''.join(parts) + '</div></details>'


def _dashboard(analysis, agent_result, provenance, failure):
    """Assemble a complete HTML document. Every data value passes through _h()."""
    portfolio = analysis['portfolio']
    narrative_status = _narrative_label(agent_result, failure)
    notice_class = 'notice failure' if failure is not None else 'notice'
    notice = f'<div class="{notice_class}"><strong>{_h(narrative_status)}</strong><br>'
    notice += 'Deterministic financial and schedule evidence appears separately below. No budget, schedule, or approval is changed by this report.'
    if portfolio.get('net_variance_at_completion') is not None:
        notice += ('<br><strong>Net portfolio variance at completion:</strong> ' +
                   _h(_money(portfolio['net_variance_at_completion'])) +
                   ' (approved budget minus EAC). Positive project overruns below do not net out savings.')
    notice += '</div>'
    cards = [
        ('Approved budget', _money(portfolio['budget']), 'USD · aggregate approved budgets'),
        ('Estimate at completion', _money(portfolio['eac']), 'Actual cost + estimate to complete'),
        ('Positive project overruns', _money(portfolio['overrun_amount']), 'Sum of overruns; savings do not offset this total'),
        ('Projects needing attention', str(portfolio['red_count'] + portfolio['amber_count']),
         f"{portfolio['red_count']} red · {portfolio['amber_count']} amber · {portfolio['green_count']} green"),
    ]
    kpis = ''.join('<div class="kpi"><div class="label">' + _h(label) + '</div><div class="value">' +
                   _h(value) + '</div><small>' + _h(note) + '</small></div>' for label, value, note in cards)
    table_rows, project_cards = [], []
    for index, project in enumerate(analysis['projects']):
        pid, rag = project['id'], project['rag']
        # The CSS class is chosen from a trusted fixed vocabulary, not supplied markup.
        rag_class = rag if rag in ('red', 'amber', 'green') else 'amber'
        badge = f'<span class="badge {rag_class}">{_h(rag.upper())}</span>'
        table_rows.append(f'<tr id="row-{index}"><td><a href="#project-{index}"><strong>{_h(project["name"])}</strong></a><br><span class="muted">{_h(pid)}</span></td>'
                          f'<td>{badge}</td><td>{_h(project["manager"])}</td><td class="num">{_h(_money(project["eac"]))}</td>'
                          f'<td class="num">{_h(project["overrun_percent"])}%</td><td class="num">{_h(project["max_finish_slip_days"])} d</td>'
                          f'<td class="num">{_h(_ratio(project["cpi"]))}</td><td class="num">{_h(_ratio(project["spi"]))}</td></tr>')
        metric_pairs = [('Approved budget', _money(project['budget'])), ('Estimate at completion', _money(project['eac'])),
                        ('Variance at completion', _money(project['variance_at_completion'])), ('Max finish slippage', str(project['max_finish_slip_days']) + ' days'),
                        ('Cost performance index', _ratio(project['cpi'])), ('Schedule performance index', _ratio(project['spi'])),
                        ('Overdue milestones', project['overdue_milestones']), ('Open high / overdue issues', str(project['open_high_issues']) + ' / ' + str(project['overdue_issues']))]
        metrics = ''.join('<div class="metric"><span>' + _h(label) + '</span><strong>' + _h(value) + '</strong></div>' for label, value in metric_pairs)
        flags = []
        for flag in project['flags']:
            severity = 'red' if flag['severity'] == 'red' else 'amber'
            flags.append(f'<li class="flag-{severity}"><strong>{_h(flag["code"])}</strong><br>{_h(flag["message"])}<br><span class="evidence-ref">Evidence: {_h(", ".join(flag["evidence_ids"]))}</span></li>')
        if not flags:
            flags.append('<li>No configured warning triggered. Green does not establish completeness or compliance.</li>')
        trend = project.get('trend')
        if trend:
            trend_text = (f"EAC change: {_money(trend['eac_delta'])}; maximum slip change: {trend['finish_slip_delta_days']} days. "
                          f"Budget changed: {trend['budget_changed']}; baseline changed: {trend['baseline_changed']}.")
        else:
            trend_text = 'No comparable prior-project snapshot. No trend is inferred.'
        money_basis = (f"Actual cost {_money(project['actual_cost'])} + ETC {_money(project['estimate_to_complete'])}. "
                       f"Remaining commitments {_money(project['remaining_committed_cost'])} are already included in ETC.")
        narratives = []
        for role in ROLES:
            observation = _observation(agent_result, role, pid)
            if observation:
                narratives.append(f'<div class="narrative"><h4>{ROLE_LABELS[role]} · draft</h4><p>{_h(observation["summary"])}</p>'
                                  f'<p><strong>Suggested action for review:</strong> {_h(observation["recommended_action"])}</p>'
                                  f'<div class="evidence-ref">Evidence: {_h(", ".join(observation["evidence_ids"]))}</div></div>')
        narratives_html = ''.join(narratives) or '<p class="muted">Agent narrative is unavailable. Review the deterministic evidence.</p>'
        search_value = ' '.join([pid, project['name'], project['manager']]).lower()
        project_cards.append(f'<article id="project-{index}" class="project-card" data-rag="{_h(rag)}" data-search="{_h(search_value)}" data-row="row-{index}">'
                             f'<div class="project-top"><div><h3>{_h(project["name"])}</h3><p>{_h(pid)} · Manager: {_h(project["manager"])}</p></div>{badge}</div>'
                             f'<div class="metrics">{metrics}</div><div class="body"><div class="two-col"><div><h4 class="subhead">Deterministic warning rules</h4><ul class="flags">{"".join(flags)}</ul></div>'
                             f'<div><h4 class="subhead">Comparison with previous snapshot</h4><div class="trend">{_h(trend_text)}</div><p class="small muted">{_h(money_basis)}</p></div></div>'
                             f'<h4 class="subhead" style="margin-top:22px">Narrative — {_h(narrative_status)}</h4>{narratives_html}</div>'
                             f'{_source_details(project)}<details><summary>Inspect project evidence and formulas</summary>{_evidence_table(analysis["evidence"], pid)}</details></article>')
    warnings = ''.join('<li>' + _h(item) + '</li>' for item in analysis.get('quality_warnings', []))
    if not warnings:
        warnings = '<li>No configured quality warning. Input validation does not establish source accuracy or completeness.</li>'
    limits = list(ASSUMPTIONS)
    for role in ROLES:
        limits.extend(ROLE_LABELS[role] + ': ' + item for item in _role_output(agent_result, role).get('limitations', []))
    limitations = ''.join('<li>' + _h(item) + '</li>' for item in limits)
    provenance_html = ''.join('<p><strong>' + _h(key) + ':</strong> ' + _h(value if value is not None else 'Not supplied') + '</p>' for key, value in provenance.items())
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="referrer" content="no-referrer"><title>PMO early-warning pilot</title><style>' + CSS + '</style></head><body>'
            '<header><div class="eyebrow">Engineering delivery intelligence · synthetic pilot</div><h1>Project performance, with evidence.</h1>'
            '<p>A review workspace for cost exposure, milestone slippage, and decisions that need attention. Read-only; requires project manager review.</p>'
            f'<div class="meta"><span>As of {_h(analysis["as_of"])}</span><span>Prior snapshot: {_h(analysis.get("previous_as_of") or "Not supplied")}</span>'
            f'<span>Weighted CPI {_h(_ratio(portfolio["cpi"]))} · SPI {_h(_ratio(portfolio["spi"]))}</span></div></header>'
            f'<main>{notice}<div class="cards">{kpis}</div><section class="panel"><div class="panel-heading"><h2>Portfolio overview</h2><button id="print" type="button">Print / save PDF</button></div>'
            '<div class="toolbar"><label for="search">Find project</label><input id="search" type="search" placeholder="Name, ID, or manager"><label for="rag">Status</label>'
            '<select id="rag"><option value="">All statuses</option><option value="red">Red</option><option value="amber">Amber</option><option value="green">Green</option></select><span id="visible-count" class="count"></span></div>'
            '<div class="table-wrap"><table><thead><tr><th>Project</th><th>Status</th><th>Manager</th><th class="num">EAC</th><th class="num">Overrun</th><th class="num">Max slip</th><th class="num">CPI</th><th class="num">SPI</th></tr></thead><tbody>' +
            ''.join(table_rows) + '</tbody></table></div><div id="empty" class="empty" hidden>No projects match these filters.</div></section>' + ''.join(project_cards) +
            '<section class="panel"><div class="panel-heading"><h2>Data quality and comparison warnings</h2></div><div class="body"><ul class="warnings">' + warnings + '</ul></div></section>'
            '<section class="panel"><div class="panel-heading"><h2>Interpretation and limits</h2></div><div class="body"><p><strong>CPI</strong> = earned value ÷ actual cost. <strong>SPI</strong> = earned value ÷ planned value. Ratios below configured policy thresholds trigger a watch flag.</p><ul class="warnings">' +
            limitations + '</ul></div><details><summary>Run provenance</summary><div class="body provenance">' + provenance_html + '</div></details></section></main>'
            '<footer>Independent Mesa-aligned learning pilot. No internal system integration, autonomous project changes, or engineering certification is provided. Review JSON evidence before acting.</footer><script>' + SCRIPT + '</script></body></html>')


def write_reports(analysis: dict, agent_result: dict | None, output_dir: Path,
                  provenance: dict, failure: dict | None = None) -> None:
    """Write the complete evidence bundle. The CLI enforces overwrite policy.

    A failed agent chain never appears as a completed narrative. Callers can
    still inspect the deterministic baseline, provenance, and failure type.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Discard a supplied partial narrative whenever a failure is present.
    checked_agents = None if failure is not None else agent_result
    bundle = {'analysis': analysis, 'agents': checked_agents,
              'provenance': provenance, 'failure': failure}
    encoded = json.dumps(bundle, indent=2, ensure_ascii=False, allow_nan=False)
    brief = _brief(analysis, checked_agents, provenance, failure)
    dashboard = _dashboard(analysis, checked_agents, provenance, failure)
    # Render every representation before writing; data/encoding errors cannot leave
    # a completed-looking HTML report generated from a partially serialized input.
    (output_dir / 'report.json').write_text(encoded + '\n', encoding='utf-8')
    (output_dir / 'executive_brief.md').write_text(brief, encoding='utf-8')
    (output_dir / 'dashboard.html').write_text(dashboard, encoding='utf-8')
