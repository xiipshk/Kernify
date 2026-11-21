// Решение: Сортировка пузырьком
// Тема: Массивы/списки (одномерные)

function solve() {
    const n = nextInt();
    const arr = [];
    for (let i = 0; i < n; i++) arr.push(nextInt());
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n - 1 - i; j++) {
            if (arr[j] > arr[j + 1]) [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        }
    }
    console.log(arr.join(' '));
}
