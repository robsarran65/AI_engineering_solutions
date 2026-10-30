# Ten-minute demo

Prepare in the solution folder. Use the synthetic sample only. Keep an earlier
output folder or select a new one so the overwrite guard is not a surprise.
Do not depend on a paid API call completing during the demo.

| Time | Action | Explain |
| --- | --- | --- |
| 0:00–1:00 | Introduce the portfolio-review problem | Pilot supports PM review; thresholds are configured signals, not predictions |
| 1:00–2:00 | Open `data/sample_portfolio.json` | Current/prior snapshots, cost inputs, milestone dates, issue status, policy |
| 2:00–3:00 | Run the offline command below | Calculations need no AI key or external packages |
| 3:00–5:00 | Open dashboard; filter and inspect a flagged project | Distinguish cost/finish/issue signals and follow evidence references |
| 5:00–6:00 | Inspect a trend and quality warnings | Changed budgets/baselines can affect apparent improvement |
| 6:00–7:00 | Open `report.json` and `executive_brief.md` | Structured source of truth versus draft interpretation |
| 7:00–8:00 | Show four-role architecture | Cost/schedule parallel, then risk, then executive; offline templates clearly labeled |
| 8:00–9:00 | Run tests or show a completed local test run | Demonstrate validation and failure handling, not production certification |
| 9:00–10:00 | Review product handoff | Agree data owner, reference cases, reviewer rubric, and pilot decision criteria |

```powershell
python pmo.py --input data/sample_portfolio.json --output outputs_demo
python -m unittest discover -s tests -v
```

For a rerun, choose a fresh output folder or intentionally add `--overwrite`.
Open `outputs_demo/dashboard.html` using Explorer or the browser's file-open menu.

## Expected results to point out

These results come from the supplied synthetic JSON and the implemented calculations:

- Portfolio: $240,000 budget, $257,000 EAC, $19,000 in positive project overruns;
  one red, one amber, one green project.
- P001: $115,000 EAC, 15% overrun, 12-day maximum finish slip, one open high issue.
  Cite `P001.eac`, `P001.overrun_percent`, `P001.max_finish_slip_days`, and
  `P001.open_high_issues`. Its EAC rose $10,000 and max slip rose 7 days versus
  October 23, with no budget/baseline change in this sample.
- P002: $84,000 EAC, 5% overrun, four-day slip, one overdue issue; amber.
- P003: $58,000 EAC against $60,000 budget, no positive finish slip or issue flags;
  green is a policy result, not a guarantee.

Net VAC is −$17,000 rather than −$19,000 because P003's projected $2,000 underrun
reduces the net variance. Show why netting can hide individual overrun exposure.
The sample's general risk-coverage warning is expected. Budget/baseline-change
warnings do not appear for these unchanged sample baselines; explain the rule
without pretending this sample demonstrates a changed baseline.

## Questions to ask the audience

- Which existing review decision should this package make easier?
- Are ETC and commitments defined consistently across the intended source systems?
- Which threshold policies and source forecasts are authoritative?
- Who reviews narrative errors and owns the go/no-go decision?

AI mode is optional. If showing an existing AI run, identify its mode and model
provenance and remind reviewers that evidence references do not prove every prose
claim. No partial failed-agent output should be presented as a completed review.
