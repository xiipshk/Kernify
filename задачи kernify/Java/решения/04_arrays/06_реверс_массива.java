// Решение: Реверс массива
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = in.nextInt();
        for (int i = n - 1; i >= 0; i--) {
            out.print(arr[i]);
            if (i > 0) out.print(' ');
        }
        out.println();
    }
