// Решение: НОД (Евклид)
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let mut a = nums[0];
    let mut b = nums[1];
    while b != 0 {
        let tmp = a % b;
        a = b;
        b = tmp;
    }
    writeln!(out, "{}", a).unwrap();
    out.flush().unwrap();
}
