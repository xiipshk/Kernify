"""Урок 1.7 курса C++: контейнеры STL."""

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
    "topic_order": 7,
    "name": "1.7. Контейнеры",
    "slug": "cpp-1-7-контейнеры",
    "short_description": (
        "STL контейнеры: std::vector, std::pair, std::map, std::set, "
        "std::unordered_map/unordered_set, адаптеры, алгоритмы."
    ),
    "topic_name": "Контейнеры",
    "topic_description": (
        "Изучение стандартных контейнеров STL: vector, pair, map, set, "
        "unordered_map/unordered_set, адаптеры контейнеров (stack, queue, priority_queue), "
        "базовые алгоритмы. Понимание производительности, итераторов, аллокации памяти."
    ),
    "learning_objectives": [
        "Создавать и использовать std::vector: инициализация, доступ, изменение размера, reserve/shrink_to_fit",
        "Понимать внутреннее устройство vector: capacity, size, реаллокации, инвалидация итераторов",
        "Работать с std::pair: создание, structured bindings, сравнение",
        "Использовать ассоциативные контейнеры: std::map (упорядоченный map), std::set (упорядоченное множество)",
        "Понимать разницу между упорядоченными (map/set) и хеш-таблицами (unordered_map/unordered_set)",
        "Применять адаптеры контейнеров: stack, queue, priority_queue",
        "Использовать базовые алгоритмы: sort, find, binary_search, for_each",
        "Понимать инвалидацию итераторов при реаллокации vector",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "cpp",
        "stl",
        "vector",
        "pair",
        "map",
        "set",
        "unordered_map",
        "алгоритмы",
        "итераторы",
    ],
    "starter_code": code(
        r"""
        #include <iostream>
        #include <vector>
        #include <map>
        #include <string>

        int main() {
            std::vector<int> v = {3, 1, 4, 1, 5};
            std::sort(v.begin(), v.end());
            for (int x : v) std::cout << x << ' ';  // 1 1 3 3 5
            return 0;
        }
        """
    ),
    "hints": [
        "vector — основной контейнер по умолчанию. Используйте reserve() для известного размера.",
        "map — упорядоченный (O(log n)), unordered_map — хеш-таблица (O(1) среднее).",
        "Итераторы инвалидируются при реаллокации vector. Не храните итераторы между push_back.",
        "map[key] создаёт элемент, если его нет. Используйте find()/contains()/at() для чтения.",
    ],
    "content": [
        text(
            "STL (Standard Template Library) — сердце C++. Контейнеры, итераторы, алгоритмы — "
            "три кита, на которых стоит эффективный C++ код. Контейнеры управляют памятью, "
            "итераторы дают унифицированный доступ, алгоритмы работают с итераторами, "
            "не зная деталей контейнеров. В этом уроке разберём основные контейнеры STL: "
            "vector, pair, map, set, unordered_map/unordered_set, адаптеры и алгоритмы.\n\n"
            "STL — это не просто библиотека контейнеров. Это архитектурная философия C++: "
            "обобщённое программирование, где алгоритмы отделены от контейнеров через итераторы. "
            "Это позволяет писать алгоритм один раз (например, std::sort) и применять его к "
            "любому контейнеру, поддерживающему нужные итераторы (vector, deque, array, list). "
            "Понимание этой архитектуры — ключ к эффективному C++."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "создавать и эффективно использовать std::vector: reserve, push_back, emplace_back, shrink_to_fit;",
            "понимать внутреннее устройство vector: capacity, size, реаллокации, инвалидация итераторов;",
            "работать с std::pair: structured bindings, сравнение, возврат нескольких значений;",
            "использовать ассоциативные контейнеры: map (упорядоченный), set (уникальные ключи);",
            "различать упорядоченные (map/set) и хеш-таблицы (unordered_map/unordered_set);",
            "применять адаптеры контейнеров: stack, queue, priority_queue;",
            "использовать базовые алгоритмы: sort, find, binary_search, for_each;",
            "понимать инвалидацию итераторов при реаллокации vector и других операциях.",
        ),
        heading("std::vector — динамический массив"),
        text(
            "std::vector — основной контейнер по умолчанию. Динамический массив с автоматическим "
            "управлением памятью. Элементы хранятся непрерывно, что обеспечивает кэш-локальность "
            "и совместимость с C API через data().\n\n"
            "Почему vector — контейнер по умолчанию:\n"
            "- Непрерывная память = идеальная кэш-локальность = высокая производительность\n"
            "- Амортизированное O(1) push_back — эффективное добавление\n"
            "- Непрерывная память = совместимость с C API (data())\n"
            "- Поддерживает все операции: доступ по индексу, итераторы, алгоритмы STL\n"
            "- Автоматическое управление памятью (RAII) — никаких утечек\n\n"
            "Когда НЕ использовать vector:\n"
            "- Частые вставки/удаления в середине (O(n)) — лучше list/deque\n"
            "- Частые вставки в начало — deque\n"
            "- Нужны стабильные итераторы при вставках — list/forward_list\n"
            "- Фиксированный размер, известный на этапе компиляции — std::array"
        ),
        heading("Создание и инициализация", 3),
        example(
            "cpp",
            """
            #include <vector>
            #include <iostream>

            int main() {
                // Создание
                std::vector<int> v1;                    // пустой
                std::vector<int> v2(5);                 // 5 элементов = 0
                std::vector<int> v3(5, 42);             // 5 элементов = 42
                std::vector<int> v4 = {1,2,3,4,5};      // список инициализации
                std::vector v5 = {1,2,3};               // CTAD (C++17)

                // Доступ
                v4[0] = 10;              // без проверки
                v4.at(1) = 20;           // с проверкой (out_of_range)
                v4.front();              // первый
                v4.back();               // последний
                v4.data();               // указатель на массив (C API)

                // Размер и ёмкость
                v4.size();       // 5 — количество элементов
                v4.capacity();   // >=5 — выделенная память
                v4.empty();      // false
                v4.max_size();   // теоретический максимум

                // Изменение размера
                v4.push_back(6);         // добавить в конец (амортизированное O(1))
                v4.emplace_back(7);      // конструкция на месте (избегает копирования)
                v4.pop_back();           // убрать последний
                v4.insert(v4.begin()+2, 99); // вставить в середину O(n)
                v4.erase(v4.begin()+2);       // удалить из середины O(n)
                v4.clear();              // удалить все (capacity не меняется)

                // Резервирование — избегает реаллокаций
                std::vector<int> v6;
                v6.reserve(1000);        // выделить память под 1000 элементов
                for (int i=0; i<1000; ++i) v6.push_back(i); // никаких реаллокаций!

                v6.shrink_to_fit();      // запрос освободить лишнюю память (C++11)

                // Перебор
                for (int x : v4) std::cout << x << ' ';
                for (auto& x : v4) x *= 2;
                for (auto it = v4.begin(); it != v4.end(); ++it) { ... }
            }
            """,
        ),
        heading("Внутреннее устройство vector", 3),
        text(
            "std::vector хранит элементы непрерывно в памяти. Два ключевых поля:\n"
            "- size() — количество элементов\n"
            "- capacity() — выделенная память (в элементах)\n\n"
            "При `push_back` за пределами `capacity`:\n"
            "1. Выделяется новая память (обычно ×1.5 или ×2)\n"
            "2. Элементы копируются/перемещаются\n"
            "3. Старая память освобождается\n"
            "→ **Итераторы, указатели, ссылки инвалидируются!**\n\n"
            "Поэтому: **не храните итераторы/указатели/ссылки между операциями, меняющими capacity**.\n\n"
            "Детали реаллокации:\n"
            "- Коэффициент роста: реализационно-зависимый (обычно 1.5 или 2.0)\n"
            "- Амортизированная сложность push_back: O(1)\n"
            "- При реаллокации элементы перемещаются (move) если noexcept move constructor, иначе копируются\n"
            "- Используйте reserve() для известного размера — избегает множественных реаллокаций\n"
            "- shrink_to_fit() — запрос на освобождение лишней capacity (C++11), не гарантирует результат"
        ),
        heading("std::pair — пара значений", 3),
        text(
            "std::pair — простой контейнер для двух гетерогенных значений. "
            "Используется для возврата нескольких значений, в map (key-value), "
            "в алгоритмах (minmax_element).\n\n"
            "std::pair — это агрегатный тип, поэтому поддерживает агрегатную инициализацию "
            "и structured bindings (C++17). Это делает его удобным для возврата пары значений "
            "без создания отдельного struct. В map/unordered_map value_type — это pair<const Key, Value>."
        ),
        example(
            "cpp",
            """
            #include <utility>
            #include <string>

            std::pair<int, std::string> p1(42, "hello"); // C++11: make_pair
            auto p2 = std::make_pair(3.14, true);        // тип выводится
            auto p3 = std::pair{10, "world"};            // CTAD (C++17)

            // Доступ
            p1.first;   // 42
            p1.second;  // "hello"

            // Structured bindings (C++17)
            auto [num, str] = p1; // num=42, str="hello"

            // Сравнение — лексикографическое
            std::pair<int,int> a{1,2}, b{1,3};
            std::cout << (a < b); // true
            """,
        ),
        heading("std::map — ассоциативный массив (ключ → значение)", 3),
        text(
            "std::map — ассоциативный контейнер: ключи уникальны, отсортированы "
            "(красно-чёрное дерево, O(log n) для поиска/вставки/удаления).\n\n"
            "Реализация: красно-чёрное дерево (self-balancing BST). Гарантирует O(log n) для всех операций. "
            "Ключи всегда отсортированы — позволяет range queries (lower_bound, upper_bound, equal_range). "
            "Итерация всегда в отсортированном порядке. Ключи должны быть comparable (operator< или кастомный компаратор).\n\n"
            "Важные методы:\n"
            "- operator[] — доступ/создание (создаёт элемент, если нет)\n"
            "- at() — безопасный доступ с проверкой (бросает out_of_range)\n"
            "- find/contains — поиск без создания\n"
            "- emplace/try_emplace — эффективная вставка без лишних копий\n"
            "- lower_bound/upper_bound/equal_range — range queries\n"
            "- extract/merge (C++17) — перемещение узлов между map без копирования"
        ),
        example(
            "cpp",
            """
            #include <map>
            #include <string>

            int main() {
                // Ключи уникальны, отсортированы (красно-чёрное дерево, O(log n))
                std::map<std::string, int> ages;
                ages["Alice"] = 25;
                ages["Bob"] = 30;
                ages.emplace("Charlie", 35); // эффективнее для сложных типов

                // Доступ
                ages["Alice"];     // 25 (создаёт запись, если нет!)
                ages.at("Alice");  // 25 (бросает out_of_range, если нет)
                // ages["Unknown"] = 0; // создаст запись!

                // Поиск
                auto it = ages.find("Bob");
                if (it != ages.end()) {
                    std::cout << it->first << ": " << it->second; // "Bob: 30"
                }

                // Проверка наличия (C++20)
                if (ages.contains("Alice")) { ... } // true

                // Перебор (отсортирован по ключу)
                for (const auto& [name, age] : ages) {
                    std::cout << name << " -> " << age << '\n';
                }

                // Удаление
                ages.erase("Bob");
                ages.clear();
            }
            """,
        ),
        text(
            "Ключевые моменты:\n"
            "- `operator[]` создаёт элемент, если ключа нет (возвращает value-initialized).\n"
            "- `at()` бросает исключение, если ключа нет (безопаснее для чтения).\n"
            "- `emplace` / `try_emplace` — эффективнее для сложных типов (нет лишнего копирования).\n"
            "- Итерация даёт упорядоченную последовательность по ключу (лексикографически для string).\n"
            "- Ключи должны быть comparable (operator< или кастомный компаратор)."
        ),
        heading("std::set — упорядоченное множество уникальных ключей", 3),
        example(
            "cpp",
            """
            #include <set>
            #include <string>

            std::set<int> s = {3, 1, 4, 1, 5}; // {1, 3, 4, 5} — дубликаты удалены, отсортировано
            s.insert(2);    // {1, 2, 3, 4, 5}
            s.erase(3);     // {1, 2, 4, 5}
            s.count(4);     // 1 (есть)
            s.count(99);    // 0 (нет)
            s.contains(4);  // C++20: true

            // Перебор в отсортированном порядке
            for (int x : s) std::cout << x << ' '; // 1 2 4 5
            """,
        ),
        text(
            "std::set — это упорядоченное множество уникальных ключей. "
            "Аналогичен map, но только ключи, без значений. "
            "Если нужны дубликаты — используйте std::multiset.\n\n"
            "Реализация та же, что и map (RB-tree). Все операции O(log n).\n"
            "Ключевые методы:\n"
            "- insert/emplace — вставка (игнорирует дубликаты)\n"
            "- erase — удаление по ключу/итератору/диапазону\n"
            "- find/count/contains — поиск\n"
            "- lower_bound/upper_bound/equal_range — диапазонные запросы\n"
            "- extract/merge (C++17) — перемещение узлов между set\n\n"
            "Итерация всегда в отсортированном порядке. "
            "Если порядок не важен и нужна скорость — используйте unordered_set."
        ),
        heading("std::unordered_map / unordered_set — хеш-таблицы (O(1) среднее)", 3),
        text(
            "Хеш-таблицы: среднее O(1) для поиска/вставки/удаления. Не упорядочены — порядок итерации не определён. "
            "Требуют хеш-функцию и operator== для ключа.\n\n"
            "Реализация: массив бакетов + цепочки (chaining) или open addressing. "
            "Load factor (load_factor = size / bucket_count) контролирует рехеширование. "
            "По умолчанию max_load_factor = 1.0 — при превышении происходит rehash.\n\n"
            "Ключевые моменты:\n"
            "- Нужен специализированный std::hash<Key> и operator==\n"
            "- Для пользовательских типов: специализируйте std::hash или передайте кастомный Hash в template\n"
            "- reserve(n) — предварительно выделяет бакеты под n элементов (избегает rehash)\n"
            "- max_load_factor() — настройка агрессивности rehash\n\n"
            "Когда unordered_map быстрее map:\n"
            "- Большое количество элементов (>1000)\n"
            "- Только поиск/вставка/удаление, не нужен порядок\n"
            "- Ключ имеет хорошую хеш-функцию (int, string, простые структуры)\n\n"
            "Когда map:\n"
            "- Нужен упорядоченный обход\n"
            "- Нужен range query (lower_bound, upper_bound)\n"
            "- Мало элементов (< 50) — overhead хеша не оправдан\n"
            "- Ключ сложно хешировать или нет operator=="
        ),
        example(
            "cpp",
            """
            #include <unordered_map>
            #include <string>

            std::unordered_map<std::string, int> umap;
            umap["key"] = 42;
            // Не упорядочены, быстрее для поиска, но нет итерации в сортированном порядке
            // Требуют хеш-функцию и operator== для ключа

            // Для пользовательских типов:
            struct Point { int x, y; };
            struct PointHash {
                size_t operator()(const Point& p) const noexcept {
                    return std::hash<int>{}(p.x) ^ (std::hash<int>{}(p.y) << 1);
                }
            };
            std::unordered_map<Point, int, PointHash> point_map;
            """,
        ),
        text(
            "Когда выбирать unordered_map:\n"
            "- Нужна максимальная скорость поиска (O(1) среднее)\n"
            "- Порядок элементов не важен\n"
            "- Ключ имеет хорошую хеш-функцию\n\n"
            "Когда map:\n"
            "- Нужен упорядоченный обход\n"
            "- Нужен range query (lower_bound, upper_bound)\n"
            "- Ключ сложно хешировать или нет operator=="
        ),
        heading("Адаптеры контейнеров", 3),
        example(
            "cpp",
            """
            #include <stack>
            #include <queue>

            std::stack<int> st;       // LIFO: push, pop, top
            std::queue<int> q;        // FIFO: push, pop, front, back
            std::priority_queue<int> pq; // max-heap: push, pop, top (больший сверху)

            // Примеры
            std::stack<int> st;
            st.push(1); st.push(2);
            st.top();   // 2
            st.pop();   // удаляет 2

            std::queue<int> q;
            q.push(1); q.push(2);
            q.front();  // 1
            q.back();   // 2
            q.pop();    // удаляет 1

            std::priority_queue<int> pq;
            pq.push(3); pq.push(1); pq.push(2);
            pq.top();   // 3 (максимум)
            """,
        ),
        heading("Алгоритмы (перебор, поиск, сортировка)", 3),
        text(
            "Алгоритмы из <algorithm> работают с итераторами, не зная деталей контейнеров. "
            "Это разделение контейнеров и алгоритмов — ключевая идея STL.\n\n"
            "Алгоритмы классифицируются по категории итераторов, которые они требуют:\n"
            "- InputIterator: find, count, accumulate, copy\n"
            "- ForwardIterator: replace, remove, unique\n"
            "- BidirectionalIterator: reverse, reverse_copy\n"
            "- RandomAccessIterator: sort, nth_element, binary_search, random_shuffle\n\n"
            "Категория итераторов контейнера:\n"
            "- vector, deque, array, string: RandomAccessIterator\n"
            "- list, forward_list: BidirectionalIterator / ForwardIterator\n"
            "- map, set: BidirectionalIterator\n"
            "- unordered_map/unordered_set: ForwardIterator"
        ),
        example(
            "cpp",
            """
            #include <algorithm>
            #include <vector>

            std::vector<int> v = {5, 2, 8, 1, 9};

            std::sort(v.begin(), v.end());           // {1,2,5,8,9}
            std::reverse(v.begin(), v.end());        // {9,8,5,2,1}
            auto it = std::find(v.begin(), v.end(), 5); // итератор на 5
            bool has = std::binary_search(v.begin(), v.end(), 5); // true (требует сортировки)
            std::for_each(v.begin(), v.end(), [](int& x){ x *= 2; });
            """,
        ),
        text(
            "Популярные алгоритмы:\n"
            "- Сортировка: sort, stable_sort, partial_sort, nth_element\n"
            "- Поиск: find, find_if, binary_search, lower_bound, upper_bound, equal_range\n"
            "- Модификация: copy, move, transform, fill, fill_n, generate\n"
            "- Удаление: remove, remove_if, unique (работают с erase)\n"
            "- Разделение: partition, stable_partition\n"
            "- Свертка: accumulate, reduce (C++17), inner_product\n"
            "- Перестановки: next_permutation, prev_permutation, shuffle\n\n"
            "Все алгоритмы работают через итераторы — унифицированный интерфейс для любых контейнеров.\n\n"
            "Важные паттерны:\n"
            "- erase-remove idiom: v.erase(std::remove(v.begin(), v.end(), val), v.end())\n"
            "- erase-remove_if: v.erase(std::remove_if(...), v.end())\n"
            "- copy_if для фильтрации: std::copy_if(src.begin(), src.end(), back_inserter(dst), pred)\n"
            "- transform для маппинга: std::transform(in.begin(), in.end(), out.begin(), func)\n"
            "- accumulate для суммы/произведения: std::accumulate(v.begin(), v.end(), 0)\n"
            "- minmax_element для одновременного поиска min/max"
        ),
        heading("Инвалидация итераторов — частая ошибка", 3),
        text(
            "Итераторы, указатели и ссылки на элементы vector инвалидируются при:\n"
            "- push_back/emplace_back (если size > capacity → реаллокация)\n"
            "- insert/erase (все итераторы после точки вставки/удаления)\n"
            "- resize (если новый размер > capacity)\n"
            "- shrink_to_fit (может реаллоцировать)\n\n"
            "Правила безопасности:\n"
            "- Не храните итераторы/указатели/ссылки между операциями, меняющими capacity\n"
            "- Используйте индексы (size_t) вместо итераторов, если нужна устойчивость\n"
            "- reserve() заранее — гарантирует отсутствие реаллокаций до заданного размера\n"
            "- Для list/map/set — итераторы стабильны при вставке/удалении (кроме удалённого элемента)\n\n"
            "Подробная таблица инвалидации (C++ стандарт):\n"
            "| Операция | vector | deque | list | map/set | unordered_map/set |\n"
            "|----------|--------|-------|------|---------|-------------------|\n"
            "| push_back | все (если реаллокация) | все | нет | нет | все (если rehash) |\n"
            "| insert | после точки вставки | все | нет | нет | все (если rehash) |\n"
            "| erase | после удалённого | после удалённого | только удалённый | только удалённый | только удалённый |\n"
            "| resize (увеличение) | все (если реаллокация) | все | нет | нет | все (если rehash) |\n"
            "| clear | все | все | все | все | все |\n"
            "| swap | нет | нет | нет | нет | нет |\n\n"
            "Правило: reserve(N) гарантирует отсутствие реаллокаций до N элементов. "
            "Для list/map/set/unordered_map — итераторы стабильны (кроме erase элемента)."
        ),
        heading("Сравнение контейнеров", 3),
        table(
            ["Контейнер", "Поиск", "Вставка/Удаление", "Порядок", "Память", "Итераторы"],
            [
                ["vector", "O(n)", "O(1) amortized (конец), O(n) (середина)", "Вставки", "Непрерывная", "RandomAccess"],
                ["deque", "O(n)", "O(1) (оба конца)", "Вставки", "Блоки", "RandomAccess"],
                ["list", "O(n)", "O(1) (с итератором)", "Вставки", "Разрозненная", "Bidirectional"],
                ["map/set", "O(log n)", "O(log n)", "Отсортирован", "Узлы (overhead)", "Bidirectional"],
                ["unordered_map/set", "O(1) средн.", "O(1) средн.", "Хеш", "Бакеты (overhead)", "Forward"],
                ["array", "O(n)", "N/A (фиксированный)", "Вставки", "Непрерывная", "RandomAccess"],
                ["forward_list", "O(n)", "O(1) (после элемента)", "Вставки", "Разрозненная", "Forward"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Собирайте программу после каждого изменения: "
            "`g++ -std=c++20 -Wall -Wextra -o app main.cpp && ./app`.\n\n"
            "Советы по выполнению:\n"
            "- Для MyVector начните с простой структуры: pointer, size, capacity. Реализуйте конструктор, деструктор, копирование, перемещение.\n"
            "- Для частоты слов используйте std::map<std::string, int> и std::cin >> word в цикле.\n"
            "- Для телефонной книги используйте std::map<std::string, std::vector<std::string>> — map для имён, vector для списка телефонов.\n"
            "- Для reserve vs без: замеряйте через std::chrono::high_resolution_clock. Ожидаемое ускорение в 5-10 раз с reserve."
        ),
        numbered(
            "Динамический массив: реализуйте простой вектор вручную: `MyVector<int>` с `push_back`, `pop_back`, `size`, `capacity`, `operator[]`, итераторами. Сравните с `std::vector`.",
            "Частота слов: прочитайте текст из `std::cin` до EOF. Посчитайте частоту каждого слова (`std::map<std::string, int>`). Выведите топ-10 самых частых.",
            "Телефонная книга: `std::map<std::string, std::vector<std::string>>` — имя → список телефонов. Команды: add имя телефон, find имя, delete имя, list (все в алфавитном порядке).",
            "Уникальные слова: введите N строк. Выведите все уникальные слова в алфавитном порядке (`std::set`).",
            "reserve vs без: замерьте время `push_back` 1 млн элементов с `reserve(1'000'000)` и без. Объясните разницу.",
            "Pair и structured bindings: напишите функцию, возвращающую `std::pair<std::string, int>` (имя, длина). Используйте structured bindings при вызове.",
        ),
        text("Пример ожидаемого результата для первого задания (структура):"),
        example(
            "text",
            "MyVector:\n"
            "push_back 5 элементов\n"
            "size: 5, capacity: 8\n"
            "Элементы: 1 2 3 4 5\n"
            "std::vector:\n"
            "size: 5, capacity: 8\n"
            "Элементы: 1 2 3 4 5",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "Используйте `std::map<std::string, int> freq;`. Читайте слова через `std::string word; while (std::cin >> word) freq[word]++;`. Для топ-10: скопируйте в `std::vector<std::pair<std::string, int>>`, отсортируйте по `second` (убывание) с кастомным компаратором: `[](auto& a, auto& b) { return a.second > b.second; }`. Затем выведите первые 10 элементов.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем std::vector отличается от std::array?",
            "Почему после push_back итераторы могут стать невалидными?",
            "В чём разница между map[key] и map.at(key)?",
            "Когда использовать map, а когда unordered_map?",
            "Какие операции инвалидируют итераторы vector?",
            "Как вернуть из функции два значения?",
            "Зачем нужен shrink_to_fit() и когда он полезен?",
            "В чём разница между emplace_back и push_back?",
            "Как работает reserve() и зачем он нужен?",
            "Что такое structured bindings и как они работают с pair/tuple?",
        ),
        heading("Ответы", 3),
        numbered(
            "vector — динамический размер, array — фиксированный (compile-time). vector в куче, array — на стеке. vector умеет расти.",
            "push_back может вызвать реаллокацию (перемещение элементов в новую память). Старые итераторы/указатели/ссылки становятся невалидными (dangling).",
            "map[key] создаёт элемент, если ключа нет (value-initialized). at() бросает out_of_range, если ключа нет. Для чтения — at() или find().",
            "map — O(log n), упорядочен, нужен operator<. unordered_map — O(1) среднее, хеш-таблица, порядок не гарантирован, нужен hash и operator==.",
            "push_back/emplace_back (если реаллокация), insert/erase (все после точки), resize (если расширение), shrink_to_fit. list/map/set — стабильны.",
            "std::pair<T1, T2>, std::tuple<...>, std::optional, структурированные привязки (C++17): auto [a, b] = f();",
            "shrink_to_fit() запрашивает освобождение лишней capacity (C++11). Полезен после удаления большого количества элементов, когда память не нужна. Не гарантирует освобождение (implementation-defined).",
            "emplace_back конструирует элемент прямо в памяти вектора (in-place), избегая копирования/перемещения. push_back требует уже созданный объект. Для сложных типов emplace_back быстрее.",
            "reserve(N) предварительно выделяет память под N элементов, гарантирует отсутствие реаллокаций до N элементов. Критично для производительности при известном заранее размере.",
            "Structured bindings (C++17): auto [a, b] = pair; auto [x, y, z] = tuple; Работают с pair, tuple, array, struct. Упрощают возврат нескольких значений.",
        ),
        heading("Итоги"),
        bullets(
            "vector — главный контейнер: непрерывная память, амортизированное O(1) push_back, cache-friendly. reserve() для известного размера.",
            "pair — два значения, structured bindings (C++17), сравнение лексикографическое.",
            "map — упорядоченный map (RB-tree, O(log n)), ключи уникальны. operator[] создаёт элемент, at() — безопасный доступ.",
            "set — упорядоченное множество уникальных ключей. multiset — разрешает дубликаты.",
            "unordered_map/set — хеш-таблицы, O(1) среднее, нет порядка. Нужен hash и operator==.",
            "Адаптеры: stack (LIFO), queue (FIFO), priority_queue (heap). Адаптируют базовый контейнер.",
            "Алгоритмы: sort, find, binary_search, for_each, copy, transform, remove_if + erase. Работают через итераторы.",
            "Инвалидация: vector реаллоцирует при росте capacity — итераторы/указатели/ссылки ломаются. reserve() предотвращает. list/map/set — стабильны.",
            "Best practices: reserve() для известного размера, emplace вместо push_back для сложных типов, at() вместо [] для безопасности, structured bindings для пар, reserve() перед большими вставками.",
        ),
        heading("Что дальше"),
        text(
            "Контейнеры STL освоены. В следующем уроке разберём указатели и умные указатели: "
            "сырые указатели, unique_ptr, shared_ptr, weak_ptr, RAII, управление ресурсами, "
            "передача владения, циклы владения."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "cppreference: std::vector — en.cppreference.com/w/cpp/container/vector",
            "cppreference: std::map — en.cppreference.com/w/cpp/container/map",
            "cppreference: std::set — en.cppreference.com/w/cpp/container/set",
            "cppreference: Algorithms — en.cppreference.com/w/cpp/algorithm",
            "C++ Core Guidelines: SL containers — isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#sl-containers",
            "Big-O Cheat Sheet — www.bigocheatsheet.com/ — сложность операций",
        ),
    ],
}