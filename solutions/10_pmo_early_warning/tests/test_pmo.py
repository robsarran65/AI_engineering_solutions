"""Behavioral verification of the PMO pilot. No test uses a network or live API.

From the solution folder: python -m unittest discover -s tests -v
Fixtures are deliberately small and independent of the shipped demo portfolio.
"""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

from metrics import analyze_portfolio, validate_portfolio
from agents import run_agents

ROOT = Path(__file__).resolve().parents[1]


def project(identifier, large=False):
    """Use two differently weighted projects to expose naive ratio averaging."""
    if large:
        values = ('10000', '8000', '8000', '8000', '1500', '500')
        tasks = [dict(id='M1', name='Future milestone', baseline_finish='2026-11-10',
                      forecast_finish='2026-11-10', actual_finish=None,
                      progress_percent=50, depends_on=[])]
        issues = []
    else:
        values = ('1000', '400', '300', '400', '700', '200')
        tasks = [
            dict(id='M2', name='Late future milestone', baseline_finish='2026-10-25',
                 forecast_finish='2026-11-02', actual_finish=None,
                 progress_percent=50, depends_on=['M1']),
            dict(id='M1', name='Completed milestone', baseline_finish='2026-10-20',
                 forecast_finish='2026-10-22', actual_finish='2026-10-22',
                 progress_percent=100, depends_on=[]),
        ]
        issues = [
            dict(id='I1', title='Approval needed', owner='Owner A', severity='high',
                 due_date='2026-10-29', status='open', category='approval'),
            dict(id='I2', title='Closed item', owner='Owner B', severity='high',
                 due_date='2026-10-01', status='closed', category='quality'),
        ]
    fields = ['approved_budget', 'planned_value', 'earned_value', 'actual_cost',
              'estimate_to_complete', 'remaining_committed_cost']
    return dict(id=identifier, name='Project ' + identifier, manager='Demo Manager',
                tasks=tasks, issues=issues, **dict(zip(fields, values)))


def fixture():
    current = {'as_of': '2026-10-30', 'projects': [project('P001'), project('P002', True)]}
    previous = copy.deepcopy(current)
    previous['as_of'] = '2026-10-23'
    previous['projects'][0]['actual_cost'] = '300'
    previous['projects'][0]['estimate_to_complete'] = '750'
    previous['projects'][0]['tasks'][0]['forecast_finish'] = '2026-10-29'
    previous['projects'][1]['actual_cost'] = '7000'
    previous['projects'][1]['earned_value'] = '7000'
    previous['projects'][1]['planned_value'] = '7000'
    previous['projects'][1]['estimate_to_complete'] = '2000'
    return dict(schema_version='1.0', synthetic=True, currency='USD', current=current,
                previous=previous, policy=dict(cost_watch_percent='5', cost_high_percent='10',
                schedule_watch_days=3, schedule_high_days=7,
                cpi_watch_below='0.9', spi_watch_below='0.9'))


def role_output(analysis, role):
    metric = 'max_finish_slip_days' if role == 'schedule' else 'eac'
    return {'observations': [dict(project_id=p['id'], evidence_ids=[p['id'] + '.' + metric],
             summary=role + ' evidence summary for ' + p['id'],
             recommended_action='Have the PM review the cited evidence.')
             for p in analysis['projects']], 'limitations': ['Unverified draft; PM review required.']}


class MetricsTests(unittest.TestCase):
    def test_estimate_does_not_double_count_remaining_commitments(self):
        data = fixture()
        self.assertEqual(validate_portfolio(data), data)
        report = analyze_portfolio(data)
        first = report['projects'][0]
        self.assertEqual(first['eac'], '1100.00')  # 400 actual + 700 ETC, not +200 again.
        self.assertEqual(first['variance_at_completion'], '-100.00')
        self.assertEqual(first['overrun_amount'], '100.00')
        self.assertEqual(first['overrun_percent'], '10.00')
        self.assertEqual(first['cpi'], '0.7500')
        self.assertEqual(first['spi'], '0.7500')
        self.assertEqual(report['status'], 'REQUIRES_PM_REVIEW')

    def test_portfolio_uses_weighted_ratios_and_gross_positive_overruns(self):
        report = analyze_portfolio(fixture())
        portfolio = report['portfolio']
        self.assertEqual(portfolio['budget'], '11000.00')
        self.assertEqual(portfolio['actual_cost'], '8400.00')
        self.assertEqual(portfolio['eac'], '10600.00')
        self.assertEqual(portfolio['overrun_amount'], '100.00')
        self.assertEqual(portfolio['cpi'], '0.9881')  # 8300/8400, not mean(.75,1).
        self.assertEqual(portfolio['spi'], '0.9881')
        self.assertEqual((portfolio['red_count'], portfolio['amber_count'],
                          portfolio['green_count']), (1, 0, 1))

    def test_schedule_and_issue_status_use_as_of_date_and_actuals(self):
        report = analyze_portfolio(fixture())
        first = report['projects'][0]
        self.assertEqual(first['max_finish_slip_days'], 8)
        self.assertEqual(first['overdue_milestones'], 1)
        self.assertEqual(first['open_high_issues'], 1)
        self.assertEqual(first['overdue_issues'], 1)
        self.assertEqual(first['rag'], 'red')
        # Closed high-severity issues do not remain active risk triggers.
        self.assertEqual(report['projects'][1]['rag'], 'green')
        data = fixture()
        task = data['current']['projects'][0]['tasks'][0]
        task.update(actual_finish='2026-10-28', progress_percent=100,
                    forecast_finish='2026-12-01')
        self.assertEqual(analyze_portfolio(data)['projects'][0]['max_finish_slip_days'], 3)

    def test_due_today_is_not_overdue(self):
        data = fixture()
        p = data['current']['projects'][0]
        p['tasks'][0]['baseline_finish'] = '2026-10-30'
        p['issues'][0]['due_date'] = '2026-10-30'
        result = analyze_portfolio(data)['projects'][0]
        self.assertEqual(result['overdue_milestones'], 0)
        self.assertEqual(result['overdue_issues'], 0)

    def test_evidence_exists_for_every_flag_and_is_project_scoped(self):
        report = analyze_portfolio(fixture())
        self.assertIn('P001.rag', report['evidence'])
        for p in report['projects']:
            for flag in p['flags']:
                self.assertTrue(flag['evidence_ids'])
                for identifier in flag['evidence_ids']:
                    self.assertIn(identifier, report['evidence'])
                    self.assertEqual(report['evidence'][identifier]['project_id'], p['id'])

    def test_zero_denominators_are_null_with_warnings_not_false_zero(self):
        data = fixture()
        p = data['current']['projects'][0]
        p.update(planned_value='0', earned_value='0', actual_cost='0')
        result = analyze_portfolio(data)
        self.assertIsNone(result['projects'][0]['cpi'])
        self.assertIsNone(result['projects'][0]['spi'])
        self.assertTrue(result['quality_warnings'])
        self.assertEqual(result['portfolio']['cpi'], '1.0000')
        self.assertEqual(result['portfolio']['spi'], '1.0000')

    def test_raw_precision_controls_cost_rag_before_money_rounding(self):
        data = fixture()
        p = project('P003', True)
        p.update(approved_budget='1000', actual_cost='500', estimate_to_complete='599.999',
                 remaining_committed_cost='0', planned_value='500', earned_value='500')
        data.update(current={'as_of': '2026-10-30', 'projects': [p]}, previous=None)
        result = analyze_portfolio(data)['projects'][0]
        self.assertEqual(result['overrun_percent'], '10.00')
        self.assertEqual(result['rag'], 'amber')  # Raw 9.9999% is below red 10%.

    def test_cpi_uses_unrounded_ratio_for_threshold(self):
        data = fixture()
        p = project('P003', True)
        p.update(approved_budget='20000', actual_cost='10000', estimate_to_complete='10000',
                 remaining_committed_cost='0', planned_value='8000', earned_value='8999.6')
        data.update(current={'as_of': '2026-10-30', 'projects': [p]}, previous=None)
        result = analyze_portfolio(data)['projects'][0]
        self.assertEqual(result['cpi'], '0.9000')
        self.assertIn('LOW_CPI', [f['code'] for f in result['flags']])

    def test_zero_watch_threshold_does_not_flag_zero_overrun(self):
        data = fixture()
        data['policy']['cost_watch_percent'] = '0'
        p = project('P003', True)
        p.update(approved_budget='10000', actual_cost='8000', estimate_to_complete='2000')
        data.update(current={'as_of': '2026-10-30', 'projects': [p]}, previous=None)
        result = analyze_portfolio(data)['projects'][0]
        self.assertNotIn('COST_OVERRUN', [f['code'] for f in result['flags']])

    def test_snapshot_trend_and_rebaseline_warning(self):
        data = fixture()
        report = analyze_portfolio(data)
        trend = report['projects'][0]['trend']
        self.assertEqual(trend['eac_delta'], '50.00')
        self.assertEqual(trend['finish_slip_delta_days'], 4)
        self.assertFalse(trend['budget_changed'])
        self.assertFalse(trend['baseline_changed'])
        data['current']['projects'][0]['approved_budget'] = '1200'
        data['current']['projects'][0]['tasks'][0]['baseline_finish'] = '2026-10-26'
        result = analyze_portfolio(data)
        self.assertTrue(result['projects'][0]['trend']['budget_changed'])
        self.assertTrue(result['projects'][0]['trend']['baseline_changed'])
        self.assertTrue(result['quality_warnings'])

    def test_stale_or_inconsistent_forecasts_are_flagged_without_rewriting(self):
        data = fixture()
        data['current']['projects'][0]['tasks'][0]['forecast_finish'] = '2026-10-28'
        result = analyze_portfolio(data)
        self.assertTrue(any('refresh forecasts' in warning.lower()
                            for warning in result['quality_warnings']))
        self.assertEqual(data['current']['projects'][0]['tasks'][0]['forecast_finish'], '2026-10-28')
        data['current']['projects'][0]['tasks'][0]['forecast_finish'] = '2026-10-21'
        result = analyze_portfolio(data)
        self.assertTrue(any('dependency inconsist' in warning.lower()
                            for warning in result['quality_warnings']))

    def test_new_removed_or_absent_prior_projects_do_not_invent_trends(self):
        data = fixture()
        data['previous']['projects'] = [data['previous']['projects'][1]]
        result = analyze_portfolio(data)
        self.assertIsNone(result['projects'][0]['trend'])
        self.assertTrue(result['quality_warnings'])
        data = fixture()
        data['current']['projects'] = [data['current']['projects'][0]]
        self.assertTrue(analyze_portfolio(data)['quality_warnings'])
        data['previous'] = None
        self.assertIsNone(analyze_portfolio(data)['projects'][0]['trend'])


class ValidationTests(unittest.TestCase):
    def test_bad_money_and_numeric_types_rejected(self):
        for value in ['NaN', 'Infinity', '-1', True, 0.1, None, '1000000000001']:
            with self.subTest(value=value):
                data = fixture()
                data['current']['projects'][0]['actual_cost'] = value
                with self.assertRaises(ValueError):
                    validate_portfolio(data)
        for field, value in [('approved_budget', '0'), ('earned_value', '1001'),
                             ('planned_value', '1001'), ('remaining_committed_cost', '701')]:
            with self.subTest(field=field):
                data = fixture()
                data['current']['projects'][0][field] = value
                with self.assertRaises(ValueError):
                    validate_portfolio(data)

    def test_root_policy_and_unknown_fields_rejected(self):
        for field, value in [('synthetic', 1), ('schema_version', '2.0'), ('currency', 'EUR')]:
            data = fixture()
            data[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_portfolio(data)
        for field, value in [('cost_watch_percent', '10'), ('schedule_watch_days', True),
                             ('schedule_high_days', 3), ('cpi_watch_below', '0'),
                             ('spi_watch_below', '1.01')]:
            data = fixture()
            data['policy'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_portfolio(data)
        data = fixture()
        data['current']['projects'][0]['currency'] = 'USD'
        with self.assertRaises(ValueError):
            validate_portfolio(data)

    def test_ids_dependencies_dates_and_progress_consistency_rejected(self):
        mutations = [
            lambda d: d['current']['projects'][1].update(id='P001'),
            lambda d: d['current']['projects'][0]['tasks'][1].update(id='M2'),
            lambda d: d['current']['projects'][0]['tasks'][0].update(depends_on=['UNKNOWN']),
            lambda d: d['current']['projects'][0]['tasks'][0].update(depends_on=['M1', 'M1']),
            lambda d: d['current']['projects'][0]['tasks'][1].update(depends_on=['M2']),
            lambda d: d['current']['projects'][0]['tasks'][0].update(actual_finish='2026-10-31', progress_percent=100),
            lambda d: d['current']['projects'][0]['tasks'][0].update(progress_percent=100),
            lambda d: d['current']['projects'][0]['tasks'][1].update(progress_percent=50),
            lambda d: d['current']['projects'][0]['tasks'][0].update(progress_percent=True),
            lambda d: d['current']['projects'][0]['tasks'][0].update(baseline_finish='2026-1-1'),
            lambda d: d['previous'].update(as_of='2026-10-30'),
            lambda d: d['current']['projects'][0]['issues'][0].update(severity='critical'),
        ]
        for mutate in mutations:
            data = fixture()
            mutate(data)
            with self.subTest(mutation=mutations.index(mutate)), self.assertRaises(ValueError):
                validate_portfolio(data)

    def test_completed_successor_cannot_precede_predecessor(self):
        data = fixture()
        data['current']['projects'][0]['tasks'][0].update(actual_finish='2026-10-21', progress_percent=100)
        with self.assertRaises(ValueError):
            validate_portfolio(data)


class AgentTests(unittest.TestCase):
    def test_four_role_handoffs_and_parallel_independent_roles(self):
        analysis = analyze_portfolio(fixture())
        barrier = threading.Barrier(2)
        payloads = {}
        lock = threading.Lock()

        def backend(role, payload):
            with lock:
                payloads[role] = copy.deepcopy(payload)
            if role in ('cost', 'schedule'):
                barrier.wait(timeout=3)  # A sequential implementation cannot satisfy this.
            return role_output(analysis, role)

        result = run_agents(analysis, mode='ai', backend=backend)
        self.assertEqual(set(payloads), {'cost', 'schedule', 'risk', 'executive'})
        self.assertEqual(set(result['roles']), set(payloads))
        self.assertEqual(result['ai_status'], 'DRAFT_REQUIRES_REVIEW')
        risk_payload = json.dumps(payloads['risk'])
        executive_payload = json.dumps(payloads['executive'])
        self.assertIn('cost evidence summary', risk_payload)
        self.assertIn('schedule evidence summary', risk_payload)
        self.assertIn('risk evidence summary', executive_payload)
        self.assertEqual(len(result['trace']), 4)

    def test_backend_mutation_cannot_change_analysis_or_later_evidence(self):
        analysis = analyze_portfolio(fixture())
        original = copy.deepcopy(analysis)

        def mutate(node):
            if isinstance(node, dict):
                for key, value in list(node.items()):
                    if key in ('eac', 'budget', 'rag'):
                        node[key] = 'MUTATED'
                    else:
                        mutate(value)
            elif isinstance(node, list):
                for item in node:
                    mutate(item)

        seen = []
        def backend(role, payload):
            seen.append(json.dumps(payload))
            mutate(payload)
            return role_output(original, role)

        result = run_agents(analysis, mode='ai', backend=backend)
        self.assertEqual(analysis, original)
        self.assertTrue(all('MUTATED' not in text for text in seen))
        self.assertEqual(result['mode'], 'ai')

    def test_ai_project_limit_fails_before_any_backend_call(self):
        data = fixture()
        data['previous'] = None
        data['current']['projects'] = [project(f'P{i:03}', True) for i in range(11)]
        analysis = analyze_portfolio(data)
        called = []
        def backend(role, payload):
            called.append(role)
            return role_output(analysis, role)
        with self.assertRaises(ValueError):
            run_agents(analysis, mode='ai', backend=backend)
        self.assertEqual(called, [])

    def test_ai_context_omits_raw_registers_without_erasing_local_evidence(self):
        analysis = analyze_portfolio(fixture())
        analysis['projects'][0]['milestone_details'] = [{'name': 'RAW_REGISTER_PRIVATE_MARKER'}]
        analysis['projects'][0]['open_issue_details'] = [{'title': 'RAW_REGISTER_PRIVATE_MARKER'}]
        payloads = []
        def backend(role, payload):
            payloads.append(json.dumps(payload))
            return role_output(analysis, role)
        run_agents(analysis, mode='ai', backend=backend)
        self.assertEqual(len(payloads), 4)
        self.assertTrue(all('RAW_REGISTER_PRIVATE_MARKER' not in payload for payload in payloads))
        self.assertIn('milestone_details', analysis['projects'][0])
        self.assertIn('open_issue_details', analysis['projects'][0])

    def test_bad_citations_coverage_and_self_approval_rejected(self):
        analysis = analyze_portfolio(fixture())
        cases = []
        out = role_output(analysis, 'cost')
        out['observations'][0]['evidence_ids'] = ['UNKNOWN']
        cases.append(out)
        out = role_output(analysis, 'cost')
        out['observations'][0]['evidence_ids'] = ['P002.eac']
        cases.append(out)
        out = role_output(analysis, 'cost')
        out['observations'].pop()
        cases.append(out)
        out = role_output(analysis, 'cost')
        out['status'] = 'APPROVED'
        cases.append(out)
        out = role_output(analysis, 'cost')
        out['limitations'] = []
        cases.append(out)
        out = role_output(analysis, 'cost')
        out['observations'][1]['project_id'] = 'P001'
        cases.append(out)
        for bad in cases:
            def backend(role, payload):
                return copy.deepcopy(bad if role == 'cost' else role_output(analysis, role))
            with self.subTest(case=cases.index(bad)), self.assertRaises(ValueError):
                run_agents(analysis, mode='ai', backend=backend)

    def test_failed_parallel_stage_does_not_invoke_dependent_agents(self):
        analysis = analyze_portfolio(fixture())
        called = []
        def backend(role, payload):
            called.append(role)
            if role == 'cost':
                raise RuntimeError('Mocked failure')
            return role_output(analysis, role)
        with self.assertRaises((ValueError, RuntimeError)):
            run_agents(analysis, mode='ai', backend=backend)
        self.assertNotIn('risk', called)
        self.assertNotIn('executive', called)

    def test_mocked_sdk_rejects_incomplete_or_malformed_model_responses(self):
        analysis = analyze_portfolio(fixture())
        for status, text in [('incomplete', '{}'), ('completed', 'not JSON')]:
            calls = []
            def create(**kwargs):
                calls.append(kwargs)
                return types.SimpleNamespace(status=status, output_text=text)
            fake_client = types.SimpleNamespace(responses=types.SimpleNamespace(create=create))
            fake_module = types.SimpleNamespace(OpenAI=lambda **kwargs: fake_client)
            with self.subTest(status=status), patch.dict(sys.modules, {'openai': fake_module}), \
                 patch.dict(os.environ, {'OPENAI_API_KEY': 'fake-test-key'}):
                with self.assertRaises(ValueError):
                    run_agents(analysis, mode='ai', model='mock-model')
            self.assertLessEqual(len(calls), 2)
            for call in calls:
                self.assertEqual(call['text']['format']['type'], 'json_schema')
                self.assertFalse(call['store'])

    def test_offline_mode_is_not_labeled_as_real_ai(self):
        result = run_agents(analyze_portfolio(fixture()))
        self.assertEqual(result['mode'], 'offline')
        self.assertEqual(result['ai_status'], 'NOT_REQUESTED')
        self.assertEqual(len(result['roles']), 4)


class ReportingAndCliTests(unittest.TestCase):
    def test_html_escapes_untrusted_project_and_agent_text(self):
        from reporting import write_reports
        data = fixture()
        injection = '<script>alert("unsafe")</script>'
        data['current']['projects'][0]['name'] = injection
        data['current']['projects'][0]['tasks'][0]['name'] = injection
        data['current']['projects'][0]['issues'][0]['title'] = injection
        analysis = analyze_portfolio(data)
        result = run_agents(analysis)
        result['roles']['cost']['observations'][0]['summary'] = injection
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            write_reports(analysis, result, output, dict(input_sha256='a'*64,
                          generated_utc='2026-10-30T12:00:00+00:00', mode='offline',
                          model=None, input_filename='demo.json'))
            page = (output / 'dashboard.html').read_text(encoding='utf-8')
            self.assertNotIn(injection, page)
            self.assertIn('&lt;script&gt;', page)
            self.assertTrue((output / 'executive_brief.md').exists())
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['analysis']['projects'][0]['eac'], '1100.00')

    def test_failure_report_discards_partial_agent_products(self):
        from reporting import write_reports
        analysis = analyze_portfolio(fixture())
        partial = {'untrusted_partial': 'PARTIAL_AI_DRAFT_MARKER'}
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            write_reports(analysis, partial, output, dict(input_sha256='a'*64,
                          generated_utc='2026-10-30T12:00:00+00:00', mode='ai',
                          model='mock-model', input_filename='demo.json'),
                          failure={'status': 'FAILED', 'error_type': 'ValueError',
                                   'message': 'Mocked narrative generation failure.'})
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertIsNone(report['agents'])
            self.assertEqual(report['analysis']['projects'][0]['eac'], '1100.00')
            self.assertTrue(report['failure'])
            for name in ['report.json', 'dashboard.html', 'executive_brief.md']:
                self.assertNotIn('PARTIAL_AI_DRAFT_MARKER', (output / name).read_text(encoding='utf-8'))

    def cli(self, input_file, output, *extra, env=None):
        return subprocess.run([sys.executable, str(ROOT / 'pmo.py'), '--input', str(input_file),
                               '--output', str(output), *extra], capture_output=True,
                              text=True, timeout=15, env=env)

    def test_cli_offline_outputs_and_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / 'input.json'
            source.write_text(json.dumps(fixture()), encoding='utf-8')
            output = base / 'result'
            first = self.cli(source, output)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = (output / 'report.json').read_bytes()
            second = self.cli(source, output)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual((output / 'report.json').read_bytes(), original)
            third = self.cli(source, output, '--overwrite')
            self.assertEqual(third.returncode, 0, third.stderr)

    def test_validate_only_does_not_write_reports_or_need_api_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / 'input.json'
            source.write_text(json.dumps(fixture()), encoding='utf-8')
            output = base / 'result'
            env = dict(os.environ)
            env.pop('OPENAI_API_KEY', None)
            result = self.cli(source, output, '--validate-only', '--mode', 'ai', env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(output.exists())

    def test_cli_missing_key_retains_baseline_and_no_partial_agents(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source = base / 'input.json'
            source.write_text(json.dumps(fixture()), encoding='utf-8')
            env = dict(os.environ)
            env.pop('OPENAI_API_KEY', None)
            output = base / 'result'
            result = self.cli(source, output, '--mode', 'ai', '--model', 'mock-model', env=env)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['analysis']['projects'][0]['eac'], '1100.00')
            self.assertIsNone(report['agents'])
            self.assertTrue(report['failure'])
            self.assertIn('fail', (output / 'dashboard.html').read_text(encoding='utf-8').lower())

    def test_invalid_input_and_duplicate_json_keys_create_no_reports(self):
        duplicate = json.dumps(fixture()).replace('"currency": "USD"', '"currency": "USD", "currency": "USD"', 1)
        bad_inputs = [duplicate, json.dumps({**fixture(), 'currency': 'EUR'})]
        for text in bad_inputs:
            with self.subTest(text=text[:40]), tempfile.TemporaryDirectory() as folder:
                base = Path(folder)
                source = base / 'bad.json'
                source.write_text(text, encoding='utf-8')
                output = base / 'result'
                result = self.cli(source, output)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((output / 'report.json').exists())


if __name__ == '__main__':
    unittest.main()
