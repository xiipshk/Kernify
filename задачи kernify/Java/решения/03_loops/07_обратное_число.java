// Решение: Обратное число
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        int rev = 0;
        while (n > 0) {
            rev = rev * 10 + n % 10;
            n /= 10;
        }
        out.println(rev);
    }
