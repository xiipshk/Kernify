// Решение: Количество делителей
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut count = 0;
    let mut i = 1;
    while i * i <= n {
        if n % i == 0 {
            count += if i * i == n { 1 } else { 2 };
        }
        i += 1;
    }
    writeln!(out, "{}", count).unwrap();
    out.flush().unwrap();
}
