"""
Банк практических задач для генератора.

Каждое упражнение — это классическая задача с вводом/выводом (в духе acmp.ru,
Project Euler, LeetCode easy), с эталонным решением на исполняемых языках сайта
(Python, C++, JavaScript, Rust).

CSS-задания вынесены отдельно (CSS не исполняется как программа).

Формат упражнения:
    id, title, statement, category, difficulty,
    tests: [(вход, ожидаемый вывод), ...],
    solutions: {lang_slug: код}
"""

# ---------------------------------------------------------------------------
# Кодинг-упражнения (общие для исполняемых языков)
# ---------------------------------------------------------------------------

EXERCISES = [
    # ======================= БАЗЫ =======================
    {
        'id': 'sum_two',
        'title': 'Сумма двух чисел',
        'statement': 'Даны два целых числа a и b (каждое на своей строке). Выведите их сумму.',
        'category': 'basics', 'difficulty': 1,
        'tests': [('2\n3\n', '5'), ('-4\n10\n', '6'), ('100\n250\n', '350')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nprint(a + b)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    std::cout << a + b << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(a + b);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{}", v[0] + v[1]);\n}\n',
        },
    },
    {
        'id': 'diff_two',
        'title': 'Разность двух чисел',
        'statement': 'Даны два целых числа a и b. Выведите a − b.',
        'category': 'basics', 'difficulty': 1,
        'tests': [('10\n3\n', '7'), ('3\n10\n', '-7')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nprint(a - b)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    std::cout << a - b << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(a - b);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{}", v[0] - v[1]);\n}\n',
        },
    },
    {
        'id': 'product_two',
        'title': 'Произведение',
        'statement': 'Даны два целых числа a и b. Выведите их произведение.',
        'category': 'basics', 'difficulty': 1,
        'tests': [('6\n7\n', '42'), ('-3\n5\n', '-15')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nprint(a * b)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    std::cout << a * b << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(a * b);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{}", v[0] * v[1]);\n}\n',
        },
    },
    {
        'id': 'square_number',
        'title': 'Квадрат числа',
        'statement': 'Дано целое число n. Выведите n².',
        'category': 'basics', 'difficulty': 1,
        'tests': [('5\n', '25'), ('-9\n', '81')],
        'solutions': {
            'python': 'n = int(input())\nprint(n * n)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    std::cout << n * n << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(n * n);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    println!("{}", n * n);\n}\n',
        },
    },
    {
        'id': 'rect_area',
        'title': 'Площадь прямоугольника',
        'statement': 'Даны стороны прямоугольника a и b. Выведите его площадь.',
        'category': 'basics', 'difficulty': 1,
        'tests': [('3\n4\n', '12'), ('7\n5\n', '35')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nprint(a * b)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    std::cout << a * b << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(a * b);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{}", v[0] * v[1]);\n}\n',
        },
    },
    {
        'id': 'last_digit',
        'title': 'Последняя цифра',
        'statement': 'Дано целое число n. Выведите его последнюю цифру.',
        'category': 'basics', 'difficulty': 1,
        'tests': [('1234\n', '4'), ('90\n', '0')],
        'solutions': {
            'python': 'n = int(input())\nprint(abs(n) % 10)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    if (n < 0) n = -n;\n    std::cout << n % 10 << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(Math.abs(n) % 10);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    println!("{}", n.abs() % 10);\n}\n',
        },
    },
    {
        'id': 'avg_three',
        'title': 'Среднее арифметическое (целое)',
        'statement': 'Даны три целых числа. Выведите их среднее арифметическое, округлённое вниз (целочисленное деление).',
        'category': 'basics', 'difficulty': 2,
        'tests': [('2\n4\n6\n', '4'), ('3\n6\n9\n', '6')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nc = int(input())\nprint((a + b + c) // 3)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b, c;\n    std::cin >> a >> b >> c;\n    std::cout << (a + b + c) / 3 << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b, c] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(Math.trunc((a + b + c) / 3));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{}", (v[0] + v[1] + v[2]) / 3);\n}\n',
        },
    },
    {
        'id': 'swap_two',
        'title': 'Обмен значений',
        'statement': 'Даны два числа a и b. Выведите их в обратном порядке (сначала b, затем a).',
        'category': 'basics', 'difficulty': 1,
        'tests': [('1\n2\n', '2 1'), ('5\n9\n', '9 5')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nprint(b, a)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    std::cout << b << " " << a << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(b + " " + a);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{} {}", v[1], v[0]);\n}\n',
        },
    },

    # ======================= УСЛОВИЯ =======================
    {
        'id': 'max_two',
        'title': 'Максимум из двух',
        'statement': 'Даны два числа. Выведите большее из них.',
        'category': 'conditionals', 'difficulty': 1,
        'tests': [('3\n7\n', '7'), ('10\n2\n', '10'), ('5\n5\n', '5')],
        'solutions': {
            'python': 'a = int(input())\nb = int(input())\nprint(max(a, b))\n',
            'cpp': '#include <iostream>\nint main() {\n    long long a, b;\n    std::cin >> a >> b;\n    std::cout << (a > b ? a : b) << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconsole.log(Math.max(a, b));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    println!("{}", v[0].max(v[1]));\n}\n',
        },
    },
    {
        'id': 'even_odd',
        'title': 'Чётное или нечётное',
        'statement': 'Дано целое число n. Выведите «even», если оно чётное, иначе «odd».',
        'category': 'conditionals', 'difficulty': 1,
        'tests': [('4\n', 'even'), ('7\n', 'odd'), ('0\n', 'even')],
        'solutions': {
            'python': 'n = int(input())\nprint("even" if n % 2 == 0 else "odd")\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    std::cout << (n % 2 == 0 ? "even" : "odd") << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(n % 2 === 0 ? "even" : "odd");\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    println!("{}", if n % 2 == 0 { "even" } else { "odd" });\n}\n',
        },
    },
    {
        'id': 'sign_number',
        'title': 'Знак числа',
        'statement': 'Дано число n. Выведите «positive», «negative» или «zero».',
        'category': 'conditionals', 'difficulty': 1,
        'tests': [('5\n', 'positive'), ('-3\n', 'negative'), ('0\n', 'zero')],
        'solutions': {
            'python': 'n = int(input())\nprint("positive" if n > 0 else "negative" if n < 0 else "zero")\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    if (n > 0) std::cout << "positive";\n    else if (n < 0) std::cout << "negative";\n    else std::cout << "zero";\n    std::cout << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(n > 0 ? "positive" : n < 0 ? "negative" : "zero");\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    println!("{}", if n > 0 { "positive" } else if n < 0 { "negative" } else { "zero" });\n}\n',
        },
    },
    {
        'id': 'leap_year',
        'title': 'Високосный год',
        'statement': 'Дан год. Выведите «yes», если он високосный, иначе «no». Високосный: делится на 4, но не на 100, либо делится на 400.',
        'category': 'conditionals', 'difficulty': 2,
        'tests': [('2024\n', 'yes'), ('2023\n', 'no'), ('1900\n', 'no'), ('2000\n', 'yes')],
        'solutions': {
            'python': 'y = int(input())\nprint("yes" if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else "no")\n',
            'cpp': '#include <iostream>\nint main() {\n    int y;\n    std::cin >> y;\n    bool leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;\n    std::cout << (leap ? "yes" : "no") << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst y = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log((y % 4 === 0 && y % 100 !== 0) || y % 400 === 0 ? "yes" : "no");\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let y: i64 = s.trim().parse().unwrap();\n    let leap = (y % 4 == 0 && y % 100 != 0) || y % 400 == 0;\n    println!("{}", if leap { "yes" } else { "no" });\n}\n',
        },
    },

    # ======================= ЦИКЛЫ =======================
    {
        'id': 'sum_1_to_n',
        'title': 'Сумма от 1 до n',
        'statement': 'Дано натуральное число n. Выведите сумму чисел от 1 до n.',
        'category': 'loops', 'difficulty': 1,
        'tests': [('5\n', '15'), ('10\n', '55'), ('1\n', '1')],
        'solutions': {
            'python': 'n = int(input())\nprint(n * (n + 1) // 2)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    std::cout << n * (n + 1) / 2 << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(n * (n + 1) / 2);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    println!("{}", n * (n + 1) / 2);\n}\n',
        },
    },
    {
        'id': 'factorial',
        'title': 'Факториал',
        'statement': 'Дано число n. Выведите n! (факториал).',
        'category': 'loops', 'difficulty': 2,
        'tests': [('5\n', '120'), ('0\n', '1'), ('10\n', '3628800')],
        'solutions': {
            'python': 'n = int(input())\nr = 1\nfor i in range(2, n + 1):\n    r *= i\nprint(r)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n, r = 1;\n    std::cin >> n;\n    for (long long i = 2; i <= n; i++) r *= i;\n    std::cout << r << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nlet r = 1n;\nfor (let i = 2n; i <= BigInt(n); i++) r *= i;\nconsole.log(r.toString());\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    let mut r: i64 = 1;\n    for i in 2..=n { r *= i; }\n    println!("{}", r);\n}\n',
        },
    },
    {
        'id': 'count_digits',
        'title': 'Количество цифр',
        'statement': 'Дано натуральное число n. Выведите количество цифр в нём.',
        'category': 'loops', 'difficulty': 2,
        'tests': [('12345\n', '5'), ('7\n', '1'), ('1000\n', '4')],
        'solutions': {
            'python': 'n = abs(int(input()))\nprint(len(str(n)))\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    if (n < 0) n = -n;\n    int c = 0;\n    if (n == 0) c = 1;\n    while (n > 0) { c++; n /= 10; }\n    std::cout << c << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Math.abs(Number(fs.readFileSync(0, "utf8").trim()));\nconsole.log(String(n).length);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    println!("{}", n.abs().to_string().len());\n}\n',
        },
    },
    {
        'id': 'reverse_number',
        'title': 'Разворот числа',
        'statement': 'Дано натуральное число n. Выведите число, записанное в обратном порядке (ведущие нули отбрасываются).',
        'category': 'loops', 'difficulty': 2,
        'tests': [('1234\n', '4321'), ('1200\n', '21'), ('7\n', '7')],
        'solutions': {
            'python': 'n = int(input())\nprint(int(str(n)[::-1]))\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n, r = 0;\n    std::cin >> n;\n    while (n > 0) { r = r * 10 + n % 10; n /= 10; }\n    std::cout << r << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = fs.readFileSync(0, "utf8").trim();\nconsole.log(String(Number(n.split("").reverse().join(""))));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    let mut x = n; let mut r: i64 = 0;\n    while x > 0 { r = r * 10 + x % 10; x /= 10; }\n    println!("{}", r);\n}\n',
        },
    },
    {
        'id': 'primes_upto',
        'title': 'Простые числа до n',
        'statement': 'Дано число n. Выведите количество простых чисел, не превышающих n.',
        'category': 'loops', 'difficulty': 3,
        'tests': [('10\n', '4'), ('20\n', '8'), ('1\n', '0')],
        'solutions': {
            'python': 'n = int(input())\nc = 0\nfor x in range(2, n + 1):\n    ok = True\n    i = 2\n    while i * i <= x:\n        if x % i == 0:\n            ok = False\n            break\n        i += 1\n    if ok:\n        c += 1\nprint(c)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n;\n    std::cin >> n;\n    int c = 0;\n    for (long long x = 2; x <= n; x++) {\n        bool ok = true;\n        for (long long i = 2; i * i <= x; i++) if (x % i == 0) { ok = false; break; }\n        if (ok) c++;\n    }\n    std::cout << c << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nlet c = 0;\nfor (let x = 2; x <= n; x++) {\n  let ok = true;\n  for (let i = 2; i * i <= x; i++) if (x % i === 0) { ok = false; break; }\n  if (ok) c++;\n}\nconsole.log(c);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    let mut c = 0;\n    for x in 2..=n {\n        let mut ok = true;\n        let mut i = 2;\n        while i * i <= x { if x % i == 0 { ok = false; break; } i += 1; }\n        if ok { c += 1; }\n    }\n    println!("{}", c);\n}\n',
        },
    },

    # ======================= КОЛЛЕКЦИИ =======================
    {
        'id': 'sum_list',
        'title': 'Сумма элементов массива',
        'statement': 'В первой строке число n, во второй — n целых чисел. Выведите их сумму.',
        'category': 'collections', 'difficulty': 2,
        'tests': [('5\n1 2 3 4 5\n', '15'), ('3\n-1 0 1\n', '0')],
        'solutions': {
            'python': 'n = int(input())\na = list(map(int, input().split()))\nprint(sum(a))\n',
            'cpp': '#include <iostream>\n#include <vector>\nint main() {\n    int n; std::cin >> n;\n    long long s = 0;\n    for (int i = 0; i < n; i++) { long long x; std::cin >> x; s += x; }\n    std::cout << s << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst t = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst n = t[0];\nconst a = t.slice(1, 1 + n);\nconsole.log(a.reduce((s, x) => s + x, 0));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let n = v[0] as usize;\n    let sum: i64 = v[1..=n].iter().sum();\n    println!("{}", sum);\n}\n',
        },
    },
    {
        'id': 'max_list',
        'title': 'Максимальный элемент',
        'statement': 'В первой строке число n, во второй — n целых чисел. Выведите максимум.',
        'category': 'collections', 'difficulty': 2,
        'tests': [('4\n3 9 2 7\n', '9'), ('3\n-5 -1 -3\n', '-1')],
        'solutions': {
            'python': 'n = int(input())\na = list(map(int, input().split()))\nprint(max(a))\n',
            'cpp': '#include <iostream>\n#include <climits>\nint main() {\n    int n; std::cin >> n;\n    long long best = LLONG_MIN, x;\n    for (int i = 0; i < n; i++) { std::cin >> x; if (x > best) best = x; }\n    std::cout << best << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst t = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst n = t[0]; const a = t.slice(1, 1 + n);\nconsole.log(Math.max(...a));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let n = v[0] as usize;\n    println!("{}", v[1..=n].iter().max().unwrap());\n}\n',
        },
    },
    {
        'id': 'second_largest',
        'title': 'Второй максимум',
        'statement': 'Дано n чисел. Выведите второй по величине элемент (различные значения).',
        'category': 'collections', 'difficulty': 3,
        'tests': [('5\n3 9 2 9 7\n', '7'), ('4\n1 2 3 4\n', '3')],
        'solutions': {
            'python': 'n = int(input())\na = sorted(set(map(int, input().split())))\nprint(a[-2])\n',
            'cpp': '#include <iostream>\n#include <set>\nint main() {\n    int n; std::cin >> n;\n    std::set<long long> s;\n    for (int i = 0; i < n; i++) { long long x; std::cin >> x; s.insert(x); }\n    auto it = s.rbegin(); ++it;\n    std::cout << *it << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst t = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst n = t[0]; const a = [...new Set(t.slice(1, 1 + n))].sort((x, y) => x - y);\nconsole.log(a[a.length - 2]);\n',
            'rust': 'use std::io::{self, Read};\nuse std::collections::BTreeSet;\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let n = v[0] as usize;\n    let set: BTreeSet<i64> = v[1..=n].iter().cloned().collect();\n    let mut it = set.iter().rev(); it.next();\n    println!("{}", it.next().unwrap());\n}\n',
        },
    },
    {
        'id': 'count_positive',
        'title': 'Количество положительных',
        'statement': 'Дано n чисел. Выведите количество положительных.',
        'category': 'collections', 'difficulty': 2,
        'tests': [('5\n1 -2 3 0 4\n', '3'), ('3\n-1 -2 -3\n', '0')],
        'solutions': {
            'python': 'n = int(input())\na = list(map(int, input().split()))\nprint(sum(1 for x in a if x > 0))\n',
            'cpp': '#include <iostream>\nint main() {\n    int n, c = 0; std::cin >> n;\n    for (int i = 0; i < n; i++) { long long x; std::cin >> x; if (x > 0) c++; }\n    std::cout << c << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst t = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst n = t[0]; const a = t.slice(1, 1 + n);\nconsole.log(a.filter(x => x > 0).length);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let n = v[0] as usize;\n    println!("{}", v[1..=n].iter().filter(|&&x| x > 0).count());\n}\n',
        },
    },

    # ======================= СТРОКИ =======================
    {
        'id': 'reverse_string',
        'title': 'Разворот строки',
        'statement': 'Дана строка. Выведите её в обратном порядке.',
        'category': 'strings', 'difficulty': 1,
        'tests': [('hello\n', 'olleh'), ('abc\n', 'cba')],
        'solutions': {
            'python': 's = input()\nprint(s[::-1])\n',
            'cpp': '#include <iostream>\n#include <string>\n#include <algorithm>\nint main() {\n    std::string s; std::getline(std::cin, s);\n    std::reverse(s.begin(), s.end());\n    std::cout << s << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\nconsole.log(s.split("").reverse().join(""));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let t = s.trim_end();\n    println!("{}", t.chars().rev().collect::<String>());\n}\n',
        },
    },
    {
        'id': 'is_palindrome',
        'title': 'Палиндром',
        'statement': 'Дана строка. Выведите «yes», если она читается одинаково в обе стороны, иначе «no».',
        'category': 'strings', 'difficulty': 2,
        'tests': [('level\n', 'yes'), ('hello\n', 'no'), ('abba\n', 'yes')],
        'solutions': {
            'python': 's = input()\nprint("yes" if s == s[::-1] else "no")\n',
            'cpp': '#include <iostream>\n#include <string>\n#include <algorithm>\nint main() {\n    std::string s; std::getline(std::cin, s);\n    std::string r = s; std::reverse(r.begin(), r.end());\n    std::cout << (r == s ? "yes" : "no") << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\nconsole.log(s === s.split("").reverse().join("") ? "yes" : "no");\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let t = s.trim_end();\n    println!("{}", if t == t.chars().rev().collect::<String>() { "yes" } else { "no" });\n}\n',
        },
    },
    {
        'id': 'count_vowels',
        'title': 'Подсчёт гласных',
        'statement': 'Дана строка из строчных латинских букв. Выведите количество гласных (a, e, i, o, u).',
        'category': 'strings', 'difficulty': 2,
        'tests': [('hello\n', '2'), ('programming\n', '3')],
        'solutions': {
            'python': 's = input()\nprint(sum(1 for c in s if c in "aeiou"))\n',
            'cpp': '#include <iostream>\n#include <string>\nint main() {\n    std::string s; std::getline(std::cin, s);\n    int c = 0;\n    for (char ch : s) if (std::string("aeiou").find(ch) != std::string::npos) c++;\n    std::cout << c << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst s = fs.readFileSync(0, "utf8").replace(/\\n$/, "");\nconsole.log([...s].filter(c => "aeiou".includes(c)).length);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let t = s.trim_end();\n    println!("{}", t.chars().filter(|c| "aeiou".contains(*c)).count());\n}\n',
        },
    },
    {
        'id': 'word_count',
        'title': 'Количество слов',
        'statement': 'Дана строка. Выведите количество слов в ней (слова разделены пробелами).',
        'category': 'strings', 'difficulty': 2,
        'tests': [('hello world\n', '2'), ('a b c d\n', '4')],
        'solutions': {
            'python': 's = input()\nprint(len(s.split()))\n',
            'cpp': '#include <iostream>\n#include <string>\n#include <sstream>\nint main() {\n    std::string line; std::getline(std::cin, line);\n    std::istringstream ss(line);\n    std::string w; int c = 0;\n    while (ss >> w) c++;\n    std::cout << c << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst s = fs.readFileSync(0, "utf8").trim();\nconsole.log(s.length === 0 ? 0 : s.split(/\\s+/).length);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    println!("{}", s.split_whitespace().count());\n}\n',
        },
    },

    # ======================= ФУНКЦИИ / АЛГОРИТМЫ =======================
    {
        'id': 'gcd',
        'title': 'НОД',
        'statement': 'Даны два натуральных числа. Выведите их наибольший общий делитель.',
        'category': 'functions', 'difficulty': 2,
        'tests': [('12\n18\n', '6'), ('7\n13\n', '1')],
        'solutions': {
            'python': 'import math\na = int(input())\nb = int(input())\nprint(math.gcd(a, b))\n',
            'cpp': '#include <iostream>\n#include <numeric>\nint main() {\n    long long a, b; std::cin >> a >> b;\n    std::cout << std::gcd(a, b) << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst [a, b] = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst gcd = (x, y) => y === 0 ? x : gcd(y, x % y);\nconsole.log(gcd(a, b));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let (mut a, mut b) = (v[0], v[1]);\n    while b != 0 { let t = b; b = a % b; a = t; }\n    println!("{}", a);\n}\n',
        },
    },
    {
        'id': 'fibonacci',
        'title': 'Числа Фибоначчи',
        'statement': 'Дано n. Выведите n-е число Фибоначчи (F(1)=1, F(2)=1).',
        'category': 'algorithms', 'difficulty': 2,
        'tests': [('1\n', '1'), ('7\n', '13'), ('10\n', '55')],
        'solutions': {
            'python': 'n = int(input())\na, b = 1, 1\nfor _ in range(n - 1):\n    a, b = b, a + b\nprint(a)\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n; std::cin >> n;\n    long long a = 1, b = 1;\n    for (long long i = 1; i < n; i++) { long long t = a + b; a = b; b = t; }\n    std::cout << a << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nlet a = 1n, b = 1n;\nfor (let i = 1; i < n; i++) { const t = a + b; a = b; b = t; }\nconsole.log(a.toString());\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: u64 = s.trim().parse().unwrap();\n    let (mut a, mut b) = (1u128, 1u128);\n    for _ in 1..n { let t = a + b; a = b; b = t; }\n    println!("{}", a);\n}\n',
        },
    },
    {
        'id': 'binary_search',
        'title': 'Двоичный поиск',
        'statement': 'В первой строке n и искомое x, во второй — n чисел по возрастанию. Выведите индекс x (с 0) или -1.',
        'category': 'algorithms', 'difficulty': 3,
        'tests': [('5 7\n1 3 5 7 9\n', '3'), ('4 2\n1 3 5 7\n', '-1')],
        'solutions': {
            'python': 'n, x = map(int, input().split())\na = list(map(int, input().split()))\nlo, hi = 0, n - 1\nres = -1\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    if a[mid] == x:\n        res = mid\n        break\n    elif a[mid] < x:\n        lo = mid + 1\n    else:\n        hi = mid - 1\nprint(res)\n',
            'cpp': '#include <iostream>\n#include <vector>\nint main() {\n    int n; long long x; std::cin >> n >> x;\n    std::vector<long long> a(n);\n    for (auto &v : a) std::cin >> v;\n    int lo = 0, hi = n - 1, res = -1;\n    while (lo <= hi) { int mid = (lo + hi) / 2; if (a[mid] == x) { res = mid; break; } else if (a[mid] < x) lo = mid + 1; else hi = mid - 1; }\n    std::cout << res << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst t = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst n = t[0], x = t[1]; const a = t.slice(2, 2 + n);\nlet lo = 0, hi = n - 1, res = -1;\nwhile (lo <= hi) { const mid = Math.floor((lo + hi) / 2); if (a[mid] === x) { res = mid; break; } else if (a[mid] < x) lo = mid + 1; else hi = mid - 1; }\nconsole.log(res);\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let n = v[0] as usize; let x = v[1];\n    let a = &v[2..2 + n];\n    let (mut lo, mut hi, mut res) = (0i64, n as i64 - 1, -1i64);\n    while lo <= hi {\n        let mid = (lo + hi) / 2;\n        if a[mid as usize] == x { res = mid; break; }\n        else if a[mid as usize] < x { lo = mid + 1; }\n        else { hi = mid - 1; }\n    }\n    println!("{}", res);\n}\n',
        },
    },
    {
        'id': 'bubble_sort',
        'title': 'Сортировка пузырьком',
        'statement': 'Дано n чисел. Выведите их по возрастанию через пробел.',
        'category': 'algorithms', 'difficulty': 3,
        'tests': [('5\n5 2 4 1 3\n', '1 2 3 4 5'), ('3\n3 3 1\n', '1 3 3')],
        'solutions': {
            'python': 'n = int(input())\na = list(map(int, input().split()))\nfor i in range(n):\n    for j in range(n - 1 - i):\n        if a[j] > a[j + 1]:\n            a[j], a[j + 1] = a[j + 1], a[j]\nprint(*a)\n',
            'cpp': '#include <iostream>\n#include <vector>\nint main() {\n    int n; std::cin >> n;\n    std::vector<long long> a(n);\n    for (auto &v : a) std::cin >> v;\n    for (int i = 0; i < n; i++)\n        for (int j = 0; j + 1 < n - i; j++)\n            if (a[j] > a[j + 1]) std::swap(a[j], a[j + 1]);\n    for (int i = 0; i < n; i++) std::cout << a[i] << (i + 1 < n ? " " : "\\n");\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst t = fs.readFileSync(0, "utf8").trim().split(/\\s+/).map(Number);\nconst n = t[0]; const a = t.slice(1, 1 + n);\nfor (let i = 0; i < n; i++)\n  for (let j = 0; j + 1 < n - i; j++)\n    if (a[j] > a[j + 1]) [a[j], a[j + 1]] = [a[j + 1], a[j]];\nconsole.log(a.join(" "));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let v: Vec<i64> = s.split_whitespace().map(|x| x.parse().unwrap()).collect();\n    let n = v[0] as usize;\n    let mut a: Vec<i64> = v[1..=n].to_vec();\n    for i in 0..n { for j in 0..n - 1 - i { if a[j] > a[j + 1] { a.swap(j, j + 1); } } }\n    let parts: Vec<String> = a.iter().map(|x| x.to_string()).collect();\n    println!("{}", parts.join(" "));\n}\n',
        },
    },
    {
        'id': 'digit_sum',
        'title': 'Сумма цифр',
        'statement': 'Дано натуральное число n. Выведите сумму его цифр.',
        'category': 'loops', 'difficulty': 2,
        'tests': [('1234\n', '10'), ('999\n', '27')],
        'solutions': {
            'python': 'n = abs(int(input()))\nprint(sum(int(c) for c in str(n)))\n',
            'cpp': '#include <iostream>\nint main() {\n    long long n; std::cin >> n;\n    if (n < 0) n = -n;\n    long long s = 0;\n    while (n > 0) { s += n % 10; n /= 10; }\n    std::cout << s << std::endl;\n    return 0;\n}\n',
            'javascript': 'const fs = require("fs");\nconst n = String(Math.abs(Number(fs.readFileSync(0, "utf8").trim())));\nconsole.log([...n].reduce((s, c) => s + Number(c), 0));\n',
            'rust': 'use std::io::{self, Read};\nfn main() {\n    let mut s = String::new();\n    io::stdin().read_to_string(&mut s).unwrap();\n    let n: i64 = s.trim().parse().unwrap();\n    let sum: i64 = n.abs().to_string().chars().map(|c| c.to_digit(10).unwrap() as i64).sum();\n    println!("{}", sum);\n}\n',
        },
    },
]


# ---------------------------------------------------------------------------
# CSS-упражнения (не исполняются, но с готовым HTML/CSS)
# ---------------------------------------------------------------------------

CSS_EXERCISES = [
    ('css_selector_class', 'Селектор по классу', 'Напишите правило для класса .box: красный цвет текста.', '.box {\n    color: red;\n}\n'),
    ('css_selector_id', 'Селектор по идентификатору', 'Сделайте элемент #header жирным.', '#header {\n    font-weight: bold;\n}\n'),
    ('css_margin', 'Внешний отступ', 'Задайте блоку .card внешний отступ 16px со всех сторон.', '.card {\n    margin: 16px;\n}\n'),
    ('css_padding', 'Внутренний отступ', 'Задайте .box внутренний отступ 20px.', '.box {\n    padding: 20px;\n}\n'),
    ('css_border', 'Рамка', 'Обведите .panel рамкой 2px сплошного синего цвета.', '.panel {\n    border: 2px solid blue;\n}\n'),
    ('css_border_radius', 'Скругление углов', 'Скруглите углы .avatar на 50%, чтобы получился круг.', '.avatar {\n    border-radius: 50%;\n}\n'),
    ('css_bg_color', 'Фон', 'Задайте фону body светло-серый цвет #f5f5f5.', 'body {\n    background-color: #f5f5f5;\n}\n'),
    ('css_text_align', 'Выравнивание текста', 'Отцентрируйте текст в .title.', '.title {\n    text-align: center;\n}\n'),
    ('css_font_size', 'Размер шрифта', 'Задайте .heading размер шрифта 32px.', '.heading {\n    font-size: 32px;\n}\n'),
    ('css_font_family', 'Шрифт', 'Задайте body шрифт Arial с запасным sans-serif.', 'body {\n    font-family: Arial, sans-serif;\n}\n'),
    ('css_line_height', 'Межстрочный интервал', 'Задайте абзацам line-height 1.6.', 'p {\n    line-height: 1.6;\n}\n'),
    ('css_width_height', 'Размеры блока', 'Задайте .box ширину 200px и высоту 100px.', '.box {\n    width: 200px;\n    height: 100px;\n}\n'),
    ('css_box_model', 'Блочная модель', 'Для .card: padding 10px, border 1px solid #ccc, margin 8px.', '.card {\n    padding: 10px;\n    border: 1px solid #ccc;\n    margin: 8px;\n}\n'),
    ('css_display_block', 'Блочный элемент', 'Сделайте ссылки в .menu блочными.', '.menu a {\n    display: block;\n}\n'),
    ('css_display_inline', 'Строчный элемент', 'Сделайте .tag строчными элементами.', '.tag {\n    display: inline;\n}\n'),
    ('css_flex_center', 'Flexbox: центрирование', 'Отцентрируйте содержимое .container по обеим осям через flex.', '.container {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n}\n'),
    ('css_flex_row', 'Flexbox: ряд', 'Расположите элементы .row в строку с равными промежутками.', '.row {\n    display: flex;\n    justify-content: space-between;\n}\n'),
    ('css_flex_column', 'Flexbox: колонка', 'Расположите элементы .col в колонку.', '.col {\n    display: flex;\n    flex-direction: column;\n}\n'),
    ('css_flex_wrap', 'Flexbox: перенос', 'Разрешите перенос строк во flex-контейнере .wrap.', '.wrap {\n    display: flex;\n    flex-wrap: wrap;\n}\n'),
    ('css_grid_columns', 'Grid: колонки', 'Создайте сетку из трёх равных колонок в .grid.', '.grid {\n    display: grid;\n    grid-template-columns: repeat(3, 1fr);\n}\n'),
    ('css_grid_gap', 'Grid: промежутки', 'Задайте сетке .grid промежуток 20px.', '.grid {\n    display: grid;\n    gap: 20px;\n}\n'),
    ('css_grid_template', 'Grid: области', 'Задайте .layout две колонки: 200px и 1fr.', '.layout {\n    display: grid;\n    grid-template-columns: 200px 1fr;\n}\n'),
    ('css_position_relative', 'Позиционирование', 'Сместите .badge относительно себя на 5px вправо.', '.badge {\n    position: relative;\n    left: 5px;\n}\n'),
    ('css_position_absolute', 'Абсолютное позиционирование', 'Прижмите .close к правому верхнему углу .modal.', '.modal {\n    position: relative;\n}\n.modal .close {\n    position: absolute;\n    top: 0;\n    right: 0;\n}\n'),
    ('css_z_index', 'Слои', 'Поднимите .popup над остальными: z-index 100.', '.popup {\n    position: absolute;\n    z-index: 100;\n}\n'),
    ('css_transition', 'Переход', 'Добавьте плавный переход цвета 0.3s для .btn.', '.btn {\n    transition: color 0.3s;\n}\n'),
    ('css_hover', 'Псевдокласс hover', 'Меняйте цвет фона .btn на синий при наведении.', '.btn:hover {\n    background-color: blue;\n}\n'),
    ('css_pseudo_before', 'Псевдоэлемент ::before', 'Добавьте звёздочку перед .required.', '.required::before {\n    content: "*";\n    color: red;\n}\n'),
    ('css_shadow', 'Тень', 'Добавьте .card тень 0 4px 8px rgba(0,0,0,0.1).', '.card {\n    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);\n}\n'),
    ('css_media_query', 'Адаптивность', 'Скройте .sidebar на экранах уже 768px.', '@media (max-width: 767px) {\n    .sidebar {\n        display: none;\n    }\n}\n'),
    ('css_overflow', 'Переполнение', 'Включите прокрутку по вертикали для .list.', '.list {\n    overflow-y: auto;\n}\n'),
    ('css_opacity', 'Прозрачность', 'Сделайте .disabled полупрозрачным (opacity 0.5).', '.disabled {\n    opacity: 0.5;\n}\n'),
    ('css_text_transform', 'Регистр текста', 'Сделайте текст .label заглавными.', '.label {\n    text-transform: uppercase;\n}\n'),
]


# ---------------------------------------------------------------------------
# Темы-концепты (без исполнения): продвинутые/теоретические темы
# ---------------------------------------------------------------------------

CONCEPT_TASKS = {
    'advanced': [
        ('Разбор кода: декоратор', 'Объясните, что делает декоратор @timer и как он измеряет время выполнения функции.'),
        ('Разбор кода: замыкание', 'Объясните, почему счётчик сохраняет значение между вызовами функции.'),
        ('Разбор кода: генератор', 'Объясните разницу между списком и генератором на примере больших данных.'),
        ('Разбор кода: контекстный менеджер', 'Объясните, как работает with и какие методы вызывает.'),
        ('Разбор кода: метакласс', 'Опишите, зачем нужен метакласс и как он создаёт класс.'),
        ('Разбор кода: асинхронность', 'Объясните, почему async-функция возвращает корутину, а не результат.'),
        ('Разбор кода: потокобезопасность', 'Объясните, как блокировка защищает общий ресурс.'),
        ('Разбор кода: сериализация', 'Опишите, как объект превращается в JSON и обратно.'),
        ('Разбор кода: кэширование', 'Объясните стратегию кэширования с временем жизни.'),
        ('Разбор кода: логирование', 'Опишите уровни логирования и когда какой использовать.'),
        ('Разбор кода: тестирование', 'Объясните, чем модульный тест отличается от интеграционного.'),
        ('Разбор кода: профилирование', 'Опишите, как найти узкое место в программе.'),
        ('Разбор кода: рефакторинг', 'Предложите, как разделить большую функцию на части.'),
        ('Разбор кода: SOLID', 'Объясните принцип единственной ответственности на примере.'),
        ('Разбор кода: паттерн', 'Опишите, где уместен паттерн «Стратегия».'),
        ('Разбор кода: безопасность', 'Объясните, почему нельзя хранить пароли в открытом виде.'),
        ('Разбор кода: CI/CD', 'Опишите этапы пайплайна от коммита до деплоя.'),
        ('Разбор кода: контейнеризация', 'Объясните, зачем приложению Docker-образ.'),
        ('Разбор кода: микросервисы', 'Опишите плюсы и минусы разбиения на сервисы.'),
        ('Разбор кода: наблюдаемость', 'Объясните разницу метрик, логов и трассировки.'),
    ],
}
