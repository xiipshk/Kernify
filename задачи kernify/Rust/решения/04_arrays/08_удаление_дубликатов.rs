// Решение: Удаление дубликатов
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .take(n)
        .map(|s| s.parse().unwrap())
        .collect();
    let mut seen = std::collections::HashSet::new();
    let mut result = Vec::new();
    for &v in &nums {
        if seen.insert(v) { result.push(v); }
    }
    for (i, &v) in result.iter().enumerate() {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", v).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
