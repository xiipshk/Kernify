// Решение: Четное/нечетное
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    cout << (n % 2 == 0 ? "even" : "odd");
    return 0;
}
