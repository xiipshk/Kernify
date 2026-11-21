// Решение: Минимум массива
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
    let min_val = nums.iter().min().unwrap();
    writeln!(out, "{}", min_val).unwrap();
    out.flush().unwrap();
}
