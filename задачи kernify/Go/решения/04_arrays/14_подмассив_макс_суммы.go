// Решение: Подмассив макс суммы
// Тема: Массивы/списки (одномерные)

func solve() {
    n := nextInt()
    arr := make([]int, n)
    for i := 0; i < n; i++ { arr[i] = nextInt() }
    maxSum, curr := arr[0], arr[0]
    for i := 1; i < n; i++ {
        if arr[i] > curr+arr[i] { curr = arr[i] } else { curr += arr[i] }
        if curr > maxSum { maxSum = curr }
    }
    println(maxSum)
}
