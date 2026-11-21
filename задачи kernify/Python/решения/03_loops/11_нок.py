# Решение: НОК
# Тема: Циклы (for, while)

def solve():
    a, b = map(int, input().split())
    def gcd(x, y):
        while y: x, y = y, x % y
        return x
    print(a * b // gcd(a, b))
