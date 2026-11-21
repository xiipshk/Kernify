// Решение: Перевод секунд
// Тема: Основы: переменные, ввод/вывод, типы данных

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int s;
    cin >> s;
    int h = s / 3600;
    s %= 3600;
    int m = s / 60;
    s %= 60;
    cout << h << " " << m << " " << s;
    return 0;
}
