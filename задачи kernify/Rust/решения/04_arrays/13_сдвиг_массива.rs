// Решение: Сдвиг массива
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let first = lines.next().unwrap().unwrap();
    let parts: Vec<&str> = first.split_whitespace().collect();
    let n: usize = parts[0].parse().unwrap();
    let k: usize = parts[1].parse().unwrap();
    let arr: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(n).map(|s| s.parse().unwrap()).collect();
    let k = k % n;
    let mut result = Vec::new();
    result.extend_from_slice(&arr[n-k..]);
    result.extend_from_slice(&arr[..n-k]);
    for (i, &v) in result.iter().enumerate() {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", v).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
