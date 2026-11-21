// Решение: Сдвиг массива
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    k %= n;
    rotate(arr.begin(), arr.end() - k, arr.end());
    for (int i = 0; i < n; i++) { if (i) cout << ' '; cout << arr[i]; }
    return 0;
}
