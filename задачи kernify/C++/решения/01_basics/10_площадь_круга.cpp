// Решение: Площадь круга
// Тема: Основы: переменные, ввод/вывод, типы данных

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    double r;
    cin >> r;
    cout << fixed << setprecision(6) << M_PI * r * r;
    return 0;
}
