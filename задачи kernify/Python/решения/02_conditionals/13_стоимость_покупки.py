# Решение: Стоимость покупки
# Тема: Условные операторы (if, else, elif)

def solve():
    n, a, b = map(int, input().split())  # items, price, discount_threshold
    total = n * a
    if total > b:
        total = int(total * 0.9)  # 10% discount
    print(total)
