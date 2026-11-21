# Решение: Координатные четверти
# Тема: Условные операторы (if, else, elif)

def solve():
    x, y = map(int, input().split())
    if x > 0 and y > 0:
        print(1)
    elif x < 0 and y > 0:
        print(2)
    elif x < 0 and y < 0:
        print(3)
    elif x > 0 and y < 0:
        print(4)
    else:
        print("on axis")
