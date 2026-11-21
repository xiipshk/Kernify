// Решение: Сумма цифр числа
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int total = 0;
    while (n > 0) {
        total += n % 10;
        n /= 10;
    }
    cout << total;
    return 0;
}
