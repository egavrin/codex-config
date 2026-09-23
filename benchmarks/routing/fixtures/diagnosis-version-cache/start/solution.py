from cache import Cache

def solve(initial, operations):
    store = dict(initial)
    cache = Cache()
    result = []
    for operation in operations:
        if operation[0] == 'set':
            store[operation[1]] = operation[2]
        else:
            result.append(cache.get(operation[1], store))
    return result
