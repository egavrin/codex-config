def solve(record):
    return {key: ('[REDACTED]' if key in {'token', 'password', 'secret'} else value)
            for key, value in record.items()}
