// Решение: НОД (Евклид)
// Тема: Циклы (for, while)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        while (b != 0) {
            int tmp = a % b;
            a = b;
            b = tmp;
        }
        out.println(a);
    }
