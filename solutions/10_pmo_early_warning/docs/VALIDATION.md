# Validation record — version 0.1.0

Prepared October 30, 2026. This is a synthetic, local pilot. It has not been
accepted by Mesa, evaluated on Mesa project data, or deployed to a production system.

## Completed checks

- Thirty standard-library unit/integration tests pass with synthetic fixtures
  and mocked model backends. Run `python -m unittest discover -s tests -v`.
- Confirmed sample output: budget $240,000; actual cost $132,000; EAC $257,000;
  positive project overruns $19,000; net VAC −$17,000; one red, one amber, one green.
- Covered cost formulas, weighted CPI/SPI, raw-precision threshold decisions,
  zero denominators, dated snapshots, baseline changes, invalid schemas/numbers,
  dependencies, model evidence references, and copied-data boundaries.
- Covered concurrent cost/schedule execution, later role handoffs, malformed
  model responses, AI context limits, overwrite protection, failure baseline
  preservation, and HTML text escaping.
- Ran the report's JavaScript in a small DOM harness: status filtering, project
  search, synchronized row/card visibility, empty state, and print dispatch passed.
  This harness is an additional build check, not browser rendering validation.
- Generated the committed `sample_outputs` using the actual offline CLI.

Every run records exact input-byte and source-code fingerprints, a solution
version, and generation time. The source fingerprint covers `pmo.py`, `metrics.py`,
`agents.py`, and `reporting.py`; it does not cover documentation or dependency
versions. Retain the source input alongside the reports for reproducibility.

## Not yet verified

- Live API responses, model factual consistency, narrative quality, actual
  token cost, and model-specific latency. No API credentials were supplied.
- Desktop/mobile browser layout and print rendering. A browser executable was
  unavailable in the build environment. Check the generated report in the team's
  supported Chrome/Edge versions before presenting it as a visually accepted UI.
- Representative operational data, source integrations, production security,
  reliability, accessibility, or multiuser behavior.

## Product-team acceptance exercise

1. Follow README setup on a clean workstation and run the offline demo.
2. Check the sample values above against the dashboard and executive brief.
3. In the browser, filter to Red, search for P003, clear filters, jump to project
   cards, and inspect milestone/issue rows and evidence values.
4. Review responsive layout and print preview; confirm no data is clipped or
   confusing at the team's supported desktop/mobile sizes.
5. Reconcile additional approved reference cases with PM/finance SMEs.
6. For approved AI evaluation, use the chosen model on a synthetic evaluation
   set and score material omissions, incorrect assertions, and action usefulness.
7. Resolve findings and obtain the agreed pilot approvals before using real data.

Code-enforced synthetic-only validation remains in place. Real-data processing
requires an intentional product/security change and a corresponding review;
changing a file label does not make real data synthetic.
