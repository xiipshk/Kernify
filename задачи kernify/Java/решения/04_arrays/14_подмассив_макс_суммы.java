// Решение: Подмассив макс суммы
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = in.nextInt();
        int maxSum = arr[0], curr = arr[0];
        for (int i = 1; i < n; i++) {
            curr = Math.max(arr[i], curr + arr[i]);
            maxSum = Math.max(maxSum, curr);
        }
        out.println(maxSum);
    }
