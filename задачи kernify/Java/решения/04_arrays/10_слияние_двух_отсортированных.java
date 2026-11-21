// Решение: Слияние двух отсортированных
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = in.nextInt();
        int m = in.nextInt();
        int[] b = new int[m];
        for (int i = 0; i < m; i++) b[i] = in.nextInt();
        int i = 0, j = 0;
        List<Integer> result = new ArrayList<>();
        while (i < n && j < m) {
            if (a[i] <= b[j]) result.add(a[i++]);
            else result.add(b[j++]);
        }
        while (i < n) result.add(a[i++]);
        while (j < m) result.add(b[j++]);
        out.println(result.stream().map(String::valueOf).collect(Collectors.joining(" ")));
    }
