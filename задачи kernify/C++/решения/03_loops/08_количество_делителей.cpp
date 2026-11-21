// Решение: Количество делителей
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int count = 0;
    for (int i = 1; i * i <= n; i++) {
        if (n % i == 0) count += (i * i == n) ? 1 : 2;
    }
    cout << count;
    return 0;
}
