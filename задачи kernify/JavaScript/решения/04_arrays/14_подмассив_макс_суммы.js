// Решение: Подмассив макс суммы
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const arr = []; for (let i = 0; i < n; i++) arr.push(nextInt());
    let maxSum = arr[0], curr = arr[0];
    for (let i = 1; i < n; i++) {
        curr = Math.max(arr[i], curr + arr[i]);
        maxSum = Math.max(maxSum, curr);
    }
    console.log(maxSum);
}
