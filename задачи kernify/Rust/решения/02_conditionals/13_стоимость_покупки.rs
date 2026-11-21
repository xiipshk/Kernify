// Решение: Стоимость покупки
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (n, a, b) = (nums[0], nums[1], nums[2]);
    let mut total = n * a;
    if total > b {
        total = total * 9 / 10;
    }
    writeln!(out, "{}", total).unwrap();
    out.flush().unwrap();
}
