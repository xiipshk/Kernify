// Решение: Среднее значение
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    sum := 0
    for i := 0; i < n; i++ {
        sum += nextInt()
    }
    println(float64(sum) / float64(n))
}
