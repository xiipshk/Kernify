// Решение: Коллац
// Тема: Циклы (for, while)

func solve() {
    n := nextInt()
    steps := 0
    for n != 1 {
        printf("%d ", n)
        if n%2 == 0 {
            n /= 2
        } else {
            n = 3*n + 1
        }
        steps++
    }
    println(1)
    printf("Steps: %d\n", steps)
}
