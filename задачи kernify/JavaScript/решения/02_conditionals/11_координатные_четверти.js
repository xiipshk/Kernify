// Решение: Координатные четверти
// Тема: Условные операторы (if, else, elif)

function solve() {
    const x = nextInt();
    const y = nextInt();
    if (x > 0 && y > 0) console.log(1);
    else if (x < 0 && y > 0) console.log(2);
    else if (x < 0 && y < 0) console.log(3);
    else if (x > 0 && y < 0) console.log(4);
    else console.log("on axis");
}
