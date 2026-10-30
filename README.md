# AI Engineering Solutions

Commented Python examples for engineering workflows aligned with Mesa Associates' public service descriptions. This is an independent learning project, not an official Mesa product. Examples use synthetic data and require engineer review.

## Examples

| Example | Scope | AI workflow |
| --- | --- | --- |
| [01 — Engineering Studies & System Analysis](examples/01_engineering_studies/README.md) | Validate a synthetic asset snapshot, screen load-growth assumptions, rank findings | Deterministic workers plus an optional AI explanation |
| [02 — Designs, Specifications, Schedules, Cost Estimates](examples/02_engineering_artifacts/README.md) | Draft conceptual documentation, calculate an estimate and dependency schedule, review project-checklist gaps | Three AI roles: design assistant, document automation, review; offline templates also available |
| [10 — EPCM Project Management](solutions/10_pmo_early_warning/README.md) | Portfolio cost/schedule/issue indicators, prior-snapshot trends, evidence-linked dashboard and executive brief | Cost and schedule roles run in parallel, then risk and executive roles; optional AI and offline templates |

Python 3.10 or later is required. No third-party packages are needed for offline runs. AI mode needs the optional OpenAI package, an existing API key, and an account-accessible compatible model; usage charges can apply. See each example's README for Windows/VS Code setup and commented code walkthroughs.

## Run example 1

From the repository root:

```powershell
cd examples/01_engineering_studies
python mesa_workflow.py --stage intake --output intake_report.json
python mesa_workflow.py --output mesa_report.json
python -m unittest -v
```

## Run example 2

From the repository root:

```powershell
cd examples/02_engineering_artifacts
python engineering_workflow.py --input sample_project.json --output outputs
python -m unittest -v
```

Example 2 writes `report.json` and `draft_package.md`. Use a new output folder for each run or explicitly add `--overwrite`. Its committed `sample_outputs` folder shows an actual offline template run, not live AI output. Python calculates money and schedule values; AI text cannot approve the package or alter the authoritative numerical evidence.

These are teaching prototypes. They do not provide validated power-system simulation, construction-ready designs, regulatory certification, or equipment-control interfaces. Public website descriptions do not establish access to Mesa's internal systems, standards, or data.

## Solution 10: PMO early-warning pilot

[Start with setup and use](solutions/10_pmo_early_warning/README.md), or share the [product-team handoff](solutions/10_pmo_early_warning/docs/PRODUCT_HANDOFF.md), [ten-minute demo](solutions/10_pmo_early_warning/docs/DEMO_SCRIPT.md), and [validation record](solutions/10_pmo_early_warning/docs/VALIDATION.md).

From the repository root:

```powershell
cd solutions/10_pmo_early_warning
python pmo.py --output outputs
python -m unittest discover -s tests -v
```

Open `outputs/dashboard.html` in your browser. The committed `sample_outputs` demonstrates a synthetic offline run with three projects. No API key or third-party packages are required for offline use. AI mode adds four evidence-referencing narrative drafts; Python remains responsible for financial calculations and configured risk statuses.

The pilot is synthetic-only. Live AI quality, browser rendering acceptance, approved source data, integration, and production controls require further validation as documented in the handoff.
