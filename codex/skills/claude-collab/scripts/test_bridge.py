#!/usr/bin/env python3
"""Black-box acceptance; fixtures never contact Claude. Tests precede implementation.
Failures considered: wrong auth, ambient credentials/tools/context, malformed/failed
responses, secret disclosure, timeout descendants, unsafe/stale/conflicting patches,
missing skill documents, and destructive or non-idempotent shared-skill syncing.
Ponytail failures considered: unpinned identity, missing or changed documents and policy,
symlinks, reference escapes, name conflicts, invalid levels, new shared links, and oversize bundles.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

SCRIPT = Path(__file__).with_name('bridge.py')
PONYTAIL_REGISTRY = SCRIPT.parent.parent / 'references/ponytail-source.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', default='all', choices=['all', 'review', 'repair', 'stream', 'init', 'profile', 'ponytail', 'reliability'])
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix='claude-collab-e2e-'))
    root.chmod(0o700)
    report = {'command': sys.argv, 'revision_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), 'cases': []}

    def case(name, scenario='review', expected=0, patch=None, extra=None, setup=None, action='run'):
        home = root / name
        skills = home / '.codex/skills'
        own = skills / 'claude-collab/scripts'
        own.mkdir(parents=True)
        shutil.copy2(SCRIPT, own / 'bridge.py')
        (skills / 'sample/references').mkdir(parents=True)
        (skills / 'sample/SKILL.md').write_text('---\nname: sample\ndescription: fixture\n---\nRead [detail](references/detail.md).\n')
        (skills / 'sample/references/detail.md').write_text('REFERENCE_SENTINEL\n')
        policy = skills / 'writing-for-agents/references'
        policy.mkdir(parents=True)
        (policy.parent/'SKILL.md').write_text('---\nname: writing-for-agents\ndescription: Write agent instructions.\n---\n')
        for policy_name, sentinel in [('controlled-english.md','PROFILE_SENTINEL'), ('ste-rule-map.md','RULE_MAP_SENTINEL'), ('software-terms.md','TERMS_SENTINEL')]:
            (policy/policy_name).write_text(sentinel+'\n')
        project = home / 'project'
        project.mkdir()
        (project / 'a.txt').write_text('old\n')
        subprocess.run(['git', 'init', '-q', str(project)], check=True)
        packet = {'project_root': str(project), 'objective': 'Review FIXTURE_SENTINEL', 'acceptance_criteria': ['Correct result'], 'scope': ['a.txt'], 'project_instructions': [], 'skills': [{'name': 'sample', 'references': []}], 'sources': [], 'diffs': [], 'uncertainties': []}
        if extra:
            packet.update(extra)
        fake = home / 'claude'
        fake.write_text('#!' + sys.executable + '\n' + '''import json, os, sys, subprocess, time
from pathlib import Path
args = sys.argv[1:]
base = Path(__file__).parent
with (base / 'calls.jsonl').open('a') as f: f.write(json.dumps(args)+'\\n')
scenario = SCENARIO
if '--version' in args:
 print('2.1.296 (Claude Code)'); sys.exit(0)
if '--help' in args:
 print('--safe-mode --restricted --tools --no-session-persistence --setting-sources --strict-mcp-config --settings --max-turns --permission-mode --disable-slash-commands --model --effort --output-format --verbose --include-partial-messages'); sys.exit(0)
if 'auth' in args:
 print(json.dumps({'loggedIn': True, 'authMethod': 'api_key' if scenario == 'auth' else 'claude.ai', 'apiProvider': 'firstParty'})); sys.exit(0)
assert '--safe-mode' in args and '--restricted' in args and '--strict-mcp-config' in args
assert args[args.index('--tools')+1] == ''
assert args[args.index('--model')+1] == 'opus'
assert args[args.index('--effort')+1] == 'high'
assert args[args.index('--output-format')+1] == 'stream-json'
assert '--verbose' in args and '--include-partial-messages' in args
assert args[args.index('--max-turns')+1] == '1'
assert args[args.index('--setting-sources')+1] == ''
assert '--no-session-persistence' in args and '--disable-slash-commands' in args
assert args[args.index('--permission-mode')+1] == 'plan'
assert not any(k.startswith(('ANTHROPIC_', 'CLAUDE_CODE_OAUTH', 'AWS_', 'OPENAI_')) or k == 'NODE_OPTIONS' for k in os.environ)
assert 'FIXTURE_SENTINEL' not in ' '.join(args)
if scenario == 'duplex': sys.stderr.write('x'*60000); sys.stderr.flush()
payload = sys.stdin.read()
bundle = json.loads(payload)
(base / 'request-payload.json').write_text(payload)
if bundle['skills']: assert 'REFERENCE_SENTINEL' in payload and 'name: sample' in payload
for sentinel in ('PROFILE_SENTINEL','RULE_MAP_SENTINEL','TERMS_SENTINEL'): assert sentinel in payload
assert 'communication_policy' in bundle

if (base / '.codex/skills/related').exists(): assert 'SIBLING_SENTINEL' in payload and 'Related detail' in payload
(base / 'request-observed.json').write_text(json.dumps({'args': args, 'stdin_sha256': __import__('hashlib').sha256(payload.encode()).hexdigest(), 'bundled_reference': True, 'env_restricted': True}))
if scenario in ('timeout', 'cancel'):
 subprocess.Popen([sys.executable, '-c', "import time; from pathlib import Path; time.sleep(2); Path("+repr(str(base/'descendant-survived'))+").write_text('bad')"])
 time.sleep(10)
def event(value): print(json.dumps(value), flush=True)
if scenario == 'init-stall': time.sleep(10)
plugins = []
if scenario.startswith('plugin-'):
 plugins = [{'name':name,'source':name+'@builtin'} for name in ('cc-plugin-agents-md','cc-plugin-plugin-authoring')]
 if scenario == 'plugin-custom': plugins.append({'name':'custom','source':'custom@marketplace'})
 if scenario == 'plugin-spoof-source': plugins[0]['source'] = 'cc-plugin-agents-md@marketplace'
 if scenario == 'plugin-spoof-name': plugins[0]['name'] = 'custom'
 if scenario == 'plugin-unknown-builtin': plugins.append({'name':'unknown','source':'unknown@builtin'})
 if scenario == 'plugin-malformed': plugins = {'name':'cc-plugin-agents-md','source':'cc-plugin-agents-md@builtin'}
event({'type':'system','subtype':'init','model':'claude-sonnet-fixture' if scenario == 'nonopus-init' else 'claude-opus-fixture','plugins':plugins,'tools':['Read'] if scenario == 'plugin-tools' else [],'mcp_servers':[{'name':'custom'}] if scenario == 'plugin-mcp' else []})
if scenario.startswith('estimate-'):
 for i in range(12):
  if scenario != 'estimate-no-message' and (i == 0 or scenario == 'estimate-zero-reset' or (scenario == 'estimate-reset' and i == 6)):
   event({'type':'stream_event','event':{'type':'message_start','message':{'model':'claude-opus-fixture'}}})
  value = (i % 6 + 1) * 50 if scenario == 'estimate-reset' else (i + 1) * 50
  if scenario == 'estimate-repeat': value = 50
  if scenario == 'estimate-decrease': value = 600 - i * 50
  if scenario in ('estimate-zero', 'estimate-zero-reset'): value = 0
  if scenario == 'estimate-invalid': value = [True, -1, 1.5, 'PRIVATE_ESTIMATE'][i % 4]
  event({'type':'system','subtype':'thinking_tokens','estimated_tokens':value,'estimated_tokens_delta':50})
  event({'type':'stream_event','event':{'type':'content_block_delta','delta':{'type':'thinking_delta','thinking':''}}})
  time.sleep(.1)
if scenario in ('progress', 'total', 'noise', 'unknown', 'empty', 'stderr', 'retry', 'cancel'):
 for i in range(12):
  if scenario in ('progress','total'): event({'type':'stream_event','event':{'type':'content_block_delta','delta':{'type':'thinking_delta','thinking':'PRIVATE_INTERMEDIATE'}}})
  elif scenario == 'noise': event({'type':'system','subtype':'status','status':'heartbeat'})
  elif scenario == 'unknown': event({'type':'PRIVATE_INTERMEDIATE','subtype':'PRIVATE_STDERR','text':'PRIVATE_ESTIMATE'})
  elif scenario == 'empty': print('',flush=True)
  elif scenario == 'stderr': print('PRIVATE_STDERR',file=sys.stderr,flush=True)
  elif scenario == 'retry': event({'type':'system','subtype':'api_retry','error_status':429,'attempt':1})
  # Offset healthy progress from the heartbeat cadence; still outlive inactivity.
  time.sleep(.05 if scenario == 'progress' else .1)
if scenario == 'oversize': print('x'*(2*1024*1024),flush=True); time.sleep(10)
if scenario == 'stderr-oversize': print('x'*(300*1024),file=sys.stderr,flush=True); time.sleep(10)
if scenario == 'missing-final': sys.exit(0)
if scenario == 'empty-event': event({}); sys.exit(0)
if scenario == 'bad-delta': event({'type':'stream_event','event':{'type':'content_block_delta','delta':{'type':'text_delta','text':23}}}); sys.exit(0)
if scenario == 'malformed': print('broken'); sys.exit(0)
if scenario == 'limit': print(json.dumps({'type':'result','is_error':True,'result':'Rate limit reached'})); sys.exit(0)
if scenario == 'stale': (base / 'project/a.txt').write_text('concurrent edit\\n')
answer = {'explanation': 'Review complete', 'diff': PATCH}
result = {'type':'result','subtype':'success','is_error':False,'result':json.dumps(answer),'modelUsage':{'claude-sonnet-fixture' if scenario == 'nonopus-final' else 'claude-opus-fixture':{}},'usage':{'input_tokens':2,'output_tokens':3},'total_cost_usd':0.01}
if scenario == 'incomplete': result.pop('subtype')
encoded = json.dumps(result)
if scenario == 'fragmented':
 for i in range(0,len(encoded),7): sys.stdout.write(encoded[i:i+7]); sys.stdout.flush()
else: print(encoded,flush=True)
if scenario == 'cli-error': sys.exit(2)
if scenario == 'final-hang': time.sleep(10)
'''.replace('SCENARIO', repr(scenario)).replace('PATCH', repr(patch or '')))
        fake.chmod(0o700)
        if setup:
            setup(home, packet)
        packet_file = home / 'packet.json'
        packet_file.write_text(json.dumps(packet))
        mode = 'patch' if patch is not None else 'review'
        cmd = [sys.executable, str(own/'bridge.py'), '--claude-bin', str(fake), action, '--mode', mode, '--packet', str(packet_file)]
        if action == 'run':
            cmd += ['--timeout', '0.4' if scenario.startswith('estimate-') or scenario in ('timeout','cancel','init-stall','progress','total','noise','unknown','empty','stderr','retry') else '10', '--progress-interval', '0.1']
        if scenario in ('total','estimate-total'): cmd += ['--total-timeout','0.4']
        if scenario == 'final-hang': cmd += ['--finish-timeout','0.3']
        env = dict(os.environ, HOME=str(home), ANTHROPIC_API_KEY='fixture-not-real', CLAUDE_CODE_OAUTH_TOKEN='fixture-not-real', AWS_SECRET_ACCESS_KEY='fixture-not-real', NODE_OPTIONS='--trace-warnings')
        if scenario == 'cancel':
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            deadline = time.monotonic()+5
            while not (home/'request-observed.json').exists() and time.monotonic()<deadline: time.sleep(.02)
            assert (home/'request-observed.json').exists(), 'request never started'
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=5)
            result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=15)
        (home/'stdout.txt').write_text(result.stdout)
        (home/'stderr.txt').write_text(result.stderr)
        assert result.returncode == expected, (name, result.returncode, result.stdout, result.stderr)
        artifact = Path(json.loads(result.stdout)['artifact'])
        progress = json.loads((artifact/'progress.json').read_text())
        assert progress['status'] in ('finished','failure')
        assert (artifact/'progress.json').stat().st_mode & 0o777 == 0o600
        assert 'PRIVATE_INTERMEDIATE' not in result.stderr and 'PRIVATE_STDERR' not in result.stderr
        assert 'PRIVATE_INTERMEDIATE' not in (artifact/'progress.json').read_text()
        if name.startswith('reliability-'):
            status = json.loads((artifact/'status.json').read_text())
            for path in artifact.glob('*.json'):
                assert not any(s in path.read_text() for s in ('PRIVATE_INTERMEDIATE', 'PRIVATE_STDERR', 'PRIVATE_ESTIMATE', 'REFERENCE_SENTINEL', 'FIXTURE_SENTINEL'))
            assert isinstance(progress['event_counts'], dict)
            assert 'last_transport_event_elapsed_seconds' in progress
            if expected:
                assert status['failure_stage'] and status['failure_reason']
            if action == 'preflight' and expected:
                assert status['failure_stage'] == 'packet'
            if name == 'reliability-preflight-path':
                assert status['diagnostic'] == {'field':'scope', 'index':0}, 'packet diagnostics must identify the field and index'
            if name.startswith('reliability-patch-') or scenario == 'stale':
                assert status['failure_stage'] == 'patch'
            if scenario == 'retry':
                assert status['failure_reason'] == 'provider_rate_limit'
            if scenario in ('estimate-progress', 'estimate-reset'):
                assert progress['meaningful_events'] == 12 and progress['elapsed_seconds'] > .4
                assert progress['progress_source'] == 'thinking_estimate'
                assert progress['estimated_thinking_tokens'] == (300 if scenario == 'estimate-reset' else 600)
            if scenario in ('estimate-zero', 'estimate-zero-reset'):
                assert progress['meaningful_events'] == 0, 'zero estimates must not hide a stall'
            if scenario == 'unknown':
                assert progress['meaningful_events'] == 0 and progress['event_counts']['unknown'] > 0
            if action == 'preflight':
                assert not (home/'calls.jsonl').exists(), 'preflight must not invoke Claude'
                assert not (home/'.claude').exists(), 'preflight must not synchronize skills'
            elif status.get('command'):
                assert status['cli_version'] == '2.1.296'
        if scenario == 'progress':
            assert progress['elapsed_seconds'] > .4 and progress['meaningful_events'] >= 12
            events = [json.loads(line) for line in result.stderr.splitlines()]
            assert any(event['status']=='running' for event in events)
            assert max(b['elapsed_seconds']-a['elapsed_seconds'] for a,b in zip(events,events[1:])) < 1
        if scenario in ('noise','empty','stderr','init-stall'):
            assert progress['meaningful_events'] == 0
        calls = [json.loads(line) for line in (home/'calls.jsonl').read_text().splitlines()] if (home/'calls.jsonl').exists() else []
        if scenario == 'auth':
            assert not any('-p' in call for call in calls)
        if scenario in ('timeout', 'cancel'):
            time.sleep(2.2)
            assert not (home/'descendant-survived').exists()
        if expected == 0 and patch is not None:
            assert (project/'a.txt').read_text() == 'old\n', 'bridge must never apply patch'
        item = {'case': name, 'command': cmd, 'input_sha256': hashlib.sha256(packet_file.read_bytes()).hexdigest(), 'expected_exit': expected, 'observed_exit': result.returncode, 'evidence': str(home), 'pass': True}
        report['cases'].append(item)
        (root/'report.json').write_text(json.dumps(report, indent=2))
        return home

    patch = 'diff --git a/a.txt b/a.txt\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-old\n+new\n'
    def alias_setup(home, packet):
        source = home/'.codex/skills/sample'
        external = home/'installed-skill'
        source.rename(external)
        source.symlink_to(external, target_is_directory=True)

    def excluded_alias_setup(home, packet):
        source = home/'.codex/skills/sample'
        external = home/'.codex/plugins/cache/sample'
        external.parent.mkdir(parents=True)
        source.rename(external)
        source.symlink_to(external, target_is_directory=True)

    def sibling_setup(home, packet):
        sibling = home/'.codex/skills/related'
        sibling.mkdir()
        (sibling/'SKILL.md').write_text('SIBLING_SENTINEL\n[detail](DETAIL.md)')
        (sibling/'DETAIL.md').write_text('Related detail')
        entry = home/'.codex/skills/sample/SKILL.md'
        entry.write_text(entry.read_text() + '[sibling](../related/SKILL.md)\n')

    def ponytail_sentinel(name):
        return 'PONYTAIL_' + name.upper().replace('-', '_') + '_SENTINEL'

    def ponytail_install(home, overrides=None):
        # Pinned identity comes from the installed registry. Fixture documents get fixture hashes.
        registry = json.loads(PONYTAIL_REGISTRY.read_text())
        source = home / registry['root']
        texts = {path: '---\nname: ' + name + '\ndescription: fixture\n---\n' + ponytail_sentinel(name) + '\n' for name, path in registry['skills'].items()}
        texts['skills/ponytail-gain/SKILL.md'] += 'Source: `benchmarks/results/2026-10-07-agentic.md` and the README.\n'
        texts['README.md'] = 'PONYTAIL_README_SENTINEL\n'
        texts['benchmarks/results/2026-10-07-agentic.md'] = 'PONYTAIL_BENCHMARK_SENTINEL\n'
        texts.update(overrides or {})
        for relative, text in texts.items():
            (source/relative).parent.mkdir(parents=True, exist_ok=True)
            (source/relative).write_text(text)
        registry['documents'] = {relative: hashlib.sha256((source/relative).read_bytes()).hexdigest() for relative in registry['documents']}
        target = home/'.codex/skills/claude-collab/references/ponytail-source.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(registry, indent=2))
        (home/'.codex/ponytail-policy.md').write_text('PONYTAIL_POLICY_SENTINEL\n')

    def edit_registry(home, change):
        target = home/'.codex/skills/claude-collab/references/ponytail-source.json'
        registry = json.loads(target.read_text())
        change(registry)
        target.write_text(json.dumps(registry))

    def symlink_copy(path, copy):
        copy.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(copy)

    def ponytail_case(name, selection, objective='Review FIXTURE_SENTINEL', expected=0, setup=None, references=None):
        def prepare(home, packet):
            ponytail_install(home)
            if setup:
                setup(home, packet)
        skills = [{'name': 'sample', 'references': []}] + [{'name': item, 'references': (references or {}).get(item, [])} for item in selection]
        home = case(name, expected=expected, extra={'objective': objective, 'skills': skills}, setup=prepare)
        calls = [json.loads(line) for line in (home/'calls.jsonl').read_text().splitlines()]
        requests = [call for call in calls if '-p' in call]
        if expected:
            error = json.loads((home/'stdout.txt').read_text())['error']
            assert not requests, (name, 'invalid Ponytail material must stop before request')
            assert error != 'Selected skill unavailable in approved user skill catalogue', (name, error)
            return home, error
        assert len(requests) == 1, name
        system = requests[0][requests[0].index('--system-prompt')+1]
        assert 'compatibility policy' in system and 'bounded request' in system, name
        payload = json.loads((home/'request-payload.json').read_text())
        pinned = json.loads(PONYTAIL_REGISTRY.read_text())
        installed = json.loads((home/'.codex/skills/claude-collab/references/ponytail-source.json').read_text())
        source = home/pinned['root']
        assert payload['ponytail']['source'] == {key: pinned[key] for key in ('repository', 'revision', 'version', 'root')}, name
        assert payload['ponytail']['skills'] == list(dict.fromkeys(selection)), name
        policy = (home/'.codex/ponytail-policy.md').read_bytes()
        assert payload['ponytail']['policy']['text'] == policy.decode() and payload['ponytail']['policy']['sha256'] == hashlib.sha256(policy).hexdigest(), name
        keys = [(document.get('source'), document['path']) for document in payload['skills']]
        assert len(keys) == len(set(keys)), (name, 'duplicate bundled document')
        documents = {document['path']: document for document in payload['skills'] if document.get('source') == 'ponytail'}
        for relative, document in documents.items():
            data = (source/relative).read_bytes()
            assert document['text'] == data.decode() and document['sha256'] == hashlib.sha256(data).hexdigest() == installed['documents'][relative], (name, relative)
        for item in selection:
            entry = documents[pinned['skills'][item]]
            assert entry['skill'] == item and ponytail_sentinel(item) in entry['text'], (name, item)
        assert any(document['skill'] == 'sample' and 'source' not in document for document in payload['skills']), name
        assert sorted(link.name for link in (home/'.claude/skills').iterdir()) == ['sample', 'writing-for-agents'], (name, 'Ponytail must not add shared skill links')
        assert sorted(json.loads((home/'.codex/skills/claude-collab/.state/links.json').read_text())) == ['sample', 'writing-for-agents'], name
        return home, payload

    def ponytail_suite():
        plain = case('ponytail-no-selection')
        observed = (plain/'request-payload.json').read_text()
        assert 'ponytail' not in json.loads(observed) and 'PONYTAIL' not in observed
        assert not (plain/'.codex/third-party').exists() and not (plain/'.codex/ponytail-policy.md').exists()
        for level in ('full', 'lite', 'ultra'):
            _, payload = ponytail_case('ponytail-level-' + level, ['ponytail'], 'Review FIXTURE_SENTINEL\nPonytail level: ' + level)
            assert payload['ponytail']['mode'] == level
        for label, line in (('off', 'Ponytail level: off'), ('missing', ''), ('unknown', 'Ponytail level: max'), ('conflict', 'Ponytail level: full\nPonytail level: lite'), ('inline', 'Use Ponytail level: full here.')):
            ponytail_case('ponytail-level-' + label, ['ponytail'], 'Review FIXTURE_SENTINEL\n' + line, expected=1)
        for name in ('ponytail-review', 'ponytail-audit', 'ponytail-debt', 'ponytail-gain', 'ponytail-help'):
            _, payload = ponytail_case('ponytail-one-shot-' + name, [name], 'Review FIXTURE_SENTINEL\nPonytail level: off')
            assert payload['ponytail']['mode'] is None and 'skills/ponytail/SKILL.md' not in {document['path'] for document in payload['skills']}
        _, payload = ponytail_case('ponytail-one-shot-no-level', ['ponytail-help'])
        assert payload['ponytail']['mode'] is None
        _, payload = ponytail_case('ponytail-gain-references', ['ponytail-gain', 'ponytail-gain'])
        texts = {document['path']: document['text'] for document in payload['skills'] if document.get('source') == 'ponytail'}
        assert sorted(texts) == ['README.md', 'benchmarks/results/2026-10-07-agentic.md', 'skills/ponytail-gain/SKILL.md'], sorted(texts)
        assert 'PONYTAIL_README_SENTINEL' in texts['README.md'] and 'PONYTAIL_BENCHMARK_SENTINEL' in texts['benchmarks/results/2026-10-07-agentic.md']
        evidence = {'README.md': 'PONYTAIL_README_SENTINEL\n[install](INSTALL.md)\n[core](skills/ponytail/SKILL.md)\n[method](benchmarks/results/2026-10-07-agentic.md)\n',
                    'benchmarks/results/2026-10-07-agentic.md': 'PONYTAIL_BENCHMARK_SENTINEL\n[reproduce](../agentic/README.md)\n',
                    'INSTALL.md': 'UNREGISTERED_NAVIGATION_SENTINEL\n', 'benchmarks/agentic/README.md': 'UNREGISTERED_NAVIGATION_SENTINEL\n'}
        home, payload = ponytail_case('ponytail-gain-evidence-navigation', ['ponytail-gain'], setup=lambda h, p: ponytail_install(h, evidence))
        assert sorted(document['path'] for document in payload['skills'] if document.get('source') == 'ponytail') == ['README.md', 'benchmarks/results/2026-10-07-agentic.md', 'skills/ponytail-gain/SKILL.md']
        assert 'UNREGISTERED_NAVIGATION_SENTINEL' not in (home/'request-payload.json').read_text()
        ponytail_case('ponytail-selection-unregistered', ['ponytail-review'], expected=1, setup=lambda h, p: ponytail_install(h, {'skills/ponytail-review/NOTES.md': 'UNREGISTERED_SENTINEL\n'}), references={'ponytail-review': ['NOTES.md']})
        linked = '---\nname: ponytail-review\ndescription: fixture\n---\nPONYTAIL_PONYTAIL_REVIEW_SENTINEL\n[core](../ponytail/SKILL.md)\n'
        _, payload = ponytail_case('ponytail-registered-reference', ['ponytail-review'], setup=lambda h, p: ponytail_install(h, {'skills/ponytail-review/SKILL.md': linked}), references={'ponytail-review': ['../../README.md']})
        assert sorted(document['path'] for document in payload['skills'] if document.get('source') == 'ponytail') == ['README.md', 'skills/ponytail-review/SKILL.md', 'skills/ponytail/SKILL.md']
        assert payload['ponytail']['mode'] is None
        _, payload = ponytail_case('ponytail-changed-policy', ['ponytail-help'], setup=lambda h, p: (h/'.codex/ponytail-policy.md').write_text('CHANGED_POLICY_SENTINEL\n'))
        assert payload['ponytail']['policy']['text'] == 'CHANGED_POLICY_SENTINEL\n'
        source = lambda home: home/'.codex/third-party/ponytail'
        help_entry = lambda home: source(home)/'skills/ponytail-help/SKILL.md'
        registry = lambda home: home/'.codex/skills/claude-collab/references/ponytail-source.json'

        def move_root(home, packet):
            source(home).rename(home/'ponytail-real')
            source(home).symlink_to(home/'ponytail-real', target_is_directory=True)

        def replace_with_directory(home, packet):
            help_entry(home).unlink()
            help_entry(home).mkdir()

        def user_collision(home, packet):
            (home/'.codex/skills/ponytail-help').mkdir()
            (home/'.codex/skills/ponytail-help/SKILL.md').write_text('---\nname: ponytail-help\ndescription: user\n---\nUSER_COPY\n')

        for label, setup in (
            ('missing-registry', lambda h, p: registry(h).unlink()),
            ('missing-root', lambda h, p: shutil.rmtree(source(h))),
            ('changed-revision', lambda h, p: edit_registry(h, lambda r: r.update(revision='0' * 40))),
            ('changed-root', lambda h, p: edit_registry(h, lambda r: r.update(root='.codex/third-party/other'))),
            ('changed-names', lambda h, p: edit_registry(h, lambda r: r['skills'].update({'ponytail-extra': 'skills/ponytail-extra/SKILL.md'}))),
            ('registry-traversal', lambda h, p: edit_registry(h, lambda r: r['documents'].update({'../outside.md': '0' * 64}))),
            ('missing-document', lambda h, p: help_entry(h).unlink()),
            ('hash-mismatch', lambda h, p: help_entry(h).write_text('---\nname: ponytail-help\ndescription: fixture\n---\nCHANGED\n')),
            ('missing-policy', lambda h, p: (h/'.codex/ponytail-policy.md').unlink()),
            ('policy-symlink', lambda h, p: symlink_copy(h/'.codex/ponytail-policy.md', h/'policy-copy.md')),
            ('document-symlink', lambda h, p: symlink_copy(help_entry(h), h/'help-copy.md')),
            ('root-symlink', move_root),
            ('non-regular', replace_with_directory),
            ('name-collision', user_collision),
        ):
            ponytail_case('ponytail-' + label, ['ponytail-help'], expected=1, setup=setup)
        escape = '---\nname: ponytail-review\ndescription: fixture\n---\n[outside](../../../../outside.md)\n'
        ponytail_case('ponytail-reference-escape', ['ponytail-review'], expected=1, setup=lambda h, p: ponytail_install(h, {'skills/ponytail-review/SKILL.md': escape}))
        unregistered = '---\nname: ponytail-review\ndescription: fixture\n---\n[notes](NOTES.md)\n'
        ponytail_case('ponytail-unregistered-reference', ['ponytail-review'], expected=1, setup=lambda h, p: ponytail_install(h, {'skills/ponytail-review/SKILL.md': unregistered, 'skills/ponytail-review/NOTES.md': 'UNREGISTERED_SENTINEL\n'}))
        ponytail_case('ponytail-selection-escape', ['ponytail-review'], expected=1, references={'ponytail-review': ['../../../outside.md']})
        _, error = ponytail_case('ponytail-combined-size', ['ponytail-gain'], 'Review FIXTURE_SENTINEL ' + 'x' * 120000, expected=1, setup=lambda h, p: ponytail_install(h, {'README.md': 'PONYTAIL_README_SENTINEL ' + 'x' * 150000 + '\n'}))
        assert error == 'Bundled packet exceeds 256 KiB; narrow the package', error

    def reliability_suite():
        for scenario in ('estimate-progress', 'estimate-reset'):
            case('reliability-' + scenario, scenario)
        for scenario in ('estimate-zero-reset', 'estimate-zero', 'estimate-repeat', 'estimate-decrease', 'estimate-invalid', 'estimate-no-message', 'estimate-total'):
            case('reliability-' + scenario, scenario, 1)
        for scenario in ('noise', 'unknown', 'stderr', 'retry', 'malformed', 'limit', 'cli-error', 'final-hang', 'cancel'):
            case('reliability-' + scenario, scenario, 1)
        for label, patch_value in [('bad-format', 'not a diff\n'), ('conflict', patch.replace('-old', '-wrong')), ('escape', patch.replace('a.txt', '../outside'))]:
            case('reliability-patch-' + label, expected=1, patch=patch_value)
        case('reliability-stale', 'stale', 1, patch=patch)
        case('reliability-preflight-path', expected=1, action='preflight', extra={'scope':['../PRIVATE_ESTIMATE']})
        case('reliability-preflight-policy', expected=1, action='preflight', setup=lambda h,p:(h/'.codex/skills/writing-for-agents/references/software-terms.md').unlink())
        case('reliability-preflight-mode', expected=1, action='preflight', extra={'skills':[{'name':'ponytail'}]}, setup=lambda h,p:ponytail_install(h))
        for repaired in (True, False):
            bad = patch.replace('-old', '-wrong')
            home = case('reliability-repair-first-' + str(repaired), expected=1, patch=bad)
            calls = lambda: [json.loads(line) for line in (home/'calls.jsonl').read_text().splitlines() if '-p' in json.loads(line)]
            assert len(calls()) == 1, 'helper must not retry a rejected patch'
            packet_path = home/'packet.json'
            followup = json.loads(packet_path.read_text())
            followup['uncertainties'] = ['The first patch conflicts with supplied source. Correct only that defect.']
            packet_path.write_text(json.dumps(followup))
            if repaired:
                fake = home/'claude'
                original = fake.read_text()
                assert repr(bad) in original
                fake.write_text(original.replace(repr(bad), repr(patch)))
            command = report['cases'][-1]['command']
            result = subprocess.run(command, env=dict(os.environ, HOME=str(home)), capture_output=True, text=True, timeout=15)
            assert result.returncode == (0 if repaired else 1) and len(calls()) == 2
            assert (home/'project/a.txt').read_text() == 'old\n'
            artifact = Path(json.loads(result.stdout)['artifact'])
            if repaired:
                subprocess.run(['git','apply','--check','--whitespace=error',str(artifact/'patch.diff')], cwd=home/'project', check=True)
                subprocess.run(['git','apply','--whitespace=error',str(artifact/'patch.diff')], cwd=home/'project', check=True)
                assert (home/'project/a.txt').read_text() == 'new\n'
            report['cases'].append({'case':'reliability-one-focused-repair-' + str(repaired), 'command':command, 'input_sha256':hashlib.sha256(packet_path.read_bytes()).hexdigest(), 'expected_exit':0 if repaired else 1, 'observed_exit':result.returncode, 'evidence':str(artifact), 'next_route':'accepted' if repaired else 'native-fallback', 'request_count':len(calls()), 'pass':True})
        home = case('reliability-preflight-boundary', action='preflight')
        initial = json.loads((Path(json.loads((home/'stdout.txt').read_text())['artifact'])/'status.json').read_text())
        assert initial['packet_bytes'] > 0 and initial['packet_size']['limit_bytes'] == 256 * 1024
        packet_path = home/'packet.json'
        packet = json.loads(packet_path.read_text())
        packet['objective'] += 'x' * (256 * 1024 - initial['packet_bytes'])
        command = [sys.executable, str(home/'.codex/skills/claude-collab/scripts/bridge.py'), 'preflight', '--mode', 'review', '--packet', str(packet_path)]
        for increment, expected in [(0,0),(1,1)]:
            packet_path.write_text(json.dumps({**packet, 'objective':packet['objective'] + 'x' * increment}))
            result = subprocess.run(command, env=dict(os.environ, HOME=str(home)), capture_output=True, text=True, timeout=15)
            assert result.returncode == expected, result.stderr
            artifact = Path(json.loads(result.stdout)['artifact'])
            status = json.loads((artifact/'status.json').read_text())
            assert status['packet_size']['total_bytes'] == 256 * 1024 + increment
            assert not (home/'calls.jsonl').exists() and not (home/'.claude').exists()
            report['cases'].append({'case':'reliability-exact-boundary-' + str(increment), 'command':command, 'input_sha256':hashlib.sha256(packet_path.read_bytes()).hexdigest(), 'expected_exit':expected, 'observed_exit':result.returncode, 'evidence':str(artifact), 'pass':True})

    try:
        if args.case in ('all', 'reliability'):
            reliability_suite()
        if args.case == 'reliability':
            report['status'] = 'pass'
            return
        if args.case in ('all','profile'):
            case('profile-with-skill')
            case('profile-without-skill', extra={'skills':[]})
            missing = case('profile-missing', expected=1, setup=lambda h,p:(h/'.codex/skills/writing-for-agents/references/controlled-english.md').unlink())
            missing_map = case('profile-missing-map', expected=1, setup=lambda h,p:(h/'.codex/skills/writing-for-agents/references/ste-rule-map.md').unlink())
            missing_terms = case('profile-missing-terms', expected=1, setup=lambda h,p:(h/'.codex/skills/writing-for-agents/references/software-terms.md').unlink())
            oversized = case('profile-combined-boundary', expected=1, extra={'objective':'Review FIXTURE_SENTINEL '+'x'*100000}, setup=lambda h,p:(h/'.codex/skills/writing-for-agents/references/software-terms.md').write_text('TERMS_SENTINEL '+'x'*180000))
            for home in (missing,missing_map,missing_terms,oversized):
                calls=[json.loads(line) for line in (home/'calls.jsonl').read_text().splitlines()]
                assert not any('-p' in call for call in calls), 'invalid policy must stop before request'
        if args.case == 'profile':
            report['status']='pass'
            return
        if args.case in ('all', 'ponytail'):
            ponytail_suite()
        if args.case == 'ponytail':
            report['status'] = 'pass'
            return
        case('review')
        if args.case in ('all', 'stream', 'init'):
            case('plugin-builtin','plugin-builtin')
            for scenario in ('plugin-custom','plugin-spoof-source','plugin-spoof-name','plugin-unknown-builtin','plugin-malformed','plugin-tools','plugin-mcp'):
                case(scenario,scenario,1)
        if args.case in ('all', 'stream'):
            for scenario in ('progress','fragmented'):
                case('stream-'+scenario, scenario)
            case('stream-duplex','duplex',extra={'objective':'Review FIXTURE_SENTINEL '+ 'x'*120000})
            for scenario in ('init-stall','noise','empty','stderr','retry','oversize','stderr-oversize','missing-final','empty-event','bad-delta','nonopus-init','nonopus-final','incomplete','cli-error','final-hang','total','cancel'):
                case('stream-'+scenario,scenario,1)
        if args.case in ('all', 'repair'):
            alias_home = case('source-root-alias', setup=alias_setup)
            assert (alias_home/'.claude/skills/sample').is_symlink()
            case('sibling-reference', setup=sibling_setup)
            case('excluded-plugin-alias', expected=1, setup=excluded_alias_setup)
            plain = patch.split('\n', 1)[1]
            case('plain-unified', patch=plain)
            case('plain-add', patch='--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+added\n', extra={'scope':['a.txt','new.txt']})
            case('plain-delete', patch='--- a/a.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-old\n')
            case('plain-escape', expected=1, patch=plain.replace('a.txt','../outside'))
            case('plain-rename', expected=1, patch=plain.replace('+++ b/a.txt','+++ b/other.txt'), extra={'scope':['a.txt','other.txt']})
            failed = case('retained-rejected-patch', expected=1, patch='not a unified diff\n')
            artifact = Path(json.loads((failed/'stdout.txt').read_text())['artifact'])
            assert json.loads((artifact/'response.json').read_text())['diff'] == 'not a unified diff\n'
            status = json.loads((artifact/'status.json').read_text())
            assert status['status'] == 'failure' and status['applied'] is False
            secret = case('no-retained-secret-response', expected=1, patch='sk-ant-' + 'x'*30)
            artifact = Path(json.loads((secret/'stdout.txt').read_text())['artifact'])
            assert not (artifact/'response.json').exists()
            case('sibling-outside-catalogue', expected=1, setup=lambda h,p:(h/'.codex/skills/sample/SKILL.md').write_text('[outside](../../outside.md)'))
            case('nested-skill-symlink', expected=1, setup=lambda h,p: ((h/'.codex/skills/sample/references/detail.md').unlink(), (h/'.codex/skills/sample/references/detail.md').symlink_to(h/'project/a.txt')))

        if args.case == 'all':
            case('patch', patch=patch)
            case('malformed', 'malformed', 1)
            case('auth', 'auth', 1)
            case('limit', 'limit', 1)
            case('timeout', 'timeout', 1)
            case('stale', 'stale', 1, patch=patch)
            case('conflict', expected=1, patch=patch.replace('-old', '-wrong'))
            case('escape', expected=1, patch=patch.replace('a.txt', '../outside'))
            case('mode-change', expected=1, patch='diff --git a/a.txt b/a.txt\nold mode 100644\nnew mode 100755\n')
            case('binary', expected=1, patch='diff --git a/a.txt b/a.txt\nGIT binary patch\nliteral 1\nA\n')
            case('secret', expected=1, extra={'objective': 'ANTHROPIC_API_KEY=sk-ant-' + 'a'*30})
            case('secret-file', expected=1, extra={'sources':['.env']}, setup=lambda h,p:(h/'project/.env').write_text('SECRET=value'))
            case('symlink', expected=1, setup=lambda h,p: ((h/'project/a.txt').unlink(), (h/'project/a.txt').symlink_to(h/'packet.json')))
            case('reference-escape', expected=1, setup=lambda h,p:(h/'.codex/skills/sample/SKILL.md').write_text('[outside](../../outside.md)'))
            addition = 'diff --git a/new.txt b/new.txt\nnew file mode 100644\n--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+added\n'
            case('addition', patch=addition, extra={'scope':['a.txt','new.txt']})
            deletion = 'diff --git a/a.txt b/a.txt\ndeleted file mode 100644\n--- a/a.txt\n+++ /dev/null\n@@ -1 +0,0 @@\n-old\n'
            case('deletion', patch=deletion)
            home = case('sync-start')
            own = home/'.codex/skills/claude-collab/scripts/bridge.py'
            cmd = [sys.executable,str(own),'sync-skills']
            env = dict(os.environ,HOME=str(home))
            target=home/'.claude/skills'
            sample=target/'sample'
            first=sample.lstat().st_ino
            r=subprocess.run(cmd,env=env,capture_output=True,text=True); assert r.returncode == 0
            assert sample.lstat().st_ino == first
            source=home/'.codex/skills/new-skill'; source.mkdir(); (source/'SKILL.md').write_text('new')
            r=subprocess.run(cmd,env=env,capture_output=True,text=True); assert r.returncode == 0 and (target/'new-skill').is_symlink()
            shutil.rmtree(source)
            r=subprocess.run(cmd,env=env,capture_output=True,text=True); assert r.returncode == 0 and not (target/'new-skill').is_symlink()
            sample.unlink(); sample.mkdir(); (sample/'keep').write_text('owned by user')
            r=subprocess.run(cmd,env=env,capture_output=True,text=True); assert r.returncode == 1 and (sample/'keep').read_text() == 'owned by user'
            unmanaged=target/'unmanaged'; unmanaged.symlink_to(home/'absent')
            r=subprocess.run(cmd,env=env,capture_output=True,text=True); assert unmanaged.is_symlink()
            report['cases'].append({'case':'sync-idempotent-new-stale-conflict-unmanaged','pass':True,'expected':'safe shared links','observed':'safe shared links','command':cmd})
        report['status']='pass'
    except Exception as exc:
        report['status']='fail'; report['error']=str(exc)
        raise
    finally:
        (root/'report.json').write_text(json.dumps(report,indent=2))
        print(root/'report.json')

if __name__ == '__main__':
    main()
