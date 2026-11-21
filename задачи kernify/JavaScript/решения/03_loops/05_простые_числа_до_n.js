// Решение: Простые числа до N
// Тема: Циклы (for, while)

function solve() {
    const n = nextInt();
    const sieve = new Array(n + 1).fill(true);
    sieve[0] = sieve[1] = false;
    for (let i = 2; i * i <= n; i++) {
        if (sieve[i]) {
            for (let j = i * i; j <= n; j += i) sieve[j] = false;
        }
    }
    const primes = [];
    for (let i = 2; i <= n; i++) if (sieve[i]) primes.push(i);
    console.log(primes.join(' '));
}
