// Решение: Обратное число
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    rev := 0
    for n > 0 {
        rev = rev*10 + n%10
        n /= 10
    }
    println(rev)
}
