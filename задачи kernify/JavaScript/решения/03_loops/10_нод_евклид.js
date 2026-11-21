// Решение: НОД (Евклид)
// Тема: Циклы (for, while)

function solve() {
    let a = nextInt();
    let b = nextInt();
    while (b !== 0) [a, b] = [b, a % b];
    console.log(a);
}
