// Решение: Подмассив макс суммы
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let arr: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace().take(n).map(|s| s.parse().unwrap()).collect();
    let mut max_sum = arr[0];
    let mut curr = arr[0];
    for &x in &arr[1..] {
        curr = x.max(curr + x);
        max_sum = max_sum.max(curr);
    }
    writeln!(out, "{}", max_sum).unwrap();
    out.flush().unwrap();
}
