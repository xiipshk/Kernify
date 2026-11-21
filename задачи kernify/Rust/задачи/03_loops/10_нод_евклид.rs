// Задача: НОД (Евклид)
// Тема: Циклы (for, while)
// Сложность: medium
// Описание: while b: a,b = b,a%b
// Источник: ОГЭ/ЕГЭ информатика, Codeforces, acmp.ru, informatics.msk.ru

use std::io::{self, BufRead, Write};

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let mut out = io::BufWriter::new(io::stdout());
    let mut next_line = || lines.next().unwrap().unwrap();
    let mut next_int = || next_line().parse::<i64>().unwrap();
    let mut next_ints = || next_line().split_whitespace().map(|s| s.parse::<i64>().unwrap()).collect::<Vec<_>>();

    // TODO: Реализовать решение

    out.flush().unwrap();
}
