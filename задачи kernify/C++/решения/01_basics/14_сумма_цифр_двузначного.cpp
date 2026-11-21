// Решение: Сумма цифр двузначного
// Тема: Основы: переменные, ввод/вывод, типы данных

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    cout << n / 10 + n % 10;
    return 0;
}
