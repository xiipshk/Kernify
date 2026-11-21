// Решение: Количество делителей
// Тема: Циклы (for, while)

function solve() {
    const n = nextInt();
    let count = 0;
    for (let i = 1; i * i <= n; i++) {
        if (n % i === 0) count += (i * i === n) ? 1 : 2;
    }
    console.log(count);
}
