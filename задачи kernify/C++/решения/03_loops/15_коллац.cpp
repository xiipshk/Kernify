// Решение: Коллац
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long n;
    cin >> n;
    int steps = 0;
    while (n != 1) {
        cout << n << ' ';
        n = n % 2 == 0 ? n / 2 : 3 * n + 1;
        steps++;
    }
    cout << 1 << '\n' << "Steps: " << steps;
    return 0;
}
