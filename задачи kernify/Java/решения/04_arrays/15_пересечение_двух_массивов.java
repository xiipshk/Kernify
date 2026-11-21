// Решение: Пересечение двух массивов
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        Set<Integer> a = new HashSet<>();
        for (int i = 0; i < n; i++) a.add(in.nextInt());
        int m = in.nextInt();
        Set<Integer> b = new HashSet<>();
        for (int i = 0; i < m; i++) b.add(in.nextInt());
        a.retainAll(b);
        List<Integer> list = new ArrayList<>(a);
        Collections.sort(list);
        out.println(list.stream().map(String::valueOf).collect(Collectors.joining(" ")));
    }
