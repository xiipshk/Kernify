// Решение: Слияние двух отсортированных
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let a: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(n).map(|s| s.parse().unwrap()).collect();
    let m: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let b: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(m).map(|s| s.parse().unwrap()).collect();
    let mut i = 0; let mut j = 0;
    let mut result = Vec::new();
    while i < n && j < m {
        if a[i] <= b[j] { result.push(a[i]); i += 1; }
        else { result.push(b[j]); j += 1; }
    }
    while i < n { result.push(a[i]); i += 1; }
    while j < m { result.push(b[j]); j += 1; }
    for (k, &v) in result.iter().enumerate() {
        if k > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", v).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
