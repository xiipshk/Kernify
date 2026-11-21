# Решение: Калькулятор
# Тема: Условные операторы (if, else, elif)

def solve():
    a, op, b = input().split()
    a, b = float(a), float(b)
    if op == '+':
        print(a + b)
    elif op == '-':
        print(a - b)
    elif op == '*':
        print(a * b)
    elif op == '/':
        if b == 0:
            print("Division by zero")
        else:
            print(a / b)
