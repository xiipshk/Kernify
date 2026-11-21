// Решение: Поиск элемента
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<int> arr(n);
    for (int i = 0; i < n; i++) cin >> arr[i];
    int x; cin >> x;
    int idx = -1;
    for (int i = 0; i < n; i++) if (arr[i] == x) { idx = i; break; }
    cout << idx;
    return 0;
}
