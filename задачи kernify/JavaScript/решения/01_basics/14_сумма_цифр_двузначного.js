// Решение: Сумма цифр двузначного
// Тема: Основы: переменные, ввод/вывод, типы данных

function solve() {
    const n = nextInt();
    console.log(Math.floor(n / 10) + n % 10);
}
