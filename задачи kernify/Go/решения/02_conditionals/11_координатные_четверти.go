// Решение: Координатные четверти
// Тема: Условные операторы (if, else, elif)

func solve() {
    x, y := nextInt(), nextInt()
    if x > 0 && y > 0 {
        println(1)
    } else if x < 0 && y > 0 {
        println(2)
    } else if x < 0 && y < 0 {
        println(3)
    } else if x > 0 && y < 0 {
        println(4)
    } else {
        println("on axis")
    }
}
