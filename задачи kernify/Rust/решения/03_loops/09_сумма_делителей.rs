// Решение: Сумма делителей
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut total = 0;
    let mut i = 1;
    while i * i <= n {
        if n % i == 0 {
            total += i;
            if i * i != n {
                total += n / i;
            }
        }
        i += 1;
    }
    writeln!(out, "{}", total).unwrap();
    out.flush().unwrap();
}
