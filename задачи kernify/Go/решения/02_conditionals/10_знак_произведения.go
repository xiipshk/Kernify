// Решение: Знак произведения
// Тема: Условные операторы (if, else, elif)

func solve() {
    a, b := nextInt(), nextInt()
    if a == 0 || b == 0 {
        println("zero")
    } else if (a > 0) == (b > 0) {
        println("positive")
    } else {
        println("negative")
    }
}
