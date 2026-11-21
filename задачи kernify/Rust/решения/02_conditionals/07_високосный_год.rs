// Решение: Високосный год
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let y: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let leap = y % 400 == 0 || (y % 4 == 0 && y % 100 != 0);
    writeln!(out, "{}", if leap { "YES" } else { "NO" }).unwrap();
    out.flush().unwrap();
}
