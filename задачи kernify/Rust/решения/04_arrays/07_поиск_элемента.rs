// Решение: Поиск элемента
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .take(n)
        .map(|s| s.parse().unwrap())
        .collect();
    let x: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let idx = nums.iter().position(|&v| v == x).unwrap_or(-1);
    writeln!(out, "{}", idx).unwrap();
    out.flush().unwrap();
}
