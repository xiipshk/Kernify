// Решение: Поиск элемента
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = in.nextInt();
        int x = in.nextInt();
        int idx = -1;
        for (int i = 0; i < n; i++) if (arr[i] == x) { idx = i; break; }
        out.println(idx);
    }
