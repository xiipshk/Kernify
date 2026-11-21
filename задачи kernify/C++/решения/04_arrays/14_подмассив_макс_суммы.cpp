// Решение: Подмассив макс суммы
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    int maxSum = arr[0], curr = arr[0];
    for (int i = 1; i < n; i++) {
        curr = max(arr[i], curr + arr[i]);
        maxSum = max(maxSum, curr);
    }
    cout << maxSum;
    return 0;
}
