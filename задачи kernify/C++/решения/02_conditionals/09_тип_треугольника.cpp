// Решение: Тип треугольника
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b, c;
    cin >> a >> b >> c;
    if (a == b && b == c) cout << "equilateral";
    else if (a == b || b == c || a == c) cout << "isosceles";
    else cout << "scalene";
    return 0;
}
