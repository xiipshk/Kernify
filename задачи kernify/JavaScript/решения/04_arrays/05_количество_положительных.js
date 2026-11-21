// Решение: Количество положительных
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    let count = 0;
    for (let i = 0; i < n; i++) if (nextInt() > 0) count++;
    console.log(count);
}
