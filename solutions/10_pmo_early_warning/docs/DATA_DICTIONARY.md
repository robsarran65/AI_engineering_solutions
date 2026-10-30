# Data contract, calculations, and interpretation

Read `data/sample_portfolio.json` beside this guide. Unknown fields are rejected.
All amounts are USD; use decimal strings such as `"1250.50"` or integers, never
JSON floats or booleans. Monetary inputs must be finite and nonnegative, at most
10¹² with no more than 12 decimal places. Calculations retain precision until
report formatting. The pilot accepts synthetic data only.

## Input fields

| Scope | Fields | Meaning / validation |
| --- | --- | --- |
| Root | `schema_version`, `synthetic`, `currency` | Exactly `"1.0"`, `true`, `"USD"` |
| Root | `current`, `previous`, `policy` | Current snapshot required; previous may be null |
| Snapshot | `as_of`, `projects` | Exact ISO date `YYYY-MM-DD`; previous strictly earlier |
| Project | `id`, `name`, `manager` | Bounded nonblank text; IDs unique per snapshot |
| Project | `approved_budget` | Budget at completion, BAC; must be positive |
| Project | `planned_value`, `earned_value` | PV/EV in currency units; each ≤ BAC; supplied by project team |
| Project | `actual_cost` | AC incurred as of snapshot |
| Project | `estimate_to_complete` | ETC includes all remaining committed cost |
| Project | `remaining_committed_cost` | Included subset of ETC; cannot exceed ETC |
| Project | `tasks`, `issues` | At least one task; issues may be empty |
| Task | `id`, `name`, `baseline_finish`, `forecast_finish` | Unique ID per project; baseline and supplied forecast dates |
| Task | `actual_finish`, `progress_percent` | Actual date or null; 100 iff actual date exists; actual ≤ snapshot date |
| Task | `depends_on` | Known, unique other task IDs; no cycles; actual completions must respect predecessor order |
| Issue | `id`, `title`, `owner`, `due_date` | Unique ID per project; bounded text and ISO due date |
| Issue | `severity`, `status`, `category` | Severity low/medium/high; status open/closed; category scope/procurement/approval/quality/other |

Each snapshot supports at most 100 projects, 200 tasks and 200 issues per project.
The CLI limits the input file to 5 MiB (5 × 1,024 × 1,024 bytes). AI mode further
limits the current snapshot to 10 projects and each serialized role request to
200,000 characters, including prior handoffs. These AI limits do not reduce the
offline 100-project limit. Oversized requests stop AI generation while the CLI
retains baseline reports. Tasks represent finish checkpoints; there
is no duration-based, working-calendar, critical-path, or resource solver.

## Configurable warning policy

| Field | Rule |
| --- | --- |
| `cost_watch_percent`, `cost_high_percent` | Decimal strings; 0 ≤ watch < high ≤ 100 |
| `schedule_watch_days`, `schedule_high_days` | Integers; 1 ≤ watch < high ≤ 365 |
| `cpi_watch_below`, `spi_watch_below` | Decimal strings; each > 0 and ≤ 1 |

These are demo policy inputs, not Mesa-approved thresholds. RAG comparisons use
unrounded calculated values. Display rounding can make a boundary look different;
inspect evidence and policy when explaining a classification. Ratio and overrun-
percentage evidence includes `raw_value` alongside rounded `value`; null remains
null for an undefined ratio. Use `raw_value` when auditing a threshold decision.

## Formulas

| Metric | Formula / handling |
| --- | --- |
| EAC | AC + ETC; **do not add commitments again** |
| VAC | BAC − EAC; negative means projected budget overrun |
| Overrun amount | max(EAC − BAC, 0) |
| Overrun percent | Overrun / BAC × 100 |
| CPI | EV / AC if AC > 0; otherwise null/N/A |
| SPI | EV / PV if PV > 0; otherwise null/N/A |
| Maximum finish slip | Maximum positive calendar-day difference between baseline finish and actual finish, or forecast finish when incomplete |
| Overdue milestones | Incomplete tasks with baseline finish strictly before snapshot date |
| Open high issues | Open issues with high severity |
| Overdue issues | Open issues with due date strictly before snapshot date |

Today is not overdue. Closed issues are excluded from issue counts. Completed
late milestones remain in finish-slip measurement even though no longer overdue.
SPI does not generate a finish forecast: forecast dates are supplied inputs.
Money displays to two decimals, ratios to four, percentages to two.

Red flags: cost overrun at/above high threshold, slip at/above high threshold,
or any open high issue. Amber flags: positive cost overrun at/above watch,
slip at/above watch, known CPI/SPI below policy thresholds, overdue milestones,
or overdue issues. The strongest flag determines RAG. Green means no configured
flag fired; it is not a statement of safety, completeness, or certification.

Portfolio amounts aggregate projects. Portfolio positive overrun is the **sum of
project positive overruns**, not a net amount offset by under-budget projects.
Portfolio CPI = sum(EV)/sum(AC); SPI = sum(EV)/sum(PV), with the same zero-denominator
handling. Neither is an arithmetic average of project ratios.

## Comparisons and evidence

Matched project IDs receive EAC and finish-slip deltas. Missing prior snapshot,
new projects, removed projects, undefined ratios, changed budgets, and changed
baselines produce quality warnings. Incomplete milestones with forecast dates
before `as_of` and finish forecasts that conflict with predecessor finish order
also produce quality warnings. The program does not silently repair these
forecasts; stale dates can understate finish-slip exposure. A reduced slip caused by a changed baseline
must not be described as proven performance improvement.

A flag points to IDs such as `P001.eac` or `P001.max_finish_slip_days`. Each evidence
entry records project ID, metric, value, unit, and source/formula, plus `raw_value`
for CPI, SPI, and overrun percentage. Those IDs are
illustrations; use the actual report's map. Every narrative observation must cite
existing evidence for its own project. This guards reference integrity, not the
truth of all generated statements.


## Human detail registers versus AI context

Each analyzed project retains `milestone_details` from the supplied tasks and
`open_issue_details` for its open issues. These details support human inspection
in reports; they are separate from calculated counts and scalar evidence.

AI request preparation removes those two detail registers from a copied context.
Project names, manager names, computed evidence, warnings, policy, and role
handoffs still leave the local runtime when AI mode calls the external model.
The input is not anonymized, and valid evidence IDs do not make generated prose
verified. Offline mode makes no model requests.
