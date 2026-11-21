// Решение: Сумма цифр числа
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        int total = 0;
        while (n > 0) {
            total += n % 10;
            n /= 10;
        }
        out.println(total);
    }
