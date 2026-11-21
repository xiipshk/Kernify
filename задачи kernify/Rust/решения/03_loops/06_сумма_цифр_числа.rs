// Решение: Сумма цифр числа
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut total = 0;
    while n > 0 {
        total += n % 10;
        n /= 10;
    }
    writeln!(out, "{}", total).unwrap();
    out.flush().unwrap();
}
