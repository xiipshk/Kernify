// Решение: Сумма элементов
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let sum: i64 = lines.next().unwrap().unwrap()
        .split_whitespace()
        .take(n)
        .map(|s| s.parse::<i64>().unwrap())
        .sum();
    writeln!(out, "{}", sum).unwrap();
    out.flush().unwrap();
}
