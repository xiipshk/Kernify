// Решение: Квадратное уравнение
// Тема: Условные операторы (if, else, elif)

func solve() {
    a := float64(nextInt())
    b := float64(nextInt())
    c := float64(nextInt())
    d := b*b - 4*a*c
    if d < 0 {
        println("No roots")
    } else if d == 0 {
        printf("%.6f\n", -b/(2*a))
    } else {
        x1 := (-b - math.Sqrt(d)) / (2*a)
        x2 := (-b + math.Sqrt(d)) / (2*a)
        printf("%.6f %.6f\n", x1, x2)
    }
}
