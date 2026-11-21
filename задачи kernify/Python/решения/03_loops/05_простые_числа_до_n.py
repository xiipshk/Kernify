# Решение: Простые числа до N
# Тема: Циклы (for, while)

def solve():
    n = int(input())
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    primes = [str(i) for i, is_p in enumerate(sieve) if is_p]
    print(' '.join(primes))
