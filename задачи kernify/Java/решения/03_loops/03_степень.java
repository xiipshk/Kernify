// Решение: Степень
// Тема: Циклы (for, while)

    public static void solve() {
        int a = in.nextInt();
        int n = in.nextInt();
        long result = 1;
        for (int i = 0; i < n; i++) result *= a;
        out.println(result);
    }
