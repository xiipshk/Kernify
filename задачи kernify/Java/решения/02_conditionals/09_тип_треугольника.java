// Решение: Тип треугольника
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        int c = in.nextInt();
        if (a == b && b == c) out.println("equilateral");
        else if (a == b || b == c || a == c) out.println("isosceles");
        else out.println("scalene");
    }
