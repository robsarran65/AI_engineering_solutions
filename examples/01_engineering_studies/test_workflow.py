"""Run with: python -m unittest -v. No API calls or external dependencies."""
import tempfile
import unittest
from pathlib import Path
from mesa_workflow import DataIngestionAgent, ScenarioAgent, RiskRankingAgent, run_workflow


class WorkflowTests(unittest.TestCase):
    def test_expected_ranking(self):
        result = run_workflow(Path(__file__).with_name('sample_grid.csv'), 'workflow')
        findings = result['ranked_findings']
        self.assertEqual(len(findings), 9)
        self.assertEqual(findings[0]['asset_id'], 'TX_C')
        self.assertAlmostEqual(findings[0]['utilization_percent'], 114)
        self.assertEqual(result['status'], 'REQUIRES_ENGINEER_REVIEW')

    def test_threshold_boundaries(self):
        cases = [{'utilization_percent': n} for n in [89.99, 90, 99.99, 100]]
        result = RiskRankingAgent().run(cases)
        self.assertEqual([r['screening_band'] for r in result],
                         ['HIGH', 'WATCH', 'WATCH', 'LOW'])

    def test_reject_bad_data(self):
        header = 'asset_id,timestamp,load_mva,rating_mva\n'
        bad_rows = [
            'A,2026-10-29T12:00:00Z,NaN,100\n',
            'A,2026-10-29T12:00:00Z,10,0\n',
            'A,2026-10-29T12:00:00Z,-1,100\n',
            'A,2026-10-29T12:00:00,10,100\n',
            'A,2026-10-29T12:00:00Z,10,100\nA,2026-10-29T12:00:00Z,20,100\n',
            'A,2026-10-29T12:00:00Z,10,100\nB,2026-10-29T13:00:00Z,20,100\n',
            '',
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            for rows in bad_rows:
                with self.subTest(rows=rows):
                    path.write_text(header + rows, encoding='utf-8')
                    with self.assertRaises(ValueError):
                        DataIngestionAgent().run(path)

    def test_duplicate_headers_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'duplicate_headers.csv'
            path.write_text('asset_id,timestamp,load_mva,load_mva,rating_mva\n'
                            'A,2026-10-29T12:00:00Z,90,1,100\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'headers must be unique'):
                DataIngestionAgent().run(path)

    def test_calculation_overflow_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Calculation overflow'):
            ScenarioAgent().run([{'asset_id': 'A', 'load_mva': 1e308, 'rating_mva': 1}])

    def test_first_worker_only(self):
        report = run_workflow(Path(__file__).with_name('sample_grid.csv'), 'intake')
        self.assertEqual(report['intake']['rows'], 3)
        self.assertNotIn('ranked_findings', report)


if __name__ == '__main__':
    unittest.main()
