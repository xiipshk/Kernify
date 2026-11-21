// Решение: Сумма элементов
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    let sum = 0;
    for (let i = 0; i < n; i++) sum += nextInt();
    console.log(sum);
}
