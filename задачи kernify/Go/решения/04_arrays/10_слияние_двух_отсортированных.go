// Решение: Слияние двух отсортированных
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    a := make([]int, n)
    for i := 0; i < n; i++ { a[i] = nextInt() }
    m := nextInt()
    b := make([]int, m)
    for i := 0; i < m; i++ { b[i] = nextInt() }
    i, j := 0, 0
    var result []int
    for i < n && j < m {
        if a[i] <= b[j] { result = append(result, a[i]); i++ }
        else { result = append(result, b[j]); j++ }
    }
    for i < n { result = append(result, a[i]); i++ }
    for j < m { result = append(result, b[j]); j++ }
    for k, v := range result {
        if k > 0 { printf(" ") }
        printf("%d", v)
    }
    println()
}
