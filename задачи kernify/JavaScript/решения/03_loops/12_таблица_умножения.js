// Решение: Таблица умножения
// Тема: Циклы (for, while)

function solve() {
    const n = nextInt();
    for (let i = 1; i <= n; i++) {
        let row = [];
        for (let j = 1; j <= n; j++) row.push(i * j);
        console.log(row.join(' '));
    }
}
