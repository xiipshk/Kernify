// Решение: Площадь круга
// Тема: Основы: переменные, ввод/вывод, типы данных

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let r: f64 = lines.next().unwrap().unwrap().parse().unwrap();
    writeln!(out, "{:.6}", std::f64::consts::PI * r * r).unwrap();
    out.flush().unwrap();
}
