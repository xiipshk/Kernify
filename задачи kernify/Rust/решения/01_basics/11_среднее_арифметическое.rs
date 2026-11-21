// Решение: Среднее арифметическое
// Тема: Основы: переменные, ввод/вывод, типы данных

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let nums: Vec<f64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    writeln!(out, "{:.6}", (nums[0] + nums[1] + nums[2]) / 3.0).unwrap();
    out.flush().unwrap();
}
