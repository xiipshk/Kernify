# Решение: Угадай число
# Тема: Циклы (for, while)

def solve():
    import random
    secret = random.randint(1, 100)
    attempts = 0
    while True:
        guess = int(input())
        attempts += 1
        if guess < secret:
            print("Higher")
        elif guess > secret:
            print("Lower")
        else:
            print(f"Correct! Attempts: {attempts}")
            break
