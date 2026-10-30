# PMO early-warning pilot — Mesa solution 10

Robert, this runnable Python pilot turns a **synthetic project portfolio** into a
local dashboard and executive brief. Deterministic calculations flag cost,
finish-date, and issue concerns. Four specialist roles then explain the evidence:
cost, schedule, risk, and executive reporting. Every output requires PM review.

This is a learning and product-discovery pilot, not a production PMO application.
It has no database, hosted service, live project-system connection, or predictive
ML model. It does not establish accuracy, ROI, regulatory compliance, or approval.

Mesa's public PMO service description discusses planned versus actual performance,
estimates to complete, portfolio reporting, metrics, and EPI dashboards. Those
services motivate the pilot; no internal Mesa data, APIs, templates, or system
access are assumed. Source retrieved October 30, 2026:
https://www.mesainc.com/project-management-organization/

## What you can run

| Mode | Numerical analysis | Narrative | Network/API |
| --- | --- | --- | --- |
| Offline, default | Python calculations and configured flags | Clearly labeled templates | None |
| AI, optional | Identical Python calculations | Four evidence-referencing AI drafts | Up to four model calls |

Cost and schedule roles run concurrently; risk uses their outputs; the executive
role synthesizes all three. Role outputs cannot change numerical results or RAG
status. Schema and evidence checks reject malformed responses but cannot prove
that generated prose is true.

## Windows and VS Code setup

You need Git and Python 3.10 or later. Clone into a subfolder to preserve any ZIP
examples already under `C:\Users\rober\AI_Mesa_samples`:

```powershell
git clone https://github.com/robsarran65/AI_engineering_solutions.git C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions
cd C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions\solutions\10_pmo_early_warning
```

The clone destination must be nonexistent or empty. If already cloned there, use:

```powershell
git -C C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions pull --ff-only
cd C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions\solutions\10_pmo_early_warning
```

If pull refuses to update, inspect its message and preserve your local work.
Open the solution folder in VS Code, then **Terminal > New Terminal**. Run `dir`
and confirm it contains `pmo.py` and the `data` folder. Check `python --version`.
If your machine uses the Windows launcher, substitute `py` for `python`.

## First run: no package installation or key

```powershell
python pmo.py --input data/sample_portfolio.json --output outputs
```

Open `outputs/dashboard.html` in your browser. It is a self-contained local file;
no server is needed. Filter by RAG and search for a project. Review project cards
to inspect metrics, flags, trends, and role narratives. Click a project name in
the overview to jump to its card; expand **Inspect project evidence and formulas**
to inspect supporting references. Human reports also retain milestone and open-issue
details so reviewers can identify the underlying tasks and issues.

Also inspect:

- `outputs/report.json`: authoritative calculated evidence, agent outputs, provenance.
- `outputs/executive_brief.md`: readable briefing for PM review.

Use a new folder to keep earlier runs. Existing output files are protected;
replace them intentionally with:

```powershell
python pmo.py --input data/sample_portfolio.json --output outputs --overwrite
```

To check inputs and calculate metrics without writing files or calling AI:

```powershell
python pmo.py --input data/sample_portfolio.json --validate-only
```

Run the local checks from this solution folder:

```powershell
python -m unittest discover -s tests -v
```

The tests use synthetic data and fake model backends. They do not validate live
model quality or establish suitability for a real portfolio.

## Expected synthetic sample results

The supplied snapshot is dated October 30, 2026, with October 23 as its comparison.
These values were checked using `analyze_portfolio` on the supplied JSON:

| Project | EAC | Positive overrun | Max finish slip | RAG |
| --- | ---: | ---: | ---: | --- |
| P001 — Substation expansion | $115,000 | $15,000 | 12 days | Red |
| P002 — Transmission design | $84,000 | $4,000 | 4 days | Amber |
| P003 — Hydro controls documentation | $58,000 | $0 | 0 days | Green |

Portfolio budget is **$240,000**, actual cost **$132,000**, and EAC **$257,000**.
Positive project overruns total **$19,000**; net VAC is **−$17,000**, because P003's
$2,000 projected underrun offsets the net result but does not erase other project
overruns. Portfolio CPI is **0.9242** and SPI **0.9385**. Green only means no
configured flag fired. The sample contains one red, one amber, and one green project.

## Optional AI mode

Use an existing OpenAI API key and a Responses-compatible model available to your
account. No credentials are provisioned by this pilot. Create an isolated environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ai.txt
$env:OPENAI_API_KEY = "YOUR_EXISTING_API_KEY"
$env:OPENAI_MODEL = "YOUR_MODEL_ID"
.\.venv\Scripts\python.exe pmo.py --input data/sample_portfolio.json --output outputs_ai --mode ai --model $env:OPENAI_MODEL
```

Replace the placeholders only in your local terminal. Never commit or share your
key. Environment settings above apply to that PowerShell session. The four roles
share the selected model; each request has a timeout and output bound, and the SDK
does not retry automatically. AI mode accepts at most **10 current projects** and
**200,000 serialized characters per role request**, including prior handoffs.
Offline mode accepts up to 100 projects per snapshot. Oversized AI requests fail
with baseline reports retained. AI mode can incur usage charges. No live API calls
were run during preparation because no credentials were supplied.

Model requests exclude the detailed milestone and open-issue registers. They
still send project names, manager names, computed evidence, policy/warnings, and
prior role handoffs to the external model. This is context reduction, not
anonymization. Any later real-data pilot needs approved data-processing rules.

If an AI call or response check fails, the program exits unsuccessfully and saves
baseline numerical reports with a visible AI failure indication. It does not
publish partially completed agent narratives as a successful run. Diagnose the
error before retrying; choose a new output folder or explicitly overwrite.

## Read and share the work

Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for the four-role handoff and code map,
[DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) for input definitions and formulas,
and [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for a ten-minute walkthrough.
[PRODUCT_HANDOFF.md](docs/PRODUCT_HANDOFF.md) defines the pilot backlog, ownership,
acceptance criteria, and work needed before real-system adoption.
[VALIDATION.md](docs/VALIDATION.md) records completed checks and the pending live-AI
and browser acceptance exercises.

Share the repository link with a product team and point them to
`solutions/10_pmo_early_warning/README.md`. Recipients need repository permission
if it is private. Share a synthetic generated dashboard for an immediate preview;
it contains the project data and narratives embedded in the file. A local file
path on your computer is not a public sharing URL. Do not include API keys,
private client data, or unapproved project exports in the repository.
