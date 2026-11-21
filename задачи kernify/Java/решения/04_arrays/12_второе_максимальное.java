// Решение: Второе максимальное
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int first = Integer.MIN_VALUE, second = Integer.MIN_VALUE;
        for (int i = 0; i < n; i++) {
            int x = in.nextInt();
            if (x > first) { second = first; first = x; }
            else if (x > second && x != first) { second = x; }
        }
        out.println(second);
    }
