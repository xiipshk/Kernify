// Решение: Минимум из трех
// Тема: Условные операторы (if, else, elif)

func solve() {
    a, b, c := nextInt(), nextInt(), nextInt()
    m := a
    if b < m { m = b }
    if c < m { m = c }
    println(m)
}
