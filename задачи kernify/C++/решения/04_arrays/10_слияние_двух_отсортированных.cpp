// Решение: Слияние двух отсортированных
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> a(n); for (int i = 0; i < n; i++) cin >> a[i];
    int m; cin >> m;
    vector<int> b(m); for (int i = 0; i < m; i++) cin >> b[i];
    vector<int> result;
    int i = 0, j = 0;
    while (i < n && j < m) {
        if (a[i] <= b[j]) result.push_back(a[i++]);
        else result.push_back(b[j++]);
    }
    while (i < n) result.push_back(a[i++]);
    while (j < m) result.push_back(b[j++]);
    for (int k = 0; k < result.size(); k++) { if (k) cout << ' '; cout << result[k]; }
    return 0;
}
