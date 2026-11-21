// Решение: Дни недели
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    writeln!(out, "{}", days[(n - 1) % 7]).unwrap();
    out.flush().unwrap();
}
