// Решение: Високосный год
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int y = in.nextInt();
        boolean leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);
        out.println(leap ? "YES" : "NO");
    }
