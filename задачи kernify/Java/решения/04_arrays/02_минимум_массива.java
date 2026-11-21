// Решение: Минимум массива
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int min = Integer.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            int x = in.nextInt();
            if (x < min) min = x;
        }
        out.println(min);
    }
