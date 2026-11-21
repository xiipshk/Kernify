// Решение: Таблица умножения
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    for i := 1; i <= n; i++ {
        for j := 1; j <= n; j++ {
            printf("%d", i*j)
            if j < n {
                printf(" ")
            }
        }
        println()
    }
}
