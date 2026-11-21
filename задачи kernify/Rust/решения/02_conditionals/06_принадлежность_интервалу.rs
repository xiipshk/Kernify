// Решение: Принадлежность интервалу
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (a, b, x) = (nums[0], nums[1], nums[2]);
    writeln!(out, "{}", if a < x && x < b { "YES" } else { "NO" }).unwrap();
    out.flush().unwrap();
}
