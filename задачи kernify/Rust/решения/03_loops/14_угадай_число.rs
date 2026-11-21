// Решение: Угадай число
// Тема: Циклы (for, while)

fn main() {
    use rand::Rng;
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let secret = rand::thread_rng().gen_range(1..=100);
    let mut attempts = 0;
    while let Some(Ok(line)) = lines.next() {
        let guess: i32 = line.trim().parse().unwrap();
        attempts += 1;
        if guess < secret {
            writeln!(out, "Higher").unwrap();
        } else if guess > secret {
            writeln!(out, "Lower").unwrap();
        } else {
            writeln!(out, "Correct! Attempts: {}", attempts).unwrap();
            break;
        }
    }
    out.flush().unwrap();
}
