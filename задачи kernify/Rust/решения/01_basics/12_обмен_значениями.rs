// Решение: Обмен значениями
// Тема: Основы: переменные, ввод/вывод, типы данных

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut nums: Vec<i64> = lines.next().unwrap().unwrap()
        .split_whitespace()
        .map(|s| s.parse().unwrap())
        .collect();
    nums.swap(0, 1);
    writeln!(out, "{} {}", nums[0], nums[1]).unwrap();
    out.flush().unwrap();
}
