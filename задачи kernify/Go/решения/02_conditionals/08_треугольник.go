// Решение: Треугольник
// Тема: Условные операторы (if, else, elif)

func solve() {
    a, b, c := nextInt(), nextInt(), nextInt()
    if a+b > c && a+c > b && b+c > a {
        println("YES")
    } else {
        println("NO")
    }
}
