// Решение: Сумма цифр числа
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    total := 0
    for n > 0 {
        total += n % 10
        n /= 10
    }
    println(total)
}
