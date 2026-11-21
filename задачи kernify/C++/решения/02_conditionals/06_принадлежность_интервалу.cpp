// Решение: Принадлежность интервалу
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b, x;
    cin >> a >> b >> x;
    cout << (a < x && x < b ? "YES" : "NO");
    return 0;
}
