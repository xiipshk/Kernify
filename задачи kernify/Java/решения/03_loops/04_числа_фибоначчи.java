// Решение: Числа Фибоначчи
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        long a = 0, b = 1;
        for (int i = 0; i < n; i++) {
            long tmp = a + b;
            a = b;
            b = tmp;
        }
        out.println(a);
    }
