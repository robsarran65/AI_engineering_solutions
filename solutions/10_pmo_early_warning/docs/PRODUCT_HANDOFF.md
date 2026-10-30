# Product-team handoff: PMO early-warning pilot

## Problem and proposed use

PMs need a repeatable way to review cost, forecast-finish, and unresolved-issue
signals across a portfolio. This pilot accepts normalized snapshots and creates
a reviewable evidence package. It complements existing reporting during discovery;
replacement of any dashboard or project system is not assumed.

Public alignment: Mesa's PMO page describes planned/actual/ETC reporting,
portfolio metrics, and EPI dashboards. Retrieved October 30, 2026:
https://www.mesainc.com/project-management-organization/

**In scope:** synthetic snapshots, configured thresholds, transparent metrics,
prior-snapshot comparison, four narrative roles, local dashboard/brief, evidence
references, and run provenance. **Out of scope:** live integrations, predictive
models, automated approvals/writeback, production identity/access controls,
real-time operations, and claims of regulatory certification.

## Ownership proposal — confirm with the pilot sponsor

| Work | Accountable | Responsible | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Pilot objectives and acceptance | PMO sponsor | Product owner | PMs, finance | Delivery team |
| Data definitions and approved exports | Data owner | Integration engineer | PMs, finance, security | Product owner |
| Metric and threshold validation | PMO methodology owner | PM/finance SMEs | Product owner | Developers/QA |
| Code, tests, packaging | Engineering lead | Developers/QA | Product owner | PMO sponsor |
| Narrative evaluation | PMO methodology owner | PM reviewers | AI engineer | Product owner |
| Real-data/hosting approval | Designated risk/security owner | Security/data teams | Legal, sponsor | Delivery team |
| Adoption decision | PMO sponsor | Product owner | All pilot stakeholders | Intended users |

These are proposed responsibilities, not named Mesa employees or established
Mesa governance. Each row has one accountable role.

## Pilot acceptance criteria

1. Supplied reference cases reproduce agreed EAC, VAC, CPI/SPI, slip, overdue
   counts, and threshold boundaries. Zero denominators remain explicit N/A.
2. Invalid schema, dates, dependencies, numbers, and duplicate identifiers stop
   before model calls. Changed budgets/baselines remain visible in comparisons.
3. Each role covers every current project exactly once and cites valid evidence
   belonging to that project. Numeric results remain identical across modes.
4. AI failure leaves baseline metrics available, labels failure, and discards
   partial role narratives. No output implies PM approval.
5. A fresh checkout runs offline with documented commands; generated HTML works
   locally without external resources; output protection prevents silent overwrite.
6. Reviewers score a representative, approved test set for factual consistency,
   missing material risks, and useful actions before any real-data rollout.

Automated tests cover bounded cases, not every portfolio or model behavior.
SME approval of definitions and acceptance evidence is still required.

## Evaluation and delivery backlog

| Priority | Item | Completion evidence |
| --- | --- | --- |
| P0 | Agree metric definitions, thresholds, reference cases | Signed pilot data/metric specification |
| P0 | Identify source exports, owners, classification, processing permissions | Approved access and data strategy |
| P0 | Compare deterministic outputs with SME calculations | Reconciled reference-case results |
| P0 | Evaluate four-role drafts and failure paths | Reviewer rubric, scored examples, defect log |
| P1 | Build one approved read-only export adapter | Mapping tests and lineage for every field |
| P1 | Design review workflow and user feedback capture | Usability findings and approved review steps |
| P1 | Establish logging, retention, secrets, cost and failure monitoring | Operating procedures and tested controls |
| P2 | Decide hosting, access roles, deployment and support model | Reviewed architecture and ownership |
| P2 | Consider approved integrations after pilot evidence | Scoped connector backlog; no assumed APIs |

Potential measures are **hypotheses to test**, not achieved results: time to create
a review brief, reviewer correction rate, missed-material-risk rate, evidence
coverage, and usefulness of recommended actions. Establish a manual baseline,
select a representative sample, and agree targets with the sponsor before testing.
Do not infer ROI from synthetic demonstration speed.

## Suggested rollout gates

Start with synthetic data and developer verification. Next, reconcile approved
reference cases with PM/finance SMEs. Only then consider a limited read-only pilot
using approved exports and processing controls. Production requires an explicit
hosting/security review, access policy, retention rules, monitoring, incident and
support ownership, recovery testing, model evaluation and change control.

Current gaps include authentication/authorization, multiuser isolation, managed
secrets, system integration, durable storage, scheduled refreshes, operational
monitoring, backup/recovery, accessibility validation, and representative data/model
evaluation. The current CLI/local report does not implement those capabilities.
