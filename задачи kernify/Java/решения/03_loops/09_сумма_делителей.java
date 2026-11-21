// Решение: Сумма делителей
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        int total = 0;
        for (int i = 1; i * i <= n; i++) {
            if (n % i == 0) {
                total += i;
                if (i * i != n) total += n / i;
            }
        }
        out.println(total);
    }
