#!/usr/bin/env python3
"""Black-box workflows. Run with --real to include the installed Graphify CLI."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SKILL = Path(__file__).resolve().parents[1]
LAUNCHER = SKILL / 'scripts/graphify_local.py'
FAKE = '''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
assert os.environ.get('GRAPHIFY_BACKEND') == 'none'
assert os.environ.get('GRAPHIFY_NO_AUTO_REFRESH') == '1'
assert not any(k.endswith('_API_KEY') for k in os.environ)
root = pathlib.Path.cwd()
if args[0] == 'extract':
    assert '--code-only' in args and '--incremental' not in args
    out = pathlib.Path(args[args.index('--out') + 1]) / 'graphify-out'
    out.mkdir(parents=True, exist_ok=True)
    mode = (root / 'mode.txt').read_text() if (root / 'mode.txt').exists() else ''
    if mode == 'fail':
        (out / 'graph.json').write_text('partial')
        sys.exit(9)
    if mode == 'malformed':
        (out / 'graph.json').write_text('{}')
        sys.exit(0)
    nodes = [{'id': p.stem, 'label': p.stem, 'source_file': p.name, 'source_location': '1'} for p in root.glob('*.py')]
    (out / 'graph.json').write_text(json.dumps({'nodes': nodes, 'links': []}))
else:
    graph = json.loads((root / 'graphify-out/graph.json').read_text())
    try:
        (root / 'query-side-effect').write_text('forbidden')
    except PermissionError:
        pass
    else:
        raise AssertionError('query writes were allowed')
    print(json.dumps(graph))
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true')
    parser.add_argument('--evidence', type=Path)
    options = parser.parse_args()
    evidence = options.evidence or Path(tempfile.mkdtemp(prefix='graphify-workflow-'))
    evidence.mkdir(parents=True, exist_ok=True)
    records = []
    with tempfile.TemporaryDirectory(prefix='graphify-fixtures-') as tmp:
        base = Path(tmp)
        fake = base / 'bin'
        fake.mkdir()
        cli = fake / 'graphify'
        cli.write_text(FAKE.replace('#!/usr/bin/env python3', '#!' + sys.executable))
        cli.chmod(0o700)
        env = dict(os.environ, PATH=str(fake) + os.pathsep + os.environ['PATH'],
                   XDG_CACHE_HOME=str(base / 'cache'), OPENAI_API_KEY='synthetic',
                   GEMINI_API_KEY='synthetic', GRAPHIFY_BACKEND='gemini', GRAPHIFY_FORCE='1')
        before_skill = (SKILL / 'SKILL.md').read_bytes()

        def project(name):
            root = base / name
            root.mkdir()
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'alpha.py').write_text('def alpha():\n    return beta()\n\ndef beta():\n    return 1\n')
            (root / '.gitignore').write_text('ignored.py\n')
            (root / 'ignored.py').write_text('def forbidden_ignored(): pass\n')
            (root / '.env').write_text('SECRET=synthetic\n')
            (root / '.git/info/exclude').write_text('# user entry\nkeep-me\n')
            return root

        def run(root, action='ensure', operands=(), code=0, readonly=False, environ=None):
            command = [sys.executable, str(LAUNCHER), action, '--root', str(root)]
            if readonly:
                command.append('--read-only')
            command += list(operands)
            result = subprocess.run(command, env=environ or env, text=True, capture_output=True)
            records.append({'command': command, 'expected_exit': code, 'observed_exit': result.returncode,
                            'stdout': result.stdout, 'stderr': result.stderr})
            assert result.returncode == code, records[-1]
            return result

        def snapshot(path):
            return {str(p.relative_to(path)): (p.stat().st_mtime_ns, p.stat().st_size)
                    for p in path.rglob('*') if p.is_file()}

        a, b = project('a'), project('b')
        run(a, readonly=True, code=2)
        assert not (base / 'cache').exists()
        # Both linked-worktree files and nested .git directories must stay outside the parent graph.
        worktrees = a / '.claude/worktrees'
        linked = worktrees / 'linked'
        linked.mkdir(parents=True)
        (linked / '.git').write_text('gitdir: /synthetic/worktree/metadata\n')
        (linked / 'nested.py').write_text('def excluded_worktree(): pass\n')
        clone = worktrees / 'clone'
        subprocess.run(['git', 'init', '-q', str(clone)], check=True)
        run(a)
        graph = a / 'graphify-out/graph.json'
        first = graph.stat().st_mtime_ns
        (linked / 'nested.py').write_text('def changed_worktree(): pass\n')
        (worktrees / 'another').mkdir()
        run(a, readonly=True)
        run(a)
        assert graph.stat().st_mtime_ns == first
        # Other nested projects still require a separate scope.
        other = a / 'vendor/other'
        subprocess.run(['git', 'init', '-q', str(other)], check=True)
        run(a, code=2)
        shutil.rmtree(other.parent)
        state = a / 'graphify-out/.local-state.json'
        previous = json.loads(state.read_text())
        previous['format'] = 1
        state.write_text(json.dumps(previous))
        run(a, readonly=True, code=2)
        run(a)
        assert json.loads(state.read_text())['format'] == 2
        before = snapshot(base)
        run(a, 'query', ['alpha'], readonly=True)
        run(a, 'path', ['alpha', 'beta'], readonly=True)
        run(a, 'explain', ['alpha'], readonly=True)
        run(a, readonly=True)
        assert snapshot(base) == before
        assert not (a / 'query-side-effect').exists()
        # Audit traps prove that rejected links do not open their targets.
        target = base / 'synthetic-credential.json'
        target.write_text('{"secret": "synthetic"}')
        trap = """import os, pathlib, runpy, sys
launcher, target = sys.argv[1:3]
sys.argv = sys.argv[3:]
def guard(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes)):
        if pathlib.Path(os.fsdecode(args[0])).resolve() == pathlib.Path(target).resolve():
            raise RuntimeError('SYNTHETIC_CREDENTIAL_TARGET_READ')
sys.addaudithook(guard)
runpy.run_path(launcher, run_name='__main__')
"""
        for name in ('.local-state.json', 'graph.json'):
            path = a / 'graphify-out' / name
            original = path.read_bytes()
            path.unlink()
            path.symlink_to(target)
            command = [sys.executable, '-B', '-c', trap, str(LAUNCHER), str(target),
                       str(LAUNCHER), 'query', '--root', str(a), '--read-only', 'alpha']
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            record = {'case': name + ' symlink', 'command': command, 'expected_exit': 2,
                      'observed_exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
                      'expected_target_read': False,
                      'observed_target_read': 'SYNTHETIC_CREDENTIAL_TARGET_READ' in result.stderr}
            records.append(record)
            (evidence / ('symlink-' + name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
            path.unlink()
            path.write_bytes(original)
            assert result.returncode == 2 and not record['observed_target_read'], record
        run(a, 'query', ['alpha'], readonly=True)
        (a / 'new.py').write_text('def new(): pass\n')
        run(a, 'query', ['new'], readonly=True, code=2)
        run(a)
        assert 'new.py' in run(a, 'query', ['new']).stdout
        (a / 'new.py').write_text('def changed(): pass\n')
        run(a, readonly=True, code=2)
        run(a)
        (a / 'new.py').unlink()
        run(a)
        assert 'new.py' not in graph.read_text()
        run(b)
        assert 'alpha.py' in run(b, 'query', ['alpha']).stdout
        good = graph.read_bytes()
        (a / 'mode.txt').write_text('fail')
        run(a, code=2)
        assert graph.read_bytes() == good
        (a / 'mode.txt').write_text('malformed')
        run(a, code=2)
        assert graph.read_bytes() == good
        (a / 'mode.txt').unlink()
        run(a)
        graph.write_text('{}')
        run(a, 'query', ['alpha'], code=2)
        graph.write_bytes(good)
        lock = next((base / 'cache/graphify-local/locks').glob('*.lock'))
        # Select the lock by its documented root digest.
        lock = lock.parent / (hashlib.sha256(str(a.resolve()).encode()).hexdigest() + '.lock')
        with lock.open('r') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            run(a, code=2)
            run(a, 'query', ['alpha'], readonly=True, code=2)
        run(Path.home(), code=2)
        run(Path('/'), code=2)
        run(base, code=2)
        assert '# user entry\nkeep-me\n' in (a / '.git/info/exclude').read_text()
        assert (a / '.gitignore').read_text() == 'ignored.py\n'
        assert not subprocess.check_output(['git', '-C', str(a), 'ls-files', '--others', '--exclude-standard', 'graphify-out'])
        if options.real:
            real = project('real')
            real_env = dict(env, PATH=os.environ['PATH'])
            subprocess.run(['git', '-C', str(real), '-c', 'user.name=Graphify Test',
                            '-c', 'user.email=graphify@example.invalid', 'commit',
                            '--allow-empty', '-qm', 'Fixture'], check=True)
            child = real / '.claude/worktrees/agent'
            subprocess.run(['git', '-C', str(real), 'worktree', 'add', '--detach',
                            '-q', str(child), 'HEAD'], check=True)
            (child / 'nested.py').write_text('def excluded_worktree_function(): return 9\n')
            run(real, environ=real_env)
            real_graph = (real / 'graphify-out/graph.json').read_text()
            assert 'forbidden_ignored' not in real_graph and 'synthetic' not in real_graph
            assert 'excluded_worktree_function' not in real_graph
            graph_time = (real / 'graphify-out/graph.json').stat().st_mtime_ns
            (child / 'nested.py').write_text('def changed_worktree_function(): return 10\n')
            run(real, readonly=True, environ=real_env)
            run(real, environ=real_env)
            assert (real / 'graphify-out/graph.json').stat().st_mtime_ns == graph_time
            run(child, environ=real_env)
            assert 'changed_worktree_function' in (child / 'graphify-out/graph.json').read_text()
            run(real, readonly=True, environ=real_env)
            assert 'alpha.py' in run(real, 'query', ['alpha_alpha'], readonly=True, environ=real_env).stdout
            assert 'alpha' in run(real, 'path', ['alpha_alpha', 'alpha_beta'], readonly=True, environ=real_env).stdout
            assert 'alpha.py' in run(real, 'explain', ['alpha_alpha'], readonly=True, environ=real_env).stdout
            run(real, environ=real_env)
            (real / 'added.py').write_text('def added_function():\n    return 3\n')
            run(real, environ=real_env)
            assert 'added_function' in (real / 'graphify-out/graph.json').read_text()
            (real / 'added.py').write_text('def renamed_function():\n    return 4\n')
            run(real, environ=real_env)
            assert 'renamed_function' in (real / 'graphify-out/graph.json').read_text()
            (real / 'added.py').unlink()
            run(real, environ=real_env)
            assert 'renamed_function' not in (real / 'graphify-out/graph.json').read_text()
        assert (SKILL / 'SKILL.md').read_bytes() == before_skill
        assert not (SKILL / '.graphify_version').exists()
    report = {'upstream_revision': '92741d162b2094ffc2fed58cfbd8ee823e9da62c',
              'launcher_sha256': hashlib.sha256(LAUNCHER.read_bytes()).hexdigest(),
              'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'invocation': sys.argv, 'fixtures': 'Two separate Git roots with alpha/beta functions, ignored.py and synthetic .env.',
              'result': 'PASS', 'runs': records}
    (evidence / 'workflow.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS:', evidence / 'workflow.json')


if __name__ == '__main__':
    main()
