// Решение: Треугольник
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        int c = in.nextInt();
        out.println(a + b > c && a + c > b && b + c > a ? "YES" : "NO");
    }
