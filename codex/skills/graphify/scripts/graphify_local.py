#!/usr/bin/env python3
"""Local Graphify lifecycle and guarded, write-free graph reads (Python 3.9+)."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

OUT = 'graphify-out'
STATE = '.local-state.json'
STATE_FORMAT = 4
BACKUP = '.graphify-local-backup'
SKIP = {'.git', '.hg', '.svn', 'node_modules', '.venv', 'venv', '__pycache__', OUT, BACKUP}
SENSITIVE = re.compile(r'(^\.env|^\.envrc|^\.netrc$|^\.npmrc$|^\.pypirc$|^\.pgpass$|^\.git-credentials$|^\.boto$|^id_(rsa|dsa|ecdsa|ed25519)|\.(pem|key|p12|pfx|crt|cert|der|p8)$|credentials|secrets?|service.account)', re.I)
PRIVATE_DIRS = {'.ssh', '.aws', '.gnupg', '.gcloud', '.secrets', 'secrets', 'credentials'}
EXCLUDES = ['.env*', '**/.env*', '.envrc*', '**/.envrc*', '*.pem', '*.key', '*.p12', '*.pfx', '*.crt', '*.cert', '*.der', '*.p8', '*credentials*', '**/*credentials*', '*secret*', '**/*secret*', '*service_account*', '**/*service_account*', '.ssh/', '.aws/', '.gnupg/', '.gcloud/', '.claude/worktrees/', '**/.claude/worktrees/', 'graphify-out/', '.graphify-local-*']
SCANNER_HASHES = {
    'graphify.__main__': '64781829b2b7e9f0df326f0a33fc88cf540a4a30b2c6b103b3e44e78702de08a',
    'graphify.cli': '4120138b25cab0a0439721cf6d4fa571b78067073613e4b9f917f7f0754a3464',
    'graphify.detect': '86d44989ba8b7a73512def723acc510217cd5cdf5573d5ca3791c3d82eb70074',
}


class Fallback(Exception):
    pass


def environment():
    # An allowlist also removes provider keys with nonstandard variable names.
    env = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR', 'SYSTEMROOT') if key in os.environ}
    env.update(GRAPHIFY_BACKEND='none', GRAPHIFY_NO_AUTO_REFRESH='1',
               GRAPHIFY_QUERY_LOG_DISABLE='1', PYTHONDONTWRITEBYTECODE='1',
               GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0',
               GIT_CONFIG_COUNT='2', GIT_CONFIG_KEY_0='core.hooksPath',
               GIT_CONFIG_VALUE_0='/dev/null', GIT_CONFIG_KEY_1='core.fsmonitor', GIT_CONFIG_VALUE_1='false')
    return env


def git(root, *args, text=True):
    return subprocess.run(['git', '-C', str(root), *args], env=environment(),
                          text=text, capture_output=True, check=False)


def validate_root(value, scoped):
    root = Path(value).expanduser().resolve(strict=True)
    home = Path.home().resolve()
    if not root.is_dir() or root == home or root == Path(root.anchor) or root in home.parents:
        raise Fallback('Unsafe project root. Select one project directory.')
    result = git(root, 'rev-parse', '--show-toplevel')
    if result.returncode == 0:
        if Path(result.stdout.strip()).resolve() != root:
            raise Fallback('Use the exact Git project root.')
        tracked = git(root, 'ls-files', '--', OUT, BACKUP)
        if tracked.stdout.strip():
            raise Fallback('Graph output is tracked. Resolve its ownership before extraction.')
    elif not scoped:
        raise Fallback('A non-Git target requires --scoped and an explicit single-project directory.')
    if (root / OUT).is_symlink() or (root / BACKUP).is_symlink():
        raise Fallback('Graph output must not be a symbolic link.')
    return root, result.returncode == 0


def read_gitlinks(root):
    result = git(root, 'ls-files', '--stage', '-z', text=False)
    if result.returncode or (result.stdout and not result.stdout.endswith(b'\0')):
        raise Fallback('Cannot read the Git index to establish submodule boundaries.')
    links = {}
    directory_names = {}
    for entry in result.stdout.split(b'\0')[:-1]:
        metadata, separator, raw_path = entry.partition(b'\t')
        fields = metadata.split()
        if not separator or len(fields) != 3 or not raw_path:
            raise Fallback('Invalid Git index entry.')
        mode, oid, stage = fields
        if stage != b'0':
            raise Fallback('The Git index has unmerged entries. Resolve them before using the graph.')
        if mode != b'160000':
            continue
        if not re.fullmatch(rb'(?:[0-9a-f]{40}|[0-9a-f]{64})', oid):
            raise Fallback('Invalid submodule object ID in the Git index.')
        relative = os.fsdecode(raw_path)
        parts = relative.split('/')
        if any(part in ('', '.', '..') for part in parts) or relative in links:
            raise Fallback('Invalid submodule path in the Git index.')
        if parts[0] in (OUT, BACKUP):
            raise Fallback('Graph output is tracked. Resolve its ownership before extraction.')
        current = root
        for part in parts:
            child = current / part
            try:
                info = child.lstat()
            except FileNotFoundError:
                break  # An uninitialized submodule can have no directory.
            if current not in directory_names:
                directory_names[current] = set(os.listdir(current))
            if part not in directory_names[current] or not stat.S_ISDIR(info.st_mode):
                raise Fallback(f'Cannot establish an exact submodule boundary at {relative!r}.')
            current = child
        links[relative] = oid.decode('ascii')
    return links


def source_state(root, links):
    """Read source metadata only. No source content or credentials enter this check."""
    entries = {}
    for directory, names, files in os.walk(root, followlinks=False):
        current = Path(directory)
        relative = current.relative_to(root)
        if current != root and '.git' in names + files:
            raise Fallback(f'Nested Git project found at {str(relative)!r}. Select that project root.')
        names[:] = sorted(n for n in names if n not in SKIP and n.lower() not in PRIVATE_DIRS
                          and not (n == 'worktrees' and current.name == '.claude')
                          and (not links or str(relative / n) not in links)
                          and not n.startswith('.graphify-local-') and not (current / n).is_symlink())
        # The pinned scanner omits dist content, but nested project boundaries still need detection.
        if 'dist' in relative.parts:
            continue
        for name in sorted(files):
            path = current / name
            if (links and str(relative / name) in links) or SENSITIVE.search(name) or path.is_symlink():
                continue
            info = path.stat()
            if stat.S_ISREG(info.st_mode):
                entries[str(relative / name)] = [info.st_size, info.st_mtime_ns, info.st_ctime_ns]
    # Ignore rules outside the source tree can change the indexed file set.
    for key, command in (('exclude', ('rev-parse', '--git-path', 'info/exclude')),
                         ('global-exclude', ('config', '--path', '--get', 'core.excludesFile'))):
        result = git(root, *command)
        if result.returncode == 0 and result.stdout.strip():
            path = Path(result.stdout.strip()).expanduser()
            if not path.is_absolute():
                path = root / path
            if path.is_file():
                info = path.stat()
                entries['@' + key] = [info.st_size, info.st_mtime_ns, info.st_ctime_ns]
    return {'root': str(root), 'format': STATE_FORMAT,
            'fingerprint': hashlib.sha256(json.dumps([entries, links], sort_keys=True).encode()).hexdigest(),
            'gitlink_paths': hashlib.sha256(json.dumps(sorted(links)).encode()).hexdigest()}


def read_json(path, limit):
    if path.is_symlink():
        raise Fallback('Graph input must not be a symbolic link: ' + path.name)
    # O_NOFOLLOW also closes the final-component race after the link check.
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise Fallback('Graph input is missing or unsafe: ' + path.name) from exc
    with os.fdopen(descriptor, 'rb') as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise Fallback('Graph input is not a regular file within its size limit: ' + path.name)
        data = handle.read(limit + 1)
        if len(data) > limit:
            raise Fallback('Graph input exceeds its size limit: ' + path.name)
    return json.loads(data)


def load_graph(path):
    try:
        data = read_json(path, 128 * 1024 * 1024)
        if not isinstance(data, dict) or not isinstance(data.get('nodes'), list):
            raise ValueError('nodes must be a list')
        edges = data.get('links', data.get('edges'))
        if not isinstance(edges, list):
            raise ValueError('links or edges must be a list')
        ids = set()
        for node in data['nodes']:
            if not isinstance(node, dict) or not isinstance(node.get('id'), (str, int)) or node['id'] in ids:
                raise ValueError('invalid or duplicate node id')
            ids.add(node['id'])
        for edge in edges:
            if not isinstance(edge, dict) or edge.get('source') not in ids or edge.get('target') not in ids:
                raise ValueError('invalid edge endpoints')
    except (ValueError, TypeError) as exc:
        raise Fallback('Malformed graph: ' + str(exc)) from exc
    return data


@contextmanager
def locked(root, readonly, exclusive):
    cache = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))).expanduser()
    directory = cache / 'graphify-local' / 'locks'
    if readonly and not directory.is_dir():
        raise Fallback('No existing project lock. Use normal source search in read-only mode.')
    if directory.is_symlink() or directory.parent.is_symlink():
        raise Fallback('Unsafe lock directory.')
    if not readonly:
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.parent.chmod(0o700)
        directory.chmod(0o700)
    if directory.is_symlink() or directory.parent.is_symlink():
        raise Fallback('Unsafe lock directory.')
    path = directory / (hashlib.sha256(str(root).encode()).hexdigest() + '.lock')
    flags = os.O_RDONLY if readonly else os.O_RDWR | os.O_CREAT
    try:
        descriptor = os.open(path, flags | os.O_NOFOLLOW, 0o600)
    except FileNotFoundError as exc:
        raise Fallback('No existing project lock. Use normal source search in read-only mode.') from exc
    try:
        try:
            fcntl.flock(descriptor, (fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH) | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise Fallback('Graph is busy. Use normal source search without waiting.') from exc
        yield
    finally:
        os.close(descriptor)


# The installed CLI is Python. Its audit hook blocks query writes and network use.
# This is an in-process guard for the pinned CLI, not an OS sandbox for arbitrary code.
GUARD = r'''
import hashlib, importlib.util, json, os, pathlib, re, runpy, sys
cli, writable, pattern, boundary_config = sys.argv[1:5]
sys.argv = [cli] + sys.argv[5:]
allowed = pathlib.Path(writable).resolve() if writable else None
sensitive = re.compile(pattern, re.I)
root = pathlib.Path.cwd()
paths, scanner_hashes = json.loads(boundary_config)
gitlinks = {root / path for path in paths}
def identity(path):
    try:
        info = path.lstat()
        return info.st_dev, info.st_ino
    except FileNotFoundError:
        return None
gitlink_ids = {key for path in gitlinks if (key := identity(path)) is not None}
def in_gitlink(path):
    return path in gitlinks or not gitlinks.isdisjoint(path.parents)
def linked_to_gitlink(path):
    if not path.is_symlink():
        return False
    try:
        target = path.resolve()
        return (in_gitlink(target) or identity(target) in gitlink_ids
                or any(identity(parent) in gitlink_ids for parent in target.parents))
    except (OSError, RuntimeError):
        return True
def audit(event, args):
    if event == 'os.exec':
        raise PermissionError('Replacing the guarded process is disabled')
    if event.startswith('socket.') and event not in ('socket.__new__', 'socket.gethostname'):
        raise PermissionError('Network access is disabled')
    if event == 'subprocess.Popen':
        command = args[1]
        if not allowed or not isinstance(command, (list, tuple)) or pathlib.Path(command[0]).name != 'git':
            raise PermissionError('External commands are disabled')
    if event == 'open':
        path, mode, flags = args
        if isinstance(path, (str, bytes)):
            target = pathlib.Path(os.fsdecode(path)).absolute()
            if any(p.lower() in {'.ssh', '.aws', '.gnupg', '.gcloud', '.secrets', 'secrets', 'credentials'} for p in target.parts) or sensitive.search(target.name):
                raise PermissionError('Credential reads are disabled')
            if gitlinks and target.is_relative_to(root) and (in_gitlink(target) or linked_to_gitlink(target)):
                raise PermissionError('Submodule reads are disabled')
            writing = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            if writing and (allowed is None or not target.resolve().is_relative_to(allowed)):
                raise PermissionError('Writes outside staging are disabled')
    if event == 'os.scandir' and gitlinks and isinstance(args[0], (str, bytes)):
        target = pathlib.Path(os.fsdecode(args[0])).absolute()
        if in_gitlink(target) or linked_to_gitlink(target):
            raise PermissionError('Submodule scans are disabled')
    if event in {'os.mkdir', 'os.remove', 'os.rmdir', 'os.rename', 'os.link', 'os.symlink', 'os.chmod', 'os.utime', 'os.truncate'}:
        paths = args[:2] if event in {'os.rename', 'os.link', 'os.symlink'} else args[:1]
        for path in paths:
            if not isinstance(path, (str, bytes)) or allowed is None or not pathlib.Path(os.fsdecode(path)).resolve().is_relative_to(allowed):
                raise PermissionError('Filesystem changes outside staging are disabled')
sys.addaudithook(audit)
if gitlinks:
    for module, expected in scanner_hashes.items():
        spec = importlib.util.find_spec(module)
        if spec is None or not spec.origin or hashlib.sha256(pathlib.Path(spec.origin).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Submodule exclusion requires the pinned Graphify scanner.')
    from graphify import detect
    from graphify.__main__ import main
    original_noise_dir = detect._is_noise_dir
    original_scan_ignored = detect._is_scan_ignored
    def noise_dir(name, parent=None):
        return (parent is not None and in_gitlink(parent / name)) or original_noise_dir(name, parent)
    def scan_ignored(path, *args, **kwargs):
        return in_gitlink(path) or linked_to_gitlink(path) or original_scan_ignored(path, *args, **kwargs)
    detect._is_noise_dir = noise_dir
    detect._is_scan_ignored = scan_ignored
    main()
else:
    runpy.run_path(cli, run_name='__main__')
'''


def cli_run(root, arguments, writable=None, gitlinks=()):
    executable = shutil.which('graphify')
    if not executable:
        raise Fallback('Graphify is not installed. Use normal source search.')
    executable = str(Path(executable).resolve())
    with open(executable) as handle:
        shebang = handle.readline().strip()
    interpreter = shebang[2:] if shebang.startswith('#!') else ''
    if not Path(interpreter).is_file() or 'python' not in Path(interpreter).name:
        raise Fallback('Graphify requires its installed Python entry point.')
    # The pinned CLI would otherwise re-execute outside the guard to set this seed.
    env = dict(environment(), PYTHONHASHSEED='0')
    result = subprocess.run([interpreter, '-B', '-c', GUARD, executable, str(writable or ''),
                             SENSITIVE.pattern, json.dumps([list(gitlinks), SCANNER_HASHES]),
                             *arguments], cwd=root, env=env,
                            text=True, capture_output=True)
    if result.returncode:
        # Error output can contain repository text. Keep it inert and bounded.
        detail = result.stderr[-3000:] or result.stdout[-3000:]
        raise Fallback(f'Graphify failed ({result.returncode}): {detail.strip()}')
    return result.stdout


def exclude_outputs(root):
    result = git(root, 'rev-parse', '--git-path', 'info/exclude')
    if result.returncode:
        raise Fallback('Cannot locate Git local excludes.')
    path = Path(result.stdout.strip())
    if not path.is_absolute():
        path = root / path
    if path.is_symlink():
        raise Fallback('Git local exclude file must not be a symbolic link.')
    old = path.read_text() if path.exists() else ''
    patterns = ['/graphify-out/', '/.graphify-local-backup/', '/.graphify-local-stage-*/']
    missing = [pattern for pattern in patterns if pattern not in old.splitlines()]
    if missing:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a') as handle:
            handle.write(('\n' if old and not old.endswith('\n') else '') + '\n'.join(missing) + '\n')


def load_state(root):
    try:
        saved = read_json(root / OUT / STATE, 64 * 1024)
    except (OSError, ValueError) as exc:
        raise Fallback('Graph freshness is unknown. Run ensure when writes are permitted.') from exc
    if not isinstance(saved, dict):
        raise Fallback('Graph freshness is unknown. Run ensure when writes are permitted.')
    return saved


def fresh(root, current):
    load_graph(root / OUT / 'graph.json')
    if load_state(root) != current:
        raise Fallback('Graph is stale. Run ensure when writes are permitted.')


def ensure(root, is_git, links, current):
    output, backup = root / OUT, root / BACKUP
    if backup.exists():
        if output.exists():
            load_graph(output / 'graph.json')
            shutil.rmtree(backup)
        else:
            backup.rename(output)
    try:
        fresh(root, current)
        print('Graph is current: ' + str(output / 'graph.json'))
        return
    except Fallback:
        pass
    if is_git:
        exclude_outputs(root)
    before = source_state(root, links)
    stage = Path(tempfile.mkdtemp(prefix='.graphify-local-stage-', dir=root))
    try:
        staged = stage / OUT
        if output.exists():
            # Reject links before copytree can read their targets.
            if any(path.is_symlink() for path in output.rglob('*')):
                raise Fallback('Existing graph output contains symbolic links.')
            load_graph(output / 'graph.json')
            shutil.copytree(output, staged)
            try:
                previous = load_state(root)
            except Fallback:
                previous = {}
            if (previous.get('format') != STATE_FORMAT
                    or previous.get('gitlink_paths') != before['gitlink_paths']):
                # An old graph or manifest can retain sources across a boundary change.
                (staged / 'graph.json').unlink()
                (staged / 'manifest.json').unlink(missing_ok=True)
        arguments = ['extract', str(root), '--code-only', '--no-cluster', '--no-dedup', '--out', str(stage)]
        for pattern in EXCLUDES:
            arguments += ['--exclude', pattern]
        report = cli_run(root, arguments, stage, links)
        load_graph(staged / 'graph.json')
        after = source_state(root, read_gitlinks(root) if is_git else {})
        if before != after:
            raise Fallback('Sources changed during extraction. Previous graph is preserved.')
        (staged / STATE).write_text(json.dumps(after) + '\n')
        if output.exists():
            output.rename(backup)
        try:
            staged.rename(output)
        except BaseException:
            if backup.exists() and not output.exists():
                backup.rename(output)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        print(report.rstrip())
        print('Graph is ready: ' + str(output / 'graph.json'))
    finally:
        shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['ensure', 'query', 'path', 'explain'])
    parser.add_argument('--root', required=True)
    parser.add_argument('--read-only', action='store_true', help='Create no files, including locks or query stamps.')
    parser.add_argument('--scoped', action='store_true', help='Confirm an explicit single-project non-Git target.')
    parser.add_argument('--budget', type=int, default=1200)
    parser.add_argument('operands', nargs='*')
    args = parser.parse_intermixed_args()
    counts = {'ensure': 0, 'query': 1, 'path': 2, 'explain': 1}
    if len(args.operands) != counts[args.action] or not 1 <= args.budget <= 10000:
        parser.error('Invalid operands or budget. Budget must be 1 through 10000.')
    try:
        root, is_git = validate_root(args.root, args.scoped)
        with locked(root, args.read_only, args.action == 'ensure' and not args.read_only):
            links = read_gitlinks(root) if is_git else {}
            current = source_state(root, links)
            if args.action == 'ensure' and not args.read_only:
                ensure(root, is_git, links, current)
            else:
                fresh(root, current)
                if args.action == 'ensure':
                    print('Graph is current: ' + str(root / OUT / 'graph.json'))
                else:
                    arguments = [args.action, *args.operands]
                    if args.action == 'query':
                        arguments += ['--budget', str(args.budget)]
                    print(cli_run(root, arguments).rstrip())
    except (Fallback, OSError) as exc:
        print('FALLBACK: ' + str(exc) + '\nUse normal source search.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
