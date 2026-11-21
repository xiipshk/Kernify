// Решение: Количество делителей
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    count := 0
    for i := 1; i*i <= n; i++ {
        if n%i == 0 {
            if i*i == n {
                count++
            } else {
                count += 2
            }
        }
    }
    println(count)
}
