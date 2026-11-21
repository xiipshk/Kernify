// Решение: Координатные четверти
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int x = in.nextInt();
        int y = in.nextInt();
        if (x > 0 && y > 0) out.println(1);
        else if (x < 0 && y > 0) out.println(2);
        else if (x < 0 && y < 0) out.println(3);
        else if (x > 0 && y < 0) out.println(4);
        else out.println("on axis");
    }
