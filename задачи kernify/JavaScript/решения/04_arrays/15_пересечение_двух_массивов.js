// Решение: Пересечение двух массивов
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const a = new Set(); for (let i = 0; i < n; i++) a.add(nextInt());
    const m = nextInt();
    const b = new Set(); for (let i = 0; i < m; i++) b.add(nextInt());
    const inter = [...a].filter(x => b.has(x)).sort((a, b) => a - b);
    console.log(inter.join(' '));
}
