#!/usr/bin/env python3
"""Black-box Slopo workflow checks with synthetic local embeddings."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import threading

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--slopo', default=shutil.which('slopo'))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=False, mode=0o700)
root = args.output.resolve()
repo = root / 'repository'
repo.mkdir()
records = []
requests = []
env = {key: os.environ[key] for key in ('HOME', 'PATH', 'TMPDIR') if key in os.environ}
env.update(PYTHON_DOTENV_DISABLED='1', LITELLM_LOCAL_MODEL_COST_MAP='True',
           NO_PROXY='127.0.0.1,localhost', GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')

class Embeddings(BaseHTTPRequestHandler):
    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        requests.append({'path': self.path, 'model': data.get('model'),
                         'authorization': bool(self.headers.get('Authorization'))})
        values = data.get('input', data.get('prompt', ''))
        values = values if isinstance(values, list) else [values]
        vectors = []
        for value in values:
            vector = [0.0] * 768
            vector[int(hashlib.sha256(value.encode()).hexdigest(), 16) % 768] = 1.0
            vectors.append(vector)
        response = {'embedding': vectors[0], 'embeddings': vectors,
                    'model': data.get('model'), 'prompt_eval_count': 1}
        body = json.dumps(response).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *_):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), Embeddings)
threading.Thread(target=server.serve_forever, daemon=True).start()

def run(command, cwd=repo, expected=0, contains=None):
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=120)
    text = result.stdout + result.stderr
    item = {'command': command, 'cwd': str(cwd), 'expected_exit': expected,
            'observed_exit': result.returncode, 'expected_text': contains, 'output': text}
    records.append(item)
    (root / 'commands.json').write_text(json.dumps(records, indent=2))
    assert result.returncode == expected, item
    if contains is not None:
        assert contains in text, item
    return result.stdout.strip()

def git(*command, cwd=repo):
    return run(['git', *command], cwd=cwd)

def configure(source):
    state = Path(git('rev-parse', '--absolute-git-dir', cwd=source)) / 'slopo'
    state.mkdir(mode=0o700)
    template = (Path(__file__).resolve().parents[1] / 'assets/config.yaml').read_text()
    config = template.replace('"__SOURCE_ROOT__"', json.dumps(str(source)))
    for name in ('slopo.db', 'reports', 'ignore.txt', 'agent.log'):
        config = config.replace('"__STATE_DIR__/' + name + '"', json.dumps(str(state / name)))
    # Test transport only: production configuration remains fixed at port 11434.
    config = config.replace('http://127.0.0.1:11434', f'http://127.0.0.1:{server.server_port}')
    path = state / 'config.yaml'
    path.write_text(config)
    return path, state

def slopo(*command, cfg=None, cwd=repo, expected=0, contains=None):
    return run([args.slopo, '--config', str(cfg or config), *command], cwd, expected, contains)

code = '''def calculate(values):
    result = []
    for value in values:
        normalized = value * 2
        if normalized > 10:
            result.append(normalized + 5)
        else:
            result.append(normalized - 3)
    return sorted(result)
'''
try:
    run([args.slopo, '--version'])
    git('init', '-q')
    git('config', 'user.email', 'fixture@example.invalid')
    git('config', 'user.name', 'Slopo fixture')
    (repo / 'original.py').write_text(code)
    (repo / '.env').write_text('SLOPO_EMBEDDING_API_KEY=fixture-dotenv-must-not-load\n')
    config, state = configure(repo)
    slopo('show-config', contains='embedding_api_key: <unset>')
    slopo('agent-review', '--config-version=1', expected=1, contains='No data in database')
    excluded = ['.git/hidden.py', 'node_modules/pkg/a.py', '.venv/a.py', 'dist/a.py',
                'build/a.py', '__pycache__/a.py', 'graphify-out/a.py',
                '.claude/worktrees/nested/a.py', '.codex/worktrees/nested/a.py',
                'credentials/a.py', '.aws/a.py']
    for name in excluded:
        file = repo / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(code)
    (repo / 'tests').mkdir()
    (repo / 'tests/test_sample.py').write_text(code.replace('calculate', 'test_sample').replace('value * 2', 'value * 19'))
    slopo('index')
    with sqlite3.connect(state / 'slopo.db') as db:
        indexed = {row[0] for row in db.execute('select path from files')}
    assert indexed == {'original.py', 'tests/test_sample.py'}, indexed
    slopo('embed')
    empty = git('hash-object', '-t', 'tree', '/dev/null')
    slopo('agent-review', '--config-version=1', '--base', empty, contains='No duplicates found')
    git('add', 'original.py', 'tests/test_sample.py')
    git('commit', '-qm', 'Initial fixture')
    first = git('rev-parse', 'HEAD')
    slopo('agent-review', '--config-version=1', '--base', empty)
    slopo('agent-review', '--config-version=1', '--base', 'HEAD', contains='No duplicates found')
    (repo / 'README.md').write_text('Documentation only.\n')
    slopo('agent-review', '--config-version=1', '--base', 'HEAD', contains='No duplicates found')
    git('add', 'README.md')
    git('commit', '-qm', 'Documentation fixture')
    assert git('rev-parse', 'HEAD^') == first
    slopo('agent-review', '--config-version=1', '--base', first, contains='No duplicates found')
    (repo / 'copy.py').write_text(code.replace('calculate', 'copied'))
    duplicate = slopo('agent-review', '--config-version=1', '--base', 'HEAD')
    assert 'copy.py' in duplicate and 'original.py' in duplicate and '*' in duplicate, duplicate
    slopo('agent-review', '--config-version=999', expected=1, contains='Configuration for coding agent is out of date')
    slopo('agent-review', '--config-version=1', '--base', 'missing-base', expected=1, contains='Git command failed')
    wrong = state / 'wrong.yaml'
    wrong.write_text(config.read_text().replace('embedding_dimensions: 768', 'embedding_dimensions: 384'))
    slopo('agent-review', '--config-version=1', cfg=wrong, expected=1, contains='Configuration mismatch')
    worktree = root / 'linked'
    git('worktree', 'add', '-q', '-b', 'linked-fixture', str(worktree))
    linked_config, linked_state = configure(worktree)
    assert linked_state != state and linked_state.parent.name == 'linked'
    slopo('index', cfg=linked_config, cwd=worktree)
    slopo('embed', cfg=linked_config, cwd=worktree)
    slopo('agent-review', '--config-version=1', '--base', 'HEAD', cfg=linked_config,
          cwd=worktree, contains='No duplicates found')
    many = '\n'.join(code.replace('calculate', f'calculate_{i}').replace('value * 2', f'value * {i + 100}') for i in range(1002))
    (worktree / 'pending.py').write_text(many)
    slopo('index', cfg=linked_config, cwd=worktree)
    slopo('agent-review', '--config-version=1', cfg=linked_config, cwd=worktree,
          expected=1, contains='Too many code units to embed')
    unavailable = linked_state / 'unavailable.yaml'
    unavailable.write_text(linked_config.read_text().replace(
        f'http://127.0.0.1:{server.server_port}', 'http://127.0.0.1:1'))
    slopo('embed', cfg=unavailable, cwd=worktree, expected=1)
    slopo('embed', cfg=linked_config, cwd=worktree)
    with sqlite3.connect(linked_state / 'slopo.db') as db:
        pending = db.execute('select count(*) from code_units c left join embeddings e '
                             'on c.body_hash=e.body_hash where e.body_hash is null').fetchone()[0]
    assert pending == 0, pending
    assert requests and not any(item['authorization'] for item in requests), requests
    (root / 'requests.json').write_text(json.dumps(requests, indent=2))
    (root / 'result.json').write_text(json.dumps({'status': 'PASS', 'upstream_revision':
        'cb63e8ee4c27d40f47999c96e75b18bd5816b249', 'fixture_revision': git('rev-parse', 'HEAD'),
        'checks': len(records), 'indexed_paths': sorted(indexed), 'endpoint':
        f'http://127.0.0.1:{server.server_port}', 'limit': 'Synthetic embeddings, no commit-policy enforcement.'}, indent=2))
    print(f'PASS: {len(records)} commands; evidence: {root}')
finally:
    server.shutdown()
    server.server_close()
