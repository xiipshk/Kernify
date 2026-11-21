// Решение: Удаление дубликатов
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const arr = [];
    for (let i = 0; i < n; i++) arr.push(nextInt());
    const seen = new Set();
    const result = [];
    for (const x of arr) if (!seen.has(x)) { seen.add(x); result.push(x); }
    console.log(result.join(' '));
}
