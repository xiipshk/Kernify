// Решение: Перевод секунд
// Тема: Основы: переменные, ввод/вывод, типы данных

    public static void solve() {
        int s = in.nextInt();
        int h = s / 3600;
        s %= 3600;
        int m = s / 60;
        s %= 60;
        out.println(h + " " + m + " " + s);
    }
