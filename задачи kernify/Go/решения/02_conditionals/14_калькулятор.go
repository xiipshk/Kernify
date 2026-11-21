// Решение: Калькулятор
// Тема: Условные операторы (if, else, elif)

func solve() {
    a := nextInt()
    op := next()
    b := nextInt()
    switch op {
    case "+": println(a + b)
    case "-": println(a - b)
    case "*": println(a * b)
    case "/":
        if b == 0 {
            println("Division by zero")
        } else {
            println(a / b)
        }
    default: println("Invalid operator")
    }
}
