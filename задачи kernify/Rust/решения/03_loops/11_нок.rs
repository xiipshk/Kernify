// Решение: НОК
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (mut a, mut b) = (nums[0], nums[1]);
    let (mut g, mut t) = (a, b);
    while t != 0 {
        let r = g % t;
        g = t;
        t = r;
    }
    writeln!(out, "{}", a / g * b).unwrap();
    out.flush().unwrap();
}
