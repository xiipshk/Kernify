// Решение: Калькулятор
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    double a, b;
    char op;
    cin >> a >> op >> b;
    switch (op) {
        case '+': cout << a + b; break;
        case '-': cout << a - b; break;
        case '*': cout << a * b; break;
        case '/':
            if (b == 0) cout << "Division by zero";
            else cout << a / b;
            break;
        default: cout << "Invalid operator";
    }
    return 0;
}
