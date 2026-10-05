def solve(initial, updates, fail_at):
    state = dict(initial)
    try:
        for index, (key, value) in enumerate(updates):
            state[key] = value
            if index == fail_at:
                raise RuntimeError('simulated failure')
    except RuntimeError:
        pass
    return state
