// Решение: Сумма делителей
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int total = 0;
    for (int i = 1; i * i <= n; i++) {
        if (n % i == 0) {
            total += i;
            if (i * i != n) total += n / i;
        }
    }
    cout << total;
    return 0;
}
