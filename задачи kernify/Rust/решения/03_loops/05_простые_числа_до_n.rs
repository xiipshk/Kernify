// Решение: Простые числа до N
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let mut sieve = vec![true; n + 1];
    if n >= 1 { sieve[0] = false; }
    if n >= 1 { sieve[1] = false; }
    for i in 2..=n {
        if i * i > n { break; }
        if sieve[i] {
            for j in (i*i..=n).step_by(i) {
                sieve[j] = false;
            }
        }
    }
    let mut first = true;
    for i in 2..=n {
        if sieve[i] {
            if !first { write!(out, " ").unwrap(); }
            first = false;
            write!(out, "{}", i).unwrap();
        }
    }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
