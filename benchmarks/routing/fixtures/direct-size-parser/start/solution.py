def solve(raw):
    units = {"K": 1024, "M": 1024 ** 2, "G": 1024 ** 3}
    return int(raw[:-1]) * units[raw[-1]]
