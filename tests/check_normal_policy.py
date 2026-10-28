#!/usr/bin/env python3
"""Check the saved routing contract. This check does not dispatch models.

Run with Python 3.11+ and an optional private baseline directory:
python3.12 tests/check_normal_policy.py --live ~/.codex --baseline /tmp/<baseline>
"""
import argparse
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'PROFILE: TERRA_SOL_CLAUDE_REVIEW'


def read_config(path):
    return tomllib.loads(path.read_text())


def section(text, heading):
    return text.split('## ' + heading + '\n', 1)[1].split('\n## ', 1)[0]


def check_tree(base):
    config = read_config(base / 'config.toml')
    policy = (base / 'AGENTS.md').read_text()
    # Persisted UI overrides are user choices. Baseline checks preserve their exact values.
    assert all(isinstance(config.get(key), str) and config[key] for key in ('model', 'model_reasoning_effort', 'service_tier'))
    assert MARKER in policy and MARKER in config['developer_instructions']
    assert 'EXPERIMENT: SOL_HIGH_ASTRA_MEDIUM_XHIGH' not in policy + config['developer_instructions']
    assert not re.search(r'default\s+Sol\s+High\s+route', policy), 'stale normal default reference'
    assert 'single-child model-aware branch' not in policy, 'ambiguous child lifecycle reference'
    agents = config['agents']
    assert agents['max_concurrent_threads_per_session'] == 32 and agents['max_depth'] == 1
    assert (agents['default_subagent_model'], agents['default_subagent_reasoning_effort']) == ('gpt-6.1-sol', 'high')
    for name, value in agents.items():
        if isinstance(value, dict) and 'config_file' in value:
            role_path = base / value['config_file']
            role = read_config(role_path)
            assert name == role_path.stem == role.get('name', role_path.stem), name
    role = read_config(base / agents['sol_implementer_high']['config_file'])
    assert (role['model'], role['model_reasoning_effort'], role['service_tier']) == ('gpt-6.1-sol', 'high', 'default')
    assert not any(name.startswith('astra') for name in agents), 'automatic Astra registration'
    routes = section(policy, 'Routes')
    for phrase in ('All normal code changes, including tiny edits',
                   'Desktop and runtime overrides for model, reasoning, and service tier remain authoritative.',
                   'Allow one active child and at most 32 retained native children per ordinary session.',
                   'Do not spawn Sol from Sol', 'No automatic Astra',
                   'Keep the implementation owner available and idle through acceptance.'):
        assert phrase in routes, phrase
    for text in (routes, config['developer_instructions'], role['developer_instructions']):
        assert 'Claude completion review' in text
        assert 'review_unavailable' in text
        assert 'failure_stage' in text
        assert 'preflight' in text and 'run --mode review' in text
        assert text.index('preflight') < text.index('run --mode review')
        assert 'two calls total per package' in text
        assert 'No automatic Astra' in text
    gate = section(policy, 'Claude completion review')
    for phrase in ('nine-field packet', 'Opus High', 'empty `diff`',
                   'Sol pauses edits', 'reject unsupported or out-of-scope findings',
                   'authentication, quota, CLI, or inactivity', 'root owns final acceptance',
                   'Do not request another review merely because Sol fixed review findings.',
                   'read-only technical reviews', 'Named experiments'):
        assert phrase in gate, phrase
    return config, policy


def check_preservation(baseline, live):
    for name, current in (('live', live), ('snapshot', ROOT / 'codex')):
        old = read_config(baseline / name / 'config.toml')
        new = read_config(current / 'config.toml')
        def preserved(config):
            result = {k: v for k, v in config.items() if k != 'developer_instructions'}
            result['agents'] = {k: v for k, v in config['agents'].items() if not k.startswith('astra')}
            return result
        assert preserved(old) == preserved(new), name
        for role_path in (baseline / name / 'agents').glob('*.toml'):
            if role_path.name == 'sol_implementer_high.toml':
                continue
            assert role_path.read_bytes() == (current / 'agents' / role_path.name).read_bytes(), role_path.name
    before = (baseline / 'live/AGENTS.md').read_text()
    after = (live / 'AGENTS.md').read_text()
    protected = ['Controlled English', 'Ponytail compatibility', 'API Keys and Local Environment', 'Engineering Choices', 'Verification', 'Graphify code discovery', 'Mandatory Slopo commit review']
    for heading in protected:
        assert section(before, heading) == section(after, heading), heading
    experiments = ['Jev routing-adviser shadow experiment', 'Terra-Astra plan/build experiment', 'Astra-Luna nested Astra experiment', 'Astra-Sol research profile', 'Astra-Terra Standard comparison profile', 'Terra-Luna-Sol-Astra experiment', 'Luna-Terra-context-Sol-Astra experiment', 'Luna-Astra implementer experiment', 'Luna-Sol-Astra escalation experiment']
    for heading in experiments:
        assert section(before, heading).split('### Context Packet contract')[0] == section(after, heading).split('### Context Packet contract')[0], heading
    for name, current in (('live', live), ('snapshot', ROOT / 'codex')):
        for profile in (baseline / name).glob('*config.toml'):
            if profile.name != 'config.toml':
                assert profile.read_bytes() == (current / profile.name).read_bytes(), profile.name
    old_skill = baseline / 'claude-collab'
    new_skill = live / 'skills/claude-collab'
    for old in (old_skill / 'scripts').rglob('*.py'):
        assert old.read_bytes() == (new_skill / old.relative_to(old_skill)).read_bytes(), old.name
    skill = (new_skill / 'SKILL.md').read_text()
    assert 'PROFILE: TERRA_SOL_CLAUDE_REVIEW' in skill
    assert 'allow_implicit_invocation: false' in (new_skill / 'agents/openai.yaml').read_text()
    assert 'two calls total per package' in skill
    assert section((baseline / 'README.md').read_text(), 'Restore') == section((ROOT / 'README.md').read_text(), 'Restore')


def check_awareness(live):
    codex = (ROOT / 'codex/RTK.md').read_text()
    claude = (ROOT / 'claude/RTK.md').read_text()
    marker = '<!-- rtk-owned: written by `rtk init --codex`, removed by `rtk init --codex --uninstall` -->'
    assert codex.startswith(marker + '\n\n')
    assert codex.removeprefix(marker + '\n\n') == claude
    for text in (codex, claude):
        for phrase in ('Filtered summaries can omit details.', 'complete acceptance evidence',
                       'RTK_DISABLED=1', 'material diagnostic details', 'exit codes',
                       '10 MiB', '200 entries', '30 days', 'subscription charges',
                       'Do not prefix every command', 'Local adaptation', 'OSS 1.1.0'):
            assert phrase in text, phrase
        for stale in ('keeping every signal', 'Treat it as the complete result', 'only when its result is unusable'):
            assert stale not in text, stale
    personal = (ROOT / 'claude/CLAUDE.md').read_text()
    for reference in ('@RTK.md', '@../.codex/ponytail-policy.md',
                      '@../.codex/skills/writing-for-agents/references/controlled-english.md'):
        assert reference in personal, reference
    if live:
        assert (live / 'RTK.md').read_text() == codex
        assert (live.parent / '.claude/RTK.md').read_text() == claude
        assert (live.parent / '.claude/CLAUDE.md').read_text() == personal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', type=Path)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    check_awareness(args.live)
    _, snapshot_policy = check_tree(ROOT / 'codex')
    if args.live:
        _, live_policy = check_tree(args.live)
        assert live_policy == snapshot_policy
    if args.baseline:
        assert args.live, '--baseline requires --live'
        check_preservation(args.baseline, args.live)
    print('PASS: routing contract, scenario clauses, role settings, TOML, and requested preservation checks')


if __name__ == '__main__':
    main()
