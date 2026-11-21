// Решение: Афинное шифрование
// Тема: Циклы (for, while)

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let first_line = lines.next().unwrap().unwrap();
    let parts: Vec<&str> = first_line.split_whitespace().collect();
    let a: i64 = parts[0].parse().unwrap();
    let b: i64 = parts[1].parse().unwrap();
    let text = if parts.len() > 2 { parts[2..].join(" ") } else { lines.next().unwrap().unwrap() };
    let mut result = String::new();
    for ch in text.chars() {
        if ch.is_ascii_alphabetic() {
            let base = if ch.is_ascii_uppercase() { 'A' as u8 } else { 'a' as u8 } as i64;
            let x = ch as i64 - base;
            let y = (a * x + b) % 26;
            result.push((base + y) as u8 as char);
        } else {
            result.push(ch);
        }
    }
    writeln!(out, "{}", result).unwrap();
    out.flush().unwrap();
}
