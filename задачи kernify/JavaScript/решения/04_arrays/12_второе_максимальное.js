// Решение: Второе максимальное
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    let first = -Infinity, second = -Infinity;
    for (let i = 0; i < n; i++) {
        const x = nextInt();
        if (x > first) { second = first; first = x; }
        else if (x > second && x !== first) { second = x; }
    }
    console.log(second);
}
