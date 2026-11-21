// Решение: Знак произведения
// Тема: Условные операторы (if, else, elif)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        if (a == 0 || b == 0) out.println("zero");
        else if ((a > 0) == (b > 0)) out.println("positive");
        else out.println("negative");
    }
