// Решение: Обмен значениями
// Тема: Основы: переменные, ввод/вывод, типы данных

function solve() {
    let a = nextInt();
    let b = nextInt();
    [a, b] = [b, a];
    console.log(a, b);
}
