// Решение: Второе максимальное
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(n).map(|s| s.parse().unwrap()).collect();
    let mut first = i64::MIN;
    let mut second = i64::MIN;
    for &x in &nums {
        if x > first { second = first; first = x; }
        else if x > second && x != first { second = x; }
    }
    writeln!(out, "{}", second).unwrap();
    out.flush().unwrap();
}
