// Решение: Частота элементов
// Тема: Массивы/списки (одномерные)

    public static void solve() {
        int n = in.nextInt();
        Map<Integer, Integer> map = new TreeMap<>();
        for (int i = 0; i < n; i++) {
            int x = in.nextInt();
            map.put(x, map.getOrDefault(x, 0) + 1);
        }
        for (Map.Entry<Integer, Integer> e : map.entrySet()) {
            out.println(e.getKey() + " " + e.getValue());
        }
    }
