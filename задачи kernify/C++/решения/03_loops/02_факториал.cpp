// Решение: Факториал
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    long long result = 1;
    for (int i = 2; i <= n; i++) result *= i;
    cout << result;
    return 0;
}
