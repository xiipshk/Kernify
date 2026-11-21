# Решение: Сумма цифр числа
# Тема: Циклы (for, while)

def solve():
    n = int(input())
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    print(total)
