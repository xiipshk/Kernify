// Решение: Стоимость покупки
// Тема: Условные операторы (if, else, elif)

function solve() {
    const n = nextInt();
    const a = nextInt();
    const b = nextInt();
    let total = n * a;
    if (total > b) total = Math.floor(total * 0.9);
    console.log(total);
}
