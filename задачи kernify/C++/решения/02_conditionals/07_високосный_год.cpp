// Решение: Високосный год
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int y;
    cin >> y;
    bool leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);
    cout << (leap ? "YES" : "NO");
    return 0;
}
