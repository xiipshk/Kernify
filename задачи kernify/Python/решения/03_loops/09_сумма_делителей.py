# Решение: Сумма делителей
# Тема: Циклы (for, while)

def solve():
    n = int(input())
    total = 0
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            total += i
            if i * i != n:
                total += n // i
    print(total)
