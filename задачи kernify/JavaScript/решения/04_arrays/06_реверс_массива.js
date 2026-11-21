// Решение: Реверс массива
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const arr = [];
    for (let i = 0; i < n; i++) arr.push(nextInt());
    arr.reverse();
    console.log(arr.join(' '));
}
