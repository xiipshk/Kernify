// Решение: НОК
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, b;
    cin >> a >> b;
    long long g = a, t = b;
    while (t) { long long r = g % t; g = t; t = r; }
    cout << a / g * b;
    return 0;
}
