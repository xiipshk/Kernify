// Решение: Максимум массива
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    maxVal := -1 << 31
    for i := 0; i < n; i++ {
        x := nextInt()
        if x > maxVal {
            maxVal = x
        }
    }
    println(maxVal)
}
