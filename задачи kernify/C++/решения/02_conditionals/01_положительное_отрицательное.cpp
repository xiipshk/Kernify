// Решение: Положительное/отрицательное
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    if (n > 0) cout << "positive";
    else if (n < 0) cout << "negative";
    else cout << "zero";
    return 0;
}
