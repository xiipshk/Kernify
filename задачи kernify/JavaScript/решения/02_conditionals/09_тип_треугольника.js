// Решение: Тип треугольника
// Тема: Условные операторы (if, else, elif)

function solve() {
    const a = nextInt();
    const b = nextInt();
    const c = nextInt();
    if (a === b && b === c) console.log("equilateral");
    else if (a === b || b === c || a === c) console.log("isosceles");
    else console.log("scalene");
}
