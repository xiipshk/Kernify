// Решение: Положительное/отрицательное
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let result = if n > 0 { "positive" } else if n < 0 { "negative" } else { "zero" };
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
