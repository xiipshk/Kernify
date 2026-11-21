// Решение: Таблица умножения
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    for i in 1..=n {
        for j in 1..=n {
            write!(out, "{}", i * j).unwrap();
            if j < n { write!(out, " ").unwrap(); }
        }
        writeln!(out).unwrap();
    }
    out.flush().unwrap();
}
