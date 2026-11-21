// Решение: Калькулятор
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        double a = in.nextDouble();
        String op = in.next();
        double b = in.nextDouble();
        double result = 0;
        boolean valid = true;
        switch (op) {
            case "+": result = a + b; break;
            case "-": result = a - b; break;
            case "*": result = a * b; break;
            case "/":
                if (b == 0) {
                    out.println("Division by zero");
                    valid = false;
                } else result = a / b;
                break;
            default: valid = false; out.println("Invalid operator");
        }
        if (valid) out.println(result);
    }
