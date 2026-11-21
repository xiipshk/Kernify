// Решение: Знак произведения
// Тема: Условные операторы (if, else, elif)

function solve() {
    const a = nextInt();
    const b = nextInt();
    if (a === 0 || b === 0) console.log("zero");
    else if ((a > 0) === (b > 0)) console.log("positive");
    else console.log("negative");
}
