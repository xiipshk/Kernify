// Решение: Сдвиг массива
// Тема: Массивы/списки (одномерные)

func solve() {
    n, k := nextInt(), nextInt()
    arr := make([]int, n)
    for i := 0; i < n; i++ { arr[i] = nextInt() }
    k %= n
    result := append(arr[n-k:], arr[:n-k]...)
    for i, v := range result {
        if i > 0 { printf(" ") }
        printf("%d", v)
    }
    println()
}
