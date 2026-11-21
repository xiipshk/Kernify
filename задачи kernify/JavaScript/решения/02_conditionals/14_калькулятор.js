// Решение: Калькулятор
// Тема: Условные операторы (if, else, elif)

function solve() {
    const a = parseFloat(next());
    const op = next();
    const b = parseFloat(next());
    let result;
    switch (op) {
        case '+': result = a + b; break;
        case '-': result = a - b; break;
        case '*': result = a * b; break;
        case '/': result = b === 0 ? "Division by zero" : a / b; break;
        default: result = "Invalid operator";
    }
    console.log(result);
}
