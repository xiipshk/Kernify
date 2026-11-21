// Решение: Минимум из трех
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let m = nums[0].min(nums[1]).min(nums[2]);
    writeln!(out, "{}", m).unwrap();
    out.flush().unwrap();
}
