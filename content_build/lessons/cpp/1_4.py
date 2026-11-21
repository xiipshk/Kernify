"""Урок 1.4 курса C++: условия и циклы."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


def text(content: str) -> dict:
    return {"type": "text", "content": content.strip()}


def heading(content: str, level: int = 2) -> dict:
    return {"type": "heading", "level": level, "content": content.strip()}


def bullets(*items: str, ordered: bool = False) -> dict:
    return {"type": "list", "ordered": ordered, "items": list(items)}


def numbered(*items: str) -> dict:
    return bullets(*items, ordered=True)


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


def callout(style: str, title: str, content: str) -> dict:
    return {"type": "callout", "style": style, "title": title, "content": content}


def example(language: str, source: str) -> dict:
    return {"type": "code", "language": language, "content": code(source)}


LESSON = {
    "language": "cpp",
    "program_order": 1,
    "topic_order": 4,
    "name": "1.4. Условия и циклы",
    "slug": "cpp-1-4-условия-и-циклы",
    "short_description": (
        "Условные конструкции if/else, switch с инициализатором (C++17), "
        "циклы while, do-while, for, range-based for, управление потоком break/continue."
    ),
    "topic_name": "Условия и циклы",
    "topic_description": (
        "Полное руководство по управлению потоком выполнения в C++: "
        "if/else с инициализатором (C++17), constexpr if, switch с инициализатором, "
        "циклы while/do-while/for/range-based for, break/continue, типичные ошибки."
    ),
    "learning_objectives": [
        "Писать условные конструкции if/else/else if с правильными скобками",
        "Использовать if/switch с инициализатором (C++17) для ограничения области видимости",
        "Применять constexpr if (C++17) для compile-time branching",
        "Писать switch с инициализатором (C++17) и атрибутом [[fallthrough]]",
        "Работать с циклами: while, do-while, классический for, range-based for",
        "Управлять потоком циклов: break, continue, лейблы для вложенных циклов",
        "Выбирать правильный цикл: while для неопределенного числа итераций, for для известного",
        "Избегать типичных ошибок: off-by-one, забытый break, копирование в range-based for",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "cpp",
        "if",
        "else",
        "switch",
        "while",
        "for",
        "range-based",
        "break",
        "continue",
    ],
    "starter_code": code(
        r"""
        #include <iostream>

        int main() {
            int x = 42;

            if (x > 0) {
                std::cout << "Positive\n";
            } else if (x < 0) {
                std::cout << "Negative\n";
            } else {
                std::cout << "Zero\n";
            }

            for (int i = 0; i < 5; ++i) {
                std::cout << i << ' ';
            }
            std::cout << '\n';

            return 0;
        }
        """
    ),
    "hints": [
        "Всегда ставьте фигурные скобки {} даже для одиночных инструкций — это предотвращает ошибки при рефакторинге.",
        "В switch всегда пишите break или [[fallthrough]], иначе выполнение «провалится» в следующий case.",
        "Range-based for (for (auto& x : v)) — предпочтительнее классического for для контейнеров.",
        "continue пропускает только текущую итерацию, break — выходит из цикла полностью.",
    ],
    "content": [
        text(
            "Управление потоком — скелет любой программы. Без условий программа линейна, "
            "без циклов — не может обрабатывать массивы данных. В C++ инструменты управления "
            "потоком мощные и гибкие: if с инициализатором, constexpr if для compile-time "
            "branching, switch с инициализатором, range-based for, атрибут [[fallthrough]]. "
            "В этом уроке разберём все конструкции управления потоком от if до range-based for "
            "и разберём типичные ошибки: off-by-one, забытый break, копирование в range-based for."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "писать if/else/else if с правильными скобками и инициализатором (C++17);",
            "использовать constexpr if (C++17) для compile-time branching;",
            "писать switch с инициализатором и атрибутом [[fallthrough]];",
            "работать с циклами: while, do-while, классический for, range-based for;",
            "управлять потоком: break, continue, лейблы для вложенных циклов;",
            "выбирать правильный цикл: while для неизвестного числа итераций, for — когда известно число шагов;",
            "избегать off-by-one, забытого break, копирования в range-based for.",
        ),
        heading("Условные операторы"),
        heading("if / else", 3),
        text(
            "Базовая условная конструкция. Всегда ставьте фигурные скобки {} — даже для одной "
            "инструкции. Это предотвращает ошибки при рефакторинге и делает код читаемым."
        ),
        example(
            "cpp",
            """
            int x = 42;

            if (x > 0) {
                std::cout << "Positive\n";
            } else if (x < 0) {
                std::cout << "Negative\n";
            } else {
                std::cout << "Zero\n";
            }
            """,
        ),
        text(
            "Правила хорошего тона:\n"
            "- Всегда ставьте { } даже для одной инструкции.\n"
            "- Пишите условие в скобках: if (x > 0), а не if x > 0.\n"
            "- Выносите сложные условия в именованные переменные: `bool is_adult = age >= 18;`.\n"
            "- Используйте early return: проверяйте граничные условия в начале, возвращайтесь рано."
        ),
        heading("if с инициализатором (C++17)", 3),
        text(
            "C++17 добавил if с инициализатором: переменная объявлена в условии, видна только "
            "внутри if/else блоков. Это ограничивает область видимости и предотвращает случайное "
            "использование переменной снаружи."
        ),
        example(
            "cpp",
            """
            // Область видимости переменной только в if/else блоках
            if (auto it = map.find(key); it != map.end()) {
                std::cout << "Found: " << it->second << '\n';
            } else {
                std::cout << "Not found\n";
            }
            // it недоступен здесь — ошибка компиляции

            // Классический пример: чтение из потока
            if (std::string line; std::getline(std::cin, line)) {
                process(line);
            }
            // line недоступен здесь
            """,
        ),
        text(
            "Синтаксис: `if (init; condition)`. Инициализатор может быть объявлением с инициализацией "
            "или присваиванием. Область видимости переменной — только if и else блоки. "
            "Это заменяет идиому: `{ auto it = map.find(key); if (it != map.end()) { ... } }`."
        ),
        heading("constexpr if (C++17) — compile-time branching", 3),
        text(
            "constexpr if вычисляет условие на этапе компиляции и отбрасывает неиспользуемую ветку. "
            "Это позволяет писать обобщённый код без runtime overhead и без SFINAE/Enable_if."
        ),
        example(
            "cpp",
            """
            template<typename T>
            void print_type(T value) {
                if constexpr (std::is_integral_v<T>) {
                    std::cout << "Integral: " << value << '\n';
                } else if constexpr (std::is_floating_point_v<T>) {
                    std::cout << "Float: " << value << '\n';
                } else {
                    std::cout << "Other\n";
                }
            }

            // Использование:
            print_type(42);       // Integral: 42
            print_type(3.14);     // Float: 3.14
            print_type("hello");  // Other

            // В неиспользуемых ветках код не компилируется!
            // Можно безопасно вызывать методы, которых нет у других типов.
            """,
        ),
        text(
            "constexpr if — мощный инструмент метапрограммирования:\n"
            "- Условие вычисляется на этапе компиляции.\n"
            "- Неиспользуемая ветка полностью отбрасывается (код даже не компилируется).\n"
            "- Можно безопасно обращаться к членам, которых нет в других типах.\n"
            "- Заменяет SFINAE, tag dispatching, tag::type в большинстве случаев.\n\n"
            "Требует `#include <type_traits>` для type traits: `is_integral_v`, `is_floating_point_v`, "
            "`is_same_v`, `is_base_of_v` и др."
        ),
        callout(
            "info",
            "constexpr if vs обычный if",
            "Обычный if: условие вычисляется во время выполнения, обе ветки компилируются. "
            "constexpr if: условие вычисляется на этапе компиляции, неиспользуемая ветка отбрасывается. "
            "Используйте constexpr if, когда условие известно на этапе компиляции (template параметры, constexpr переменные)."
        ),
        heading("Switch"),
        text(
            "Switch работает с интегральными типами и enum. Всегда пишите break — без него "
            "выполнение «проваливается» в следующий case (fallthrough). C++17 добавил инициализатор "
            "и атрибут [[fallthrough]] для явного управления fallthrough.\n\n"
            "Switch компилируется в jump table (таблицу переходов) для плотных case значений — "
            "O(1) поиск. Для редких значений компилятор может использовать binary search или if-else chain. "
            "Сравнение со строкой через switch невозможно напрямую — используйте if/else или unordered_map."
        ),
        example(
            "cpp",
            """
            enum class Color { Red, Green, Blue };

            void process(Color c) {
                switch (c) {
                    case Color::Red:
                        std::cout << "Red\n";
                        break;  // без break — fallthrough!
                    case Color::Green:
                        std::cout << "Green\n";
                        break;
                    case Color::Blue:
                        std::cout << "Blue\n";
                        break;
                    default:
                        std::cout << "Unknown\n";
                }
            }
            """,
        ),
        text(
            "Правила switch:\n"
            "- Выражение должно быть интегральным типом (int, char, enum, enum class).\n"
            "- case должны быть константами времени компиляции.\n"
            "- default опционален, но рекомендуется для обработки неожиданных значений.\n"
            "- Без break выполнение «проваливается» в следующий case (fallthrough).\n"
            "- case не создают область видимости — переменные лучше объявлять во вложенных { }."
        ),
        heading("Switch с инициализатором (C++17)", 3),
        text(
            "Аналогично if, switch в C++17 поддерживает инициализатор. Переменная видна только "
            "внутри switch. Удобно для ограничения области видимости временных переменных.\n\n"
            "Синтаксис: `switch (init; condition)`. Инициализатор может быть объявлением с инициализацией "
            "или присваиванием. Область видимости переменной — только switch блок (case/default). "
            "Это заменяет идиому: `{ auto status = get_status(); switch (status) { ... } }`."
        ),
        example(
            "cpp",
            """
            switch (auto status = get_status(); status) {
                case Status::Ok:
                    // ...
                    break;
                case Status::Error:
                    // ...
                    break;
            }
            // status недоступен снаружи
            """,
        ),
        heading("[[fallthrough]] атрибут (C++17)", 3),
        text(
            "Иногда fallthrough нужен намеренно. Атрибут [[fallthrough]] подавляет предупреждение "
            "компилятора и документирует намерение программиста.\n\n"
            "Без [[fallthrough]] современные компиляторы (GCC, Clang, MSVC) выдают предупреждение "
            "о неявном fallthrough. Атрибут говорит: «я знаю, что делаю». Используйте редко — "
            "обычно лучше перестроить логику без fallthrough.\n\n"
            "Атрибут должен стоять как отдельное выражение перед следующим case/default. "
            "Не путать с `fallthrough` в других языках — в C++ это именно атрибут, а не ключевое слово."
        ),
        example(
            "cpp",
            """
            switch (x) {
                case 1:
                    do_something();
                    [[fallthrough]];  // намеренный fallthrough, подавляет warning
                case 2:
                    do_other();
                    break;
            }
            """,
        ),
        text(
            "Без [[fallthrough]] современные компиляторы (GCC, Clang, MSVC) выдают предупреждение "
            "о неявном fallthrough. Атрибут говорит: «я знаю, что делаю». Используйте редко — "
            "обычно лучше перестроить логику без fallthrough."
        ),
        heading("Цикл while"),
        text(
            "while проверяет условие перед каждой итерацией. Тело может не выполниться ни разу, "
            "если условие ложно с начала."
        ),
        example(
            "cpp",
            """
            int i = 0;
            while (i < 10) {
                std::cout << i << ' ';
                ++i;
            }
            // 0 1 2 3 4 5 6 7 8 9
            """,
        ),
        heading("Бесконечный цикл", 3),
        example(
            "cpp",
            """
            while (true) {
                auto input = get_input();
                if (input == "quit") break;
                process(input);
            }
            """,
        ),
        text(
            "while (true) — идиома для бесконечного цикла с выходом через break. "
            "Альтернатива: for (;;). Обязательно должен быть путь выхода (break, return, throw), "
            "иначе программа зависнет.\n\n"
            "Паттерн «цикл с условием в середине» (loop-and-a-half):\n"
            "```cpp\nwhile (true) {\n    auto data = read();\n    if (!data) break;\n    process(data);\n}\n```\n"
            "Часто чище, чем дублирование кода чтения перед и внутри цикла. "
            "Используйте для чтения потоков, обработки очередей, игровых циклов."
        ),
        heading("Цикл do-while"),
        text(
            "do-while проверяет условие ПОСЛЕ выполнения тела. Тело гарантированно выполняется "
            "ХОТЯ БЫ ОДИН РАЗ. Идеален для меню и ввода с проверкой."
        ),
        example(
            "cpp",
            """
            // Тело выполняется ХОТЯ БЫ ОДИН РАЗ
            std::string input;
            do {
                std::cout << "Enter command: ";
                std::cin >> input;
                process(input);
            } while (input != "exit");
            """,
        ),
        text(
            "Ключевое отличие: do-while выполняет тело минимум один раз, while — может не выполниться ни разу. "
            "Используйте do-while для меню, ввода данных, повторных попыток операции."
        ),
        heading("Цикл for"),
        heading("Классический for", 3),
        text(
            "Классический for имеет три части: инициализация, условие, итерация. "
            "Область видимости переменной инициализации ограничена циклом (C++11)."
        ),
        example(
            "cpp",
            """
            for (int i = 0; i < 10; ++i) {
                std::cout << i << ' ';
            }

            // Множественные переменные
            for (int i = 0, j = 10; i < j; ++i, --j) {
                // ...
            }

            // Область видимости i ограничена циклом (C++11)
            // for (int i = 0; ... — i не видна снаружи
            """,
        ),
        text(
            "Синтаксис: `for (init; condition; increment) body`.\n"
            "- init: выполняется один раз перед циклом (объявление/присваивание).\n"
            "- condition: проверяется перед каждой итерацией, если false — выход.\n"
            "- increment: выполняется после каждой итерации.\n\n"
            "Любая часть может быть опущена: `for (;;)` — бесконечный цикл. "
            "Переменная инициализации видна только внутри цикла (C++11)."
        ),
        heading("Range-based for (C++11) — ПРЕДПОЧТИТЕЛЬНЫЙ", 3),
        text(
            "Range-based for — современный, безопасный и читаемый способ итерации по контейнерам. "
            "Работает с любым типом, имеющим begin()/end() (массивы, vector, map, set и т.д.). "
            "Предпочтительнее классического for для контейнеров.\n\n"
            "Как это работает: компилятор преобразует range-based for в итерацию с итераторами:\n"
            "```cpp\nfor (auto&& __range = range; auto __begin = begin(__range), __end = end(__range); __begin != __end; ++__begin) {\n    auto&& element = *__begin;\n    // body\n}\n```\n"
            "Поэтому работает с любым типом, имеющим begin()/end() (или свободные функции begin/end в том же namespace)."
        ),
        example(
            "cpp",
            """
            std::vector<int> v = {1, 2, 3, 4, 5};

            // По значению (копия)
            for (int x : v) {
                std::cout << x << ' ';
            }

            // По ссылке (модификация)
            for (int& x : v) {
                x *= 2;
            }

            // По const ссылке (чтение без копии) — ПРЕДПОЧТИТЕЛЬНО для чтения
            for (const auto& x : v) {
                std::cout << x << ' ';
            }

            // С инициализатором (C++20)
            for (auto vec = get_vector(); const auto& x : vec) {
                // vec живёт только в цикле
            }
            """,
        ),
        text(
            "Три формы range-based for:\n"
            "- `for (auto x : v)` — копия значения (для мелких типов: int, char, small structs).\n"
            "- `for (auto& x : v)` — ссылка для модификации элементов.\n"
            "- `for (const auto& x : v)` — константная ссылка для чтения без копии (рекомендуется по умолчанию).\n\n"
            "`auto` автоматически выводит тип элемента. `const auto&` — безопасный дефолт для чтения."
        ),
        heading("Работает с любым range (имеющим begin/end)", 3),
        example(
            "cpp",
            """
            int arr[] = {1, 2, 3};
            for (int x : arr) { ... }

            std::map<int, std::string> m;
            for (const auto& [key, value] : m) {  // structured bindings (C++17)
                std::cout << key << ": " << value << '\n';
            }
            """,
        ),
        text(
            "Range-based for работает с:\n"
            "- Массивами (включая std::array)\n"
            "- STL контейнерами (vector, list, deque, map, set, unordered_map...)\n"
            "- Строками (std::string, std::string_view)\n"
            "- Любым типом с begin()/end() (пользовательские контейнеры)\n\n"
            "Structured bindings (C++17): `for (auto& [key, value] : map)` — "
            "распаковка пары в именованные переменные. Читабельнее `it->first` / `it->second`."
        ),
        heading("Управление циклом"),
        heading("break — выход из цикла", 3),
        example(
            "cpp",
            """
            for (int i = 0; i < 100; ++i) {
                if (found(i)) {
                    std::cout << "Found at " << i << '\n';
                    break;  // выходит только из этого цикла
                }
            }
            """,
        ),
        text(
            "break завершает выполнение ближайшего охватывающего цикла (while, do-while, for, switch). "
            "Во вложенных циклах break выходит только из внутреннего цикла.\n\n"
            "break также работает в switch. В C++ break не принимает аргумент (в отличие от Java/C#). "
            "Для выхода из функции используйте return, для завершения программы — exit() или return из main."
        ),
        heading("continue — пропуск итерации", 3),
        example(
            "cpp",
            """
            for (int i = 0; i < 10; ++i) {
                if (i % 2 == 0) continue;  // пропускаем чётные
                std::cout << i << ' ';  // 1 3 5 7 9
            }
            """,
        ),
        text(
            "continue пропускает остаток текущей итерации и переходит к следующей. "
            "В for — переходит к итерационной части, в while/do-while — к проверке условия. "
            "Полезно для фильтрации: `if (skip_condition) continue;` в начале тела.\n\n"
            "Важно: в for continue переходит к итерационной части (increment), а не к условию. "
            "В while/do-while — сразу к проверке условия. В range-based for continue работает корректно, "
            "переходя к следующему элементу. Не используйте goto для имитации continue — это антипаттерн."
        ),
        heading("Вложенные циклы — break выходит только из внутреннего", 3),
        example(
            "cpp",
            """
            outer: for (int i = 0; i < 10; ++i) {  // label для break outer (редко)
                for (int j = 0; j < 10; ++j) {
                    if (condition) break outer;  // выход из обоих (через label)
                }
            }
            // Лучше: вынести во функцию и использовать return
            """,
        ),
        text(
            "break выходит только из внутреннего цикла. Для выхода из нескольких уровней:\n"
            "1. Вынести во функцию — return (рекомендуется).\n"
            "- Использовать лейбл: `outer: for (...) { for (...) { break outer; } }` (редко).\n"
            "- Использовать флаг: `bool done = false; for (...) { if (cond) { done = true; break; } } if (done) break;`.\n\n"
            "Рекомендация: выносите сложную логику поиска в отдельную функцию с return.\n\n"
            "Почему лейблы лучше избегать: нарушают структурное программирование, "
            "ухудшают читаемость, усложняют рефакторинг. Функция с return — чистое решение, "
            "которое также улучшает тестируемость и переиспользование кода."
        ),
        heading("Практические паттерны"),
        heading("Поиск с break", 3),
        example(
            "cpp",
            """
            auto it = std::find(v.begin(), v.end(), value);
            if (it != v.end()) {
                // найдено
            }
            """,
        ),
        heading("Итерация с индексом", 3),
        example(
            "cpp",
            """
            // C++20: ranges
            for (auto [i, x] : std::views::enumerate(v)) { ... }

            // До C++20
            for (size_t i = 0; i < v.size(); ++i) { ... }
            """,
        ),
        heading("Цикл с условием в середине", 3),
        example(
            "cpp",
            """
            while (true) {
                auto data = read_chunk();
                if (!data) break;  // конец данных
                process(data);
            }
            """,
        ),
        text(
            "Паттерн «цикл с условием в середине» — идиома для чтения потоков, "
            "обработки пакетов, игровых циклов. Бесконечный цикл с break в середине "
            "часто чище, чем дублирование кода чтения перед и внутри цикла."
        ),
        heading("Практические задания"),
        text(
            "Выполните задания по порядку. Собирайте программу после каждого изменения: "
            "`g++ -std=c++20 -Wall -Wextra -o app main.cpp && ./app`."
        ),
        numbered(
            "FizzBuzz: выведите числа 1..100, кратные 3 → \"Fizz\", 5 → \"Buzz\", 3 и 5 → \"FizzBuzz\".",
            "Простые числа: выведите все простые числа до 100 (вложенный цикл, оптимизация до sqrt(n)).",
            "Меню: do-while меню: 1) Add 2) List 3) Exit. Используйте switch для обработки выбора.",
            "Коллац: введите n, пока n != 1: чётное → /2, нечётное → *3+1. Выведите последовательность.",
            "Range-based: дан vector<string>, выведите длину каждой строки через range-based for.",
        ),
        text("Пример ожидаемого результата для первого задания (начало):"),
        example(
            "text",
            "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n..."
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "Внутренний цикл проверки делителей можно ограничить sqrt(n): "
            "`for (int d = 2; d * d <= n; ++d)`. Число простое, если ни один делитель не подошёл.",
        ),
        heading("Практические паттерны (дополнительно)"),
        heading("Поиск с break", 3),
        example(
            "cpp",
            """
            auto it = std::find(v.begin(), v.end(), value);
            if (it != v.end()) {
                // найдено
            }
            """,
        ),
        heading("Итерация с индексом", 3),
        example(
            "cpp",
            """
            // C++20: ranges
            for (auto [i, x] : std::views::enumerate(v)) { ... }

            // До C++20
            for (size_t i = 0; i < v.size(); ++i) { ... }
            """,
        ),
        heading("Цикл с условием в середине", 3),
        example(
            "cpp",
            """
            while (true) {
                auto data = read_chunk();
                if (!data) break;  // конец данных
                process(data);
            }
            """,
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["`for (int i = 0; i <= 10; ++i)` для 10 элементов", "11 итераций (0..10), выход за границы", "`i < 10` (0..9)"],
                ["`if (x = 5)` вместо `==`", "Присваивает 5, условие всегда истинно", "`if (x == 5)` или `if (auto v = x; v == 5)`"],
                ["Забыли `break` в switch", "Fallthrough — выполнение следующего case", "Всегда добавляйте `break` или `[[fallthrough]]`"],
                ["Модификация контейнера в range-based for", "UB: итераторы инвалидируются", "Используйте итераторы или собирайте индексы для удаления"],
                ["`for (auto x : v)` копирует элементы", "Потеря производительности, изменения не сохраняются", "`for (const auto& x : v)` для чтения, `for (auto& x : v)` для записи"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Собирайте программу после каждого изменения: "
            "`g++ -std=c++20 -Wall -Wextra -o app main.cpp && ./app`."
        ),
        numbered(
            "FizzBuzz: выведите числа 1..100, кратные 3 → \"Fizz\", 5 → \"Buzz\", 3 и 5 → \"FizzBuzz\".",
            "Простые числа: выведите все простые числа до 100 (вложенный цикл, оптимизация до sqrt(n)).",
            "Меню: do-while меню: 1) Add 2) List 3) Exit. Используйте switch для обработки выбора.",
            "Коллац: введите n, пока n != 1: чётное → /2, нечётное → *3+1. Выведите последовательность.",
            "Range-based: дан vector<string>, выведите длину каждой строки через range-based for.",
        ),
        text("Пример ожидаемого результата для первого задания (начало):"),
        example(
            "text",
            "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n..."
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "Внутренний цикл проверки делителей можно ограничить sqrt(n): "
            "`for (int d = 2; d * d <= n; ++d)`. Число простое, если ни один делитель не подошёл.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем while отличается от do-while?",
            "Зачем нужен break в switch?",
            "В чём разница между `for (auto x : v)` и `for (auto& x : v)`?",
            "Что делает continue в цикле for?",
            "Как выйти из двух вложенных циклов одновременно?",
            "Когда использовать while, а когда for?",
        ),
        heading("Ответы", 3),
        numbered(
            "while проверяет условие перед итерацией (может не выполниться), do-while — после (минимум 1 раз).",
            "Без break выполнение «проваливается» в следующий case (fallthrough).",
            "`auto x` — копия значения, `auto& x` — ссылка на элемент (модификация видна в контейнере).",
            "continue пропускает остаток текущей итерации, переходит к следующей (в for — к инкременту).",
            "Вынести во функцию с return (рекомендуется), или использовать лейбл `outer: for (...) { break outer; }`, или флаг.",
            "for — когда известно число итераций или есть явный счётчик. while — когда условие сложное или итераций заранее неизвестно.",
        ),
        heading("Итоги"),
        bullets(
            "if/else: всегда скобки, early return, инициализатор в C++17 ограничивает область видимости.",
            "constexpr if (C++17): compile-time branching, неиспользуемые ветки отбрасываются.",
            "Switch: всегда break или [[fallthrough]], инициализатор в C++17, default для безопасности.",
            "While: условие перед телом. Do-while: тело минимум 1 раз, условие после.",
            "For: классический (init; cond; inc) и range-based (C++11). Range-based — предпочтителен для контейнеров.",
            "Break: выход из цикла/switch. Continue: пропуск итерации. Вложенные циклы — выносите в функцию с return.",
            "Range-based for: `const auto&` для чтения, `auto&` для модификации, `auto` — копия.",
            "Ошибки: off-by-one (i <= n вместо i < n), забытый break, копирование вместо ссылки, модификация контейнера во время итерации.",
        ),
        heading("Что дальше"),
        text(
            "Условия и циклы освоены. В следующем уроке разберём функции: объявление и определение, "
            "передача параметров (по значению, ссылке, rvalue), перегрузка, шаблоны, лямбды, "
            "корректность и производительность."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "cppreference: Statements — en.cppreference.com/w/cpp/language/statements",
            "C++ Core Guidelines: ES.70 — prefer range-for over indexed for",
            "C++ Core Guidelines: ES.71 — prefer for-statement over while-statement when there is an obvious loop variable",
            "C++17: if/switch with initializer — https://en.cppreference.com/w/cpp/language/if",
            "C++20: ranges, views, enumerate — https://en.cppreference.com/w/cpp/ranges",
        ),
    ],
}