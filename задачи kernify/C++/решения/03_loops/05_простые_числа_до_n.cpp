// Решение: Простые числа до N
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<bool> sieve(n + 1, true);
    sieve[0] = sieve[1] = false;
    for (int i = 2; i * i <= n; i++) {
        if (sieve[i]) {
            for (int j = i * i; j <= n; j += i) sieve[j] = false;
        }
    }
    bool first = true;
    for (int i = 2; i <= n; i++) {
        if (sieve[i]) {
            if (!first) cout << ' ';
            first = false;
            cout << i;
        }
    }
    return 0;
}
