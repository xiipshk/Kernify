"""Урок 1.8 курса C++: указатели и ссылки."""

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
    "topic_order": 8,
    "name": "1.8. Указатели и ссылки",
    "slug": "cpp-1-8-указатели-и-ссылки",
    "short_description": (
        "Указатели и ссылки: адреса памяти, указательная арифметика, "
        "lvalue/rvalue ссылки, динамическая память, умные указатели, RAII."
    ),
    "topic_name": "Указатели и ссылки",
    "topic_description": (
        "Фундаментальные понятия C++: указатели и ссылки. Адреса памяти, "
        "указательная арифметика, lvalue/rvalue ссылки, динамическая память "
        "(new/delete), умные указатели (unique_ptr, shared_ptr, weak_ptr), "
        "RAII, правило трёх/пяти, безопасность владения."
    ),
    "learning_objectives": [
        "Понимать адреса памяти, операторы & (address-of) и * (dereference)",
        "Работать с указателями: арифметика указателей, nullptr, void*, указатели на функции",
        "Освоить ссылки: lvalue-ссылки, const-ссылки, привязка к временным объектам",
        "Понять rvalue-ссылки (C++11) и move semantics: std::move, rvalue references",
        "Работать с динамической памятью: new, delete, new[], delete[], опасности ручного управления",
        "Использовать умные указатели: unique_ptr, shared_ptr, weak_ptr, make_unique/make_shared",
        "Понимать RAII: Resource Acquisition Is Initialization, правило трёх/пяти",
        "Использовать this указатель, method chaining, RAII-обёртки",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "cpp",
        "указатели",
        "ссылки",
        "умные указатели",
        "динамическая память",
        "raii",
        "move semantics",
    ],
    "starter_code": code(
        r"""
        #include <iostream>

        int main() {
            int x = 42;
            int* ptr = &x;
            std::cout << "Address: " << ptr << "\n";
            std::cout << "Value: " << *ptr << "\n";
            return 0;
        }
        """
    ),
    "hints": [
        "Указатель хранит адрес, ссылка — альтернативное имя. Ссылка всегда должна быть инициализирована.",
        "Указательная арифметика работает в единицах размера типа: p+1 сдвигает на sizeof(T) байт.",
        "const ссылка может привязаться к временному объекту, не-const — нет.",
        "Умные указатели (unique_ptr, shared_ptr) — стандарт современного C++. Избегайте raw new/delete.",
    ],
    "content": [
        text(
            "Указатели и ссылки — фундаментальные механизмы C++ для работы с памятью и косвенным доступом к данным. "
            "В отличие от высокоуровневых языков с автоматическим управлением памятью, C++ даёт программисту "
            "прямой контроль над адресами и временем жизни объектов. Это сила и ответственность: "
            "правильное использование даёт максимальную производительность и контроль, ошибки ведут к UB, "
            "утечкам памяти и крашам. В этом уроке разберём указатели, ссылки, динамическую память, "
            "умные указатели и RAII — фундамент безопасного современного C++."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать адреса памяти, операторы & (address-of) и * (dereference)",
            "работать с указателями: арифметика указателей, nullptr, void*, указатели на функции",
            "осваивать ссылки: lvalue-ссылки, const-ссылки, привязка к временным объектам",
            "понимать rvalue-ссылки (C++11) и move semantics: std::move, rvalue references",
            "работать с динамической памятью: new, delete, new[], delete[], опасности ручного управления",
            "использовать умные указатели: unique_ptr, shared_ptr, weak_ptr, make_unique/make_shared",
            "понимать RAII: Resource Acquisition Is Initialization, правило трёх/пяти",
            "использовать this указатель, method chaining, RAII-обёртки",
        ),
        heading("Адреса и указатели"),
        text(
            "Каждый байт памяти имеет адрес. Указатель — переменная, хранящая адрес. "
            "Оператор `&` (address-of) получает адрес переменной. Оператор `*` (dereference) "
            "достаёт значение по адресу. Указатель имеет тип: `int*` — указатель на int."
        ),
        heading("Базовые операции", 3),
        example(
            "cpp",
            """
            #include <iostream>

            int main() {
                int x = 42;
                int* ptr = &x;        // ptr хранит адрес x
                std::cout << ptr;     // адрес (например, 0x7ffc1234)
                std::cout << *ptr;    // 42 — разыменование (доступ к значению)

                *ptr = 100;           // меняет x через указатель
                std::cout << x;       // 100

                // Нулевой указатель (C++11)
                int* p1 = nullptr;    // лучше чем NULL или 0
                int* p2 = nullptr;
                if (!p1) std::cout << "nullptr\n";

                // void* — указатель на любой тип (нужен static_cast для разыменования)
                void* vp = &x;
                int* ip = static_cast<int*>(vp);
            }
            """,
        ),
        text(
            "Ключевые моменты:\n"
            "- `&x` — адрес переменной x (тип `T*`)\n"
            "- `*ptr` — разыменование, доступ к значению (тип `T`)\n"
            "- `nullptr` (C++11) — типобезопасный нулевой указатель, лучше `NULL` или `0`\n"
            "- `void*` — универсальный указатель, требует `static_cast` для разыменования\n"
            "- Указатель на `const` (`const int*`) — нельзя менять значение\n"
            "- `const` указатель (`int* const`) — нельзя менять адрес"
        ),
        heading("Указательная арифметика", 3),
        text(
            "Указательная арифметика работает в единицах размера типа, а не в байтах. "
            "`p + n` сдвигает указатель на `n * sizeof(T)` байт. Это позволяет эффективно "
            "перебирать массивы и работать с памятью."
        ),
        example(
            "cpp",
            """
            int arr[5] = {10, 20, 30, 40, 50};
            int* p = arr;           // p указывает на arr[0]

            p + 1;      // адрес arr[1] (смещение на sizeof(int) байт)
            p + 2;      // адрес arr[2]
            *(p + 2);   // 30 — то же что arr[2]

            p++;        // теперь p указывает на arr[1]
            ++p;        // arr[2]
            p += 2;     // arr[4]

            // Разница указателей — количество элементов между ними
            int* p2 = arr + 4;
            std::cout << p2 - p;    // 4 (тип ptrdiff_t)

            // Сравнение
            p < p2;     // true
            """,
        ),
        text(
            "Правила указательной арифметики:\n"
            "- `p + n` сдвигает на `n * sizeof(T)` байт\n"
            "- `p - q` возвращает `ptrdiff_t` — количество элементов между указателями\n"
            "- Сравнение указателей (`<`, `>`, `==`) работает для элементов одного массива\n"
            "- Выход за границы массива через указательную арифметику — UB\n"
            "- Для `void*` арифметика запрещена (размер типа неизвестен)"
        ),
        heading("Ссылки", 3),
        text(
            "Ссылка — альтернативное имя для существующего объекта (alias). "
            "Ссылка должна быть инициализирована при объявлении и не может быть перепривязана. "
            "Операции над ссылкой прозрачно перенаправляются к исходному объекту."
        ),
        example(
            "cpp",
            """
            int x = 10;
            int& ref = x;       // ref — другое имя для x (алиас)
            ref = 20;           // x становится 20

            // Ссылка должна быть инициализирована при объявлении
            // int& bad; // ОШИБКА

            // const ссылка — может привязываться к временным и литералам
            const int& cref = 42;           // OK: продлевает время жизни временного
            const int& cref2 = x + y;       // OK
            // int& r = 42;                 // ОШИБКА: не-const ссылка не привязывается к rvalue

            // Ссылки не могут быть null, не могут быть перепривязаны
            """,
        ),
        text(
            "Правила ссылок:\n"
            "- Ссылка — это не объект, это другое имя. `sizeof(ref) == sizeof(x)`\n"
            "- Нельзя иметь массив ссылок, указатель на ссылку, ссылку на ссылку\n"
            "- `const T&` привязывается ко всему (lvalue, rvalue, литералы) и продлевает жизнь временного\n"
            "- `T&` (не-const) привязывается только к lvalue\n"
            "- Ссылки не могут быть null, не могут быть перепривязаны после инициализации"
        ),
        heading("lvalue и rvalue ссылки (C++11)", 3),
        text(
            "C++11 ввёл разделение выражений на категории значений (value categories):\n"
            "- **lvalue** (locator value) — выражение, имеющее адрес, идентифицируемое имя (переменная)\n"
            "- **rvalue** — временный объект, истекающий к концу выражения (литерал, временный объект)\n"
            "- **xvalue** (eXpiring value) — объект, чьи ресурсы можно «украсть» (std::move(x))\n"
            "- **prvalue** (pure rvalue) — чистый rvalue (литерал, временный)\n\n"
            "Ссылки двух видов:\n"
            "- **lvalue reference** (`T&`) — привязывается к lvalue\n"
            "- **rvalue reference** (`T&&`) — привязывается к rvalue (xvalue или prvalue)"
        ),
        heading("rvalue-ссылки и move semantics (C++11)", 3),
        example(
            "cpp",
            """
            int x = 10;
            int&& rref = 42;        // привязывается к rvalue (временному)
            int&& rref2 = std::move(x); // приведение lvalue к rvalue

            // std::move — не перемещает, а кастует к rvalue-ссылке
            std::string s1 = "hello";
            std::string s2 = std::move(s1); // s1 теперь в "valid but unspecified state"
            // s1 может быть пустой, но деструктор безопасен
            """,
        ),
        text(
            "rvalue-ссылки (`T&&`) позволяют реализовать move semantics — перемещение ресурсов "
            "вместо копирования. `std::move(x)` — это `static_cast<T&&>(x)`, каст к rvalue-ссылке. "
            "Сам по себе `std::move` ничего не перемещает, он лишь разрешает компилятору вызвать "
            "move-конструктор/оператор присваивания.\n\n"
            "Правила:\n"
            "- `std::move(x)` — каст к `T&&`, разрешает перемещение\n"
            "- Перемещающий конструктор/оператор `=` «крадёт» ресурсы (указатели, handles)\n"
            "- После move источник в «valid but unspecified state» — можно разрушать, присваивать\n"
            "- `std::move` не перемещает само по себе, это просто `static_cast<T&&>`"
        ),
        heading("Указатели на функции", 3),
        example(
            "cpp",
            """
            int add(int a, int b) { return a + b; }
            int sub(int a, int b) { return a - b; }

            int (*func_ptr)(int, int) = add;  // тип: указатель на функцию(int,int)->int
            func_ptr = sub;                   // можно переназначать

            std::cout << func_ptr(5, 3);      // 2

            // Использование с алгоритмами
            #include <algorithm>
            #include <vector>
            std::vector<int> v = {3,1,4,1,5};
            std::sort(v.begin(), v.end(), [](int a, int b){ return a > b; });
            // lambda неявно конвертируется в указатель на функцию (если не захватывает)
            """,
        ),
        text(
            "Указатели на функции позволяют передавать поведение как параметр. "
            "Синтаксис: `ReturnType (*name)(ParamTypes)`. "
            "Лямбды без захватов неявно конвертируются в указатель на функцию. "
            "Для обобщённого кода лучше использовать шаблоны или `std::function`."
        ),
        heading("Динамическая память", 3),
        text(
            "Динамическое выделение памяти в куче (heap) через `new`/`delete`. "
            "Даёт контроль над временем жизни объекта, но требует ручного управления. "
            "Опасности: утечки памяти, double delete, use-after-delete, mismatch new/delete."
        ),
        heading("Одиночный объект и массивы", 3),
        example(
            "cpp",
            """
            #include <iostream>

            // Одиночный объект
            int* p = new int(42);     // выделяет память, вызывает конструктор
            std::cout << *p;          // 42
            delete p;                 // вызывает деструктор, освобождает память
            p = nullptr;              // хорошая практика после delete

            // Массив
            int* arr = new int[5]{1,2,3,4,5};
            delete[] arr;             // ВАЖНО: delete[] для массивов!
            arr = nullptr;

            // Опасности:
            // 1. Утечка памяти: забыли delete
            // 2. Double delete: delete дважды
            // 3. Use after delete: обращение через висячий указатель
            // 4. Mismatch: new[] с delete или new с delete[]
            """,
        ),
        callout(
            "warning",
            "Правила new/delete",
            "Правило: `new` ↔ `delete`, `new[]` ↔ `delete[]`. Нарушение — UB. "
            "Никогда не смешивайте. Для массивов всегда `delete[]`, даже для `char[]`. "
            "После `delete` указатель становится dangling — присваивайте `nullptr`."
        ),
        heading("Умные указатели (C++11) — RAII для памяти", 3),
        text(
            "Умные указатели — обёртки над сырой памятью, реализующие RAII. "
            "Автоматически освобождают память при выходе из области видимости. "
            "Стандартная библиотека: `unique_ptr`, `shared_ptr`, `weak_ptr` в `<memory>`."
        ),
        heading("unique_ptr — единственное владение", 3),
        example(
            "cpp",
            """
            #include <memory>
            #include <iostream>

            class Resource {
            public:
                Resource() { std::cout << "Acquired\n"; }
                ~Resource() { std::cout << "Released\n"; }
                void use() { std::cout << "Using\n"; }
            };

            void demo() {
                // unique_ptr — единственное владение (не копируется, только move)
                std::unique_ptr<Resource> u1 = std::make_unique<Resource>();
                u1->use();
                // std::unique_ptr<Resource> u2 = u1; // ОШИБКА: копирование запрещено
                std::unique_ptr<Resource> u2 = std::move(u1); // OK: передача владения
                // u1 теперь nullptr

                // unique_ptr для массивов
                std::unique_ptr<int[]> arr = std::make_unique<int[]>(5);
                arr[0] = 42;
            }
            """,
        ),
        text(
            "`unique_ptr` — реализация exclusive ownership. Не копируется, только move. "
            "`std::make_unique<T>()` (C++14) — безопасное создание. "
            "Для массивов: `std::unique_ptr<T[]>` с `operator[]`. "
            "Допускает custom deleter: `std::unique_ptr<T, Deleter>`."
        ),
        heading("shared_ptr — совместное владение", 3),
        example(
            "cpp",
            """
            // shared_ptr — совместное владение (reference counting)
            std::shared_ptr<Resource> s1 = std::make_shared<Resource>();
            std::shared_ptr<Resource> s2 = s1; // копируется, счётчик = 2
            std::cout << s1.use_count(); // 2

            // Память освободится когда последний shared_ptr умрёт
            {
                std::shared_ptr<Resource> s3 = s1;
                std::cout << s1.use_count(); // 3
            } // s3 умирает, count = 2
            // s1, s2 умирают, count = 0 → деструктор Resource
            """,
        ),
        text(
            "`shared_ptr` использует control block с reference count (атомарный, потокобезопасный). "
            "Копирование увеличивает счётчик, деструктор уменьшает. При достижении 0 — `delete`. "
            "Overhead: control block (~16-32 байт), атомарные операции. "
            "Используйте когда реально нужно совместное владение."
        ),
        heading("weak_ptr — слабая ссылка", 3),
        example(
            "cpp",
            """
            // weak_ptr — слабая ссылка (не увеличивает счётчик, для кэшей, родителей)
            std::weak_ptr<Resource> w = s1;
            if (auto locked = w.lock()) { locked->use(); } // проверка жив ли объект

            // Проверка истечения:
            std::weak_ptr<Resource> w2 = s1;
            s1.reset(); // удаляем shared_ptr
            if (w2.expired()) { std::cout << "Expired\n"; }
            """,
        ),
        text(
            "`weak_ptr` не увеличивает reference count. Используется для:\n"
            "- Кэши (объект может быть удалён, если на него только weak_ptr)\n"
            "- Обратные ссылки (parent-child, observer pattern) — предотвращает циклы\n"
            "`lock()` возвращает `shared_ptr` (или пустой, если объект умер). `expired()` проверяет без блокировки."
        ),
        heading("Правила умных указателей", 3),
        bullets(
            "По умолчанию используйте `unique_ptr` — простое, быстрое, явное владение",
            "`shared_ptr` когда нужно совместное владение (кэши, графы объектов)",
            "`weak_ptr` для обратных ссылок, кэшей, родительских ссылок — предотвращает циклы",
            "Никогда не делайте `new`/`shared_ptr` вручную — используйте `make_unique`/`make_shared`",
            "`make_shared` эффективнее: выделяет объект + control block в одном аллокаторе",
            "Избегайте raw `new`/`delete` в современном C++",
        ),
        heading("RAII (Resource Acquisition Is Initialization)", 3),
        text(
            "RAII — идиома: ресурс приобретается в конструкторе, освобождается в деструкторе. "
            "Гарантирует: никаких утечек при исключениях, раннем return, goto."
        ),
        example(
            "cpp",
            """
            // Принцип: ресурс приобретается в конструкторе, освобождается в деструкторе
            // Гарантирует: никаких утечек при исключениях, раннем return и т.д.

            class FileHandle {
                FILE* f;
            public:
                FileHandle(const char* name) : f(std::fopen(name, "r")) {
                    if (!f) throw std::runtime_error("Cannot open");
                }
                ~FileHandle() { if (f) std::fclose(f); }
                // Запрет копирования
                FileHandle(const FileHandle&) = delete;
                FileHandle& operator=(const FileHandle&) = delete;
                // Move разрешен
                FileHandle(FileHandle&& other) noexcept : f(other.f) { other.f = nullptr; }
                FILE* get() const { return f; }
            };

            void func() {
                FileHandle f("data.txt"); // при выходе из области — автоматическое закрытие
                // даже если брошено исключение!
            }
            """,
        ),
        text(
            "Принципы RAII:\n"
            "- Ресурс захватывается в конструкторе\n"
            "- Ресурс освобождается в деструкторе (гарантированно вызывается)\n"
            "- Объект не копируем (delete copy ctor/assignment), но может быть movable\n"
            "- Все ресурсы: память, файлы, сокеты, мьютексы, handles, GPU ресурсы\n\n"
            "Стандартные RAII-обёртки: `unique_ptr`, `shared_ptr`, `lock_guard`, `scoped_lock`, "
            "`std::fstream`, `std::vector`, `std::string`."
        ),
        heading("Правило трёх/пяти", 3),
        text(
            "Если класс управляет ресурсом, скорее всего нужны специальные функции-члены:\n\n"
            "**Правило трёх (C++98)**: если нужен один из — нужны все три:\n"
            "- Деструктор\n"
            "- Копирующий конструктор\n"
            "- Копирующий оператор присваивания\n\n"
            "**Правило пяти (C++11)**: + move-семантика:\n"
            "- Move-конструктор\n"
            "- Move-оператор присваивания\n\n"
            "**Правило нуля (Rule of Zero)**: предпочитайте классы, которым не нужны ни один из этих "
            "пяти методов — используйте RAII-члены (`unique_ptr`, `vector`, `string`), "
            "которые сами управляют ресурсами. Компилятор сгенерирует правильные умолчания."
        ),
        heading("this указатель", 3),
        example(
            "cpp",
            """
            struct Counter {
                int count = 0;
                Counter& increment() {
                    ++count;
                    return *this; // возврат ссылки на себя для чейнинга
                }
                void print() const { std::cout << count; }
            };

            Counter c;
            c.increment().increment().print(); // 2
            """,
        ),
        text(
            "`this` — неявный указатель на текущий объект (`ClassName* const this`). "
            "В const методах — `const ClassName* const this`. "
            "Используется для: чейнинга (`return *this`), разрешения имён (`this->member`), "
            "передачи `*this` в функции, сравнения адресов (`this == &other`)."
        ),
        heading("Правило нуля (Rule of Zero)", 3),
        text(
            "Лучшая практика современного C++: **не пишите** деструктор/копирование/перемещение вручную, "
            "если члены класса сами управляют ресурсами (RAII).\n\n"
            "`class Widget { std::unique_ptr<Impl> p; std::string name; };` — компилятор сгенерирует "
            "все пять специальных функций правильно. `unique_ptr` — move-only, `string` — копируется/перемещается.\n\n"
            "Если пишете ручной деструктор — подумайте, можно ли заменить на RAII-член. "
            "Rule of Zero: классы либо управляют ресурсами (и имеют все 5), либо не управляют (и имеют 0)."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Причина", "Решение"],
            [
                ["Разыменование nullptr", "UB, краш", "Проверяйте `if (ptr)` перед использованием"],
                ["`delete` вместо `delete[]` для массива", "UB, утечка/краш", "Всегда `new[]` ↔ `delete[]`, `new` ↔ `delete`"],
                ["Возврат указателя на локальную переменную", "Висячий указатель", "Возвращайте `unique_ptr` или по значению"],
                ["Копирование `unique_ptr`", "Ошибка компиляции", "Используйте `std::move`"],
                ["Циклические `shared_ptr`", "Утечка памяти (счётчик никогда не 0)", "Используйте `weak_ptr` для обратных ссылок"],
                ["`new` без `delete` в исключительной ситуации", "Утечка", "Используйте умные указатели / RAII"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Собирайте программу после каждого изменения: "
            "`g++ -std=c++20 -Wall -Wextra -o app main.cpp && ./app`."
        ),
        numbered(
            "Указательная арифметика: дан `int arr[10] = {1,2,3,4,5,6,7,8,9,10};` используя только указатели (не индексы `[]`): выведите все элементы, найдите максимум, реверсните массив на месте.",
            "Swap через указатели и ссылки: реализуйте `void swap_ptr(int* a, int* b)` и `void swap_ref(int& a, int& b)`. Какая версия безопаснее? Почему?",
            "Динамический массив вручную: реализуйте класс `DynamicArray` с `new[]`/`delete[]`, конструктором копирования, оператором присваивания, move-семантикой. Правило трёх/пяти.",
            "unique_ptr vs shared_ptr: создайте `std::vector<std::unique_ptr<Resource>>` с 1000 элементов. Замерьте время создания и уничтожения. Сравните с `shared_ptr`.",
            "Функция, возвращающая указатель: `int* create_array(int n, int init)`. Кто отвечает за `delete[]`? Как улучшить с `unique_ptr<int[]>`?",
            "this и method chaining: создайте класс `Builder` с методами `set_name`, `set_age`, `set_email`, возвращающими `*this`. Постройте объект одной цепочкой.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "Elements: 1 2 3 4 5 6 7 8 9 10\n"
            "Max: 10\n"
            "Reversed: 10 9 8 7 6 5 4 3 2 1",
        ),
        callout(
            "success",
            "Подсказка к заданию 3",
            "Правило пяти: деструктор, копирующий конструктор, копирующее присваивание, move-конструктор, move-присваивание. "
            "Для `DynamicArray<int>`: данные в `int* data`, `size_t size`, `size_t capacity`. "
            "Move-конструктор: `data = other.data; other.data = nullptr;` — передача владения без копирования.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем указатель отличается от ссылки?",
            "Что такое rvalue reference и зачем она нужна?",
            "Почему `delete[]` обязателен для массивов?",
            "В чём разница между `unique_ptr` и `shared_ptr`?",
            "Что такое RAII и зачем оно нужно?",
            "Когда `unique_ptr` лучше `shared_ptr`?",
            "Что такое Rule of Zero и зачем его следовать?",
        ),
        heading("Ответы", 3),
        numbered(
            "Указатель — переменная с адресом, может быть null, перепривязываема. Ссылка — алиас, не null, не перепривязываемая.",
            "Rvalue reference (`T&&`) привязывается к временным объектам, позволяет move semantics — перемещение ресурсов вместо копирования.",
            "`new[]` выделяет массив + метаданные (размер). `delete` вызовет только первый деструктор, `delete[]` — все деструкторы + освободит память правильно.",
            "`unique_ptr` — единственное владение, move-only, быстрый, нет overhead. `shared_ptr` — совместное владение, reference counting, control block overhead.",
            "RAII — Resource Acquisition Is Initialization: ресурс захватывается в конструкторе, освобождается в деструкторе. Гарантирует отсутствие утечек при исключениях.",
            "unique_ptr — по умолчанию (exclusive ownership, быстрый). shared_ptr — только когда реально нужно совместное владение (кэши, графы).",
            "Rule of Zero: не пишите специальные функции-члены, если члены класса сами RAII. Пусть компилятор генерирует умолчания.",
        ),
        heading("Итоги"),
        bullets(
            "Указатель — переменная с адресом, `&` (address-of), `*` (dereference). Арифметика в единицах `sizeof(T)`.",
            "Ссылка — альтернативное имя, не null, не перепривязываемая. `const T&` привязывается к rvalue.",
            "rvalue reference (`T&&`) — основа move semantics, `std::move` кастует к rvalue.",
            "Динамическая память: `new`/`delete`, `new[]`/`delete[]`. Опасности: утечки, double delete, use-after-free.",
            "Умные указатели: `unique_ptr` (exclusive), `shared_ptr` (shared), `weak_ptr` (weak). `make_unique`/`make_shared`.",
            "RAII: ресурс в конструкторе, освобождение в деструкторе. Никаких утечек при исключениях.",
            "Rule of Three/Five/Zero: если нужен один специальный метод — нужны все. Лучше Rule of Zero через RAII-члены.",
            "this — неявный указатель на текущий объект. Метод чейнинга: `return *this;`.",
        ),
        heading("Что дальше"),
        text(
            "Указатели и ссылки освоены. В следующем уроке разберём классы и ООП: конструкторы, деструкторы, "
            "наследование, виртуальные функции, полиморфизм, абстрактные классы, интерфейсы, "
            "композиция vs наследование, SOLID принципы."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "cppreference: Pointers — en.cppreference.com/w/cpp/language/pointer",
            "cppreference: References — en.cppreference.com/w/cpp/language/reference",
            "cppreference: Smart pointers — en.cppreference.com/w/cpp/memory",
            "C++ Core Guidelines: R. Resource management — isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r-resource-management",
            "Rule of Zero — https://en.cppreference.com/w/cpp/language/rule_of_three",
            "C++ Core Guidelines: R.1-R.40 — Resource management",
        ),
    ],
}