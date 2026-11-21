// Решение: НОК
// Тема: Циклы (for, while)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        int gcd = a, tmp = b;
        while (tmp != 0) { int r = gcd % tmp; gcd = tmp; tmp = r; }
        out.println(a / gcd * b);
    }
