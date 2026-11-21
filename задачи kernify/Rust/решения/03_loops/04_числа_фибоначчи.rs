// Решение: Числа Фибоначчи
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: u32 = lines.next().unwrap().unwrap().parse().unwrap();
    let mut a: i64 = 0;
    let mut b: i64 = 1;
    for _ in 0..n {
        let tmp = a + b;
        a = b;
        b = tmp;
    }
    writeln!(out, "{}", a).unwrap();
    out.flush().unwrap();
}
