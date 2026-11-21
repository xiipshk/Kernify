// Решение: Перевод секунд
// Тема: Основы: переменные, ввод/вывод, типы данных

function solve() {
    let s = nextInt();
    const h = Math.floor(s / 3600);
    s %= 3600;
    const m = Math.floor(s / 60);
    s %= 60;
    console.log(h, m, s);
}
