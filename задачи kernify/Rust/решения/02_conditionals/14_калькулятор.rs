// Решение: Калькулятор
// Тема: Условные операторы (if, else, elif)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let parts: Vec<String> = lines.next().unwrap().unwrap().split_whitespace().map(|s| s.to_string()).collect();
    let a: f64 = parts[0].parse().unwrap();
    let op = &parts[1];
    let b: f64 = parts[2].parse().unwrap();
    let result = match op.as_str() {
        "+" => a + b,
        "-" => a - b,
        "*" => a * b,
        "/" => if b == 0.0 { 
            writeln!(out, "Division by zero").unwrap(); 
            out.flush().unwrap(); 
            return; 
        } else { a / b },
        _ => { writeln!(out, "Invalid operator").unwrap(); out.flush().unwrap(); return; }
    };
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
