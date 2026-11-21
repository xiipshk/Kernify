// Решение: Стоимость покупки
// Тема: Условные операторы (if, else, elif)

func solve() {
    n, a, b := nextInt(), nextInt(), nextInt()
    total := n * a
    if total > b {
        total = total * 9 / 10
    }
    println(total)
}
