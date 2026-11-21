// Решение: Максимум массива
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    int max_val = INT_MIN;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        max_val = max(max_val, x);
    }
    cout << max_val;
    return 0;
}
