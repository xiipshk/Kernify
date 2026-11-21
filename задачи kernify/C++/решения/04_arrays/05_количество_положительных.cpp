// Решение: Количество положительных
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int count = 0;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        if (x > 0) count++;
    }
    cout << count;
    return 0;
}
