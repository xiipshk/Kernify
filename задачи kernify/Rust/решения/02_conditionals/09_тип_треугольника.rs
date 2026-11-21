// Решение: Тип треугольника
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
    let result = if a == b && b == c { "equilateral" }
        else if a == b || b == c || a == c { "isosceles" }
        else { "scalene" };
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
