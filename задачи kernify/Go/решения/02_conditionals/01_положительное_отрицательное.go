// Решение: Положительное/отрицательное
// Тема: Условные операторы (if, else, elif)

func solve() {
    n := nextInt()
    if n > 0 {
        println("positive")
    } else if n < 0 {
        println("negative")
    } else {
        println("zero")
    }
}
