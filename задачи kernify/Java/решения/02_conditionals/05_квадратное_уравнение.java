// Решение: Квадратное уравнение
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        double a = in.nextDouble();
        double b = in.nextDouble();
        double c = in.nextDouble();
        double d = b*b - 4*a*c;
        if (d < 0) out.println("No roots");
        else if (d == 0) out.printf("%.6f%n", -b / (2*a));
        else {
            double x1 = (-b - Math.sqrt(d)) / (2*a);
            double x2 = (-b + Math.sqrt(d)) / (2*a);
            out.printf("%.6f %.6f%n", x1, x2);
        }
    }
