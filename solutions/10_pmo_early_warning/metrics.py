"""Trusted calculations for the synthetic PMO early-warning pilot.

This module does not call a model or change project data. It validates snapshots,
computes reproducible metrics, and records evidence for each configured flag.
The colors support PM review; green does not certify safety or future success.
"""

# Decimal avoids binary floating-point surprises at monetary/threshold boundaries.
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from datetime import date  # Calendar days, not workdays or resource schedules.
import copy  # Return independent objects rather than sharing caller-owned policy.
import re  # Enforce the exact YYYY-MM-DD date representation.

MONEY_LIMIT = Decimal('1000000000000')
PROJECT_KEYS = {'id', 'name', 'manager', 'approved_budget', 'planned_value',
                'earned_value', 'actual_cost', 'estimate_to_complete',
                'remaining_committed_cost', 'tasks', 'issues'}
MONEY_FIELDS = ('approved_budget', 'planned_value', 'earned_value', 'actual_cost',
                'estimate_to_complete', 'remaining_committed_cost')
POLICY_KEYS = {'cost_watch_percent', 'cost_high_percent', 'schedule_watch_days',
               'schedule_high_days', 'cpi_watch_below', 'spi_watch_below'}


def _shape(value, keys, label):
    """An exact input schema catches typos instead of silently ignoring them."""
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError(f'{label} must contain exactly {sorted(keys)}')


def _text(value, label, limit=300):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{label} must be nonblank text of at most {limit} characters')
    if any(ord(character) < 32 for character in value):
        raise ValueError(f'{label} must not contain control characters')
    return value


def _decimal(value, label, maximum=MONEY_LIMIT):
    # bool inherits int in Python; checking it separately prevents True meaning $1.
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f'{label} must be a decimal string or integer, never float/bool')
    if isinstance(value, str) and (not value.strip() or len(value) > 100):
        raise ValueError(f'{label} is empty or too long')
    try:
        number = Decimal(value)
    except (ValueError, InvalidOperation, OverflowError) as exc:
        raise ValueError(f'{label} is not a decimal number') from exc
    if not number.is_finite() or number < 0 or number > maximum:
        raise ValueError(f'{label} must be finite and between 0 and {maximum}')
    if number.as_tuple().exponent < -12:
        raise ValueError(f'{label} supports at most 12 decimal places')
    return number


def _date(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'{label} must use exact YYYY-MM-DD format')
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f'{label} must be a valid calendar date') from exc


def _list(value, label, maximum, minimum=0):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValueError(f'{label} requires {minimum} to {maximum} items')
    return value


def _unique(items, label):
    identifiers = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f'{label} entries must be objects')
        identifier = _text(item.get('id'), f'{label}.id', 100)
        if identifier in identifiers:
            raise ValueError(f'{label} IDs must be unique')
        identifiers.add(identifier)
    return identifiers


def _validate_project(project, as_of):
    _shape(project, PROJECT_KEYS, 'project')
    _text(project['id'], 'project.id', 100)
    _text(project['name'], 'project.name')
    _text(project['manager'], 'project.manager')
    values = {key: _decimal(project[key], key) for key in MONEY_FIELDS}
    if values['approved_budget'] <= 0:
        raise ValueError('approved_budget must be greater than zero')
    if values['planned_value'] > values['approved_budget'] or values['earned_value'] > values['approved_budget']:
        raise ValueError('planned_value and earned_value must not exceed approved_budget')
    if values['remaining_committed_cost'] > values['estimate_to_complete']:
        raise ValueError('remaining_committed_cost must already be included within estimate_to_complete')
    tasks = _list(project['tasks'], 'tasks', 200, 1)
    task_ids = _unique(tasks, 'tasks')
    task_map = {}
    for task in tasks:
        _shape(task, {'id', 'name', 'baseline_finish', 'forecast_finish',
                      'actual_finish', 'progress_percent', 'depends_on'}, 'task')
        _text(task['name'], 'task.name')
        _date(task['baseline_finish'], 'baseline_finish')
        _date(task['forecast_finish'], 'forecast_finish')
        actual = task['actual_finish']
        if actual is not None and _date(actual, 'actual_finish') > as_of:
            raise ValueError('actual_finish must not be after snapshot.as_of')
        progress = task['progress_percent']
        if type(progress) is not int or not 0 <= progress <= 100:
            raise ValueError('progress_percent must be an integer from 0 to 100')
        if (progress == 100) != (actual is not None):
            raise ValueError('progress_percent must be 100 if and only if actual_finish exists')
        dependencies = _list(task['depends_on'], 'depends_on', 200)
        for dependency in dependencies:
            _text(dependency, 'dependency ID', 100)
        if len(set(dependencies)) != len(dependencies):
            raise ValueError('Task dependencies must be unique')
        if any(dep not in task_ids or dep == task['id'] for dep in dependencies):
            raise ValueError('Task dependency must identify another known task')
        task_map[task['id']] = task
    # Iteratively remove ready tasks. If nothing is ready, the graph has a cycle.
    pending = dict(task_map)
    visited = set()
    while pending:
        ready = [task for task in pending.values() if all(dep in visited for dep in task['depends_on'])]
        if not ready:
            raise ValueError('Task dependency graph must be acyclic')
        for task in ready:
            if task['actual_finish'] is not None:
                for predecessor_id in task['depends_on']:
                    predecessor = task_map[predecessor_id]
                    if predecessor['actual_finish'] is None or predecessor['actual_finish'] > task['actual_finish']:
                        raise ValueError('Completed successor requires predecessors completed no later than it')
            visited.add(task['id'])
            del pending[task['id']]
    issues = _list(project['issues'], 'issues', 200)
    _unique(issues, 'issues')
    for issue in issues:
        _shape(issue, {'id', 'title', 'owner', 'severity', 'due_date', 'status', 'category'}, 'issue')
        _text(issue['title'], 'issue.title', 1000)
        _text(issue['owner'], 'issue.owner')
        if issue['severity'] not in ('low', 'medium', 'high'):
            raise ValueError('issue.severity must be low, medium, or high')
        if issue['status'] not in ('open', 'closed'):
            raise ValueError('issue.status must be open or closed')
        if issue['category'] not in ('scope', 'procurement', 'approval', 'quality', 'other'):
            raise ValueError('Unsupported issue.category')
        _date(issue['due_date'], 'issue.due_date')


def _validate_snapshot(snapshot):
    _shape(snapshot, {'as_of', 'projects'}, 'snapshot')
    as_of = _date(snapshot['as_of'], 'snapshot.as_of')
    projects = _list(snapshot['projects'], 'projects', 100, 1)
    _unique(projects, 'projects')
    for project in projects:
        _validate_project(project, as_of)
    return as_of


def validate_portfolio(data: dict) -> dict:
    """Validate all snapshots/policy and return the supplied object on success."""
    _shape(data, {'schema_version', 'synthetic', 'currency', 'current', 'previous', 'policy'}, 'portfolio input')
    if data['schema_version'] != '1.0' or data['synthetic'] is not True or data['currency'] != 'USD':
        raise ValueError('Requires schema_version 1.0, synthetic exactly true, and currency USD')
    current_date = _validate_snapshot(data['current'])
    if data['previous'] is not None:
        if _validate_snapshot(data['previous']) >= current_date:
            raise ValueError('previous.as_of must be strictly earlier than current.as_of')
    policy = data['policy']
    _shape(policy, POLICY_KEYS, 'policy')
    watch = _decimal(policy['cost_watch_percent'], 'cost_watch_percent', Decimal('100'))
    high = _decimal(policy['cost_high_percent'], 'cost_high_percent', Decimal('100'))
    if not watch < high:
        raise ValueError('cost_watch_percent must be less than cost_high_percent')
    for field in ('schedule_watch_days', 'schedule_high_days'):
        if type(policy[field]) is not int or not 1 <= policy[field] <= 365:
            raise ValueError(f'{field} must be an integer from 1 to 365')
    if policy['schedule_watch_days'] >= policy['schedule_high_days']:
        raise ValueError('schedule_watch_days must be less than schedule_high_days')
    for field in ('cpi_watch_below', 'spi_watch_below'):
        if _decimal(policy[field], field, Decimal('1')) <= 0:
            raise ValueError(f'{field} must be greater than zero and at most 1')
    return data


def _money(number):
    # Normalize signed zero so a zero variance is consistently displayed as 0.00.
    rounded = number.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return format(abs(rounded) if rounded == 0 else rounded, '.2f')


def _ratio(numerator, denominator):
    return numerator / denominator if denominator > 0 else None


def _ratio_text(number):
    if number is None:
        return None
    return format(number.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP), '.4f')


def _raw_metrics(project, as_of):
    """Keep full precision until final formatting and policy comparisons."""
    values = {key: _decimal(project[key], key) for key in MONEY_FIELDS}
    eac = values['actual_cost'] + values['estimate_to_complete']
    overrun = max(eac - values['approved_budget'], Decimal('0'))
    slips = [(date.fromisoformat(task['actual_finish'] or task['forecast_finish']) -
              date.fromisoformat(task['baseline_finish'])).days for task in project['tasks']]
    return {**values, 'eac': eac,
            'variance_at_completion': values['approved_budget'] - eac,
            'overrun_amount': overrun,
            'overrun_percent': overrun / values['approved_budget'] * Decimal('100'),
            'cpi': _ratio(values['earned_value'], values['actual_cost']),
            'spi': _ratio(values['earned_value'], values['planned_value']),
            'max_finish_slip_days': max([0] + slips),
            'overdue_milestones': sum(task['actual_finish'] is None and date.fromisoformat(task['baseline_finish']) < as_of
                                      for task in project['tasks']),
            'open_high_issues': sum(issue['status'] == 'open' and issue['severity'] == 'high' for issue in project['issues']),
            'overdue_issues': sum(issue['status'] == 'open' and date.fromisoformat(issue['due_date']) < as_of
                                  for issue in project['issues'])}


def _analyze(data):
    as_of = date.fromisoformat(data['current']['as_of'])
    previous = data['previous']
    previous_projects = {project['id']: project for project in previous['projects']} if previous else {}
    policy = data['policy']
    results, evidence, warnings = [], {}, []
    totals = {field: Decimal('0') for field in ('approved_budget', 'actual_cost', 'eac',
                                               'overrun_amount', 'earned_value', 'planned_value')}
    for index, project in enumerate(data['current']['projects']):
        identifier = project['id']
        raw = _raw_metrics(project, as_of)
        result = {'id': identifier, 'name': project['name'], 'manager': project['manager'],
                  'budget': _money(raw['approved_budget']), 'actual_cost': _money(raw['actual_cost']),
                  'estimate_to_complete': _money(raw['estimate_to_complete']),
                  'remaining_committed_cost': _money(raw['remaining_committed_cost']),
                  'eac': _money(raw['eac']), 'variance_at_completion': _money(raw['variance_at_completion']),
                  'overrun_amount': _money(raw['overrun_amount']),
                  'overrun_percent': _money(raw['overrun_percent']),
                  'cpi': _ratio_text(raw['cpi']), 'spi': _ratio_text(raw['spi']),
                  **{key: raw[key] for key in ('max_finish_slip_days', 'overdue_milestones', 'open_high_issues', 'overdue_issues')},
                  'flags': [], 'rag': 'green', 'trend': None,
                  # Keep actionable sources for human reports; the AI adapter omits them.
                  'milestone_details': copy.deepcopy(project['tasks']),
                  'open_issue_details': copy.deepcopy([issue for issue in project['issues'] if issue['status'] == 'open'])}
        prefix = f'$.current.projects[{index}]'
        formulas = {
            'budget': prefix + '.approved_budget', 'actual_cost': prefix + '.actual_cost',
            'estimate_to_complete': prefix + '.estimate_to_complete',
            'remaining_committed_cost': prefix + '.remaining_committed_cost (included in ETC)',
            'eac': f'{prefix}.actual_cost + {prefix}.estimate_to_complete',
            'variance_at_completion': 'approved_budget - (actual_cost + estimate_to_complete)',
            'overrun_amount': 'max(actual_cost + estimate_to_complete - approved_budget, 0)',
            'overrun_percent': '100 * max(EAC - approved_budget, 0) / approved_budget',
            'cpi': 'earned_value / actual_cost; undefined when actual_cost = 0',
            'spi': 'earned_value / planned_value; undefined when planned_value = 0',
            'max_finish_slip_days': f'max(0, (actual_finish or forecast_finish) - baseline_finish) over {prefix}.tasks',
            'overdue_milestones': f'count incomplete {prefix}.tasks with baseline_finish < $.current.as_of',
            'open_high_issues': f'count {prefix}.issues where status=open and severity=high',
            'overdue_issues': f'count {prefix}.issues where status=open and due_date < $.current.as_of',
        }
        for metric, source in formulas.items():
            unit = ('ratio' if metric in ('cpi', 'spi') else 'percent' if metric == 'overrun_percent'
                    else 'days' if metric == 'max_finish_slip_days'
                    else 'count' if metric in ('overdue_milestones', 'open_high_issues', 'overdue_issues') else 'USD')
            evidence[f'{identifier}.{metric}'] = {'project_id': identifier, 'metric': metric,
                                                 'value': result[metric], 'unit': unit, 'source': source}
            # Preserve full precision beside presentation rounding for threshold audits.
            if metric in ('cpi', 'spi', 'overrun_percent'):
                evidence[f'{identifier}.{metric}']['raw_value'] = (
                    format(raw[metric], 'f') if raw[metric] is not None else None)
        for field in ('earned_value', 'planned_value'):
            evidence[f'{identifier}.{field}'] = {'project_id': identifier, 'metric': field,
                                                  'value': _money(raw[field]), 'unit': 'USD', 'source': prefix + '.' + field}

        def flag(code, severity, message, metric):
            result['flags'].append({'code': code, 'severity': severity, 'message': message,
                                    'evidence_ids': [f'{identifier}.{metric}']})

        if raw['overrun_percent'] >= _decimal(policy['cost_high_percent'], 'cost_high_percent'):
            flag('COST_OVERRUN', 'red', 'Forecast cost overrun meets the configured high threshold.', 'overrun_percent')
        elif raw['overrun_amount'] > 0 and raw['overrun_percent'] >= _decimal(policy['cost_watch_percent'], 'cost_watch_percent'):
            flag('COST_OVERRUN', 'amber', 'Forecast cost overrun meets the configured watch threshold.', 'overrun_percent')
        if raw['max_finish_slip_days'] >= policy['schedule_high_days']:
            flag('FINISH_SLIP', 'red', 'Maximum milestone finish slip meets the configured high threshold.', 'max_finish_slip_days')
        elif raw['max_finish_slip_days'] >= policy['schedule_watch_days']:
            flag('FINISH_SLIP', 'amber', 'Maximum milestone finish slip meets the configured watch threshold.', 'max_finish_slip_days')
        for metric, threshold in (('cpi', 'cpi_watch_below'), ('spi', 'spi_watch_below')):
            if raw[metric] is None:
                warnings.append(f'{identifier}: {metric.upper()} is undefined because its denominator is zero; risk coverage is incomplete.')
            elif raw[metric] < _decimal(policy[threshold], threshold):
                flag('LOW_' + metric.upper(), 'amber', f'{metric.upper()} is below its configured watch threshold.', metric)
        if raw['open_high_issues']:
            flag('OPEN_HIGH_ISSUE', 'red', 'At least one open high-severity issue needs PM review.', 'open_high_issues')
        if raw['overdue_milestones']:
            flag('OVERDUE_MILESTONES', 'amber', 'At least one incomplete milestone is past its baseline finish date.', 'overdue_milestones')
        if raw['overdue_issues']:
            flag('OVERDUE_ISSUES', 'amber', 'At least one open issue is past its due date.', 'overdue_issues')
        result['rag'] = ('red' if any(f['severity'] == 'red' for f in result['flags'])
                         else 'amber' if result['flags'] else 'green')
        evidence[f'{identifier}.rag'] = {'project_id': identifier, 'metric': 'rag', 'value': result['rag'],
                                         'unit': 'status', 'source': 'highest configured flag severity; green if no flags'}
        # Team-provided finish forecasts can be stale or mutually inconsistent.
        # Warn instead of silently rewriting them into a fictitious forecast.
        stale = [task['id'] for task in project['tasks']
                 if task['actual_finish'] is None and date.fromisoformat(task['forecast_finish']) < as_of]
        if stale:
            warnings.append(f'{identifier}: {len(stale)} incomplete milestone forecast(s) are before as_of '
                            f'(stale forecasts) and may understate finish slip; refresh forecasts. Examples: {", ".join(stale[:10])}.')
        task_map = {task['id']: task for task in project['tasks']}
        inconsistent, examples = 0, []
        for task in project['tasks']:
            task_finish = task['actual_finish'] or task['forecast_finish']
            for predecessor_id in task['depends_on']:
                predecessor = task_map[predecessor_id]
                predecessor_finish = predecessor['actual_finish'] or predecessor['forecast_finish']
                if task_finish < predecessor_finish:
                    inconsistent += 1
                    if len(examples) < 10:
                        examples.append(f'{task["id"]} before {predecessor_id}')
        if inconsistent:
            warnings.append(f'{identifier}: {inconsistent} finish dependency inconsistencies in supplied forecasts '
                            f'or actuals; PM must reconcile without assuming an automatic schedule correction. '
                            f'Examples: {", ".join(examples)}.')
        old = previous_projects.get(identifier)
        if old is not None:
            old_raw = _raw_metrics(old, date.fromisoformat(previous['as_of']))
            budget_changed = _decimal(old['approved_budget'], 'old budget') != raw['approved_budget']
            old_baselines = {task['id']: task['baseline_finish'] for task in old['tasks']}
            new_baselines = {task['id']: task['baseline_finish'] for task in project['tasks']}
            baseline_changed = old_baselines != new_baselines
            result['trend'] = {'eac_delta': _money(raw['eac'] - old_raw['eac']),
                               'finish_slip_delta_days': raw['max_finish_slip_days'] - old_raw['max_finish_slip_days'],
                               'budget_changed': budget_changed, 'baseline_changed': baseline_changed}
            if budget_changed:
                warnings.append(f'{identifier}: approved budget changed; apparent performance changes may reflect rebaselining, not improvement.')
            if baseline_changed:
                warnings.append(f'{identifier}: milestone baselines or task membership changed; finish-slip changes are not directly comparable performance improvement.')
        elif previous is None:
            warnings.append(f'{identifier}: no previous snapshot; baseline only, no trend can be calculated.')
        else:
            warnings.append(f'{identifier}: new project not present in previous snapshot; no trend can be calculated.')
        for field in totals:
            totals[field] += raw[field]
        results.append(result)
    current_ids = {project['id'] for project in data['current']['projects']}
    for identifier in previous_projects.keys() - current_ids:
        warnings.append(f'{identifier}: removed from current snapshot; portfolio comparison coverage changed.')
    warnings.append('Risk coverage is limited to supplied cost, finish milestones, and issue data; green is not a safety or completion guarantee.')
    portfolio = {'project_count': len(results), 'budget': _money(totals['approved_budget']),
                 'actual_cost': _money(totals['actual_cost']), 'eac': _money(totals['eac']),
                 'overrun_amount': _money(totals['overrun_amount']),
                 'net_variance_at_completion': _money(totals['approved_budget'] - totals['eac']),
                 'red_count': sum(result['rag'] == 'red' for result in results),
                 'amber_count': sum(result['rag'] == 'amber' for result in results),
                 'green_count': sum(result['rag'] == 'green' for result in results),
                 'cpi': _ratio_text(_ratio(totals['earned_value'], totals['actual_cost'])),
                 'spi': _ratio_text(_ratio(totals['earned_value'], totals['planned_value']))}
    return {'schema_version': '1.0', 'synthetic': True, 'currency': 'USD',
            'as_of': data['current']['as_of'], 'previous_as_of': previous['as_of'] if previous else None,
            'status': 'REQUIRES_PM_REVIEW', 'projects': results, 'portfolio': portfolio,
            'evidence': evidence, 'quality_warnings': warnings, 'policy': copy.deepcopy(policy)}


def analyze_portfolio(data: dict) -> dict:
    """Validate first, then compute all metrics in a private precision context."""
    validate_portfolio(data)
    with localcontext() as context:
        # Input limits require far fewer digits; 70 also covers tiny denominators.
        context.prec = 70
        return _analyze(data)
