// Решение: Количество положительных
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    count := 0
    for i := 0; i < n; i++ {
        if nextInt() > 0 {
            count++
        }
    }
    println(count)
}
