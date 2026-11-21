// Решение: Второе максимальное
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    first, second := -1<<31, -1<<31
    for i := 0; i < n; i++ {
        x := nextInt()
        if x > first { second = first; first = x }
        else if x > second && x != first { second = x }
    }
    println(second)
}
