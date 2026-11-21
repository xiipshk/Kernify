// Решение: Афинное шифрование
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int a, b;
    string text;
    cin >> a >> b >> text;
    for (char &ch : text) {
        if (isalpha(ch)) {
            char base = isupper(ch) ? 'A' : 'a';
            int x = ch - base;
            int y = (a * x + b) % 26;
            ch = base + y;
        }
    }
    cout << text;
    return 0;
}
