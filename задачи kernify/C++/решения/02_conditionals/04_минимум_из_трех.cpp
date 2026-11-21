// Решение: Минимум из трех
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b, c;
    cin >> a >> b >> c;
    cout << min({a, b, c});
    return 0;
}
