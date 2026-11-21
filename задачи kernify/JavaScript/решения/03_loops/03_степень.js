// Решение: Степень
// Тема: Циклы (for, while)

function solve() {
    const a = nextInt();
    const n = nextInt();
    let result = 1;
    for (let i = 0; i < n; i++) result *= a;
    console.log(result);
}
