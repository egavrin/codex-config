#!/usr/bin/env python3
"""Black-box acceptance; fixtures never contact Claude. Tests precede implementation.
Failures considered: wrong auth, ambient credentials/tools/context, malformed/failed
responses, secret disclosure, timeout descendants, unsafe/stale/conflicting patches,
missing skill documents, and destructive or non-idempotent shared-skill syncing.
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', default='all', choices=['all', 'review', 'repair', 'stream', 'init', 'profile'])
    args = parser.parse_args()
    root = Path(tempfile.mkdtemp(prefix='claude-collab-e2e-'))
    root.chmod(0o700)
    report = {'command': sys.argv, 'revision_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), 'cases': []}

    def case(name, scenario='review', expected=0, patch=None, extra=None, setup=None):
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
if scenario in ('progress', 'total', 'noise', 'empty', 'stderr', 'retry', 'cancel'):
 for i in range(12):
  if scenario in ('progress','total'): event({'type':'stream_event','event':{'type':'content_block_delta','delta':{'type':'thinking_delta','thinking':'PRIVATE_INTERMEDIATE'}}})
  elif scenario == 'noise': event({'type':'system','subtype':'status','status':'heartbeat'})
  elif scenario == 'empty': print('',flush=True)
  elif scenario == 'stderr': print('PRIVATE_STDERR',file=sys.stderr,flush=True)
  elif scenario == 'retry': event({'type':'system','subtype':'api_retry','error_status':429,'attempt':1})
  time.sleep(.1)
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
        cmd = [sys.executable, str(own/'bridge.py'), '--claude-bin', str(fake), 'run', '--mode', mode, '--packet', str(packet_file), '--timeout', '0.4' if scenario in ('timeout','cancel','init-stall','progress','total','noise','empty','stderr','retry') else '10', '--progress-interval', '0.1']
        if scenario == 'total': cmd += ['--total-timeout','0.4']
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

    try:
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
