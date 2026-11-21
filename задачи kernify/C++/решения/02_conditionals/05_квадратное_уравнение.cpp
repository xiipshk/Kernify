// Решение: Квадратное уравнение
// Тема: Условные операторы (if, else, elif)

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    double a, b, c;
    cin >> a >> b >> c;
    double d = b*b - 4*a*c;
    if (d < 0) cout << "No roots";
    else if (d == 0) cout << fixed << setprecision(6) << -b / (2*a);
    else {
        double x1 = (-b - sqrt(d)) / (2*a);
        double x2 = (-b + sqrt(d)) / (2*a);
        cout << fixed << setprecision(6) << x1 << " " << x2;
    }
    return 0;
}
