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
READ_ONLY_ASTRA_ROLES = ('astra_planner_high', 'astra_reviewer_high')
FALLBACK_ROLE = 'astra_fallback_high'
NORMAL_ROLES = ('sol_implementer_high', *READ_ONLY_ASTRA_ROLES, FALLBACK_ROLE)
CONCURRENCY_CLAUSES = (
    'Allow up to six active children and at most 128 retained native children per ordinary session.',
    'Count active children across tasks. Never start a seventh active child.',
    'Run concurrent children only for independent packages with non-overlapping write scopes and no unresolved interface dependencies.',
    'Keep dependent packages and competing writes sequential.',
    'Start implementation only after its planner finishes.',
    'Start each reviewer only after all implementation under review finishes.',
    'Do not run a reviewer concurrently with implementation or repair of the changes under review.',
    'Keep each implementation owner idle during review and acceptance of its package.',
)

# Failure cases: missing stages, planning edits, implicit execution/approval,
# unauthorized nested dispatch, wrong roles, lost settings, capacity evasion,
# and false completion.
# Concurrency failures: one-child restriction, seventh active child, overlapping
# writes, unresolved dependencies, early implementation/review, and repair overlap.
SCENARIOS = {
    'planned coding': ('root evidence -> Astra High plan -> Sol High implementation -> Astra High read-only review -> root acceptance',),
    'planning trigger': ('user requests a plan for code', 'material design decision', 'cross-component change', 'ordered implementation packages'),
    'small edit': ('Small obvious code edits use Sol without the planner or reviewer.', 'The planned-route triggers take precedence over the small-edit shortcut.'),
    'artifact': ('One-off scripts and commands for a specific artifact', 'For mixed tasks, assign only the software package to Sol.'),
    'plan mode': ('In Plan Mode, stop after the plan.', 'Do not edit files or start implementation implicitly.', 'In Plan Mode, reserve only the planner slot.'),
    'normal execution': ('Outside Plan Mode, continue authorized implementation without an extra approval step.',),
    'root dispatch': ('Sol sends planning or review requests to the root.', 'Only the root dispatches the planner and reviewer.'),
    'repair': ('same reviewer', 'Follow **Implementation and Repair Ownership**'),
    'capacity': ('Preflight retained capacity before the planned route.', 'Reserve slots for the planner, each required Sol owner, and the reviewer.', 'Do not evade the cap'),
    'unavailable stage': ('Report each unavailable stage', 'user-authorized fallback', 'Do not claim the full planned route completed'),
    'fallback gate': ('An evidence-backed Sol repair leaves the same acceptance criterion unmet.',
                      'A focused Sol attempt identifies a materially hard unresolved implementation problem.',
                      'Explain why Astra is necessary.', 'same reviewer recheck the failed repair',
                      'The root confirms the evidence before dispatch.',
                      'Return material scope, architecture, contract, security, migration, or ambiguous findings to the root'),
    'fallback scope': ('at most one fresh `astra_fallback_high` per Sol package',
                       'smallest unresolved write scope', 'expected and observed results',
                       'Assign Astra sole ownership'),
    'nested fallback': ('Astra Fallback Slot: reserved', 'active higher-priority instructions',
                        'native nested tools', 'Suspend Sol writes', 'Do not delegate deeper.'),
    'fallback parentage': ('If Sol cannot dispatch, send the failure packet and the exact limit to the root.',
                           'The root dispatches the same bounded role',
                           'Record whether Sol or the root dispatched Astra.'),
    'fallback limits': ('Count all descendants across tasks', 'Count outstanding reservations',
                        'If neither dispatch path is available, report the unmet criterion and the exact limit.'),
    'fallback acceptance': ('Keep the same Astra owner through repair and acceptance.',
                            'reuse the same read-only reviewer',
                            'The root inspects the combined diff', 'Do not start another fallback for that package.'),
}

CONTINUATION_SCENARIOS = {
    'collect a repair group': ('Run all feasible relevant checks before sending a repair group.',
                               'Group confirmed in-scope failures by current owner.'),
    'record a blocked check': ('Record each blocked check, its blocker, and the affected acceptance criteria.',
                              'Continue independent authorized work when a check or package is blocked.'),
    'repair B after repair A passes': ('Send each repair group to the current owner',
                                      'Send new in-scope failures to the current owner even after an earlier repair passes.'),
    'invalidate stale evidence': ('Record review findings and check results against the revision or diff they examine.',
                                  'Invalidate evidence affected by changes to the code, inputs, or environment.',
                                  'Repeat affected checks after changes',
                                  'same Astra reviewer for a focused recheck'),
    'reassess a repeated unchanged failure': ('If the same failure recurs without meaningful new evidence or a justified new approach, reassess before retrying.',),
    'prevent false completion': ('Report unmet criteria and blockers.', 'Claim acceptance only when current evidence supports all required criteria.'),
}


def check_scenarios(text, scenarios):
    text = ' '.join(text.split())
    for scenario, phrases in scenarios.items():
        for phrase in phrases:
            assert phrase in text, (scenario, phrase)


def check_no_repair_cap(*normal_texts):
    for text in normal_texts:
        for stale in (r'\b(?:at most |its )?one (?:ordinary |evidence-backed )?repair\b',
                      r'\bat most one ordinary (?:Sol |Astra )?repair\b',
                      r'\bonly after (?:one |an )?evidence-backed (?:ordinary )?Sol repair\b',
                      r'\bthe one permitted repair\b', r"\broot's one repair\b"):
            assert not re.search(stale, ' '.join(text.split()), re.IGNORECASE), stale


def check_concurrency(text):
    for clause in CONCURRENCY_CLAUSES:
        assert clause in text, clause
    for stale in ('one active child', 'one-active-child', 'previous active child finishes',
                  'after the previous owner finishes'):
        assert stale not in text, stale


def check_concurrency_regressions():
    contract = '\n'.join(CONCURRENCY_CLAUSES)
    check_concurrency(contract)
    # The saved policy permits up to six independent active packages.
    assert 'up to six active children' in contract
    invalid = [contract.replace('up to six', f'up to {limit}') for limit in ('one', 'three', 'seven')]
    invalid.append(contract.replace('128 retained', '32 retained'))
    invalid.extend(contract.replace(clause, '') for clause in CONCURRENCY_CLAUSES)
    for changed in invalid:
        try:
            check_concurrency(changed)
        except AssertionError:
            continue
        raise AssertionError('concurrency regression was not detected')


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
    assert agents['max_concurrent_threads_per_session'] == 128 and agents['max_depth'] == 2
    assert (agents['default_subagent_model'], agents['default_subagent_reasoning_effort']) == ('gpt-6.1-sol', 'high')
    for name, value in agents.items():
        if isinstance(value, dict) and 'config_file' in value:
            role_path = base / value['config_file']
            role = read_config(role_path)
            assert name == role_path.stem == role.get('name', role_path.stem), name
    role = read_config(base / agents['sol_implementer_high']['config_file'])
    assert (role['model'], role['model_reasoning_effort'], role['service_tier']) == ('gpt-6.1-sol', 'high', 'default')
    assert {name for name in agents if name.startswith('astra')} == {*READ_ONLY_ASTRA_ROLES, FALLBACK_ROLE}
    for name in (*READ_ONLY_ASTRA_ROLES, FALLBACK_ROLE):
        astra = read_config(base / agents[name]['config_file'])
        assert (astra['model'], astra['model_reasoning_effort'], astra['service_tier']) == ('gpt-6-astra', 'high', 'default')
        instructions = astra['developer_instructions']
        for phrase in ('Do not spawn agents or use nested Codex.',
                       'The root owns final acceptance.', 'Do not request Claude automatically.'):
            assert phrase in instructions, (name, phrase)
        if name == FALLBACK_ROLE:
            assert astra['sandbox_mode'] == 'workspace-write'
            for phrase in ('after a failed Sol repair or a focused Sol attempt',
                           'materially hard unresolved implementation problem',
                           'smallest unresolved write scope', 'In Plan Mode',
                           'one lightweight focused check', 'Remain available for evidence-backed repairs'):
                assert phrase in instructions, (name, phrase)
        else:
            assert astra['sandbox_mode'] == 'read-only'
            assert 'Do not edit files.' in instructions, name
            if name == 'astra_reviewer_high':
                assert 'Tie each finding to the revision or diff under review.' in instructions
                assert 'Remain idle and available for focused rechecks' in instructions
        check_no_repair_cap(instructions)
    routes = section(policy, 'Routes')
    for phrase in ('All normal code changes, including tiny edits',
                   'Desktop and runtime overrides for model, reasoning, and service tier remain authoritative.',
                   'Do not spawn Sol from Sol',
                   'Keep the implementation owner available and idle through acceptance.'):
        assert phrase in routes, phrase
    check_concurrency(routes)
    check_concurrency(config['developer_instructions'])
    assert 'six-active-child model-aware branch' in section(policy, 'Batching and Root Rollout Control')
    assert "normal route's six-active-child and 128-retained-child limits" in section(policy, 'Adaptive Delegation Budget')
    assert 'one wave of up to six agents' in section(policy, 'Adaptive Delegation Budget')
    assert 'It permits up to six active children and at most 128 retained children per ordinary session.' in section(policy, 'Runtime Routing Contract')
    assert 'same 128-child cap' in routes
    for text in (routes, config['developer_instructions'], role['developer_instructions']):
        check_no_automatic_claude(text)
        assert 'Do not request Claude automatically.' in text
        assert 'No automatic Astra implementation fallback' not in text
    assert 'root owns integration and final acceptance' in routes
    check_scenarios(routes, SCENARIOS)
    ownership = section(policy, 'Implementation and Repair Ownership').split('The remaining ownership guidance')[0]
    check_scenarios(ownership, CONTINUATION_SCENARIOS)
    check_no_repair_cap(routes, ownership, section(policy, 'Delegated Route Entry'),
                        config['developer_instructions'], role['developer_instructions'])
    for phrase in ('Run all feasible relevant checks', 'Record blocked checks', 'current owner',
                   'Repeat affected checks', 'same planned reviewer', 'meaningful new evidence',
                   'materially hard unresolved implementation problem'):
        assert phrase in config['developer_instructions'], phrase
    for phrase in ('PROFILE: TERRA_SOL` selects the normal policy', 'No automatic Astra fallback, separate verifier, second native opinion'):
        assert phrase not in routes
    assert 'Sol sends planning or review requests to the root.' in role['developer_instructions']
    assert 'After planned implementation, request root-dispatched Astra High read-only review.' in role['developer_instructions']
    for phrase in ('Astra Fallback Slot: reserved', 'active higher-priority instructions',
                   'Native nested tools', 'Suspend writes', 'failure packet',
                   'failed Sol repair or a focused Sol attempt', 'Remain available for evidence-backed repairs'):
        assert phrase in role['developer_instructions'], phrase
    for route in ('terra-direct', 'terra-sol', 'luna-direct', 'luna-sol', 'sol-direct', '<effective-root>-sol', '<effective-root>-astra-sol-review'):
        assert route in routes and route in config['developer_instructions'], route
    for phrase in ('astra_planner_high', 'astra_reviewer_high', FALLBACK_ROLE, 'Plan Mode',
                   'user-authorized fallback', '128 retained', 'V1 guard', 'Count all descendants across tasks'):
        assert phrase in config['developer_instructions'], phrase
    for name in (*READ_ONLY_ASTRA_ROLES, FALLBACK_ROLE):
        assert f'| `{name}` | `gpt-6-astra` | `high` | `default` |' in policy
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
            if FALLBACK_ROLE not in old['agents']:
                result['agents'] = {k: v for k, v in result['agents'].items() if k not in (*READ_ONLY_ASTRA_ROLES, FALLBACK_ROLE, 'max_concurrent_threads_per_session', 'max_depth')}
            return result
        assert preserved(old) == preserved(new), name
        editable_roles = set(NORMAL_ROLES)
        if FALLBACK_ROLE in old['agents']:
            editable_roles.remove('astra_planner_high')
        for role_path in (baseline / name / 'agents').glob('*.toml'):
            if role_path.stem in editable_roles:
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


def check_claude_instructions(live):
    personal = (ROOT / 'claude/CLAUDE.md').read_text()
    for reference in ('@../.codex/ponytail-policy.md',
                      '@../.codex/skills/writing-for-agents/references/controlled-english.md'):
        assert reference in personal, reference
    if live:
        assert (live.parent / '.claude/CLAUDE.md').read_text() == personal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', type=Path)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    check_concurrency_regressions()
    check_claude_instructions(args.live)
    check_no_automatic_claude((ROOT / 'README.md').read_text())
    check_claude_calls((ROOT / 'README.md').read_text())
    _, snapshot_policy = check_tree(ROOT / 'codex')
    if args.live:
        live_config, live_policy = check_tree(args.live)
        assert live_policy == snapshot_policy
        snapshot_config = read_config(ROOT / 'codex/config.toml')
        assert live_config['developer_instructions'] == snapshot_config['developer_instructions']
        for name in NORMAL_ROLES:
            live_role = live_config['agents'][name]
            assert live_role == snapshot_config['agents'][name], name
            role_file = live_role['config_file']
            assert (args.live / role_file).read_bytes() == (ROOT / 'codex' / role_file).read_bytes(), name
    readme = (ROOT / 'README.md').read_text()
    normal_readme = section(readme, 'Orchestration model')
    check_no_repair_cap(normal_readme)
    for phrase in ('all feasible relevant checks', 'current owner', 'blocked checks', 'same reviewer',
                   'focused Sol attempt', 'materially hard unresolved implementation problem'):
        assert phrase in normal_readme, phrase
    for phrase in (MARKER, 'astra_planner_high', 'astra_reviewer_high', FALLBACK_ROLE, 'Plan Mode',
                   'user-authorized fallback', 'Nested dispatch remains unverified', 'Fresh sessions'):
        assert phrase in readme, phrase
    for phrase in ('up to six active children', 'Never start a seventh active child.',
                   '128 open child threads', 'same 128-child cap',
                   'independent packages', 'non-overlapping write scopes',
                   'all implementation under review finishes', 'competing writes sequential'):
        assert phrase in readme, phrase
    if args.baseline:
        assert args.live, '--baseline requires --live'
        check_preservation(args.baseline, args.live)
    print('PASS: routing contract, scenario clauses, role settings, TOML, and requested preservation checks')


if __name__ == '__main__':
    main()
