// Решение: Простые числа до N
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    sieve := make([]bool, n+1)
    for i := 2; i <= n; i++ {
        sieve[i] = true
    }
    for i := 2; i*i <= n; i++ {
        if sieve[i] {
            for j := i * i; j <= n; j += i {
                sieve[j] = false
            }
        }
    }
    first := true
    for i := 2; i <= n; i++ {
        if sieve[i] {
            if !first {
                print(" ")
            }
            first = false
            print(i)
        }
    }
    println()
}
