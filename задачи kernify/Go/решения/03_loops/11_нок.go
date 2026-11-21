// Решение: НОК
// Тема: Циклы (for, while)

func solve() {
    a, b := nextInt(), nextInt()
    g, t := a, b
    for t != 0 {
        g, t = t, g%t
    }
    println(a / g * b)
}
