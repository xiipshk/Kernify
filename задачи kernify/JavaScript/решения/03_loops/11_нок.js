// Решение: НОК
// Тема: Циклы (for, while)

function solve() {
    const a = nextInt();
    const b = nextInt();
    const gcd = (x, y) => y === 0 ? x : gcd(y, x % y);
    console.log(a * b / gcd(a, b));
}
