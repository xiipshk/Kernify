// Решение: Угадай число
// Тема: Циклы (for, while)

func solve() {
    rand.Seed(time.Now().UnixNano())
    secret := rand.Intn(100) + 1
    attempts := 0
    for {
        guess := nextInt()
        attempts++
        if guess < secret {
            println("Higher")
        } else if guess > secret {
            println("Lower")
        } else {
            printf("Correct! Attempts: %d\n", attempts)
            break
        }
    }
}
