// Решение: Минимум из трех
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        int c = in.nextInt();
        out.println(Math.min(a, Math.min(b, c)));
    }
