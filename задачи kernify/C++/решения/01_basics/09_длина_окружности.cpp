// Решение: Длина окружности
// Тема: Основы: переменные, ввод/вывод, типы данных

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    double r;
    cin >> r;
    cout << fixed << setprecision(6) << 2 * M_PI * r;
    return 0;
}
