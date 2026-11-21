// Решение: Дни недели
// Тема: Условные операторы (if, else, elif)

func solve() {
    days := []string{"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    n := nextInt()
    println(days[(n-1)%7])
}
