// Решение: Знак произведения
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b;
    cin >> a >> b;
    if (a == 0 || b == 0) cout << "zero";
    else if ((a > 0) == (b > 0)) cout << "positive";
    else cout << "negative";
    return 0;
}
