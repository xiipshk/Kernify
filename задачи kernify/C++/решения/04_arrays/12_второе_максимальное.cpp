// Решение: Второе максимальное
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    int first = INT_MIN, second = INT_MIN;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        if (x > first) { second = first; first = x; }
        else if (x > second && x != first) { second = x; }
    }
    cout << second;
    return 0;
}
