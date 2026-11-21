// Решение: Факториал
// Тема: Циклы (for, while)

function solve() {
    const n = nextInt();
    let result = 1;
    for (let i = 2; i <= n; i++) result *= i;
    console.log(result);
}
