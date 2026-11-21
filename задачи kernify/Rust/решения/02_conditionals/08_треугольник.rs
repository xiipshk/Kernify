// Решение: Треугольник
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (a, b, c) = (nums[0], nums[1], nums[2]);
    let ok = a + b > c && a + c > b && b + c > a;
    writeln!(out, "{}", if ok { "YES" } else { "NO" }).unwrap();
    out.flush().unwrap();
}
