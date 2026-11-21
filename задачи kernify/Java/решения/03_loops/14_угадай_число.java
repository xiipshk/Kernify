// Решение: Угадай число
// Тема: Циклы (for, while)

    public static void solve() {
        int secret = new Random().nextInt(100) + 1;
        int attempts = 0;
        while (true) {
            int guess = in.nextInt();
            attempts++;
            if (guess < secret) out.println("Higher");
            else if (guess > secret) out.println("Lower");
            else { out.println("Correct! Attempts: " + attempts); break; }
        }
    }
