// Решение: Сумма цифр числа
// Тема: Циклы (for, while)

function solve() {
    let n = nextInt();
    let total = 0;
    while (n > 0) {
        total += n % 10;
        n = Math.floor(n / 10);
    }
    console.log(total);
}
