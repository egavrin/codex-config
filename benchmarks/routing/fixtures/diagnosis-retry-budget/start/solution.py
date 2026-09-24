from retry import attempt_numbers

def solve(failures, max_attempts):
    count = 0
    for _ in attempt_numbers(max_attempts):
        count += 1
        if count > failures:
            return [count, True]
    return [count, False]
