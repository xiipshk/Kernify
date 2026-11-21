// Решение: Среднее арифметическое
// Тема: Основы: переменные, ввод/вывод, типы данных

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    double a, b, c;
    cin >> a >> b >> c;
    cout << fixed << setprecision(6) << (a + b + c) / 3.0;
    return 0;
}
