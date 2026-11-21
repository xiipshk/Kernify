// Решение: Степень
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (a, n) = (nums[0], nums[1] as u32);
    let mut result: i64 = 1;
    for _ in 0..n {
        result *= a;
    }
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
