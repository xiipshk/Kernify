// Решение: Високосный год
// Тема: Условные операторы (if, else, elif)

func solve() {
    y := nextInt()
    leap := y%400 == 0 || (y%4 == 0 && y%100 != 0)
    if leap {
        println("YES")
    } else {
        println("NO")
    }
}
