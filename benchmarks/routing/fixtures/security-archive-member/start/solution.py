from pathlib import PurePosixPath

def solve(root, member):
    return str(PurePosixPath(root) / member)
