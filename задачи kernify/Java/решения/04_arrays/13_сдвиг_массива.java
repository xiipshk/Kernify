// Решение: Сдвиг массива
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int k = in.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = in.nextInt();
        k %= n;
        int[] result = new int[n];
        for (int i = 0; i < n; i++) result[i] = arr[(i - k + n) % n];
        for (int i = 0; i < n; i++) { if (i > 0) out.print(' '); out.print(result[i]); }
        out.println();
    }
