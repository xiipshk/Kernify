// Решение: Угадай число
// Тема: Циклы (for, while)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    srand(time(0));
    int secret = rand() % 100 + 1;
    int attempts = 0, guess;
    while (cin >> guess) {
        attempts++;
        if (guess < secret) cout << "Higher\n";
        else if (guess > secret) cout << "Lower\n";
        else { cout << "Correct! Attempts: " << attempts << "\n"; break; }
    }
    return 0;
}
