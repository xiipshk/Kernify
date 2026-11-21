// Решение: Сдвиг массива
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const k = nextInt();
    const arr = []; for (let i = 0; i < n; i++) arr.push(nextInt());
    const kk = k % n;
    const result = arr.slice(-kk).concat(arr.slice(0, -kk));
    console.log(result.join(' '));
}
