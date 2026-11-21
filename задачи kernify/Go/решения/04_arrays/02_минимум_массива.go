// Решение: Минимум массива
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    minVal := 1 << 31
    for i := 0; i < n; i++ {
        x := nextInt()
        if x < minVal {
            minVal = x
        }
    }
    println(minVal)
}
