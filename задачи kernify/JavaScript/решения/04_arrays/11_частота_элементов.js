// Решение: Частота элементов
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const map = new Map();
    for (let i = 0; i < n; i++) {
        const x = nextInt();
        map.set(x, (map.get(x) || 0) + 1);
    }
    const keys = [...map.keys()].sort((a, b) => a - b);
    for (const k of keys) console.log(k, map.get(k));
}
