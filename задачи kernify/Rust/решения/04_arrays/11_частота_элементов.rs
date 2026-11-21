// Решение: Частота элементов
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(n).map(|s| s.parse().unwrap()).collect();
    let mut freq = std::collections::BTreeMap::new();
    for &v in &nums { *freq.entry(v).or_insert(0) += 1; }
    for (k, v) in freq { writeln!(out, "{} {}", k, v).unwrap(); }
    out.flush().unwrap();
}
