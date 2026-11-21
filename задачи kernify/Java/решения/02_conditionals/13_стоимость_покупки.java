// Решение: Стоимость покупки
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int n = in.nextInt();
        int a = in.nextInt();
        int b = in.nextInt();
        int total = n * a;
        if (total > b) total = (int)(total * 0.9);
        out.println(total);
    }
