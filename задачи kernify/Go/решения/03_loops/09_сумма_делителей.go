// Решение: Сумма делителей
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    total := 0
    for i := 1; i*i <= n; i++ {
        if n%i == 0 {
            total += i
            if i*i != n {
                total += n / i
            }
        }
    }
    println(total)
}
