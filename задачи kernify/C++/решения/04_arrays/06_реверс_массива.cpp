// Решение: Реверс массива
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
    reverse(arr.begin(), arr.end());
    for (int i = 0; i < n; i++) {
        if (i) cout << ' ';
        cout << arr[i];
    }
    return 0;
}
