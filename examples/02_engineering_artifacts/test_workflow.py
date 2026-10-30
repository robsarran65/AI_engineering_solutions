"""Behavioral checks for the second Mesa learning workflow.

Run from this folder with: python -m unittest -v
These tests use synthetic data and a fake model backend; no network or API key.
"""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from engineering_workflow import (
    calculate_estimate,
    calculate_schedule,
    run_workflow,
    validate_project,
    write_outputs,
)


SAMPLE_PATH = Path(__file__).with_name("sample_project.json")


def sample():
    """Read a fresh object so mutation in one test cannot affect another test."""
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


def valid_agent_results(project):
    """Return controlled model-shaped responses, not a simulation of model quality."""
    identifiers = [item["id"] for item in project["requirements"]]
    return {
        "design": {"sections": [
            {"requirement_id": identifier, "concept": "Synthetic conceptual draft.",
             "missing_inputs": ["Engineer-approved drawings"]}
            for identifier in identifiers]},
        "document": {"specifications": [
            {"requirement_id": identifier, "draft_text": "Draft for engineer review.",
             "acceptance_check": "Engineer confirms inputs before use."}
            for identifier in identifiers]},
        "review": {"findings": [], "limitations": ["No engineering certification."]},
    }


class EstimationTests(unittest.TestCase):
    def test_sample_estimate_is_reproducible(self):
        result = calculate_estimate(sample())
        self.assertEqual(result["currency"], "USD")
        self.assertEqual(result["subtotal"], "7480.00")
        self.assertEqual(result["contingency_amount"], "1122.00")
        self.assertEqual(result["total"], "8602.00")
        self.assertEqual({item["id"]: item["line_total"] for item in result["items"]},
                         {"COST-001": "5000.00", "COST-002": "1280.00",
                          "COST-003": "1200.00"})

    def test_round_each_line_before_summing_then_round_contingency(self):
        project = sample()
        project["cost_items"] = [
            {"id": "A", "description": "Half cent", "quantity": "1", "unit": "each",
             "unit_cost": "0.005"},
            {"id": "B", "description": "Half cent", "quantity": "1", "unit": "each",
             "unit_cost": "0.005"},
        ]
        project["contingency_percent"] = "25"
        result = calculate_estimate(project)
        self.assertEqual([item["line_total"] for item in result["items"]], ["0.01", "0.01"])
        self.assertEqual(result["subtotal"], "0.02")
        self.assertEqual(result["contingency_amount"], "0.01")
        self.assertEqual(result["total"], "0.03")

    def test_zero_cost_and_contingency_endpoints(self):
        project = sample()
        project["cost_items"][0]["unit_cost"] = "0"
        for percent, amount, total in [("0", "0.00", "2480.00"),
                                        ("100", "2480.00", "4960.00")]:
            with self.subTest(percent=percent):
                project["contingency_percent"] = percent
                result = calculate_estimate(project)
                self.assertEqual(result["contingency_amount"], amount)
                self.assertEqual(result["total"], total)


class ValidationTests(unittest.TestCase):
    def test_sample_validates(self):
        project = sample()
        self.assertEqual(validate_project(project), project)

    def test_invalid_numeric_fields_fail_closed(self):
        cases = [
            ("quantity", "0"), ("quantity", "-1"), ("quantity", "NaN"),
            ("quantity", "Infinity"), ("quantity", True), ("quantity", 1.1),
            ("quantity", None), ("quantity", "invalid"),
            ("unit_cost", "-1"), ("unit_cost", "NaN"),
            ("unit_cost", "Infinity"), ("unit_cost", False),
            ("unit_cost", 1.1), ("unit_cost", "1000000001"),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                project = sample()
                project["cost_items"][0][field] = value
                with self.assertRaises(ValueError):
                    validate_project(project)

    def test_invalid_contingency_and_duration_fail_closed(self):
        for value in ["-1", "100.01", "NaN", "Infinity", True, 0.5, None, "bad"]:
            with self.subTest(contingency=value):
                project = sample()
                project["contingency_percent"] = value
                with self.assertRaises(ValueError):
                    validate_project(project)
        for value in [True, False, 0, -1, 1.5, "2", None]:
            with self.subTest(duration=value):
                project = sample()
                project["tasks"][0]["duration_days"] = value
                with self.assertRaises(ValueError):
                    validate_project(project)

    def test_missing_required_fields_and_empty_collections_fail_closed(self):
        for field in ["project_id", "synthetic", "currency", "contingency_percent",
                      "requirements", "cost_items", "tasks", "approved_reference_notes"]:
            with self.subTest(missing=field):
                project = sample()
                del project[field]
                with self.assertRaises(ValueError):
                    validate_project(project)
        for field in ["requirements", "cost_items", "tasks"]:
            with self.subTest(empty=field):
                project = sample()
                project[field] = []
                with self.assertRaises(ValueError):
                    validate_project(project)

    def test_synthetic_must_be_exactly_true_and_currency_usd(self):
        for value in [False, 1, "true", None]:
            with self.subTest(synthetic=value):
                project = sample()
                project["synthetic"] = value
                with self.assertRaises(ValueError):
                    validate_project(project)
        project = sample()
        project["currency"] = "EUR"
        with self.assertRaises(ValueError):
            validate_project(project)

    def test_ids_must_be_nonblank_strings_and_unique(self):
        for collection in ["requirements", "cost_items", "tasks", "approved_reference_notes"]:
            for value in [True, 1, "", "   "]:
                with self.subTest(collection=collection, identifier=value):
                    project = sample()
                    project[collection][0]["id"] = value
                    with self.assertRaises(ValueError):
                        validate_project(project)
            with self.subTest(duplicate=collection):
                project = sample()
                project[collection][1]["id"] = project[collection][0]["id"]
                with self.assertRaises(ValueError):
                    validate_project(project)


class SchedulingTests(unittest.TestCase):
    def test_parallel_tasks_and_unsorted_input(self):
        project = sample()
        project["tasks"].reverse()
        result = calculate_schedule(project)
        self.assertEqual(result["duration_days"], 7)
        times = {item["id"]: (item["earliest_start_day"], item["earliest_finish_day"])
                 for item in result["tasks"]}
        self.assertEqual(times, {"TASK-001": (0, 2), "TASK-002": (2, 5),
                                 "TASK-003": (2, 4), "TASK-004": (5, 7)})

    def test_malformed_unknown_duplicate_and_cyclic_dependencies_rejected(self):
        for dependencies in ["TASK-001", None, [True], ["UNKNOWN"],
                             ["TASK-001", "TASK-001"], ["TASK-002"]]:
            with self.subTest(dependencies=dependencies):
                project = sample()
                project["tasks"][1]["depends_on"] = dependencies
                with self.assertRaises(ValueError):
                    calculate_schedule(project)
        project = sample()
        project["tasks"][0]["depends_on"] = ["TASK-004"]
        with self.assertRaises(ValueError):
            calculate_schedule(project)


class AgentChainTests(unittest.TestCase):
    def test_three_ai_calls_in_order_keep_computed_results_and_require_review(self):
        project = sample()
        results = valid_agent_results(project)
        calls = []

        def backend(role, payload):
            self.assertIsInstance(payload, dict)
            calls.append(role)
            if role == "document":
                self.assertEqual(payload["design"], results["design"])
            if role == "review":
                self.assertEqual(payload["document"], results["document"])
            return copy.deepcopy(results[role])

        report = run_workflow(project, mode="ai", backend=backend)
        self.assertEqual(calls, ["design", "document", "review"])
        self.assertEqual(len(report["agent_trace"]), 3)
        self.assertEqual(report["status"], "REQUIRES_ENGINEER_REVIEW")
        self.assertEqual(report["estimate"]["total"], "8602.00")
        self.assertEqual(report["schedule"]["duration_days"], 7)
        self.assertEqual(report["review"]["findings"], [])

    def test_backend_payload_mutation_cannot_change_numeric_evidence_or_project(self):
        project = sample()
        original = copy.deepcopy(project)
        results = valid_agent_results(project)
        def backend(role, payload):
            # The adapter gets an isolated copy, even if it behaves maliciously.
            self.assertEqual(payload["estimate"]["total"], "8602.00")
            self.assertEqual(payload["schedule"]["duration_days"], 7)
            self.assertEqual(payload["project"]["cost_items"][0]["unit_cost"], "125")
            payload["estimate"]["total"] = "0.00"
            payload["schedule"]["duration_days"] = 0
            payload["project"]["cost_items"][0]["unit_cost"] = "0"
            return copy.deepcopy(results[role])
        report = run_workflow(project, mode="ai", backend=backend)
        self.assertEqual(project, original)
        self.assertEqual(report["estimate"]["total"], "8602.00")
        self.assertEqual(report["schedule"]["duration_days"], 7)

    def test_offline_is_labeled_and_requires_engineer_review(self):
        report = run_workflow(sample())
        self.assertEqual(report["mode"], "offline")
        self.assertEqual(report["status"], "REQUIRES_ENGINEER_REVIEW")
        self.assertEqual(report["estimate"]["total"], "8602.00")

    def test_incomplete_duplicate_unknown_or_extra_agent_outputs_rejected(self):
        project = sample()
        cases = []
        response = valid_agent_results(project)
        response["design"]["sections"].pop()
        cases.append(("missing requirement", response))
        response = valid_agent_results(project)
        response["document"]["specifications"][1]["requirement_id"] = "REQ-001"
        cases.append(("duplicate requirement", response))
        response = valid_agent_results(project)
        response["review"]["findings"] = [{"requirement_id": "UNKNOWN", "severity": "warning",
                                             "note": "Unrecognized requirement."}]
        cases.append(("unknown requirement", response))
        response = valid_agent_results(project)
        response["review"]["status"] = "APPROVED"
        cases.append(("model cannot self approve", response))
        response = valid_agent_results(project)
        response["review"]["limitations"] = []
        cases.append(("missing limitations", response))
        response = valid_agent_results(project)
        response["design"]["sections"][0]["concept"] = " "
        cases.append(("blank model text", response))
        response = valid_agent_results(project)
        response["document"] = "not parsed JSON"
        cases.append(("malformed response type", response))
        for name, responses in cases:
            with self.subTest(case=name):
                def backend(role, payload):
                    return copy.deepcopy(responses[role])
                with self.assertRaises(ValueError):
                    run_workflow(project, mode="ai", backend=backend)

    def test_malformed_json_from_mocked_sdk_is_rejected_before_next_agent(self):
        # Replace the optional SDK entirely, so this check cannot contact a service.
        calls = []
        def create(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(status="completed", output_text="{invalid JSON")
        fake_client = SimpleNamespace(responses=SimpleNamespace(create=create))
        fake_sdk = SimpleNamespace(OpenAI=lambda **kwargs: fake_client)
        with patch.dict(sys.modules, {"openai": fake_sdk}):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "not-a-real-key"}):
                with self.assertRaises(ValueError):
                    run_workflow(sample(), mode="ai", model="mock-model")
        self.assertEqual(len(calls), 1)

    def test_failed_backend_stops_later_calls(self):
        calls = []
        def backend(role, payload):
            calls.append(role)
            raise RuntimeError("Synthetic model failure")
        with self.assertRaises((ValueError, RuntimeError)):
            run_workflow(sample(), mode="ai", backend=backend)
        self.assertEqual(calls, ["design"])


class OutputTests(unittest.TestCase):
    def test_cli_requires_explicit_overwrite(self):
        module = Path(__file__).with_name("engineering_workflow.py")
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "outputs"
            command = [sys.executable, str(module), "--input", str(SAMPLE_PATH),
                       "--output", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {name: (output / name).read_bytes()
                      for name in ["report.json", "draft_package.md"]}
            rejected = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("overwrite", rejected.stderr.lower())
            for name, content in before.items():
                self.assertEqual((output / name).read_bytes(), content)
            permitted = subprocess.run(command + ["--overwrite"], capture_output=True, text=True)
            self.assertEqual(permitted.returncode, 0, permitted.stderr)

    def test_cli_failed_ai_keeps_baseline_without_claiming_completed_draft(self):
        module = Path(__file__).with_name("engineering_workflow.py")
        # Missing credentials must fail before optional SDK construction/network.
        environment = dict(os.environ)
        environment.pop("OPENAI_API_KEY", None)
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "failed"
            command = [sys.executable, str(module), "--input", str(SAMPLE_PATH),
                       "--output", str(output), "--mode", "ai", "--model", "mock-model"]
            result = subprocess.run(command, capture_output=True, text=True, env=environment)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads((output / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "FAILED_REQUIRES_ENGINEER_REVIEW")
            self.assertEqual(report["estimate"]["total"], "8602.00")
            self.assertEqual(report["schedule"]["duration_days"], 7)
            self.assertNotIn("design", report)
            self.assertNotIn("document", report)
            self.assertNotIn("review", report)

    def test_report_and_draft_are_written(self):
        report = run_workflow(sample())
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "package"
            write_outputs(report, output)
            saved = json.loads((output / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "REQUIRES_ENGINEER_REVIEW")
            self.assertEqual(saved["estimate"]["total"], "8602.00")
            draft = (output / "draft_package.md").read_text(encoding="utf-8")
            self.assertIn("draft", draft.lower())
            self.assertIn("synthetic", draft.lower())


if __name__ == "__main__":
    unittest.main()
