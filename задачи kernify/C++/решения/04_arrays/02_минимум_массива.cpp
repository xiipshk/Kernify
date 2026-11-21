// Решение: Минимум массива
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int min_val = INT_MAX;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        min_val = min(min_val, x);
    }
    cout << min_val;
    return 0;
}
