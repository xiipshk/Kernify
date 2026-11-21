// Решение: Принадлежность интервалу
// Тема: Условные операторы (if, else, elif)

func solve() {
    a, b, x := nextInt(), nextInt(), nextInt()
    if a < x && x < b {
        println("YES")
    } else {
        println("NO")
    }
}
