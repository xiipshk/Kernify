// Задача: Наибольшая возрастающая подпоследовательность
// Тема: Динамическое программирование
// Сложность: medium
// Описание: LIS O(n^2)
// Источник: ОГЭ/ЕГЭ информатика, Codeforces, acmp.ru, informatics.msk.ru

import java.util.*;
import java.io.*;

public class Main {
    static FastScanner in = new FastScanner(System.in);
    static PrintWriter out = new PrintWriter(System.out);

    public static void solve() {
    // TODO: Реализовать решение
    pass

    out.flush();
}

class FastScanner { BufferedReader br; StringTokenizer st; FastScanner(InputStream i) { br = new BufferedReader(new InputStreamReader(i)); } String next() { while (st == null || !st.hasMoreTokens()) try { st = new StringTokenizer(br.readLine()); } catch (IOException e) { e.printStackTrace(); } return st.nextToken(); } int nextInt() { return Integer.parseInt(next()); } }

