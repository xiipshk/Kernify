// Решение: Удаление дубликатов
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    seen := make(map[int]bool)
    var result []int
    for i := 0; i < n; i++ {
        x := nextInt()
        if !seen[x] {
            seen[x] = true
            result = append(result, x)
        }
    }
    for i, v := range result {
        if i > 0 { printf(" ") }
        printf("%d", v)
    }
    println()
}
