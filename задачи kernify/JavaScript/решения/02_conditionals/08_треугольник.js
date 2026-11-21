// Решение: Треугольник
// Тема: Условные операторы (if, else, elif)

function solve() {
    const a = nextInt();
    const b = nextInt();
    const c = nextInt();
    console.log(a + b > c && a + c > b && b + c > a ? "YES" : "NO");
}
