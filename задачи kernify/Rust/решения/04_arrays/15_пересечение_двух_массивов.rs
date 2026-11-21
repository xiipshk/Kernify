// Решение: Пересечение двух массивов
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let a: std::collections::HashSet<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(n).map(|s| s.parse().unwrap()).collect();
    let m: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let b: std::collections::HashSet<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(m).map(|s| s.parse().unwrap()).collect();
    let mut inter: Vec<i64> = a.intersection(&b).copied().collect();
    inter.sort();
    for (i, &v) in inter.iter().enumerate() {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", v).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
