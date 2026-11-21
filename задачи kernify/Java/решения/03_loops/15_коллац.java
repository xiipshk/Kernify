// Решение: Коллац
// Тема: Циклы (for, while)

    public static void solve() {
        long n = in.nextLong();
        int steps = 0;
        StringBuilder sb = new StringBuilder();
        while (n != 1) {
            sb.append(n).append(' ');
            n = n % 2 == 0 ? n / 2 : 3 * n + 1;
            steps++;
        }
        sb.append(1);
        out.println(sb.toString());
        out.println("Steps: " + steps);
    }
