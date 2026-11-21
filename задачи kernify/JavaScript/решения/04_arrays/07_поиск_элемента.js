// Решение: Поиск элемента
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const arr = [];
    for (let i = 0; i < n; i++) arr.push(nextInt());
    const x = nextInt();
    const idx = arr.indexOf(x);
    console.log(idx);
}
