// Решение: Числа Фибоначчи
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    long long a = 0, b = 1;
    for (int i = 0; i < n; i++) {
        long long tmp = a + b;
        a = b;
        b = tmp;
    }
    cout << a;
    return 0;
}
