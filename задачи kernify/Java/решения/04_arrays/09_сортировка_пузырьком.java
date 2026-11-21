// Решение: Сортировка пузырьком
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = in.nextInt();
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    int tmp = arr[j]; arr[j] = arr[j + 1]; arr[j + 1] = tmp;
                }
            }
        }
        for (int i = 0; i < n; i++) { if (i > 0) out.print(' '); out.print(arr[i]); }
        out.println();
    }
