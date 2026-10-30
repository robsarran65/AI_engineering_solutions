"""Run the Mesa-aligned PMO early-warning pilot.

First run: python pmo.py --output outputs
AI narrative: python pmo.py --mode ai --model YOUR_MODEL_ID --output outputs_ai
This synthetic teaching pilot does not change any operational system.
"""

# Standard-library modules keep offline setup simple: no package install needed.
import argparse  # Translate terminal flags into Python values.
import hashlib  # Fingerprint the exact input bytes for an auditable run.
import json  # Convert between JSON text and Python dictionaries.
import os  # Read the optional model name from an environment variable.
from datetime import datetime, timezone  # Record when the program actually ran.
from pathlib import Path  # Work with Windows and Linux paths using the same code.

from metrics import analyze_portfolio  # Trusted validation and numerical calculations.
from agents import run_agents  # Four specialist roles with controlled handoffs.
from reporting import write_reports  # Local JSON, Markdown, and HTML deliverables.


MAX_INPUT_BYTES = 5 * 1024 * 1024  # Five MiB is the input limit for this pilot.
OUTPUT_NAMES = ('report.json', 'executive_brief.md', 'dashboard.html')
SOLUTION_VERSION = '0.1.0'


def _unique_object(pairs):
    """JSON otherwise silently accepts repeated keys and keeps only the last value."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def _reject_constant(value):
    """Reject non-standard JSON NaN/Infinity values before they reach calculations."""
    raise ValueError(f'Unsupported JSON numeric constant: {value}')


def read_input(path: Path) -> tuple[dict, bytes]:
    """Read bounded bytes once; analysis and the input fingerprint use that same read."""
    # Reading one byte beyond the limit detects oversize files without loading them all.
    with path.open('rb') as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError('Input exceeds the 5 MiB limit')
    data = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=_unique_object,
                      parse_constant=_reject_constant)
    return data, raw  # A tuple hands both parsed evidence and original bytes to the caller.


def main(argv=None) -> int:
    """Coordinate input -> metrics -> specialist agents -> reviewable reports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path,
                        default=Path(__file__).parent / 'data' / 'sample_portfolio.json')
    parser.add_argument('--output', type=Path, default=Path('outputs'))
    parser.add_argument('--mode', choices=('offline', 'ai'), default='offline')
    parser.add_argument('--model', default=os.environ.get('OPENAI_MODEL'))
    parser.add_argument('--overwrite', action='store_true', help='Replace this run folder\'s three reports')
    parser.add_argument('--validate-only', action='store_true', help='Check data and calculate metrics without writing reports or calling AI')
    args = parser.parse_args(argv)

    try:
        if not args.validate_only:
            for name in OUTPUT_NAMES:
                target = args.output / name
                if target.resolve() == args.input.resolve():
                    raise ValueError('Output paths must not replace the input file')
                if target.exists() and not args.overwrite:
                    raise ValueError('Output exists; choose another folder or use --overwrite')
        data, raw = read_input(args.input)
        # Validation runs before any optional API call or file writing.
        analysis = analyze_portfolio(data)
        if args.validate_only:
            print(f"Valid synthetic portfolio: {analysis['portfolio']['project_count']} projects as of {analysis['as_of']}")
            return 0
        # Fingerprint the calculation, agent, rendering, and CLI source together.
        source_hash = hashlib.sha256()
        for module_name in ('pmo.py', 'metrics.py', 'agents.py', 'reporting.py'):
            source_hash.update(module_name.encode('utf-8'))
            source_hash.update(Path(__file__).with_name(module_name).read_bytes())
        provenance = {
            'solution_version': SOLUTION_VERSION,
            'code_sha256': source_hash.hexdigest(),
            'input_sha256': hashlib.sha256(raw).hexdigest(),
            'generated_utc': datetime.now(timezone.utc).isoformat(),
            'mode': args.mode,
            'model': args.model if args.mode == 'ai' else None,
            'input_filename': args.input.name,  # No local absolute path enters the report.
        }
        try:
            narratives = run_agents(analysis, mode=args.mode, model=args.model)
        except Exception as exc:
            # API/provider messages can include private details. Save only a safe type.
            # Retain trusted metrics, never partial narratives from a failed agent chain.
            if args.mode != 'ai':
                raise
            failure = {'status': 'FAILED', 'error_type': type(exc).__name__,
                       'message': 'AI narrative generation failed. Baseline metrics are retained; no completed AI briefing is available.'}
            write_reports(analysis, None, args.output, provenance, failure=failure)
            print('AI workflow failed. Baseline reports saved; check local model/key/package setup. No completed AI draft.')
            return 1  # A nonzero exit code lets scripts detect the failed AI run.
        write_reports(analysis, narratives, args.output, provenance)
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(1, f'Run stopped: {exc}\n')
    print(f"Saved {args.output.resolve()} — {analysis['status']}")
    print(f"Open {args.output / 'dashboard.html'} to review the portfolio.")
    return 0


# When imported by tests, definitions load without starting a command-line run.
if __name__ == '__main__':
    raise SystemExit(main())
