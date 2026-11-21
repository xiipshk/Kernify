// Решение: Координатные четверти
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (x, y) = (nums[0], nums[1]);
    let result = if x > 0 && y > 0 { "1" }
        else if x < 0 && y > 0 { "2" }
        else if x < 0 && y < 0 { "3" }
        else if x > 0 && y < 0 { "4" }
        else { "on axis" };
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
