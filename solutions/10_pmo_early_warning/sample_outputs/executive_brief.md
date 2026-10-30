# PMO early-warning executive brief

**SYNTHETIC PILOT — REQUIRES PROJECT MANAGER REVIEW**

As of: 2026-10-30
Previous snapshot: 2026-10-23
Narrative status: Offline templates — no AI model was called

## Portfolio evidence

- Projects: 3; red: 1; amber: 1; green: 1
- Approved budget: $240,000.00
- Estimate at completion: $257,000.00
- Sum of positive project overruns: $19,000.00
- Weighted CPI: 0.9242; weighted SPI: 0.9385

Net variance at completion (budget minus EAC): $-17,000.00. Positive project overruns above do not net out savings.

## P001 — Substation expansion — synthetic

Manager: Sample PM A; configured status: RED
EAC: $115,000.00; budget: $100,000.00; overrun: $15,000.00
Maximum finish slippage: 12 days; overdue milestones: 1
Open high-severity issues: 1; overdue open issues: 1

- RED: Forecast cost overrun meets the configured high threshold\. [evidence: P001\.overrun\_percent]
- RED: Maximum milestone finish slip meets the configured high threshold\. [evidence: P001\.max\_finish\_slip\_days]
- AMBER: CPI is below its configured watch threshold\. [evidence: P001\.cpi]
- AMBER: SPI is below its configured watch threshold\. [evidence: P001\.spi]
- RED: At least one open high-severity issue needs PM review\. [evidence: P001\.open\_high\_issues]
- AMBER: At least one incomplete milestone is past its baseline finish date\. [evidence: P001\.overdue\_milestones]
- AMBER: At least one open issue is past its due date\. [evidence: P001\.overdue\_issues]

Change in EAC: $10,000.00; change in maximum slip: 7 days.
Budget changed: False; baseline changed: False.

### Milestone source details

| Milestone | Baseline finish | Forecast finish | Actual finish | Progress | Dependencies |
| --- | --- | --- | --- | --- | --- |
| T1 — Inputs reviewed | 2026-10-15 | 2026-10-18 | 2026-10-18 | 100% | None |
| T2 — Design package ready | 2026-10-28 | 2026-11-09 | Not complete | 60% | T1 |
| T3 — Engineering review complete | 2026-11-10 | 2026-11-22 | Not complete | 0% | T2 |

### Open issue source details

| Issue | Owner | Due date | Severity | Category |
| --- | --- | --- | --- | --- |
| I1 — Scope decision awaiting client input | Sample scope owner | 2026-10-26 | high | scope |

### Cost analysis — draft

OFFLINE TEMPLATE: EAC USD 115000\.00 versus approved budget USD 100000\.00; positive overrun USD 15000\.00\. Remaining commitments are inside ETC\.

**Suggested action for review:** PM should review the remaining estimate, commitments, scope, and contingency basis\.

Evidence: P001\.eac, P001\.budget, P001\.overrun\_amount, P001\.cpi

### Schedule analysis — draft

OFFLINE TEMPLATE: Maximum milestone finish slip is 12 days; 1 milestone\(s\) are overdue and incomplete\.

**Suggested action for review:** PM should validate forecast finish dates and review outstanding dependencies; do not infer a new finish date from SPI\.

Evidence: P001\.max\_finish\_slip\_days, P001\.overdue\_milestones, P001\.spi

### Risk synthesis — draft

OFFLINE TEMPLATE: Configured status is RED; 1 open high-severity issue\(s\) and 1 overdue issue\(s\)\.

**Suggested action for review:** PM should examine cited cost/schedule evidence and assign owners to unresolved issues before deciding on an intervention\.

Evidence: P001\.rag, P001\.open\_high\_issues, P001\.overdue\_issues

### Executive briefing — draft

OFFLINE TEMPLATE: Substation expansion — synthetic is RED\. EAC USD 115000\.00; maximum milestone finish slip 12 days\.

**Suggested action for review:** PM should examine cited cost/schedule evidence and assign owners to unresolved issues before deciding on an intervention\.

Evidence: P001\.rag, P001\.eac, P001\.max\_finish\_slip\_days

## P002 — Transmission design — synthetic

Manager: Sample PM B; configured status: AMBER
EAC: $84,000.00; budget: $80,000.00; overrun: $4,000.00
Maximum finish slippage: 4 days; overdue milestones: 0
Open high-severity issues: 0; overdue open issues: 1

- AMBER: Forecast cost overrun meets the configured watch threshold\. [evidence: P002\.overrun\_percent]
- AMBER: Maximum milestone finish slip meets the configured watch threshold\. [evidence: P002\.max\_finish\_slip\_days]
- AMBER: At least one open issue is past its due date\. [evidence: P002\.overdue\_issues]

Change in EAC: $4,000.00; change in maximum slip: 3 days.
Budget changed: False; baseline changed: False.

### Milestone source details

| Milestone | Baseline finish | Forecast finish | Actual finish | Progress | Dependencies |
| --- | --- | --- | --- | --- | --- |
| T1 — Survey accepted | 2026-10-20 | 2026-10-19 | 2026-10-19 | 100% | None |
| T2 — Design review complete | 2026-11-01 | 2026-11-05 | Not complete | 55% | T1 |

### Open issue source details

| Issue | Owner | Due date | Severity | Category |
| --- | --- | --- | --- | --- |
| I1 — Approval package awaiting review | Sample approval owner | 2026-10-29 | medium | approval |

### Cost analysis — draft

OFFLINE TEMPLATE: EAC USD 84000\.00 versus approved budget USD 80000\.00; positive overrun USD 4000\.00\. Remaining commitments are inside ETC\.

**Suggested action for review:** PM should review the remaining estimate, commitments, scope, and contingency basis\.

Evidence: P002\.eac, P002\.budget, P002\.overrun\_amount, P002\.cpi

### Schedule analysis — draft

OFFLINE TEMPLATE: Maximum milestone finish slip is 4 days; 0 milestone\(s\) are overdue and incomplete\.

**Suggested action for review:** PM should validate forecast finish dates and review outstanding dependencies; do not infer a new finish date from SPI\.

Evidence: P002\.max\_finish\_slip\_days, P002\.overdue\_milestones, P002\.spi

### Risk synthesis — draft

OFFLINE TEMPLATE: Configured status is AMBER; 0 open high-severity issue\(s\) and 1 overdue issue\(s\)\.

**Suggested action for review:** PM should examine cited cost/schedule evidence and assign owners to unresolved issues before deciding on an intervention\.

Evidence: P002\.rag, P002\.open\_high\_issues, P002\.overdue\_issues

### Executive briefing — draft

OFFLINE TEMPLATE: Transmission design — synthetic is AMBER\. EAC USD 84000\.00; maximum milestone finish slip 4 days\.

**Suggested action for review:** PM should examine cited cost/schedule evidence and assign owners to unresolved issues before deciding on an intervention\.

Evidence: P002\.rag, P002\.eac, P002\.max\_finish\_slip\_days

## P003 — Hydro controls documentation — synthetic

Manager: Sample PM C; configured status: GREEN
EAC: $58,000.00; budget: $60,000.00; overrun: $0.00
Maximum finish slippage: 0 days; overdue milestones: 0
Open high-severity issues: 0; overdue open issues: 0

- No configured warning triggered. Review data completeness before relying on the status.

Change in EAC: $0.00; change in maximum slip: 0 days.
Budget changed: False; baseline changed: False.

### Milestone source details

| Milestone | Baseline finish | Forecast finish | Actual finish | Progress | Dependencies |
| --- | --- | --- | --- | --- | --- |
| T1 — Requirements accepted | 2026-10-21 | 2026-10-20 | 2026-10-20 | 100% | None |
| T2 — Documentation review | 2026-11-05 | 2026-11-05 | Not complete | 50% | T1 |

### Cost analysis — draft

OFFLINE TEMPLATE: EAC USD 58000\.00 versus approved budget USD 60000\.00; positive overrun USD 0\.00\. Remaining commitments are inside ETC\.

**Suggested action for review:** PM should confirm the estimate to complete and monitor future cost changes\.

Evidence: P003\.eac, P003\.budget, P003\.overrun\_amount, P003\.cpi

### Schedule analysis — draft

OFFLINE TEMPLATE: Maximum milestone finish slip is 0 days; 0 milestone\(s\) are overdue and incomplete\.

**Suggested action for review:** PM should validate forecast finish dates and review outstanding dependencies; do not infer a new finish date from SPI\.

Evidence: P003\.max\_finish\_slip\_days, P003\.overdue\_milestones, P003\.spi

### Risk synthesis — draft

OFFLINE TEMPLATE: Configured status is GREEN; 0 open high-severity issue\(s\) and 0 overdue issue\(s\)\.

**Suggested action for review:** PM should examine cited cost/schedule evidence and assign owners to unresolved issues before deciding on an intervention\.

Evidence: P003\.rag, P003\.open\_high\_issues, P003\.overdue\_issues

### Executive briefing — draft

OFFLINE TEMPLATE: Hydro controls documentation — synthetic is GREEN\. EAC USD 58000\.00; maximum milestone finish slip 0 days\.

**Suggested action for review:** PM should examine cited cost/schedule evidence and assign owners to unresolved issues before deciding on an intervention\.

Evidence: P003\.rag, P003\.eac, P003\.max\_finish\_slip\_days

## Data quality and comparison warnings

- Risk coverage is limited to supplied cost, finish milestones, and issue data; green is not a safety or completion guarantee\.

## Assumptions and limits

- Synthetic pilot data; outputs require project manager review\.
- EAC = actual cost \+ estimate to complete\. Remaining commitments are already inside ETC\.
- Finish dates come from project-team inputs; SPI is not used to predict a finish date\.
- Green means no configured warning triggered\. It does not establish safety, completeness, or compliance\.
- Undefined ratios are shown as N/A; unavailable comparisons are not invented\.
- Agent text is an unverified draft\. Evidence references establish traceability, not factual correctness\.
- Cost analysis: Offline rule/template output, not a model-generated forecast\.
- Cost analysis: EAC uses the project team estimate to complete; validate that estimate\.
- Schedule analysis: Offline rule/template output, not a schedule simulation\.
- Schedule analysis: Finish forecasts come from inputs; resource calendars are not modeled\.
- Risk synthesis: Offline checklist output; RAG means configured rule results only\.
- Risk synthesis: Risk correlations, probabilities, and causal effects are not estimated\.
- Executive briefing: Offline executive template; project manager review remains required\.
- Executive briefing: No budgets, dates, approvals, or project systems are changed\.

## Evidence index

| Evidence ID | Project | Metric | Value | Source |
| --- | --- | --- | --- | --- |
| P001\.budget | P001 | budget | 100000\.00 | $\.current\.projects\[0\]\.approved\_budget |
| P001\.actual\_cost | P001 | actual\_cost | 60000\.00 | $\.current\.projects\[0\]\.actual\_cost |
| P001\.estimate\_to\_complete | P001 | estimate\_to\_complete | 55000\.00 | $\.current\.projects\[0\]\.estimate\_to\_complete |
| P001\.remaining\_committed\_cost | P001 | remaining\_committed\_cost | 30000\.00 | $\.current\.projects\[0\]\.remaining\_committed\_cost \(included in ETC\) |
| P001\.eac | P001 | eac | 115000\.00 | $\.current\.projects\[0\]\.actual\_cost \+ $\.current\.projects\[0\]\.estimate\_to\_complete |
| P001\.variance\_at\_completion | P001 | variance\_at\_completion | -15000\.00 | approved\_budget - \(actual\_cost \+ estimate\_to\_complete\) |
| P001\.overrun\_amount | P001 | overrun\_amount | 15000\.00 | max\(actual\_cost \+ estimate\_to\_complete - approved\_budget, 0\) |
| P001\.overrun\_percent | P001 | overrun\_percent | 15\.00 | 100 \* max\(EAC - approved\_budget, 0\) / approved\_budget |
| P001\.cpi | P001 | cpi | 0\.8333 | earned\_value / actual\_cost; undefined when actual\_cost = 0 |
| P001\.spi | P001 | spi | 0\.8333 | earned\_value / planned\_value; undefined when planned\_value = 0 |
| P001\.max\_finish\_slip\_days | P001 | max\_finish\_slip\_days | 12 | max\(0, \(actual\_finish or forecast\_finish\) - baseline\_finish\) over $\.current\.projects\[0\]\.tasks |
| P001\.overdue\_milestones | P001 | overdue\_milestones | 1 | count incomplete $\.current\.projects\[0\]\.tasks with baseline\_finish &lt; $\.current\.as\_of |
| P001\.open\_high\_issues | P001 | open\_high\_issues | 1 | count $\.current\.projects\[0\]\.issues where status=open and severity=high |
| P001\.overdue\_issues | P001 | overdue\_issues | 1 | count $\.current\.projects\[0\]\.issues where status=open and due\_date &lt; $\.current\.as\_of |
| P001\.earned\_value | P001 | earned\_value | 50000\.00 | $\.current\.projects\[0\]\.earned\_value |
| P001\.planned\_value | P001 | planned\_value | 60000\.00 | $\.current\.projects\[0\]\.planned\_value |
| P001\.rag | P001 | rag | red | highest configured flag severity; green if no flags |
| P002\.budget | P002 | budget | 80000\.00 | $\.current\.projects\[1\]\.approved\_budget |
| P002\.actual\_cost | P002 | actual\_cost | 42000\.00 | $\.current\.projects\[1\]\.actual\_cost |
| P002\.estimate\_to\_complete | P002 | estimate\_to\_complete | 42000\.00 | $\.current\.projects\[1\]\.estimate\_to\_complete |
| P002\.remaining\_committed\_cost | P002 | remaining\_committed\_cost | 18000\.00 | $\.current\.projects\[1\]\.remaining\_committed\_cost \(included in ETC\) |
| P002\.eac | P002 | eac | 84000\.00 | $\.current\.projects\[1\]\.actual\_cost \+ $\.current\.projects\[1\]\.estimate\_to\_complete |
| P002\.variance\_at\_completion | P002 | variance\_at\_completion | -4000\.00 | approved\_budget - \(actual\_cost \+ estimate\_to\_complete\) |
| P002\.overrun\_amount | P002 | overrun\_amount | 4000\.00 | max\(actual\_cost \+ estimate\_to\_complete - approved\_budget, 0\) |
| P002\.overrun\_percent | P002 | overrun\_percent | 5\.00 | 100 \* max\(EAC - approved\_budget, 0\) / approved\_budget |
| P002\.cpi | P002 | cpi | 0\.9524 | earned\_value / actual\_cost; undefined when actual\_cost = 0 |
| P002\.spi | P002 | spi | 1\.0000 | earned\_value / planned\_value; undefined when planned\_value = 0 |
| P002\.max\_finish\_slip\_days | P002 | max\_finish\_slip\_days | 4 | max\(0, \(actual\_finish or forecast\_finish\) - baseline\_finish\) over $\.current\.projects\[1\]\.tasks |
| P002\.overdue\_milestones | P002 | overdue\_milestones | 0 | count incomplete $\.current\.projects\[1\]\.tasks with baseline\_finish &lt; $\.current\.as\_of |
| P002\.open\_high\_issues | P002 | open\_high\_issues | 0 | count $\.current\.projects\[1\]\.issues where status=open and severity=high |
| P002\.overdue\_issues | P002 | overdue\_issues | 1 | count $\.current\.projects\[1\]\.issues where status=open and due\_date &lt; $\.current\.as\_of |
| P002\.earned\_value | P002 | earned\_value | 40000\.00 | $\.current\.projects\[1\]\.earned\_value |
| P002\.planned\_value | P002 | planned\_value | 40000\.00 | $\.current\.projects\[1\]\.planned\_value |
| P002\.rag | P002 | rag | amber | highest configured flag severity; green if no flags |
| P003\.budget | P003 | budget | 60000\.00 | $\.current\.projects\[2\]\.approved\_budget |
| P003\.actual\_cost | P003 | actual\_cost | 30000\.00 | $\.current\.projects\[2\]\.actual\_cost |
| P003\.estimate\_to\_complete | P003 | estimate\_to\_complete | 28000\.00 | $\.current\.projects\[2\]\.estimate\_to\_complete |
| P003\.remaining\_committed\_cost | P003 | remaining\_committed\_cost | 12000\.00 | $\.current\.projects\[2\]\.remaining\_committed\_cost \(included in ETC\) |
| P003\.eac | P003 | eac | 58000\.00 | $\.current\.projects\[2\]\.actual\_cost \+ $\.current\.projects\[2\]\.estimate\_to\_complete |
| P003\.variance\_at\_completion | P003 | variance\_at\_completion | 2000\.00 | approved\_budget - \(actual\_cost \+ estimate\_to\_complete\) |
| P003\.overrun\_amount | P003 | overrun\_amount | 0\.00 | max\(actual\_cost \+ estimate\_to\_complete - approved\_budget, 0\) |
| P003\.overrun\_percent | P003 | overrun\_percent | 0\.00 | 100 \* max\(EAC - approved\_budget, 0\) / approved\_budget |
| P003\.cpi | P003 | cpi | 1\.0667 | earned\_value / actual\_cost; undefined when actual\_cost = 0 |
| P003\.spi | P003 | spi | 1\.0667 | earned\_value / planned\_value; undefined when planned\_value = 0 |
| P003\.max\_finish\_slip\_days | P003 | max\_finish\_slip\_days | 0 | max\(0, \(actual\_finish or forecast\_finish\) - baseline\_finish\) over $\.current\.projects\[2\]\.tasks |
| P003\.overdue\_milestones | P003 | overdue\_milestones | 0 | count incomplete $\.current\.projects\[2\]\.tasks with baseline\_finish &lt; $\.current\.as\_of |
| P003\.open\_high\_issues | P003 | open\_high\_issues | 0 | count $\.current\.projects\[2\]\.issues where status=open and severity=high |
| P003\.overdue\_issues | P003 | overdue\_issues | 0 | count $\.current\.projects\[2\]\.issues where status=open and due\_date &lt; $\.current\.as\_of |
| P003\.earned\_value | P003 | earned\_value | 32000\.00 | $\.current\.projects\[2\]\.earned\_value |
| P003\.planned\_value | P003 | planned\_value | 30000\.00 | $\.current\.projects\[2\]\.planned\_value |
| P003\.rag | P003 | rag | green | highest configured flag severity; green if no flags |

## Run provenance

- solution\_version: 0\.1\.0
- code\_sha256: da2f147d4c22f07a282ea103e3619dadc847d2c01cf26a178c4098c1c2cc9921
- input\_sha256: 9be3177ff5f766a0c5e3daeade181f47d6ed2781de6586bbb107df99e9cf15f8
- generated\_utc: 2026-10-30T17:48:51\.424229\+00:00
- mode: offline
- model: Not supplied
- input\_filename: sample\_portfolio\.json
