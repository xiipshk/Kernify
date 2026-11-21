// Решение: Квадрат/прямоугольник
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    writeln!(out, "{}", if nums[0] == nums[1] { "square" } else { "rectangle" }).unwrap();
    out.flush().unwrap();
}
