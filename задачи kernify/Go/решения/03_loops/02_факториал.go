// Решение: Факториал
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    result := 1
    for i := 2; i <= n; i++ {
        result *= i
    }
    println(result)
}
