// Решение: Дни недели
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        String[] days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"};
        int n = in.nextInt();
        out.println(days[(n - 1) % 7]);
    }
