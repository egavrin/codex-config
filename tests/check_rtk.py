#!/usr/bin/env python3
"""Black-box checks for pinned RTK hooks. Save repeatable evidence outside the repository."""
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path.home() / '.local/bin/rtk'
EXCLUDED = [
    'cat source.py', 'head -n 10 source.py', 'tail source.py', 'rg target .',
    'grep target source.py', 'find . -name test.py', 'sed -n 1,20p source.py',
    'git diff', 'git diff --cached', 'git show HEAD', 'git status --porcelain=v1',
    'git log --format=%H', 'git ls-files -z', 'git add source.py',
    'git -C /tmp commit -m test', 'git push origin main', 'git reset --hard',
    'git rm source.py', 'git mv source.py target.py', 'git notes add -m note',
    'docker inspect container', 'kubectl get pods -o json', 'aws s3api list-buckets --output json',
    'git status --short',
    'git checkout main', 'git clean -fd', 'gh pr view 1 --json title',
    'cargo metadata --format-version 1', 'cargo test --message-format=json',
    'npm list --json', 'curl https://example.invalid', 'jq . packet.json',
    'python3 /Users/egavrin/.codex/skills/claude-collab/scripts/bridge.py preflight --mode review --packet packet.json',
    'python3 /Users/egavrin/.codex/skills/claude-collab/scripts/bridge.py run --mode review --packet packet.json',
    'RTK_DISABLED=1 git status',
]

def main():
    evidence = Path(tempfile.mkdtemp(prefix='rtk-check-'))
    evidence.chmod(0o700)
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'command': 'python3.12 tests/check_rtk.py', 'cases': []}
    env = dict(os.environ, RTK_DB_PATH=str(evidence / 'history.db'), RTK_RECALL_DB=str(evidence / 'recall.db'))
    def run(args, stdin=None):
        result = subprocess.run(args, input=stdin, text=True, capture_output=True, env=env, cwd=evidence)
        return result
    try:
        assert BINARY.exists(), 'pinned RTK binary missing'
        report['binary_sha256'] = hashlib.sha256(BINARY.read_bytes()).hexdigest()
        assert run([str(BINARY), '--version']).stdout.strip() == 'rtk 1.1.0'
        config = tomllib.loads((Path.home() / 'Library/Application Support/rtk/config.toml').read_text())
        assert config['telemetry']['enabled'] is False
        assert config['awareness']['level'] == 'high'
        for host in ('codex', 'claude'):
            for command in ['git status', *EXCLUDED]:
                payload = {'hook_event_name': 'PreToolUse', 'permission_mode': 'default',
                           'tool_name': 'Bash', 'tool_input': {'command': command}}
                result = run([str(BINARY), 'hook', host], json.dumps(payload))
                expected = 'rewritten' if command == 'git status' else 'raw'
                case = {'command': [str(BINARY), 'hook', host], 'input': payload,
                        'expected': expected, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
                report['cases'].append(case)
                assert result.returncode == 0, case
                if expected == 'raw':
                    assert not result.stdout.strip(), case
                else:
                    output = json.loads(result.stdout)['hookSpecificOutput']
                    assert output['updatedInput']['command'] == 'rtk git status', case
                    if host == 'codex':
                        assert output['permissionDecision'] == 'allow', case
        raw = 'line one\nline two\n'
        result = run([str(BINARY), 'bypass', 'printf', raw])
        report['cases'].append({'command': ['rtk', 'bypass', 'printf', raw], 'expected': raw, 'stdout': result.stdout, 'exit': result.returncode})
        assert result.stdout == raw and result.returncode == 0
        script = evidence / 'failure.sh'
        script.write_text('printf "ordinary detail\\n"; ' * 40 + 'printf "ERROR: deterministic failure\\n"; exit 7\n')
        result = run([str(BINARY), 'err', 'sh', str(script)])
        report['cases'].append({'command': ['rtk', 'err', 'sh', 'failure.sh'],
                                'input': script.read_text(), 'expected_exit': 7,
                                'expected_diagnostic': 'ERROR: deterministic failure',
                                'stdout': result.stdout, 'stderr': result.stderr, 'exit': result.returncode})
        assert result.returncode == 7 and 'ERROR: deterministic failure' in result.stdout + result.stderr
        recalled = run([str(BINARY), 'recall', '--list'])
        report['cases'].append({'command': ['rtk', 'recall', '--list'], 'exit': recalled.returncode, 'stdout': recalled.stdout, 'stderr': recalled.stderr})
        assert recalled.returncode == 0
        # The failure fixture must keep a raw recovery record when the filter elides a line.
        match = re.search(r'rtk recall ([a-f0-9]+)', result.stdout + result.stderr)
        assert match, 'missing raw recovery hint for filtered failure'
        recovered = run([str(BINARY), 'recall', match.group(1), '--full'])
        report['cases'].append({'command': ['rtk', 'recall', match.group(1), '--full'], 'stdout': recovered.stdout, 'stderr': recovered.stderr, 'exit': recovered.returncode})
        assert recovered.returncode == 0
        assert 'ordinary detail' in recovered.stdout and 'ERROR: deterministic failure' in recovered.stdout
        report['status'] = 'PASS'
    except Exception as exc:
        report['status'] = 'FAIL'
        report['failure'] = str(exc)
        raise
    finally:
        (evidence / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(evidence / 'report.json')

if __name__ == '__main__':
    main()
