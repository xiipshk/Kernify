// Решение: Пересечение двух массивов
// Тема: Массивы/списки (одномерные)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    unordered_set<int> a; for (int i = 0; i < n; i++) { int x; cin >> x; a.insert(x); }
    int m; cin >> m;
    unordered_set<int> b; for (int i = 0; i < m; i++) { int x; cin >> x; b.insert(x); }
    vector<int> inter;
    for (int x : a) if (b.count(x)) inter.push_back(x);
    sort(inter.begin(), inter.end());
    for (int i = 0; i < inter.size(); i++) { if (i) cout << ' '; cout << inter[i]; }
    return 0;
}
