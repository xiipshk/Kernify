// Решение: НОД (Евклид)
// Тема: Циклы (for, while)

func solve() {
    a, b := nextInt(), nextInt()
    for b != 0 {
        a, b = b, a%b
    }
    println(a)
}
