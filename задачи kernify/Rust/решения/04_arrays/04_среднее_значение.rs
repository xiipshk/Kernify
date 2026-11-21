// Решение: Среднее значение
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
    writeln!(out, "{:.6}", sum as f64 / n as f64).unwrap();
    out.flush().unwrap();
}
