// Решение: Угадай число
// Тема: Циклы (for, while)

function solve() {
    const secret = Math.floor(Math.random() * 100) + 1;
    let attempts = 0;
    while (true) {
        const guess = nextInt();
        attempts++;
        if (guess < secret) console.log("Higher");
        else if (guess > secret) console.log("Lower");
        else { console.log(`Correct! Attempts: ${attempts}`); break; }
    }
}
