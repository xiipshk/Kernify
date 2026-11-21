// Решение: Коллац
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut steps = 0;
    while n != 1 {
        write!(out, "{} ", n).unwrap();
        if n % 2 == 0 { n /= 2; } else { n = 3 * n + 1; }
        steps += 1;
    }
    writeln!(out, "1").unwrap();
    writeln!(out, "Steps: {}", steps).unwrap();
    out.flush().unwrap();
}
