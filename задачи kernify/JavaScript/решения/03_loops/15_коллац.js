// Решение: Коллац
// Тема: Циклы (for, while)

function solve() {
    let n = nextInt();
    let steps = 0;
    let seq = [];
    while (n !== 1) {
        seq.push(n);
        n = n % 2 === 0 ? n / 2 : 3 * n + 1;
        steps++;
    }
    seq.push(1);
    console.log(seq.join(' '));
    console.log("Steps: " + steps);
}
