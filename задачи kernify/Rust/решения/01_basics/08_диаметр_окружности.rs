// Решение: Диаметр окружности
// Тема: Основы: переменные, ввод/вывод, типы данных

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let r: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    writeln!(out, "{}", 2 * r).unwrap();
    out.flush().unwrap();
}
