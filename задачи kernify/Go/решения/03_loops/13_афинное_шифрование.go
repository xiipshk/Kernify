// Решение: Афинное шифрование
// Тема: Циклы (for, while)

func solve() {
    a, b := nextInt(), nextInt()
    text := next()
    var result strings.Builder
    for _, ch := range text {
        if ch >= 'A' && ch <= 'Z' || ch >= 'a' && ch <= 'z' {
            base := rune('A')
            if ch >= 'a' {
                base = 'a'
            }
            x := ch - base
            y := (a*int(x) + b) % 26
            result.WriteRune(base + rune(y))
        } else {
            result.WriteRune(ch)
        }
    }
    println(result.String())
}
