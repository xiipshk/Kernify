// Решение: Квадратное уравнение
// Тема: Условные операторы (if, else, elif)

function solve() {
    const a = parseFloat(next());
    const b = parseFloat(next());
    const c = parseFloat(next());
    const d = b*b - 4*a*c;
    if (d < 0) console.log("No roots");
    else if (d === 0) console.log((-b / (2*a)).toFixed(6));
    else {
        const x1 = (-b - Math.sqrt(d)) / (2*a);
        const x2 = (-b + Math.sqrt(d)) / (2*a);
        console.log(x1.toFixed(6), x2.toFixed(6));
    }
}
