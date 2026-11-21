// Решение: Поиск элемента
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    arr := make([]int, n)
    for i := 0; i < n; i++ { arr[i] = nextInt() }
    x := nextInt()
    idx := -1
    for i, v := range arr {
        if v == x { idx = i; break }
    }
    println(idx)
}
