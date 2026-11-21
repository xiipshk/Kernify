// Решение: Сортировка пузырьком
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    arr := make([]int, n)
    for i := 0; i < n; i++ { arr[i] = nextInt() }
    for i := 0; i < n; i++ {
        for j := 0; j < n-1-i; j++ {
            if arr[j] > arr[j+1] { arr[j], arr[j+1] = arr[j+1], arr[j] }
        }
    }
    for i, v := range arr {
        if i > 0 { printf(" ") }
        printf("%d", v)
    }
    println()
}
