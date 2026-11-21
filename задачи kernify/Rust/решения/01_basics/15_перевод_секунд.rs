// Решение: Перевод секунд
// Тема: Основы: переменные, ввод/вывод, типы данных

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut s: i64 = lines.next().unwrap().unwrap().parse().unwrap();
    let h = s / 3600;
    s %= 3600;
    let m = s / 60;
    s %= 60;
    writeln!(out, "{} {} {}", h, m, s).unwrap();
    out.flush().unwrap();
}
