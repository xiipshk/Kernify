// Решение: Реверс массива
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    arr := make([]int, n)
    for i := 0; i < n; i++ {
        arr[i] = nextInt()
    }
    for i := n - 1; i >= 0; i-- {
        printf("%d", arr[i])
        if i > 0 { printf(" ") }
    }
    println()
}
