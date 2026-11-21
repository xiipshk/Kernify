# Решение: Коллац
# Тема: Циклы (for, while)

def solve():
    n = int(input())
    steps = 0
    while n != 1:
        print(n, end=' ')
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    print(1)
    print(f"Steps: {steps}")
