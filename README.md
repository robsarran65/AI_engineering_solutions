# AI Engineering Solutions

Commented Python examples for engineering workflows, starting with a prototype aligned with Mesa Associates' public engineering services. This is an independent learning project, not an official Mesa product.

## Example 1: Engineering Studies & System Analysis

See [the detailed instructions](examples/01_engineering_studies/README.md) and [commented Python code](examples/01_engineering_studies/mesa_workflow.py).

The example validates a synthetic asset snapshot, screens three load-growth assumptions, and ranks findings for engineer review. An optional OpenAI call drafts an explanation. Offline mode uses deterministic Python workers, not autonomous AI agents.

Requires Python 3.10 or later. From the repository root:

```powershell
cd examples/01_engineering_studies
python mesa_workflow.py --stage intake --output intake_report.json
python mesa_workflow.py --output mesa_report.json
python -m unittest -v
```

No third-party packages are required for offline mode. See the example README for optional AI setup. The sample is not a validated power-system simulation or an operational control tool.
