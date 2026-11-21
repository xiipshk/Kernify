// Решение: Тип треугольника
// Тема: Условные операторы (if, else, elif)

func solve() {
    a, b, c := nextInt(), nextInt(), nextInt()
    if a == b && b == c {
        println("equilateral")
    } else if a == b || b == c || a == c {
        println("isosceles")
    } else {
        println("scalene")
    }
}
