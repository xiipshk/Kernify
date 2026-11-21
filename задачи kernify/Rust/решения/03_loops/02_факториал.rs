// Решение: Факториал
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: u64 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut result: u64 = 1;
    for i in 2..=n {
        result *= i;
    }
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
