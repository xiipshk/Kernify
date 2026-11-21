// Решение: Удаление дубликатов
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    unordered_set<int> seen;
    vector<int> result;
    for (int i = 0; i < n; i++) {
        int x; cin >> x;
        if (seen.insert(x).second) result.push_back(x);
    }
    for (int i = 0; i < result.size(); i++) {
        if (i) cout << ' ';
        cout << result[i];
    }
    return 0;
}
