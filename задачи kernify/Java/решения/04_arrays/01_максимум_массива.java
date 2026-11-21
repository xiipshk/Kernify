// Решение: Максимум массива
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int max = Integer.MIN_VALUE;
        for (int i = 0; i < n; i++) {
            int x = in.nextInt();
            if (x > max) max = x;
        }
        out.println(max);
    }
