// Решение: Пересечение двух массивов
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    a := make(map[int]bool)
    for i := 0; i < n; i++ { a[nextInt()] = true }
    m := nextInt()
    b := make(map[int]bool)
    for i := 0; i < m; i++ { b[nextInt()] = true }
    var inter []int
    for k := range a { if b[k] { inter = append(inter, k) } }
    sort.Ints(inter)
    for i, v := range inter { if i > 0 { printf(" ") } printf("%d", v) }
    println()
}
