// Решение: Числа Фибоначчи
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    a, b := 0, 1
    for i := 0; i < n; i++ {
        a, b = b, a+b
    }
    println(a)
}
