"""Урок 1.6 курса C++: массивы и строки."""

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
    "topic_order": 6,
    "name": "1.6. Массивы и строки",
    "slug": "cpp-1-6-массивы-и-строки",
    "short_description": (
        "C-массивы, std::array, std::string, std::string_view — "
        "объявление, инициализация, доступ, перебор, безопасность."
    ),
    "topic_name": "Массивы и строки",
    "topic_description": (
        "Работа с последовательностями в C++: встроенные массивы, std::array, "
        "std::string, std::string_view. Безопасный доступ, перебор, строковые операции."
    ),
    "learning_objectives": [
        "Объявлять и инициализировать C-массивы, std::array, std::string",
        "Безопасно обращаться к элементам: operator[] vs at(), проверка границ",
        "Понимать ухудшение массива до указателя (array decay) и как его избежать",
        "Использовать std::array вместо C-массивов: методы, итераторы, присваивание",
        "Работать со std::string: конкатенация, поиск, подстроки, модификация",
        "Применять std::string_view для zero-copy просмотра строк",
        "Итерироваться по контейнерам через range-based for",
        "Избегать типичных ошибок: UB при выходе за границы, модификация литералов",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "cpp",
        "массивы",
        "std::array",
        "std::string",
        "std::string_view",
        "итерация",
    ],
    "starter_code": code(
        r"""
        #include <iostream>
        #include <array>
        #include <string>

        int main() {
            int arr[3] = {1, 2, 3};
            std::array<int, 3> arr2 = {1, 2, 3};
            std::string s = "hello";

            for (int x : arr) std::cout << x << ' ';
            std::cout << '\n';
            for (int x : arr2) std::cout << x << ' ';
            std::cout << '\n';
            for (char c : s) std::cout << c << ' ';
            std::cout << '\n';
            return 0;
        }
        """
    ),
    "hints": [
        "C-массив не хранит свой размер — используйте std::size(arr) или std::array.",
        "std::array — обёртка с нулевой накладной стоимостью, поддерживает =, ==, .at().",
        "std::string_view — zero-copy взгляд на строку, удобен для функций-приёмников.",
        "Range-based for работает со всеми: C-массивы, std::array, std::string, std::vector.",
    ],
    "content": [
        text(
            "Последовательности данных — основа большинства программ. В C++ есть несколько "
            "способов хранить и обрабатывать наборы значений: встроенные (C-style) массивы, "
            "std::array, std::vector, std::string, std::string_view. Выбор правильного инструмента "
            "влияет на безопасность, производительность и читаемость кода. В этом уроке разберём "
            "встроенные массивы, std::array, std::string, std::string_view — их объявление, "
            "инициализацию, доступ к элементам, перебор и типичные ошибки.\n\n"
            "Понимание различий между этими типами критично для написания эффективного и безопасного кода. "
            "C-массивы — это низкоуровневые строительные блоки с минимальной накладной стоимостью, "
            "но без встроенных проверок безопасности. std::array — это современная обёртка, "
            "добавляющая безопасность и удобство без накладных расходов. std::string — полноценный "
            "владелец строковых данных с богатым API. std::string_view — легковесный не владеющий "
            "представление для эффективного просмотра строк без копирования."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объявлять и инициализировать C-массивы и std::array, понимать разницу в размере и копировании;",
            "безопасно обращаться к элементам: operator[] vs at(), проверка границ через .at();",
            "понимать array decay — неявное приведение массива к указателю и потерю размера;",
            "использовать std::array вместо C-массивов: методы size(), at(), front(), back(), data();",
            "работать со std::string: конкатенация, поиск, подстроки, модификация, конвертация чисел;",
            "применять std::string_view для zero-copy просмотра строк без копирования;",
            "итерироваться по контейнерам через range-based for, использовать структурные привязки;",
            "избегать типичных ошибок: выход за границы, модификация строковых литералов, pointer decay.",
        ),
        heading("C-массивы (встроенные)"),
        text(
            "Встроенный (C-style) массив — непрерывная область памяти фиксированного размера, "
            "известного на этапе компиляции. Размер должен быть константой времени компиляции.\n\n"
            "C-массивы — это самый низкоуровневый способ хранения последовательностей в C++. "
            "Они отображаются напрямую на память без дополнительных накладных расходов. "
            "Однако они несут в себе исторические ограничения: фиксированный размер, "
            "отсутствие методов, невозможность присваивания и сравнения, "
            "неявное приведение к указателю (array decay) при передаче в функции."
        ),
        heading("Объявление и инициализация", 3),
        example(
            "cpp",
            """
            // Объявление
            int arr[5];              // неинициализирован (мусор в ячейках!)
            int arr2[5] = {1, 2, 3}; // {1, 2, 3, 0, 0} — остальное value-initialized
            int arr3[] = {1, 2, 3, 4, 5}; // размер выводится автоматически (5)

            // Многомерные
            int matrix[3][4] = {
                {1, 2, 3, 4},
                {5, 6, 7, 8},
                {9, 10, 11, 12}
            };
            """,
        ),
        text(
            "Важно: неинициализированный локальный массив содержит мусор (indeterminate values). "
            "Всегда инициализируйте массивы при объявлении. Частичная инициализация "
            "обнуляет остальные элементы (value-initialization).\n\n"
            "При объявлении массива без инициализатора элементы содержат неопределённые значения "
            "(indeterminate values) — остатки данных в памяти. Чтение таких значений — UB. "
            "Частичная инициализация (например, `int arr[5] = {1, 2, 3};`) гарантирует "
            "value-initialization для оставшихся элементов (нули для числовых типов). "
            "Полная инициализация `{}` обнуляет все элементы."
        ),
        heading("Доступ к элементам", 3),
        example(
            "cpp",
            """
            int arr[5] = {1, 2, 3, 4, 5};

            arr[0] = 10;       // запись
            int x = arr[2];    // чтение: 3

            // ОПАСНО: никакой проверки границ!
            // arr[10] = 5;    // UB: выход за границы

            // Безопасный способ (C++11):
            std::size(arr);    // 5 — работает для массивов и контейнеров
            """,
        ),
        callout(
            "warning",
            "Выход за границы массива",
            "Обращение за границы массива — неопределённое поведение (UB). Компилятор не проверяет границы во время выполнения. Используйте std::array::at() или std::vector::at() для проверки границ во время выполнения (бросает std::out_of_range)."
        ),
        heading("Размер массива", 3),
        example(
            "cpp",
            """
            int arr[5] = {1, 2, 3, 4, 5};
            int* ptr = arr;

            std::cout << sizeof(arr) / sizeof(arr[0]); // 5 — работает для массива
            std::cout << sizeof(ptr) / sizeof(ptr[0]); // 1 или 2 — НЕВЕРНО! ptr — указатель
            std::cout << std::size(arr);               // 5 (C++17, <iterator>)
            """,
        ),
        text(
            "Оператор sizeof для массива возвращает общий размер в байтах. "
            "Деление на sizeof(элемент) даёт количество элементов. "
            "Но при передаче массива в функцию он «ухудшается» до указателя (array decay), "
            "и sizeof перестаёт работать. Используйте std::size(arr) (C++17) или передавайте размер явно.\n\n"
            "std::size() (C++17, заголовок <iterator>) — универсальный способ получить размер "
            "для массивов, контейнеров и других типов с методом size(). "
            "В отличие от sizeof, std::size работает и для контейнеров, и для массивов, "
            "и даже для инициализационных списков."
        ),
        heading("Ухудшение массива до указателя (array decay)", 3),
        text(
            "Когда массив передаётся в функцию, он неявно преобразуется в указатель на первый элемент. "
            "Информация о размере теряется. Это называется array decay.\n\n"
            "Array decay — это неявное неявное преобразование массива в указатель на первый элемент. "
            "Оно происходит при передаче массива в функцию по значению, при присваивании указателю, "
            "в большинстве контекстов, где ожидается указатель. После decay массив теряет "
            "информацию о своём размере — он становится просто указателем на первый элемент."
        ),
        example(
            "cpp",
            """
            void func(int* ptr, size_t size);  // принимает указатель

            int arr[5] = {1,2,3,4,5};
            func(arr, 5);  // arr неявно преобразуется в int* (утеря размера!)

            // Внутри func: sizeof(ptr) == sizeof(int*), а не 5*sizeof(int)
            """,
        ),
        text(
            "Решения:\n"
            "1. Передавайте размер явно: `func(arr, 5)`\n"
            "2. Используйте std::array (размер — часть типа)\n"
            "3. Используйте std::vector для динамического размера\n"
            "4. Используйте шаблоны для вывода размера: `template<size_t N> void func(int (&arr)[N])`"
        ),
        heading("std::array (C++11) — обёртка над C-массивом"),
        text(
            "std::array — обёртка над C-массивом с нулевой накладной стоимостью (zero-overhead abstraction). "
            "Размер является частью типа: `std::array<int, 5>`. Поддерживает копирование, сравнение, итераторы."
        ),
        heading("Создание и инициализация", 3),
        example(
            "cpp",
            """
            #include <array>

            std::array<int, 5> arr = {1, 2, 3, 4, 5};  // размер — часть типа!
            std::array<int, 5> arr2{1, 2, 3, 4, 5};    // uniform init
            std::array<int, 5> arr3;                   // value-initialized: {0,0,0,0,0}
            std::array<std::string, 3> names{"a", "b", "c"};

            // До C++17 нужен double brace init для aggregate:
            // std::array<int, 3> arr = {{1, 2, 3}}; // до C++17
            """,
        ),
        heading("Методы std::array", 3),
        example(
            "cpp",
            """
            std::array<int, 5> arr = {1, 2, 3, 4, 5};

            arr.size();       // 5 (compile-time, constexpr)
            arr.max_size();   // 5
            arr.empty();      // false
            arr.front();      // 1
            arr.back();       // 5
            arr.data();       // указатель на первый элемент (int*)

            // Доступ с проверкой границ
            arr.at(2);        // 3, бросает std::out_of_range при ошибке
            arr[2];           // 3, без проверки (быстрее)

            // Присваивание и сравнение (в отличие от C-массивов!)
            std::array<int, 5> a = {1,2,3,4,5};
            std::array<int, 5> b = a;  // копирование!
            bool eq = (a == b);        // true
            """,
        ),
        text(
            "Ключевые преимущества std::array над C-массивом:\n"
            "- Размер — часть типа (std::array<int, 5> ≠ std::array<int, 6>)\n"
            "- Поддерживает копирование и присваивание (`b = a`)\n"
            "- Поддерживает сравнение (`==`, `!=`, `<`, ...)\n"
            "- Имеет методы: size(), at(), front(), back(), data()\n"
            "- Имеет итераторы: begin(), end(), rbegin(), rend()\n"
            "- Нулевые накладные расходы (zero-overhead abstraction)\n\n"
            "std::array — это агрегатный тип (aggregate), поэтому поддерживает агрегатную инициализацию. "
            "Размер является частью типа, поэтому std::array<int, 5> и std::array<int, 6> — "
            "совершенно разные, несовместимые типы. Это обеспечивает типовую безопасность размера "
            "на этапе компиляции. Память выделяется на стеке (как для C-массива), "
            "накладных расходов нет — sizeof(std::array<int, N>) == sizeof(int[N])."
        ),
        heading("std::array vs C-массив", 3),
        table(
            ["Особенность", "C-массив", "std::array"],
            [
                ["Размер в типе", "Нет", "Да (template параметр)"],
                ["Копирование", "Нет (ухудшение к указателю)", "Да"],
                ["Сравнение", "Нет", "Да"],
                ["Методы", "Нет", "size(), at(), front(), back()"],
                ["Итераторы", "Нет", "begin(), end()"],
                ["Накладные расходы", "0", "0 (zero-overhead abstraction)"],
            ],
        ),
        heading("std::string"),
        text(
            "std::string — класс для работы с текстом переменной длины. "
            "Управляет памятью автоматически, поддерживает Unicode (UTF-8), "
            "предоставляет богатый набор операций.\n\n"
            "std::string использует Small String Optimization (SSO) — оптимизацию для коротких строк. "
            "Короткие строки (обычно до 15-22 символов, зависит от реализации) хранятся прямо "
            "внутри объекта std::string без динамического выделения памяти. "
            "Это делает операции с короткими строками очень быстрыми. "
            "Строка управляет памятью автоматически: при копировании делает глубокую копию, "
            "при перемещении (C++11) — перехватывает указатель на буфер."
        ),
        heading("Создание и инициализация", 3),
        example(
            "cpp",
            """
            #include <string>

            std::string s1;           // пустая
            std::string s2 = "hello"; // из строкового литерала
            std::string s3(5, 'x');   // "xxxxx" (count, char)
            std::string s4(s2, 1, 3); // подстрока: "ell" (pos, count)
            std::string s5 = s2;      // копия
            """,
        ),
        heading("Основные операции", 3),
        example(
            "cpp",
            """
            std::string s = "hello";

            s.size()          // 5 (байт)
            s.length()        // 5 (синоним)
            s.empty()         // false
            s.front()         // 'h'
            s.back()          // 'o'

            s[0]              // 'h' (нет проверки)
            s.at(0)           // 'h' (с проверкой границ)

            s += " world";    // "hello world"
            s.append("!");    // "hello world!"
            s.push_back('?'); // "hello world!?"
            """,
        ),
        heading("Поиск и подстроки", 3),
        example(
            "cpp",
            """
            std::string s = "hello world hello";

            s.find("world")        // 6 (позиция первого вхождения)
            s.rfind("hello")       // 12 (последнее вхождение)
            s.find("xxx_example")          // std::string::npos (не найдено)

            s.substr(6, 5)         // "world" (pos, len)
            s.substr(6)            // "world hello" (до конца)
            """,
        ),
        heading("Модификация", 3),
        example(
            "cpp",
            """
            std::string s = "hello";

            s.insert(5, " world");   // "hello world"
            s.erase(5, 6);           // "hello" (pos, count)
            s.replace(0, 5, "Hi");   // "Hi world"
            s.clear();               // ""
            """,
        ),
        heading("Сравнение", 3),
        text(
            "Операторы сравнения (`==`, `!=`, `<`, `>`, `<=`, `>=`) работают лексикографически. "
            "Метод `compare()` возвращает отрицательное/ноль/положительное значение. "
            "Для регистронезависимого сравнения используйте `std::lexicographical_compare` "
            "с кастомным компаратором или приведите к одному регистру."
        ),
        example(
            "cpp",
            """
            std::string a = "apple", b = "banana";
            a == b    // false
            a < b     // true (лексикографическое)
            a.compare(b) < 0  // true
            """,
        ),
        heading("Конвертация", 3),
        example(
            "cpp",
            """
            std::string s = "42";
            int x = std::stoi(s);      // 42
            double d = std::stod("3.14"); // 3.14

            std::string s2 = std::to_string(42);      // "42"
            std::string s3 = std::to_string(3.14);    // "3.140000"
            """,
        ),
        heading("Raw string literals (C++11)", 3),
        example(
            "cpp",
            """
            std::string path = R"(C:\\Users\\Name\\Documents)";  // без экранирования
            std::string json = R"({\"key\": \"value\"})";         // удобно для JSON
            // R\"delimiter(...)delimiter\" — кастомные разделители
            std::string sql = R"sql(SELECT * FROM users WHERE name = \"John\")sql";
            """,
        ),
        heading("std::string_view (C++17) — zero-copy взгляд на строку", 3),
        text(
            "std::string_view — не владеющий взгляд на непрерывную последовательность символов. "
            "Не выделяет память, не копирует данные. Идеален для функций-приёмников строк."
        ),
        example(
            "cpp",
            """
            #include <string_view>

            void print(std::string_view sv) {  // принимает string, char*, string_view
                std::cout << sv << '\n';
            }

            std::string s = "hello";
            print(s);           // OK
            print("world");     // OK
            print(std::string_view(s, 2, 3)); // "llo" (подстрока без копии)
            """,
        ),
        text(
            "Преимущества string_view:\n"
            "- Zero-copy: не аллоцирует память, не копирует данные\n"
            "- Принимает string, char*, string_view, строковые литералы\n"
            "- Поддерживает substr(), find(), compare() без копирования\n"
            "- Подходит для функций-приёмников (input parameters)\n\n"
            "Осторожно: string_view не владеет данными. Нельзя хранить string_view дольше "
            "жизни исходной строки (dangling view).\n\n"
            "Операции с string_view:\n"
            "- `substr(pos, len)` — подстрока без копирования\n"
            "- `find()`, `rfind()`, `find_first_of()` — поиск без копирования\n"
            "- `compare()` — сравнение без копирования\n"
            "- `remove_prefix()`, `remove_suffix()` — изменение вида без копирования\n\n"
            "string_view идеально подходит для парсинга, токенизации, поиска подстрок "
            "в больших текстах, где копирование было бы дорого."
        ),
        heading("Перебор (итерация)"),
        heading("C-массив", 3),
        example(
            "cpp",
            """
            int arr[] = {1, 2, 3, 4, 5};

            for (int i = 0; i < 5; ++i) { ... }
            for (int x : arr) { ... }  // range-based for работает!
            """,
        ),
        heading("std::array", 3),
        example(
            "cpp",
            """
            std::array<int, 5> arr = {1,2,3,4,5};
            for (int& x : arr) x *= 2;  // модификация
            """,
        ),
        heading("std::string", 3),
        example(
            "cpp",
            """
            std::string s = "hello";
            for (char c : s) std::cout << c << ' ';  // h e l l o
            for (auto& c : s) c = std::toupper(c);   // HELLO
            """,
        ),
        text(
            "Range-based for работает с любым типом, имеющим begin()/end() — "
            "массивы, std::array, std::vector, std::string, std::map и т.д. "
            "Предпочтительнее классического for для контейнеров.\n\n"
            "Как это работает: компилятор преобразует range-based for в итерацию с итераторами:\n"
            "```cpp\nfor (auto&& __range = range; auto __begin = begin(__range), __end = end(__range); __begin != __end; ++__begin) {\n    auto&& element = *__begin;\n    // body\n}\n```\n"
            "Поэтому работает с любым типом, имеющим begin()/end() (или свободные функции begin/end в том же namespace)."
        ),
        heading("char* vs std::string vs std::string_view", 3),
        table(
            ["Тип", "Владение", "Копирование", "Модификация", "Применение"],
            [
                ["char*", "Нет (обычно)", "Нет (указатель)", "Опасно (UB для литералов)", "C API, legacy"],
                ["std::string", "Да", "Глубокая копия", "Да", "Владение строкой, модификация"],
                ["std::string_view", "Нет", "Zero-copy", "Нет (read-only)", "Функции-приёмники, парсинг, поиск"],
            ],
        ),
        text(
            "Правило выбора:\n"
            "- std::string — когда нужно владеть строкой и/или модифицировать её.\n"
            "- std::string_view — для функций-приёмников (read-only), парсинга, поиска.\n"
            "- char* — только для взаимодействия с C API.\n\n"
            "string_view особенно полезен в API функций-приёмников: вместо перегрузки "
            "на const std::string&, const char*, const char*, size_t — достаточно "
            "одного параметра std::string_view. Он неявно конструируется из всех этих типов."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["`std::string s[5];` — массив строк", "Фиксированный размер, неудобен", "std::vector<std::string> или std::array<std::string, 5>"],
                ["`arr[10] = 5` (UB)", "Выход за границы, UB", "arr.at(10) — exception, или проверка i < size"],
                ["`sizeof(ptr) / sizeof(ptr[0])` для указателя", "Возвращает 1 или 2, не размер массива", "Передавайте размер отдельно или используйте контейнеры"],
                ["`char* s = \"hello\"; s[0] = 'H';` (UB)", "Попытка изменения строкового литерала (read-only memory)", "std::string s = \"hello\"; s[0] = 'H';"],
                ["`std::string s = \"hello\" + \" world\";`", "Pointer arithmetic! UB", "std::string s = \"hello\" + std::string(\" world\");"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Собирайте программу после каждого изменения: "
            "`g++ -std=c++20 -Wall -Wextra -o app main.cpp && ./app`."
        ),
        numbered(
            "C-массив: создайте массив 10 int, заполните случайными числами, найдите max/min через std::minmax_element.",
            "std::array: то же самое с std::array, используйте .at() для безопасного доступа, сортируйте через std::sort.",
            "std::string: напишите функцию, подсчитывающую гласные в строке (range-based for + switch).",
            "string_view: напишите функцию split(string_view, delimiter) → vector<string_view> без копий.",
            "Сравнение: замерьте время конкатенации 1000 строк через += vs std::ostringstream.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "Min: 3\nMax: 98\n",
        ),
        callout(
            "success",
            "Подсказка к заданию 4",
            "string_view::find() и substr() возвращают string_view без копирования. "
            "Вектор string_view будет ссылаться на исходную строку. Убедитесь, что исходная строка живёт дольше векторов.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем C-массив отличается от std::array?",
            "Почему `sizeof(arr) / sizeof(arr[0])` не работает для указателя?",
            "В чём разница между `s[0]` и `s.at(0)` для std::string?",
            "Зачем нужна std::string_view, если есть std::string?",
            "Как безопасно разделить строку по разделителю без копий?",
        ),
        heading("Ответы", 3),
        numbered(
            "std::array хранит размер в типе, поддерживает копирование, сравнение, итераторы, методы at()/size(). C-массив — нет.",
            "Указатель не хранит информацию о размере массива. sizeof(ptr) возвращает размер указателя (4 или 8 байт).",
            "s[0] — без проверки границ (UB при выходе за границы). s.at(0) — с проверкой, бросает std::out_of_range.",
            "string_view — zero-copy взгляд на строку, не владеет памятью. Идеально для функций-приёмников, парсинга, избегает лишних копий.",
            "Используйте string_view::find() и substr() в цикле. substr() возвращает string_view без копирования. Собирайте позиции или сами string_view в вектор.",
        ),
        heading("Итоги"),
        bullets(
            "C-массив: фиксированный размер, array decay, нет методов, нет копирования. sizeof работает только для массива в области видимости.",
            "std::array: размер в типе, копирование/сравнение, at()/size()/front()/back()/data(), итераторы, zero overhead.",
            "std::string: владеет памятью, SSO (small string optimization), операции +, append, find, substr, конвертация чисел.",
            "std::string_view: zero-copy взгляд, не владеет памятью, для функций-приёмников, парсинга. Не хранить дольше жизни источника.",
            "Итерация: range-based for для всего (массивы, array, string, vector). auto& для модификации, const auto& для чтения.",
            "Безопасность: at() вместо [], проверка границ, не модифицировать строковые литералы, не смешивать signed/unsigned в индексах.",
        ),
        heading("Что дальше"),
        text(
            "Массивы и строки освоены. В следующем уроке разберём указатели и умные указатели: "
            "сырые указатели, unique_ptr, shared_ptr, weak_ptr, RAII, управление ресурсами, "
            "передача владения, циклы владения."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "cppreference: std::array — en.cppreference.com/w/cpp/container/array",
            "cppreference: std::string — en.cppreference.com/w/cpp/string/basic_string",
            "cppreference: std::string_view — en.cppreference.com/w/cpp/string/basic_string_view",
            "C++ Core Guidelines: SL.str.1 — Use std::string for owning strings",
            "C++ Core Guidelines: SL.str.2 — Use std::string_view for non-owning strings",
            "C++ Core Guidelines: SL.con.1 — Prefer STL containers over arrays",
        ),
    ],
}