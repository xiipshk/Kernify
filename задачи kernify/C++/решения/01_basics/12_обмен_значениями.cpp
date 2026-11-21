// Решение: Обмен значениями
// Тема: Основы: переменные, ввод/вывод, типы данных

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b;
    cin >> a >> b;
    swap(a, b);
    cout << a << " " << b;
    return 0;
}
