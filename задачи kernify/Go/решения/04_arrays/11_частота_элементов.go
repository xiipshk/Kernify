// Решение: Частота элементов
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    freq := make(map[int]int)
    for i := 0; i < n; i++ {
        x := nextInt()
        freq[x]++
    }
    keys := make([]int, 0, len(freq))
    for k := range freq { keys = append(keys, k) }
    sort.Ints(keys)
    for _, k := range keys {
        printf("%d %d\n", k, freq[k])
    }
}
