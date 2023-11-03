class LinearCongruentialGenerator:
    def __init__(self, n, x0=7, m=2**23 - 1, a=10 ** 3, c=377):
        self.n = n
        self.x = x0
        self.m = m
        self.a = a
        self.c = c
        self.rand_numbers = []

    def generate_numbers(self):
        for _ in range(self.n):
            self.x = (self.a * self.x + self.c) % self.m
            self.rand_numbers.append(self.x)
        return self.rand_numbers

    def find_period(self):
        visited = {}
        for i, num in enumerate(self.rand_numbers):
            if num in visited:
                period = i - visited[num]
                return period
            visited[num] = i
        return -1