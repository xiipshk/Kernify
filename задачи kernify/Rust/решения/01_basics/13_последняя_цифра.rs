// Решение: Последняя цифра
// Тема: Основы: переменные, ввод/вывод, типы данных

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let n: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    writeln!(out, "{}", n.abs() % 10).unwrap();
    out.flush().unwrap();
}
