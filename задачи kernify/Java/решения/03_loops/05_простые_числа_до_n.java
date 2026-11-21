// Решение: Простые числа до N
// Тема: Циклы (for, while)

    public static void solve() {
        int n = in.nextInt();
        boolean[] sieve = new boolean[n + 1];
        Arrays.fill(sieve, true);
        sieve[0] = sieve[1] = false;
        for (int i = 2; i * i <= n; i++) {
            if (sieve[i]) {
                for (int j = i * i; j <= n; j += i) sieve[j] = false;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 2; i <= n; i++) if (sieve[i]) sb.append(i).append(' ');
        out.println(sb.toString().trim());
    }
