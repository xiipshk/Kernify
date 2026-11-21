// Решение: Степень
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, n;
    cin >> a >> n;
    long long result = 1;
    for (int i = 0; i < n; i++) result *= a;
    cout << result;
    return 0;
}
