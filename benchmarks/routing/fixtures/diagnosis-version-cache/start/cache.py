class Cache:
    def __init__(self):
        self.values = {}

    def get(self, key, store):
        if key not in self.values:
            self.values[key] = store[key]
        return self.values[key]
