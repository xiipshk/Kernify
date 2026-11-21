// Решение: Удаление дубликатов
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        Set<Integer> seen = new LinkedHashSet<>();
        for (int i = 0; i < n; i++) seen.add(in.nextInt());
        out.println(seen.stream().map(String::valueOf).collect(Collectors.joining(" ")));
    }
