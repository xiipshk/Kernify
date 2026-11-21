// Решение: Четное/нечетное
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    writeln!(out, "{}", if n % 2 == 0 { "even" } else { "odd" }).unwrap();
    out.flush().unwrap();
}
