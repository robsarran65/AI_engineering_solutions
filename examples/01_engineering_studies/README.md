# Mesa workflow 1: Engineering Studies & System Analysis

Robert, start with `mesa_workflow.py`. It is deliberately contained in one file,
with comments explaining the imports, definitions, Python syntax, and handoffs.
Use Python 3.10 or later. Offline mode requires no package installation.

## What the first CSV item asks for

- Offering: Engineering Studies & System Analysis.
- Opportunity: Build intake workflows; evaluate data readiness; design AI-assisted analysis pipelines.
- Suggested workflow: data ingestion agent + scenario agent + risk-ranking agent.

This project implements a small, reproducible first version of that workflow.
The supplied mapping CSV describes business opportunities; it is NOT measurement
data. `sample_grid.csv` contains newly created, synthetic teaching measurements.
There is no connection to Mesa systems or live SCADA/PMU equipment.

## Architecture and exact scope

| Worker | Receives | Does | Returns |
| --- | --- | --- | --- |
| DataIngestionAgent | Synthetic snapshot CSV | Checks fields, values, IDs, timestamps | Validated assets and input hash |
| ScenarioAgent | Validated assets | Applies baseline, +10%, +20% load assumptions | Three cases per asset; nine with the sample |
| RiskRankingAgent | Scenario results | Assigns demo bands and sorts by utilization | Ranked numerical evidence |
| Optional AI method on RiskRankingAgent | Ranked evidence | Requests an explanation and review questions | Unverified prose draft |

The coordinator calls these workers in a fixed sequence. Offline they are
role-based Python workers, not independent AI agents. With `--ai`, one worker
uses a real LLM. This is an AI-assisted workflow; it has no autonomous planning,
tool selection loop, or independent agent negotiation. Those features would add
complexity without improving this first lesson.

The AI does not calculate or change the authoritative numerical findings.
Its draft can still contain mistakes and must be reviewed against the JSON.

## Run on Windows in VS Code

1. Download and extract `mesa-first-workflow.zip`.
2. Open the extracted `mesa_first_workflow` folder in VS Code.
3. Open **Terminal > New Terminal**.
4. Confirm the terminal is inside `mesa_first_workflow`: `dir` should show
   `mesa_workflow.py` and `sample_grid.csv`. Check Python: `python --version`.
5. Run just the first worker:

```powershell
python mesa_workflow.py --stage intake --output intake_report.json
```

6. Open `intake_report.json`. Expect readiness `PASS` and three accepted assets.
7. Run the connected workflow:

```powershell
python mesa_workflow.py --output mesa_report.json
```

8. Open `mesa_report.json` for the complete result. `example_report.json` is an
   actual offline run included for comparison.
9. Run the verification checks:

```powershell
python -m unittest -v
```

If Windows uses the Python launcher, substitute `py` for `python`.
Outputs are written in the terminal's current folder. Use a fresh output filename
to preserve earlier runs; an existing output file is replaced.

## Turn on the real AI explanation (optional)

The implementation follows the official OpenAI Responses API pattern:
https://developers.openai.com/api/docs/quickstart

Install the optional SDK in an isolated environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install openai
```

Set `OPENAI_API_KEY` using an existing API credential in your local environment.
Keep it out of source files and Git. Set `OPENAI_MODEL` to a Responses-compatible
model available to your account. No particular model or cost is assumed here.
In that same PowerShell terminal, replace these placeholders locally:

```powershell
$env:OPENAI_API_KEY = "YOUR_EXISTING_API_KEY"
$env:OPENAI_MODEL = "YOUR_MODEL_ID"
```

These variables apply only to the current terminal session. Do not paste your
real key into chat or commit it to Git. Then run:

```powershell
.\.venv\Scripts\python.exe mesa_workflow.py --ai --model YOUR_MODEL_ID --output ai_report.json
```

`YOUR_MODEL_ID` is a placeholder: replace it with your model ID.
This sends the synthetic ranked findings to the API and can incur usage charges.
There is one application-level model request and no automatic SDK retries.
The timeout is 45 seconds; the output cap is 1,600 tokens. These are bounds, not
a price quote. The report stores the AI draft separately from numerical results.
If the call fails, deterministic results remain saved, `ai_status` becomes
`FAILED`, and the program exits with a nonzero status. Offline output says
`NOT_REQUESTED`; successful AI text says `DRAFT_REQUIRES_REVIEW`.
The live AI path was not executed during delivery; no credentials were supplied.

## Learn the code in this order

1. **Imports:** `import csv` exposes a module; `from pathlib import Path` selects a name.
2. **First class:** `class DataIngestionAgent:` defines a worker type.
3. **First method:** `def run(self, input_path: Path) -> dict:` defines its behavior.
   `self` is the current instance. Type hints describe intended types.
4. **Variables:** `assets = []` creates a list; dictionaries label values with keys.
5. **Validation:** `if` chooses a branch, `for` repeats, `try/except` handles bad data.
6. **Return:** `return` hands results back to the caller.
7. **Instantiation:** `DataIngestionAgent()` creates a worker instance.
8. **Handoff:** `.run(...)` executes its method; the next worker receives its output.
9. **AI method:** `instructions` sets the role; `input` carries evidence;
   `response.output_text` contains the generated explanation.
10. **Entry point:** `if __name__ == "__main__":` runs `main()` only when launched directly.

Indentation defines Python blocks. Text after `#` is a comment. Triple-quoted
text below a class or function is its documentation string, or docstring.

## What the calculation means

Assumed projected load = snapshot load × scenario multiplier.

Utilization (%) = projected MVA / assumed MVA rating × 100.

Demo bands: LOW below 90%, WATCH from 90% to below 100%, HIGH at 100% or above.
These labels are illustrative screening bands, not failure probabilities or
approved engineering limits. Results retain full precision; terminal display
rounds to one decimal place.

Example: TX_C has 95 MVA load and a 100 MVA rating. With 20% assumed growth:
95 × 1.20 = 114 MVA; 114 / 100 × 100 = 114%. That case ranks first.
LOW does not establish safety: the example has no voltage, stability, topology,
protection, ambient-condition, or outage redistribution model.

## Input contract and readiness limits

Each row needs `asset_id`, timezone-aware ISO `timestamp`, nonnegative finite
`load_mva`, and positive finite `rating_mva`. IDs must be unique and all rows
must represent one instant. Any invalid row blocks the whole workflow.
This is a deliberately narrow readiness check: PASS does not verify calibration,
measurement freshness, engineering plausibility, complete asset coverage,
source authorization, or suitability for a real study. Historical synthetic
snapshots are allowed. PMU waveforms and streaming data are not supported.

## Before a real engineering pilot

Agree study objectives and engineer-approved inputs/limits. Integrate a tested
power-system solver and network model; compare results with reference cases.
Add telemetry adapters, quality/freshness checks, access controls, audit trails,
and model-output evaluations. Obtain approval for any external data processing.
The first version has no equipment-control interface or operating authority.

## Interview explanation

“I built a prototype that validates a synthetic engineering snapshot, runs
explicit load-growth screening scenarios, and ranks findings for engineer
review. An optional AI step drafts explanations from the computed evidence.
A production pilot would add approved telemetry and a validated grid solver.”

## Alignment with Mesa's public website

Reviewed October 29, 2026. Mesa's substation page explicitly lists load-growth
projections, load-flow analysis, short-circuit analysis, and grounding analysis.
Its electrical services page also lists protection/coordination studies and
power-quality analysis. This makes **substation load-growth screening and study
intake** a relevant narrow pilot for the CSV's broad first offering. Choosing
that pilot is a design inference; it is not an announced Mesa AI initiative.

Sources:
- https://www.mesainc.com/
- https://www.mesainc.com/power-delivery/substations-switchyard/
- https://www.mesainc.com/engineering-and-design/electrical/

The site describes experience with engineering software including ETAP, Aspen,
and CAPE. It does not establish which platform a particular team uses today,
its licensing, API availability, or permission to integrate. No such integration
is implemented or claimed. Public SCADA experience also does not establish
availability of live telemetry or PMU data for this pilot.

The code's `STUDY_CONTEXT` dictionary records the chosen service alignment,
source, and unresolved assumptions. It is included in the saved evidence and
sent to the optional AI explanation step, so those questions remain visible.

### Questions for Mesa before a real pilot

1. Which study should be supported first: load growth, load flow, short circuit,
   grounding, or protection coordination? This prototype assumes load growth.
2. What data exports, equipment ratings, model versions, and client-specific
   acceptance criteria are authoritative?
3. Which study platform and integration method are approved for this team?
4. Who reviews findings, and what evidence must accompany the review package?
5. What data may be processed by an external model, and what must stay internal?

These are project-specific gaps the public site does not answer. The learning
demo proceeds with explicit synthetic assumptions instead of inventing answers.
