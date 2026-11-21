// Решение: Афинное шифрование
// Тема: Циклы (for, while)

    public static void solve() {
        int a = in.nextInt();
        int b = in.nextInt();
        String text = in.next();
        StringBuilder sb = new StringBuilder();
        for (char ch : text.toCharArray()) {
            if (Character.isLetter(ch)) {
                char base = Character.isUpperCase(ch) ? 'A' : 'a';
                int x = ch - base;
                int y = (a * x + b) % 26;
                sb.append((char)(base + y));
            } else sb.append(ch);
        }
        out.println(sb.toString());
    }
