// Решение: НОД (Евклид)
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b;
    cin >> a >> b;
    while (b) {
        int tmp = a % b;
        a = b;
        b = tmp;
    }
    cout << a;
    return 0;
}
