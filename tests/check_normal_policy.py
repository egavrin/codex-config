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
MARKER = 'PROFILE: TERRA_ASTRA_SOL_REVIEW'
ASTRA_ROLES = ('astra_planner_high', 'astra_reviewer_high')

# Failure cases: missing stages, planning edits, implicit execution/approval,
# nested dispatch, wrong roles, lost settings, capacity evasion, and false completion.
SCENARIOS = {
    'planned coding': ('root evidence -> Astra High plan -> Sol High implementation -> Astra High read-only review -> root acceptance',),
    'planning trigger': ('user requests a plan for code', 'material design decision', 'cross-component change', 'ordered implementation packages'),
    'small edit': ('Small obvious code edits use Sol without the planner or reviewer.', 'The planned-route triggers take precedence over the small-edit shortcut.'),
    'artifact': ('One-off scripts and commands for a specific artifact', 'For mixed tasks, assign only the software package to Sol.'),
    'plan mode': ('In Plan Mode, stop after the plan.', 'Do not edit files or start implementation implicitly.', 'In Plan Mode, reserve only the planner slot.'),
    'normal execution': ('Outside Plan Mode, continue authorized implementation without an extra approval step.',),
    'root dispatch': ('Sol sends planning or review requests to the root.', 'Only the root dispatches the planner and reviewer.'),
    'repair': ('same Sol owner', 'same reviewer', 'at most one ordinary repair'),
    'capacity': ('Preflight retained capacity before the planned route.', 'Reserve slots for the planner, each required Sol owner, and the reviewer.', 'Do not evade the cap'),
    'unavailable stage': ('Report each unavailable stage', 'user-authorized fallback', 'Do not claim the full planned route completed'),
}


def check_scenarios(routes):
    for scenario, phrases in SCENARIOS.items():
        for phrase in phrases:
            assert phrase in routes, (scenario, phrase)


def check_no_automatic_claude(text):
    for stale in ('TERRA_SOL_CLAUDE_REVIEW', 'Claude completion review',
                  '-claude-review', 'Normal completion review',
                  'named normal policy completion review', 'synchronous completion review'):
        assert stale not in text, stale


def read_config(path):
    return tomllib.loads(path.read_text())


def section(text, heading):
    return text.split('## ' + heading + '\n', 1)[1].split('\n## ', 1)[0]


def check_claude_calls(text):
    assert 'No fixed request or retry count applies.' in text
    assert 'including review after fixes' in text
    for cap in ('two calls total per package', 'two-call budget',
                'one request per package', 'one initial request plus at most one',
                'at most one concrete retry', 'one focused repair request',
                'retry allowance above', 'same remaining allowance',
                'Do not request another review merely because',
                'No automatic second review after confirmed fixes',
                'no automatic second review after fixes'):
        assert cap not in text, cap


def check_tree(base):
    config = read_config(base / 'config.toml')
    policy = (base / 'AGENTS.md').read_text()
    check_no_automatic_claude(policy)
    # Persisted UI overrides are user choices. Baseline checks preserve their exact values.
    assert all(isinstance(config.get(key), str) and config[key] for key in ('model', 'model_reasoning_effort'))
    assert isinstance(config.get('service_tier', 'default'), str) and config.get('service_tier', 'default')
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
    assert {name for name in agents if name.startswith('astra')} == set(ASTRA_ROLES)
    for name in ASTRA_ROLES:
        astra = read_config(base / agents[name]['config_file'])
        assert (astra['model'], astra['model_reasoning_effort'], astra['service_tier']) == ('gpt-6-astra', 'high', 'default')
        assert astra['sandbox_mode'] == 'read-only'
        instructions = astra['developer_instructions']
        for phrase in ('Do not edit files.', 'Do not spawn agents or use nested Codex.',
                       'The root owns final acceptance.', 'Do not request Claude automatically.'):
            assert phrase in instructions, (name, phrase)
    routes = section(policy, 'Routes')
    for phrase in ('All normal code changes, including tiny edits',
                   'Desktop and runtime overrides for model, reasoning, and service tier remain authoritative.',
                   'Allow one active child and at most 32 retained native children per ordinary session.',
                   'Do not spawn Sol from Sol', 'No automatic Astra',
                   'Keep the implementation owner available and idle through acceptance.'):
        assert phrase in routes, phrase
    for text in (routes, config['developer_instructions'], role['developer_instructions']):
        check_no_automatic_claude(text)
        assert 'Do not request Claude automatically.' in text
        assert 'No automatic Astra' in text
    assert 'root owns integration and final acceptance' in routes
    check_scenarios(routes)
    for phrase in ('PROFILE: TERRA_SOL` selects the normal policy', 'No automatic Astra fallback, separate verifier, second native opinion'):
        assert phrase not in routes
    assert 'Sol sends planning or review requests to the root.' in role['developer_instructions']
    assert 'After planned implementation, request root-dispatched Astra High read-only review.' in role['developer_instructions']
    for route in ('terra-direct', 'terra-sol', 'luna-direct', 'luna-sol', 'sol-direct', '<effective-root>-sol', '<effective-root>-astra-sol-review'):
        assert route in routes and route in config['developer_instructions'], route
    for phrase in ('astra_planner_high', 'astra_reviewer_high', 'Plan Mode', 'user-authorized fallback', '32 retained'):
        assert phrase in config['developer_instructions'], phrase
    assert '| `astra_planner_high` | `gpt-6-astra` | `high` | `default` |' in policy
    assert '| `astra_reviewer_high` | `gpt-6-astra` | `high` | `default` |' in policy
    assert 'Do not create a tester or an additional model-review child.' in policy
    manual = section(policy, 'Shared skills and explicit Claude requests')
    assert 'require an explicit Claude request or `$claude-collab` invocation' in manual
    assert 'Never run the companion and a native child concurrently' in manual
    for path in ('skills/claude-collab/SKILL.md', 'skills/claude-collab/references/bridge.md'):
        text = (base / path).read_text()
        check_no_automatic_claude(text)
        check_claude_calls(text)
        assert 'explicit Claude requests' in text
    assert 'allow_implicit_invocation: false' in (base / 'skills/claude-collab/agents/openai.yaml').read_text()
    return config, policy


def check_preservation(baseline, live):
    for name, current in (('live', live), ('snapshot', ROOT / 'codex')):
        old = read_config(baseline / name / 'config.toml')
        new = read_config(current / 'config.toml')
        def preserved(config):
            result = {k: v for k, v in config.items() if k != 'developer_instructions'}
            result['agents'] = {k: v for k, v in result['agents'].items() if k not in ASTRA_ROLES}
            return result
        assert preserved(old) == preserved(new), name
        for role_path in (baseline / name / 'agents').glob('*.toml'):
            if role_path.name == 'sol_implementer_high.toml':
                continue
            assert role_path.read_bytes() == (current / 'agents' / role_path.name).read_bytes(), role_path.name
    before = (baseline / 'live/AGENTS.md').read_text()
    after = (live / 'AGENTS.md').read_text()
    protected = ['Controlled English', 'Ponytail compatibility', 'API Keys and Local Environment', 'Engineering Choices', 'Graphify code discovery', 'Mandatory Slopo commit review', 'Shared skills and explicit Claude requests']
    for heading in protected:
        assert section(before, heading) == section(after, heading), heading
    assert section(before, 'Verification').replace(
        'Do not create a tester or another model-review child.',
        'Use the required Astra High review for planned code. Do not create a tester or an additional model-review child.'
    ).replace(
        '- Do not add a separate model-review cycle when existing automated evidence is\n  sufficient.',
        '- Complete the required Astra High review for planned code.\n- Do not add an additional model-review cycle when existing automated evidence is sufficient.'
    ) == section(after, 'Verification')
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
    check_no_automatic_claude(skill)
    assert 'allow_implicit_invocation: false' in (new_skill / 'agents/openai.yaml').read_text()
    check_claude_calls(skill)
    assert section((baseline / 'README.md').read_text(), 'Restore') == section((ROOT / 'README.md').read_text(), 'Restore')


def check_awareness(live):
    codex = (ROOT / 'codex/RTK.md').read_text()
    claude = (ROOT / 'claude/RTK.md').read_text()
    marker = '<!-- rtk-owned: written by `rtk init --codex`, removed by `rtk init --codex --uninstall` -->'
    assert codex.startswith(marker + '\n\n')
    assert codex.removeprefix(marker + '\n\n') == claude
    for text in (codex, claude):
        for phrase in ('Filtered summaries can omit details.', 'complete acceptance evidence',
                       'Configured exclusions keep selected commands raw.',
                       'material diagnostic details', 'exit codes',
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
    check_no_automatic_claude((ROOT / 'README.md').read_text())
    check_claude_calls((ROOT / 'README.md').read_text())
    _, snapshot_policy = check_tree(ROOT / 'codex')
    if args.live:
        _, live_policy = check_tree(args.live)
        assert live_policy == snapshot_policy
    readme = (ROOT / 'README.md').read_text()
    for phrase in (MARKER, 'astra_planner_high', 'astra_reviewer_high', 'Plan Mode', 'user-authorized fallback'):
        assert phrase in readme, phrase
    if args.baseline:
        assert args.live, '--baseline requires --live'
        check_preservation(args.baseline, args.live)
    print('PASS: routing contract, scenario clauses, role settings, TOML, and requested preservation checks')


if __name__ == '__main__':
    main()
