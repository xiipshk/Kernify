// Решение: Квадратное уравнение
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<f64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    let (a, b, c) = (nums[0], nums[1], nums[2]);
    let d = b*b - 4.0*a*c;
    if d < 0.0 {
        writeln!(out, "No roots").unwrap();
    } else if d == 0.0 {
        writeln!(out, "{:.6}", -b / (2.0*a)).unwrap();
    } else {
        let x1 = (-b - d.sqrt()) / (2.0*a);
        let x2 = (-b + d.sqrt()) / (2.0*a);
        writeln!(out, "{:.6} {:.6}", x1, x2).unwrap();
    }
    out.flush().unwrap();
}
