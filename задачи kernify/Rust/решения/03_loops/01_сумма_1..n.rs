// Решение: Сумма 1..N
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    writeln!(out, "{}", n * (n + 1) / 2).unwrap();
    out.flush().unwrap();
}
