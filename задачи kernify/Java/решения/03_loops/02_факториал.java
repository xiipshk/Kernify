// Решение: Факториал
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        long result = 1;
        for (int i = 2; i <= n; i++) result *= i;
        out.println(result);
    }
