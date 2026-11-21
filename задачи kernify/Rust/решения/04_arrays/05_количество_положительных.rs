// Решение: Количество положительных
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let count = lines.next().unwrap().unwrap()
        .split_whitespace()
        .take(n)
        .filter(|s| s.parse::<i64>().unwrap() > 0)
        .count();
    writeln!(out, "{}", count).unwrap();
    out.flush().unwrap();
}
