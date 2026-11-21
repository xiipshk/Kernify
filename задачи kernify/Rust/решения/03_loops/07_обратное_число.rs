// Решение: Обратное число
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut rev = 0;
    while n > 0 {
        rev = rev * 10 + n % 10;
        n /= 10;
    }
    writeln!(out, "{}", rev).unwrap();
    out.flush().unwrap();
}
