"""Урок 1.5 курса C++: функции."""

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
    "topic_order": 5,
    "name": "1.5. Функции",
    "slug": "cpp-1-5-функции",
    "short_description": (
        "Объявление и определение функций, параметры (по значению, ссылке, rvalue), "
        "возвращаемые значения, перегрузка, области видимости, лямбда-функции."
    ),
    "topic_name": "Функции",
    "topic_description": (
        "Полное руководство по функциям в C++: объявление/определение, "
        "параметры (по значению, lvalue/rvalue ссылке, указателю), возвращаемые значения, "
        "перегрузка, области видимости, linkage, лямбда-функции, атрибуты."
    ),
    "learning_objectives": [
        "Объявлять и определять функции, разделять declaration/definition между .h и .cpp",
        "Выбирать правильный способ передачи параметров: по значению, lvalue/rvalue ссылке, указателю",
        "Использовать параметры по умолчанию и понимать правила их расположения",
        "Возвращать значения: по значению, по ссылке, через std::pair/tuple, через std::optional",
        "Создавать перегруженные функции и понимать правила разрешения перегрузки",
        "Понимать области видимости (block, function, global), linkage (external/internal), anonymous namespace",
        "Писать лямбда-функции с захватом переменных, generic lambdas, mutable lambdas",
        "Применять атрибуты функций: [[nodiscard]], [[noreturn]], [[deprecated]], constexpr",
        "Избегать типичных ошибок: возврат ссылки на локальную переменную, отсутствие inline в header",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "cpp",
        "функции",
        "параметры",
        "перегрузка",
        "лямбда",
        "область видимости",
        "linkage",
    ],
    "starter_code": code(
        r"""
        #include <iostream>

        int add(int a, int b) {
            return a + b;
        }

        int main() {
            std::cout << add(2, 3) << '\n';
            return 0;
        }
        """
    ),
    "hints": [
        "Объявление в .h, определение в .cpp — стандартная практика для больших проектов.",
        "Передавайте большие объекты по const&, небольшие — по значению, для модификации — по &.",
        "Возвращайте по значению (RVO/NRVO оптимизирует), по ссылке — только на долгоживущие объекты.",
        "Lambda захват: [=] по значению, [&] по ссылке, [=, &x] смешанный. mutable позволяет менять захваченные по значению.",
    ],
    "content": [
        text(
            "Функции — строительные блоки программы. Хорошо спроектированная функция делает одну вещь, "
            "и делает её хорошо. В C++ функции мощные: перегрузка, шаблоны, лямбды, constexpr, "
            "атрибуты. Понимание параметров (value/ref/rvalue), возвращаемых значений, перегрузки "
            "и областей видимости — фундамент качественного C++ кода. В этом уроке разберём всё от "
            "объявления до лямбд и атрибутов."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объявлять и определять функции, разделять declaration/definition между .h и .cpp;",
            "выбирать правильный способ передачи параметров: по значению, lvalue/rvalue ссылке, указателю;",
            "использовать параметры по умолчанию и понимать правила их расположения;",
            "возвращать значения: по значению, по ссылке, через std::pair/tuple, через std::optional;",
            "создавать перегруженные функции и понимать правила разрешения перегрузки;",
            "понимать области видимости (block, function, global), linkage (external/internal), anonymous namespace;",
            "писать лямбда-функции с захватом переменных, generic lambdas, mutable lambdas;",
            "применять атрибуты функций: [[nodiscard]], [[noreturn]], [[deprecated]], constexpr;",
            "избегать типичных ошибок: возврат ссылки на локальную переменную, отсутствие inline в header.",
        ),
        heading("Объявление и определение"),
        heading("Разделение (header + source)", 3),
        text(
            "В C++ принято разделять объявление (interface) и определение (implementation). "
            "Объявление в заголовочном файле (.h/.hpp) сообщает компилятору сигнатуру функции. "
            "Определение в исходном файле (.cpp) содержит тело функции. Это позволяет:\n"
            "- Сократить время компиляции (изменение реализации не требует перекомпиляции всех includers)\n"
            "- Скрыть детали реализации (encapsulation)\n"
            "- Избежать ошибок ODR (One Definition Rule) при множественном включении"
        ),
        example(
            "cpp",
            """
            // math.h — объявление (interface)
            #ifndef MATH_H
            #define MATH_H

            int add(int a, int b);        // объявление
            double multiply(double x, double y);

            #endif

            // math.cpp — определение (implementation)
            #include "math.h"

            int add(int a, int b) {
                return a + b;
            }

            double multiply(double x, double y) {
                return x * y;
            }

            // main.cpp
            #include "math.h"
            #include <iostream>

            int main() {
                std::cout << add(2, 3) << '\n';        // 5
                std::cout << multiply(2.5, 4.0) << '\n'; // 10
            }
            """,
        ),
        text(
            "Include guards (`#ifndef/#define/#endif` или `#pragma once`) защищают от множественного включения. "
            "`#pragma once` поддерживается всеми современными компиляторами и короче, но не стандартизирован. "
            "Include guards — переносимый стандарт."
        ),
        heading("Inline функции (в заголовочном файле)", 3),
        text(
            "Функции, определённые в заголовочном файле, должны быть отмечены `inline` (или `constexpr`), "
            "иначе при включении в несколько .cpp файлов получим ошибку ODR (multiple definitions). "
            "`inline` — подсказка компилятору подставить код функции в место вызова (встраивание), "
            "но главное — разрешает множественные определения в разных translation units."
        ),
        example(
            "cpp",
            """
            // utils.h
            inline int square(int x) { return x * x; }  // подсказка компилятору

            // или constexpr (C++11) — гарантированно inline
            constexpr int cube(int x) { return x * x * x; }
            """,
        ),
        text(
            "`constexpr` подразумевает `inline` (C++11+). `constexpr` функции могут вычисляться на этапе компиляции. "
            "Для маленьких функций в header: предпочитайте `constexpr` (если возможно) или `inline`. "
            "Для больших функций — переносите определение в .cpp."
        ),
        heading("Параметры"),
        heading("По значению (копия)", 3),
        text(
            "При передаче по значению создаётся копия аргумента. Изменения внутри функции не влияют на оригинал. "
            "Подходит для мелких типов (int, double, char, small structs до ~16-32 байт), где копия дешевле ссылки."
        ),
        example(
            "cpp",
            """
            void modify(int x) {
                x = 20;  // меняет копию
            }

            int main() {
                int a = 10;
                modify(a);
                std::cout << a;  // 10 (не изменилось)
            }
            """,
        ),
        heading("По ссылке (lvalue reference) — для модификации", 3),
        text(
            "Передача по lvalue reference (`T&`) позволяет функции модифицировать оригинальный объект. "
            "Никакой копии не создаётся. Используйте для 'in-out' параметров — когда функция должна изменить аргумент."
        ),
        example(
            "cpp",
            """
            void modify(int& x) {
                x = 20;  // меняет оригинал
            }

            int main() {
                int a = 10;
                modify(a);
                std::cout << a;  // 20
            }
            """,
        ),
        heading("По const ссылке — для чтения больших объектов", 3),
        text(
            "Передача по `const T&` — стандарт для чтения больших объектов (std::string, std::vector, большие структуры). "
            "Копия не создаётся, модификация запрещена на уровне компилятора. Это default choice для 'in' параметров."
        ),
        example(
            "cpp",
            """
            void print(const std::string& s) {  // без копирования
                std::cout << s << '\n';
            }

            void print(const std::vector<int>& v) {
                for (int x : v) std::cout << x << ' ';
            }
            """,
        ),
        heading("По rvalue reference (C++11) — для move semantics", 3),
        text(
            "Rvalue reference (`T&&`) связывается с временными объектами (rvalues). "
            "Позволяет 'украсть' ресурсы временного объекта (move semantics) вместо копирования. "
            "Используйте для 'sink' параметров — когда функция забирает владение ресурсом."
        ),
        example(
            "cpp",
            """
            void take_ownership(std::string&& s) {
                std::cout << "Taking: " << s << '\n';
                // s можно переместить: std::string mine = std::move(s);
            }

            int main() {
                take_ownership("temporary");        // rvalue — OK
                std::string s = "hello";
                take_ownership(std::move(s));       // явное приведение к rvalue
                // s теперь в валидном но неуточненном состоянии
            }
            """,
        ),
        text(
            "Правила rvalue reference:\n"
            "- `T&&` параметр принимает только rvalues (временные объекты, `std::move(x)`).\n"
            "- `std::move(x)` — приведение lvalue к rvalue (cast к `T&&`), не перемещает само по себе.\n"
            "- Внутри функции используйте `std::move(param)` для передачи дальше.\n"
            "- `std::forward<T>(param)` — в шаблонах для perfect forwarding."
        ),
        heading("Указатели — опциональные/nullable параметры", 3),
        text(
            "Указатели (`T*`) позволяют передавать 'нет значения' (nullptr). "
            "Используйте когда параметр опционален или когда нужна совместимость с C API. "
            "Всегда проверяйте на nullptr перед разыменованием."
        ),
        example(
            "cpp",
            """
            void process(int* ptr) {
                if (ptr) *ptr = 42;
            }

            int main() {
                int x = 0;
                process(&x);    // OK
                process(nullptr); // OK, ничего не делает
            }
            """,
        ),
        heading("Параметры по умолчанию", 3),
        text(
            "Параметры по умолчанию задаются в объявлении (в .h). Они должны идти после всех параметров без значений по умолчанию. "
            "Порядок: обязательные параметры → параметры с умолчанием. "
            "Значения подставляются на месте вызова (compile-time для констант)."
        ),
        example(
            "cpp",
            """
            void connect(std::string host, int port = 80, bool ssl = false) {
                // ...
            }

            connect("example.com");           // port=80, ssl=false
            connect("example.com", 443);      // port=443, ssl=false
            connect("example.com", 443, true); // все явно
            """,
        ),
        text(
            "Правила:\n"
            "- Параметры по умолчанию только в объявлении (в .h), не в определении (.cpp).\n"
            "- Все параметры после первого с умолчанием тоже должны иметь значения по умолчанию.\n"
            "- Нельзя переопределять значения по умолчанию в переопределении виртуальной функции (статическое связывание)."
        ),
        heading("Возвращаемые значения"),
        heading("Обычный возврат", 3),
        text(
            "Оператор `return` завершает функцию и возвращает значение. Для `void` функций `return;` опционален в конце. "
            "C++17 гарантирует RVO (Return Value Optimization) / NRVO — возврат больших объектов по значению не требует копирования."
        ),
        example(
            "cpp",
            """
            int add(int a, int b) {
                return a + b;
            }

            // Неявный возврат void
            void print_hello() {
                std::cout << "Hello\n";
                // return; не нужен
            }
            """,
        ),
        text(
            "RVO/NRVO: современные компиляторы (C++17 гарантирует) устраняют копирование при возврате локального объекта. "
            "`return MyBigObject();` — ноль копий. Пишите `return value;` естественно, не используйте выходные параметры для этого."
        ),
        heading("Возврат по ссылке", 3),
        text(
            "Возврат `T&` или `const T&` позволяет функции возвращать ссылку на существующий объект. "
            "Объект должен жить дольше вызова функции (не локальная переменная!). Используется для доступа к элементам контейнеров, синглтонов, статических переменных."
        ),
        example(
            "cpp",
            """
            int& get_element(std::vector<int>& v, size_t i) {
                return v[i];  // возвращает ссылку на элемент
            }

            int main() {
                std::vector<int> v = {1, 2, 3};
                get_element(v, 1) = 20;  // v[1] = 20
            }
            """,
        ),
        callout(
            "warning",
            "Возврат ссылки на локальную переменную",
            "Никогда не возвращайте ссылку/указатель на локальную переменную — она уничтожается при выходе из функции. "
            "`int& f() { int x = 5; return x; }` — UB. Возвращайте по значению или ссылку на объект с большим временем жизни."
        ),
        heading("Структурированные привязки (C++17) — возврат нескольких значений", 3),
        text(
            "Возврат нескольких значений через `std::pair`, `std::tuple` или `std::array` с structured bindings (C++17) — "
            "чистый способ вернуть несколько значений без выходных параметров."
        ),
        example(
            "cpp",
            """
            #include <tuple>

            std::pair<int, int> divide(int a, int b) {
                return {a / b, a % b};
            }

            auto [quotient, remainder] = divide(17, 5);  // 3, 2

            // Или через tuple для 3+ значений
            std::tuple<int, int, int> stats(const std::vector<int>& v) {
                return {*min_element(v.begin(), v.end()),
                        *max_element(v.begin(), v.end()),
                        std::accumulate(v.begin(), v.end(), 0)};
            }
            """,
        ),
        heading("std::optional (C++17) — отсутствие значения", 3),
        text(
            "`std::optional<T>` — тип-обёртка, который может содержать значение `T` или быть пустым (`std::nullopt`). "
            "Заменяет возврат указателя/пустого optional для сигнализации 'нет значения'. "
            "Проверка: `if (opt)`, `*opt`, `opt.value()`, `opt.value_or(default)`."
        ),
        example(
            "cpp",
            """
            #include <optional>

            std::optional<int> find(const std::vector<int>& v, int x) {
                for (size_t i = 0; i < v.size(); ++i) {
                    if (v[i] == x) return i;
                }
                return std::nullopt;  // не найдено
            }

            int main() {
                if (auto idx = find(v, 42); idx) {
                    std::cout << "Found at " << *idx << '\n';
                } else {
                    std::cout << "Not found\n";
                }
            }
            """,
        ),
        heading("Перегрузка функций (overloading)"),
        text(
            "Перегрузка позволяет нескольким функциям иметь одно имя, но разные параметры. "
            "Компилятор выбирает подходящую функцию по правилам разрешения перегрузки (overload resolution). "
            "Перегружены могут быть: обычные функции, методы классов, конструкторы, операторы."
        ),
        example(
            "cpp",
            """
            void print(int x) { std::cout << "int: " << x << '\n'; }
            void print(double x) { std::cout << "double: " << x << '\n'; }
            void print(const std::string& s) { std::cout << "string: " << s << '\n'; }

            // Шаблоны также участвуют в перегрузке
            template<typename T>
            void print(T x) { std::cout << "template: " << x << '\n'; }

            int main() {
                print(42);          // void print(int)
                print(3.14);        // void print(double)
                print("hello");     // void print(const std::string&)
                print(42L);         // template (long)
            }
            """,
        ),
        heading("Правила разрешения перегрузки", 3),
        text(
            "Компилятор выбирает лучшую функцию по рангам соответствия (от лучшего к худшему):\n\n"
            "1. **Exact match** — точное совпадение типов (включая квалификаторы cv, ref-qualifiers)\n"
            "2. **Promotion** — целочисленные продвижения (`char`→`int`, `float`→`double`)\n"
            "3. **Conversion** — стандартные преобразования (`int`→`double`, `Derived*`→`Base*`)\n"
            "4. **User-defined conversion** — конструкторы конвертации, операторы приведения\n"
            "5. **Ellipsis** (`...`) — variadic functions\n\n"
            "При равенстве рангов — ambiguous call (ошибка компиляции)."
        ),
        heading("Правила разрешения перегрузки (подробнее)", 3),
        table(
            ["Ранг", "Категория", "Примеры"],
            [
                ["1", "Exact match", "int → int, const int& → const int&, T& → T&"],
                ["2", "Promotion", "char → int, short → int, float → double, enum → int"],
                ["3", "Conversion", "int → double, int → long, Derived* → Base*, int → bool"],
                ["4", "User-defined", "MyType(int) constructor, operator double()"],
                ["5", "Ellipsis", "printf(...)"],
            ],
        ),
        text(
            "Типичные проблемы:\n"
            "- `f(int)` vs `f(double)`: `f(3.14)` выбирает `double`, `f(42)` — `int`.\n"
            "- `f(int)` vs `f(long)`: на 32-битных `int`→`long` promotion, на 64-битных `long` может быть тем же размером.\n"
            "- `f(const T&)` vs `f(T&&)`: lvalue выбирает `const T&`, rvalue — `T&&`.\n"
            "- Шаблоны имеют низший приоритет не-шаблонов при равном ранге."
        ),
        heading("Перегрузка и шаблоны", 3),
        text(
            "Шаблоны функций участвуют в перегрузке наравне с обычными функциями. "
            "Не-шаблонные функции имеют приоритет над шаблонами при равном ранге соответствия. "
            "SFINAE (Substitution Failure Is Not An Error) позволяет исключать шаблоны из перегрузки."
        ),
        example(
            "cpp",
            """
            template<typename T>
            void print(T x) { std::cout << "template: " << x << '\n'; }

            void print(int x) { std::cout << "int: " << x << '\n'; }

            int main() {
                print(42);        // int overload (exact match, non-template wins)
                print(3.14);      // template (double)
                print("hello");   // template (const char*)
            }
            """,
        ),
        heading("Области видимости и linkage"),
        heading("Блочная область видимости", 3),
        text(
            "Переменные, объявленные в блоке `{ ... }`, видны только внутри этого блока. "
            "Вложенные блоки создают вложенные области видимости. Внешний блок не видит внутренние переменные."
        ),
        example(
            "cpp",
            """
            void func() {
                int x = 1;      // видна в func
                {
                    int y = 2;  // видна только в этом блоке
                    x = y;      // OK
                }
                // y недоступна
            }
            """,
        ),
        heading("Глобальная область видимости", 3),
        text(
            "Глобальные переменные (вне функций) имеют статическое время жизни — "
            "создаются до `main`, уничтожаются после. Linkage определяет видимость в других translation units."
        ),
        example(
            "cpp",
            """
            // file1.cpp
            int global = 10;           // external linkage (видно везде)
            static int file_local = 5; // internal linkage (только в этом TU)
            const int CONST_VAL = 42;  // internal linkage по умолчанию (C++)

            // file2.cpp
            extern int global;         // объявление external linkage
            // file_local недоступен
            """,
        ),
        text(
            "Linkage в C++:\n"
            "- **External linkage** (`extern` по умолчанию для non-const): видно во всех TU, линкуется.\n"
            "- **Internal linkage** (`static`, `const` без `extern`, `anonymous namespace`): видно только в этом TU.\n"
            "- **No linkage**: локальные переменные, параметры функций.\n\n"
            "`const` переменные в глобальной области имеют internal linkage по умолчанию (в отличие от C). "
            "Для external linkage: `extern const int x = 42;`."
        ),
        heading("Anonymous namespace (современная замена static)", 3),
        example(
            "cpp",
            """
            // utils.cpp
            namespace {
                int helper() { return 42; }  // internal linkage
            }
            // helper недоступен из других TU
            """,
        ),
        text(
            "Anonymous namespace (`namespace { ... }`) — современная замена `static` для функций и переменных в .cpp. "
            "Даёт internal linkage всему содержимому. Преимущества: работает для классов, шаблонов, "
            "не загрязняет глобальное пространство имён."
        ),
        heading("Inline переменные (C++17) — определение в header", 3),
        text(
            "`inline` переменные (C++17) позволяют определять глобальные переменные в header файлах без нарушения ODR. "
            "Все TU видят одно и то же определение. Заменяет `extern` в .h + определение в .cpp."
        ),
        example(
            "cpp",
            """
            // config.h
            inline const std::string VERSION = "1.0.0";  // одно определение на всю программу
            inline int counter = 0;  // одна переменная на всю программу
            """,
        ),
        text(
            "`inline` переменная имеет external linkage, но допускает множественные определения (как inline функции). "
            "Все определения должны быть идентичны. Полезно для конфигурации, синглтонов, глобальных настроек."
        ),
        heading("Лямбда-функции (C++11)"),
        text(
            "Лямбда — анонимная функция, создаваемая на месте. Синтаксис: `[captures](params) -> ret { body }`. "
            "Могут захватывать переменные из окружающей области видимости. "
            "Generic lambdas (C++14) / template lambdas (C++20) позволяют писать полиморфные лямбды."
        ),
        example(
            "cpp",
            """
            auto add = [](int a, int b) { return a + b; };
            add(2, 3);  // 5

            // Захват переменных
            int x = 10;
            auto add_x = [x](int a) { return a + x; };      // по значению
            auto add_x_ref = [&x](int a) { return a + x; }; // по ссылке
            auto add_all = [=](int a) { return a + x; };    // все по значению
            auto add_all_ref = [&](int a) { return a + x; };// все по ссылке

            // Mutable лямбда (может менять захваченные по значению)
            auto counter = [count = 0]() mutable { return ++count; };

            // Generic lambda (C++14) / template lambda (C++20)
            auto print = [](auto x) { std::cout << x << '\n'; };
            """,
        ),
        text(
            "Захват переменных:\n"
            "- `[=]` — все по значению (копия).\n"
            "- `[&]` — все по ссылке.\n"
            "- `[x, &y]` — `x` по значению, `y` по ссылке.\n"
            "- `[=, &y]` — все по значению, кроме `y` по ссылке.\n"
            "- `[&, x]` — все по ссылке, кроме `x` по значению.\n\n"
            "`mutable` позволяет менять захваченные по значению переменные внутри лямбды. "
            "Generic lambda (`auto` параметр) — шаблонная лямбда (C++14). "
            "Template lambda (C++20): `[](auto&& x) { ... }` — perfect forwarding."
        ),
        heading("Атрибуты функций"),
        text(
            "Атрибуты (C++11+) — метаданные для компилятора. Полезные для функций:"
        ),
        example(
            "cpp",
            """
            [[nodiscard]] int compute() { return 42; }  // warning если игнорировать возврат

            [[noreturn]] void abort() { throw std::runtime_error("abort"); }

            [[deprecated("Use new_api()")]] void old_api() {}

            constexpr int factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }
            """,
        ),
        text(
            "`[[nodiscard]]` — предупреждение, если возвращаемое значение игнорируется. Критично для функций, "
            "где игнорирование результата — баг (например, `std::optional`, коды ошибок).\n\n"
            "`[[noreturn]]` — функция никогда не возвращается (throw, exit, бесконечный цикл). "
            "Помогает оптимизатору и анализу потока управления.\n\n"
            "`[[deprecated(\"msg\")]]` — помечает устаревший API, компилятор предупреждает при использовании.\n\n"
            "`constexpr` — функция может вычисляться на этапе компиляции. Подразумевает `inline`."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["Возврат ссылки на локальную переменную", "UB: dangling reference", "Возвращайте по значению или ссылку на объект с большим временем жизни"],
                ["void f(int& x) для чтения", "Можно случайно изменить аргумент", "void f(const int& x)"],
                ["Забыли 'inline' в header для не-template функций", "ODR violation при множественном включении", "'inline' или 'static' или перенесите в .cpp"],
                ["Перегрузка по возвращаемому типу", "НЕЛЬЗЯ: перегрузка только по параметрам", "Разные параметры или разные имена"],
                ["Захват по ссылке в долгоживущей лямбде", "Dangling reference после выхода из области видимости", "Захватывайте по значению или используйте shared_ptr"],
                ["Забыли 'inline' в header для функции", "Multiple definition error при линковке", "Добавьте 'inline' или перенесите в .cpp"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Собирайте программу после каждого изменения: "
            "`g++ -std=c++20 -Wall -Wextra -o app main.cpp && ./app`."
        ),
        numbered(
            "Перегрузка: напишите 3 перегрузки `max` для `int`, `double`, `std::string` (лексикографическое сравнение).",
            "Параметры: напишите `swap` по ссылке, `print` по const ссылке, `take` по rvalue ссылке. Проверьте: `swap(a, b)`, `print(large_string)`, `take(std::move(s))`.",
            "Возврат: функция `min_max(const std::vector<int>&)` → `std::pair<int, int>` (min, max). Используйте structured bindings при вызове.",
            "Optional: функция `safe_divide(double a, double b)` → `std::optional<double>`. Возвращает `nullopt` при делении на ноль.",
            "Лямбда: используйте лямбду с `std::sort` для сортировки `std::vector<int>` по убыванию. Добавьте лямбду для фильтрации чётных чисел через `std::copy_if`.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "max(3, 5) = 5\n"
            "max(3.14, 2.71) = 3.14\n"
            "max(\"apple\", \"banana\") = \"banana\""
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "`swap`: `void swap(int& a, int& b)`. `print`: `void print(const std::string& s)`. `take`: `void take(std::string&& s)` — внутри `std::cout << \"Taking: \" << std::move(s);`. Тест: `std::string s = \"hello\"; take(std::move(s));`.",
        ),
        heading("Проверьте себя"),
        numbered(
            "В чём разница между объявлением и определением функции?",
            "Когда передавать по значению, по const ссылке, по ссылке, по rvalue ссылке, по указателю?",
            "Зачем нужны параметры по умолчанию и где их задавать?",
            "Чем `std::optional` лучше возврата указателя для обозначения 'нет значения'?",
            "По каким правилам компилятор выбирает перегруженную функцию?",
            "В чём разница между `static` и anonymous namespace для internal linkage?",
            "Когда лямбда должна быть `mutable`?",
            "Какие атрибуты функций полезны в продакшн коде?",
        ),
        heading("Ответы", 3),
        numbered(
            "Объявление (declaration) — сигнатура функции (имя, параметры, возврат), сообщает компилятору что функция существует. Определение (definition) — тело функции с реализацией. Declaration в .h, definition в .cpp.",
            "По значению: мелкие типы (int, double, small struct), когда копия дешевле. const&: чтение больших объектов (string, vector). &: модификация оригинала (in-out). &&: захват владения (move). *: nullable/optional параметр или C API.",
            "В объявлении (в .h), после обязательных параметров. Значения вычисляются в точке вызова. Порядок: обязательные → с умолчанием.",
            "optional — типобезопасный, явный, нельзя случайно разыменовать null, имеет value_or(), работает со value-семантикой. Указатель — легко забыть проверить на nullptr, нет value-семантики.",
            "1. Exact match → 2. Promotion → 3. Conversion → 4. User-defined conversion → 5. Ellipsis. Non-template побеждает template при равном ранге.",
            "`static` — только для переменных/функций в TU. Anonymous namespace — работает для всего (классы, шаблоны, переменные), современный стандарт.",
            "Когда лямбда захватывает по значению (`[=]` или `[x]`) и нужно изменить захваченную копию внутри лямбды. Без `mutable` захваченные по значению `const`.",
            "[[nodiscard]] — игнорирование результата = баг. [[noreturn]] — функция не возвращается (throw/exit). [[deprecated]] — миграция API. constexpr — compile-time вычисление.",
        ),
        heading("Итоги"),
        bullets(
            "Функции: declaration в .h, definition в .cpp. inline/constexpr в header. ODR — одно определение на программу.",
            "Параметры: по значению (мелкие), const& (чтение больших), & (модификация), && (move), * (nullable). По умолчанию — в объявлении.",
            "Возврат: по значению (RVO/NRVO), & (доступ к существующему), pair/tuple/optional (множественные значения/отсутствие).",
            "Перегрузка: exact match > promotion > conversion > user-defined > ellipsis. Non-template побеждает template. SFINAE для шаблонов.",
            "Области видимости: block, function, global. Linkage: external (extern), internal (static/anon namespace/const), none (local).",
            "Лямбды: [=]/[&]/[x,&y], mutable, generic (auto), template (C++20). Захват: по значению (копия), по ссылке (оригинал).",
            "Атрибуты: [[nodiscard]], [[noreturn]], [[deprecated]], constexpr. Помогают компилятору находить баги и оптимизировать.",
            "Best practices: одна функция — одна задача, const correctness, pass by const& для больших, RVO/NRVO для возврата, constexpr где возможно.",
        ),
        heading("Что дальше"),
        text(
            "Функции освоены. В следующем уроке разберём массивы и указатели: сырые массивы, std::array, "
            "std::vector, указатели и умные указатели (unique_ptr, shared_ptr), арифметика указателей, "
            "RAII и управление ресурсами."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "cppreference: Functions — en.cppreference.com/w/cpp/language/functions",
            "C++ Core Guidelines: F.1 — Package meaningful operations as carefully named functions",
            "C++ Core Guidelines: F.15 — Prefer simple and conventional ways of passing information",
            "C++ Core Guidelines: F.16 — For 'in' parameters, pass by const reference",
            "C++ Core Guidelines: F.17 — For 'in-out' parameters, pass by reference",
            "C++ Core Guidelines: F.18 — For 'will move from' parameters, pass by rvalue reference",
            "C++ Lambda expressions — en.cppreference.com/w/cpp/language/lambda",
        ),
    ],
}