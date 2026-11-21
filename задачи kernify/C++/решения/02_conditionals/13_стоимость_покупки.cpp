// Решение: Стоимость покупки
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, a, b;
    cin >> n >> a >> b;
    int total = n * a;
    if (total > b) total = total * 9 / 10;
    cout << total;
    return 0;
}
