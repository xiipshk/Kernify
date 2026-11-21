# Решение: Дни недели
# Тема: Условные операторы (if, else, elif)

def solve():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    n = int(input())
    print(days[(n - 1) % 7])
