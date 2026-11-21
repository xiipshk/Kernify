// Решение: Таблица умножения
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                out.print(i * j);
                if (j < n) out.print(' ');
            }
            out.println();
        }
    }
