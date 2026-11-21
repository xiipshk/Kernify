// Решение: Слияние двух отсортированных
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const a = []; for (let i = 0; i < n; i++) a.push(nextInt());
    const m = nextInt();
    const b = []; for (let i = 0; i < m; i++) b.push(nextInt());
    let i = 0, j = 0;
    const result = [];
    while (i < n && j < m) {
        if (a[i] <= b[j]) result.push(a[i++]);
        else result.push(b[j++]);
    }
    while (i < n) result.push(a[i++]);
    while (j < m) result.push(b[j++]);
    console.log(result.join(' '));
}
