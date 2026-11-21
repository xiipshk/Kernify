// Решение: Количество делителей
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        int count = 0;
        for (int i = 1; i * i <= n; i++) {
            if (n % i == 0) count += (i * i == n) ? 1 : 2;
        }
        out.println(count);
    }
