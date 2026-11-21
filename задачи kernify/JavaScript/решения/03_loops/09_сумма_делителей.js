// Решение: Сумма делителей
// Тема: Циклы (for, while)

function solve() {
    const n = nextInt();
    let total = 0;
    for (let i = 1; i * i <= n; i++) {
        if (n % i === 0) {
            total += i;
            if (i * i !== n) total += n / i;
        }
    }
    console.log(total);
}
