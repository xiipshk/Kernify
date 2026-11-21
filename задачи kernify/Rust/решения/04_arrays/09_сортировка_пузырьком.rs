// Решение: Сортировка пузырьком
// Тема: Массивы/списки (одномерные)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let mut nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .take(n)
        .map(|s| s.parse().unwrap())
        .collect();
    for i in 0..n {
        for j in 0..n-1-i {
            if nums[j] > nums[j+1] { nums.swap(j, j+1); }
        }
    }
    for (i, &v) in nums.iter().enumerate() {
        if i > 0 { write!(out, " ").unwrap(); }
        write!(out, "{}", v).unwrap();
    }
    writeln!(out).unwrap();
    out.flush().unwrap();
}
