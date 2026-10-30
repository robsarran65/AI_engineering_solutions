# Mesa example 2: Engineering artifact workflow

Robert, this example covers the second item in your Mesa opportunity list:
**Designs, Specifications, Schedules, Cost Estimates**. It connects three roles:
a design assistant, a document automation agent, and a project-checklist reviewer.
The goal is to learn the Python code and the handoffs while producing a traceable,
conceptual draft package for engineer review.

This is a synthetic learning project, not a Mesa deliverable or an integration
with Mesa's internal systems. The sample describes an assumed substation equipment
replacement. It does not select equipment, invent ratings, perform engineering
design calculations, or establish compliance with any standard.

## What each agent does

| Stage | Role | Input | Output |
| --- | --- | --- | --- |
| 1 | DesignAssistantAgent | Requirements and project reference notes | One concept and missing-input list for each requirement |
| 2 | DocumentAutomationAgent | Project evidence and design handoff | One draft specification and acceptance check for each requirement |
| 3 | ComplianceReviewAgent | Draft package and project evidence | Findings and limitations for the project checklist |

“Compliance” in the third class name means checking this demo's project rules.
It is not legal, regulatory, or engineering certification. The final status always
requires engineer review, even when the reviewer finds no issues.

The two modes are deliberately different:

- **Offline mode, the default:** runs deterministic templates. These outputs are
  labeled as offline templates; no AI model is called and no API key is needed.
- **AI mode:** makes three real model calls, one per role, with information passed
  from each stage to the next. This is a fixed AI workflow. The models do not
  independently plan, choose tools, change files, approve designs, or run a
  negotiation loop.

Python computes money and schedule values in both modes. Model text never controls
those values, output paths, or approval status. Each AI handoff is checked for its
expected structure and requirement IDs before the next stage can use it.

## Get the repository onto your Windows computer

These commands assume Git and Python 3.10 or later are already installed. Because
`C:\Users\rober\AI_Mesa_samples` may already contain extracted examples, clone into
a new subfolder beneath it. This keeps the existing files in place. Open PowerShell:

```powershell
git clone https://github.com/robsarran65/AI_engineering_solutions.git C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions
cd C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions\examples\02_engineering_artifacts
```

The clone destination `AI_engineering_solutions` must be nonexistent or empty.
If you already cloned the repository into that subfolder, update that existing
clone instead of cloning again:

```powershell
git -C C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions pull --ff-only
cd C:\Users\rober\AI_Mesa_samples\AI_engineering_solutions\examples\02_engineering_artifacts
```

If the repository is already cloned directly into `C:\Users\rober\AI_Mesa_samples`,
use its existing location:

```powershell
git -C C:\Users\rober\AI_Mesa_samples pull --ff-only
cd C:\Users\rober\AI_Mesa_samples\examples\02_engineering_artifacts
```

Use the existing-clone commands only for a folder containing this Git repository.
A folder holding extracted ZIP files is not automatically a Git clone. If `pull`
reports a conflict or refuses to update, stop and inspect the message; do not
delete local work or force a reset.

Open the folder in VS Code through **File > Open Folder**, or run `code .` if the
VS Code command is available. Open **Terminal > New Terminal**. Run `dir` and
confirm it shows `engineering_workflow.py` and `sample_project.json`.

Check your Python version:

```powershell
python --version
```

If your computer uses the Windows Python launcher, use `py` instead of `python`.
The repository stays named `AI_engineering_solutions`; the parent folder
`AI_Mesa_samples` is simply its local location.

## Run the offline workflow first

From the example folder, run:

```powershell
python engineering_workflow.py --input sample_project.json --output outputs
```

The default mode is offline. Open the files in the `outputs` folder:

- `report.json`: structured evidence, numerical results, role outputs, and trace.
- `draft_package.md`: a readable Markdown draft package.

Output protection prevents silently replacing an existing run. To keep both runs,
choose another folder:

```powershell
python engineering_workflow.py --input sample_project.json --output outputs_second_run
```

To intentionally replace this example's existing output files, add `--overwrite`:

```powershell
python engineering_workflow.py --input sample_project.json --output outputs --overwrite
```

## Run the verification checks

From the example folder, run:

```powershell
python -m unittest -v
```

The checks use local synthetic data and a fake AI backend, so they do not make
paid model calls. They verify calculation results, input rejection, role handoffs,
and output behavior. They do not establish engineering validity or validate live
model quality. Live API calls were not executed during preparation because no
API credentials were supplied.

## Check the sample calculations

All quantities, rates, durations, and the contingency percentage are invented
teaching inputs in `sample_project.json`. They are not Mesa rates or quotations.

| Illustrative cost | Calculation | Amount |
| --- | --- | ---: |
| Engineering labor | 40 hours × $125 | $5,000.00 |
| Document preparation | 16 hours × $80 | $1,280.00 |
| Review labor | 8 hours × $150 | $1,200.00 |
| Subtotal | Sum of line amounts | $7,480.00 |
| Contingency | 15% × $7,480.00 | $1,122.00 |
| Total | Subtotal + contingency | **$8,602.00** |

Money uses Python's `Decimal` arithmetic, with each line rounded to cents before
summing and contingency rounded to cents. This keeps decimal rounding explicit.
The estimate is in USD and is not an equipment or construction quote.

| Task | Earliest start day | Earliest finish day |
| --- | ---: | ---: |
| Collect project inputs | 0 | 2 |
| Draft conceptual package | 2 | 5 |
| Prepare estimate | 2 | 4 |
| Engineer review | 5 | 7 |

The result is **7 elapsed days** under the sample dependency assumptions. Drafting
and estimate preparation can overlap after inputs are collected; review waits
for both. These are relative offsets, not dates. The calculation does not account
for weekends, holidays, staff availability, procurement, or resource constraints.
It is not a committed delivery schedule.

## Optional: run the three real AI roles

Use an isolated Python environment. These commands call its Python directly, so
PowerShell environment activation is unnecessary:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install openai
```

Use an **existing** OpenAI API key and a model ID available to your API account.
The following values are placeholders. Replace them locally; do not share a real
key in chat, place it in source code, or commit it to Git:

```powershell
$env:OPENAI_API_KEY = "YOUR_EXISTING_API_KEY"
$env:OPENAI_MODEL = "YOUR_MODEL_ID"
```

These environment variables apply to this PowerShell session. Then run:

```powershell
.\.venv\Scripts\python.exe engineering_workflow.py --input sample_project.json --output outputs_ai --mode ai --model $env:OPENAI_MODEL
```

AI mode sends the synthetic project and role handoffs to the API and can incur
usage charges. There are three sequential role calls on a successful run; errors
can stop it earlier. The workflow has no automatic SDK retries. A model must
support the request options used in the code. No particular model, access level,
or cost is assumed here.

If a call or response validation fails, do not treat partial draft content as a
successful deliverable. Read the terminal error and any saved failure evidence.
Keep the deterministic estimate and schedule separate from unverified model prose.
All successful AI text still requires engineer review.

## Read the commented code in this order

1. **Imports:** `import json` loads a module for reading and writing JSON.
   `from pathlib import Path` imports one named class for handling file paths.
2. **Definitions:** `def validate_project(...):` defines a function. It does not
   execute until the function is called. Indentation identifies its body.
3. **Parameters and return hints:** `project: dict` says the intended input is a
   dictionary. `-> dict` describes the expected return type. Type hints document
   intent; validation code enforces the input rules.
4. **Data structures:** `{...}` holds a dictionary of named values, while `[...]`
   holds a list. `list[dict]` means a list of dictionaries. Access such as
   `project["requirements"]` retrieves a value using its key.
5. **Loops and decisions:** `for` repeats work; `if`, `elif`, and `else` select
   branches. `raise ValueError(...)` rejects unsuitable input. `try` and `except`
   handle failures instead of pretending the stage succeeded.
6. **Calculation functions:** read `calculate_estimate` and `calculate_schedule`.
   Follow how validated inputs become reproducible numerical evidence.
7. **Agent classes:** `class` defines an object type. A method is a function inside
   that class. `self` refers to the current object. Parentheses after a class name
   create an instance; `.run(...)` invokes its behavior.
8. **Handoffs:** find `run_workflow`. Follow the design result into the document
   role and the package into review. Compare this sequence with `agent_trace` in
   `report.json`.
9. **AI boundary:** find the optional backend. Its `instructions` describe the role,
   while the JSON input supplies project evidence. The returned text is parsed
   and checked before it becomes a handoff. The lazy SDK import means offline
   mode works without installing the AI package.
10. **Files and terminal options:** read `write_outputs` and the command-line entry
    point. `argparse` converts flags into Python values; `Path` identifies files.
    The overwrite guard protects earlier outputs.

Text after `#` is a comment. Triple-quoted text immediately below a definition is
a documentation string, or docstring. An f-string such as `f"Project: {name}"`
inserts a variable's value inside braces. A comprehension builds a collection
from a loop in a compact expression. Read those expressions slowly as “for each
item, calculate this value.”

## How the public Mesa website shaped this example

The following service alignment uses official Mesa pages retrieved on **October
29, 2026**. Those pages were not freshly verified on October 30. Mesa's homepage
describes engineering studies, system analysis, designs,
specifications, schedules, and cost estimates. Its substation page describes
engineering documents such as equipment arrangements, bills of material, cable
schedules, and protection/control diagrams. Those public services make a draft
engineering-documentation package a relevant teaching example. The choice of
this particular pilot is our design inference, not an announced Mesa AI product.

Public references:

- https://www.mesainc.com/
- https://www.mesainc.com/power-delivery/substations-switchyard/
- https://www.mesainc.com/engineering-and-design/electrical/

The public site does not disclose the team's internal document templates,
engineering acceptance criteria, customer standards, software interfaces,
approval workflow, or permission to process client data externally. This example
does not assume those details.

Before adapting it for a real pilot, identify the approved document template,
source drawings, study inputs, estimate basis, scheduling conventions, review
owners, and data-processing policy. Engineers must define and approve the actual
technical requirements and acceptance criteria.
