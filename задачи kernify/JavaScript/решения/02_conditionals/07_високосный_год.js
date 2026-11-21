// Решение: Високосный год
// Тема: Условные операторы (if, else, elif)

function solve() {
    const y = nextInt();
    const leap = y % 400 === 0 || (y % 4 === 0 && y % 100 !== 0);
    console.log(leap ? "YES" : "NO");
}
