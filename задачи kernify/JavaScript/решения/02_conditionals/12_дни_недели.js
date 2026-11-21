// Решение: Дни недели
// Тема: Условные операторы (if, else, elif)

function solve() {
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const n = nextInt();
    console.log(days[(n - 1) % 7]);
}
