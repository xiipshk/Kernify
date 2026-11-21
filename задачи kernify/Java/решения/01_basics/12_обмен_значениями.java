// Решение: Обмен значениями
// Тема: Основы: переменные, ввод/вывод, типы данных

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        int temp = a;
        a = b;
        b = temp;
        out.println(a + " " + b);
    }
