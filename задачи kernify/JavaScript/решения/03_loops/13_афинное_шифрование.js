// Решение: Афинное шифрование
// Тема: Циклы (for, while)

function solve() {
    const a = nextInt();
    const b = nextInt();
    const text = next(); // reads next word, for full line need different approach
    let result = '';
    for (const ch of text) {
        if (/[a-zA-Z]/.test(ch)) {
            const base = ch === ch.toUpperCase() ? 'A'.charCodeAt(0) : 'a'.charCodeAt(0);
            const x = ch.charCodeAt(0) - base;
            const y = (a * x + b) % 26;
            result += String.fromCharCode(base + y);
        } else {
            result += ch;
        }
    }
    console.log(result);
}
