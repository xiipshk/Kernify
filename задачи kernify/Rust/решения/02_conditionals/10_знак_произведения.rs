// Решение: Знак произведения
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (a, b) = (nums[0], nums[1]);
    let result = if a == 0 || b == 0 { "zero" }
        else if (a > 0) == (b > 0) { "positive" }
        else { "negative" };
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
