import math

def calculate_combinations(n, r):
    if r < 0 or r > n:
        return 0  

    combinations = math.factorial(
        n) // (math.factorial(r) * math.factorial(n - r))
    return combinations

def calculate_long_relation_count_superposed(n):
    if n < 4:
        return 0

    s = 0
    for i in range(4, n + 1, 1):
        s+= calculate_combinations(i, i - 4)

    return s
