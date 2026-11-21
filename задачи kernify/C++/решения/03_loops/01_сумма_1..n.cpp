// Решение: Сумма 1..N
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long n;
    cin >> n;
    cout << n * (n + 1) / 2;
    return 0;
}
