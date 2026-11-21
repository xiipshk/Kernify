// Решение: Степень
// Тема: Циклы (for, while)

func solve() {
    a, n := nextInt(), nextInt()
    result := 1
    for i := 0; i < n; i++ {
        result *= a
    }
    println(result)
}
