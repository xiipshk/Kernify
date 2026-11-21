"""Урок 1.11 курса C++: первый проект."""

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
    "topic_order": 11,
    "name": "1.11. Первый проект",
    "slug": "cpp-1-11-первый-проект",
    "short_description": (
        "Итоговый проект первого уровня: консольный менеджер задач с классами, "
        "контейнерами, файловым хранилищем, обработкой ошибок и сборкой через CMake."
    ),
    "topic_name": "Первый проект",
    "topic_description": (
        "Сборка всего материала уровня в один проект: проектирование классов, "
        "разделение на файлы, персистентность, меню и валидация ввода, "
        "сборка через CMake и проверка качества."
    ),
    "learning_objectives": [
        "Планировать структуру проекта до написания кода",
        "Проектировать классы Task и TaskManager с чёткими обязанностями",
        "Хранить данные в файле и восстанавливать их при запуске",
        "Валидировать пользовательский ввод и не падать на неверных данных",
        "Разделять код на заголовочные и исходные файлы",
        "Собирать проект через CMake и через прямую команду компилятора",
        "Проверять результат: предупреждения, утечки памяти, граничные случаи",
    ],
    "estimated_minutes": 40,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "cpp",
        "проект",
        "cmake",
        "файлы",
        "классы",
        "контейнеры",
        "валидация",
    ],
    "starter_code": code(
        r"""
        #include <iostream>
        #include <string>
        #include <vector>

        struct Task {
            int id = 0;
            std::string title;
            bool done = false;
        };

        int main() {
            std::vector<Task> tasks;
            tasks.push_back({1, "Прочитать урок 1.11", false});
            for (const auto& t : tasks) {
                std::cout << "[" << t.id << "] " << t.title << "\n";
            }
            return 0;
        }
        """
    ),
    "hints": [
        "Сначала опишите данные и операции на бумаге, потом пишите код.",
        "Храните файл в простом текстовом формате: его легко проверить глазами.",
        "После каждого чтения из cin проверяйте поток и очищайте его при ошибке.",
        "Собирайте с -Wall -Wextra и устраняйте все предупреждения.",
    ],
    "content": [
        text(
            "Десять уроков назад программа состояла из одной строки `print`. "
            "Теперь вы умеете объявлять типы, управлять потоком выполнения, "
            "писать функции и классы, работать с контейнерами, указателями, "
            "файлами и исключениями. Осталось соединить это в один проект.\n\n"
            "Проект — не проверка памяти, а проверка умения **принимать решения**. "
            "Здесь нет единственно правильного ответа: важно, чтобы структура "
            "была понятной, данные не терялись, а программа не падала на "
            "неожиданном вводе. В этом уроке мы спроектируем и соберём консольный "
            "менеджер задач.\n\n"
            "Большая часть времени в таком проекте уходит не на код, а на "
            "решения: где провести границу между классами, что хранить в файле, "
            "как реагировать на ошибку — сообщением, исключением или тихим "
            "пропуском. Именно эти решения определяют, будет ли программу легко "
            "развивать через месяц. Код при этом остаётся небольшим: около "
            "трёхсот строк на всё приложение."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "планировать структуру проекта до написания кода;",
            "проектировать классы с одной понятной обязанностью у каждого;",
            "сохранять данные в файл и восстанавливать их при запуске;",
            "валидировать ввод пользователя и корректно реагировать на ошибки;",
            "разделять код на заголовочные и исходные файлы;",
            "собирать проект через CMake и напрямую компилятором;",
            "проверять результат по чек-листу качества.",
        ),
        heading("Что делает программа"),
        text(
            "**Менеджер задач** — консольное приложение, которое хранит список "
            "дел между запусками. Требования простые, но покрывают почти все "
            "темы уровня."
        ),
        numbered(
            "Добавить задачу: название, приоритет от 1 до 3, необязательный срок.",
            "Показать все задачи, только активные или только выполненные.",
            "Отметить задачу выполненной и снова активной.",
            "Удалить задачу по номеру.",
            "Найти задачи по слову в названии.",
            "Показать статистику: всего, выполнено, активно, просрочено.",
            "Сохранять состояние в файл и восстанавливать при запуске.",
        ),
        text(
            "Из требований уже видно, какие конструкции понадобятся: `struct` или "
            "класс для задачи, `std::vector` для списка, `std::optional` для "
            "необязательного срока, `std::find_if` для поиска, `std::fstream` для "
            "хранения, `std::getline` для ввода строк с пробелами.\n\n"
            "Полезно сразу выписать операции парами «что просят» и «что вернёт "
            "функция». Пользователь просит удалить задачу — функция вернёт `bool`, "
            "потому что задача может не найтись. Пользователь просит показать "
            "список — функция вернёт указатели на найденные задачи, а печатать "
            "будет вызывающий код. Такой список заранее снимает половину "
            "вопросов при написании."
        ),
        heading("Планирование структуры"),
        text(
            "Первый шаг — разложить обязанности по файлам. Каждый файл отвечает "
            "за одну вещь; тогда его можно прочитать целиком и понять."
        ),
        example(
            "text",
            """
            task_manager/
            ├── include/
            │   ├── task.h          структура задачи и её вывод
            │   ├── task_manager.h  список задач и операции над ним
            │   └── storage.h       сохранение и загрузка
            ├── src/
            │   ├── task.cpp
            │   ├── task_manager.cpp
            │   ├── storage.cpp
            │   └── main.cpp        меню и ввод
            ├── data/
            │   └── tasks.txt
            ├── CMakeLists.txt
            └── README.md
            """,
        ),
        table(
            ["Файл", "Обязанность", "Чего в нём быть не должно"],
            [
                ["`task.h`", "описание одной задачи и её вывод", "списка задач, файлов"],
                ["`task_manager.h`", "операции над коллекцией задач", "чтения с клавиатуры"],
                ["`storage.h`", "запись и чтение файла", "правил бизнес-логики"],
                ["`main.cpp`", "меню, ввод, вывод", "работы с файлами напрямую"],
            ],
        ),
        callout(
            "info",
            "Зачем такое разделение",
            "Если хранение вынести в отдельный файл, завтра можно заменить "
            "текстовый формат на JSON, не трогая остальной код. Если ввод "
            "оставить в `main`, `TaskManager` можно проверить тестами без "
            "клавиатуры. Разделение обязанностей экономит время при изменениях."
        ),
        heading("Модель задачи"),
        text(
            "Начнём с самого простого — описания одной задачи. Здесь важны две "
            "вещи: поля имеют значения по умолчанию, и логика «просрочена ли» "
            "живёт рядом с данными."
        ),
        example(
            "cpp",
            """
            // include/task.h
            #pragma once

            #include <ctime>
            #include <optional>
            #include <string>

            enum class Priority { Low = 1, Normal = 2, High = 3 };

            struct Task {
                int id = 0;
                std::string title;
                Priority priority = Priority::Normal;
                bool done = false;
                std::optional<std::time_t> due;

                bool is_overdue() const;
                std::string priority_name() const;
            };
            """,
        ),
        example(
            "cpp",
            """
            // src/task.cpp
            #include "task.h"

            bool Task::is_overdue() const {
                if (done || !due) return false;
                return *due < std::time(nullptr);
            }

            std::string Task::priority_name() const {
                switch (priority) {
                    case Priority::Low:    return "низкий";
                    case Priority::Normal: return "обычный";
                    case Priority::High:   return "высокий";
                }
                return "?";
            }
            """,
        ),
        text(
            "Обратите внимание на значения по умолчанию у полей: `id = 0`, "
            "`priority = Priority::Normal`, `done = false`. Благодаря им "
            "`Task t;` создаёт полностью определённую задачу, и ни одно поле "
            "не остаётся с мусором. Это прямое следствие урока 1.2: "
            "неинициализированное значение — источник невоспроизводимых "
            "ошибок.\n\n"
            "`std::optional<std::time_t> due` означает «срок может отсутствовать». "
            "Это лучше, чем `time_t == 0` в качестве признака: ноль — допустимое "
            "значение времени, и путать его с отсутствием опасно. Метод "
            "`is_overdue()` объединяет три условия в одном месте, поэтому "
            "проверка не разъедется по программе."
        ),
        heading("Коллекция задач"),
        text(
            "`TaskManager` владеет списком и отвечает за все операции над ним. "
            "Методы возвращают `bool` или `std::optional`, а не печатают на "
            "экран: решение, что показать пользователю, принимает `main`."
        ),
        example(
            "cpp",
            """
            // include/task_manager.h
            #pragma once

            #include "task.h"

            #include <optional>
            #include <string>
            #include <vector>

            class TaskManager {
                std::vector<Task> tasks_;
                int next_id_ = 1;

            public:
                Task& add(std::string title, Priority priority);

                bool remove(int id);
                bool toggle(int id);

                std::optional<Task> find(int id) const;
                std::vector<const Task*> search(const std::string& word) const;
                std::vector<const Task*> filter(bool done) const;
                std::vector<const Task*> overdue() const;

                struct Stats { std::size_t total, done, active, overdue; };
                Stats stats() const;

                const std::vector<Task>& all() const { return tasks_; }
                void replace_all(std::vector<Task> tasks, int next_id);
            };
            """,
        ),
        example(
            "cpp",
            """
            // src/task_manager.cpp
            #include "task_manager.h"

            #include <algorithm>
            #include <cctype>

            Task& TaskManager::add(std::string title, Priority priority) {
                Task t;
                t.id = next_id_++;
                t.title = std::move(title);
                t.priority = priority;
                tasks_.push_back(std::move(t));
                return tasks_.back();
            }

            bool TaskManager::remove(int id) {
                auto it = std::find_if(tasks_.begin(), tasks_.end(),
                                       [id](const Task& t) { return t.id == id; });
                if (it == tasks_.end()) return false;
                tasks_.erase(it);
                return true;
            }

            bool TaskManager::toggle(int id) {
                auto it = std::find_if(tasks_.begin(), tasks_.end(),
                                       [id](const Task& t) { return t.id == id; });
                if (it == tasks_.end()) return false;
                it->done = !it->done;
                return true;
            }

            std::optional<Task> TaskManager::find(int id) const {
                for (const auto& t : tasks_) {
                    if (t.id == id) return t;
                }
                return std::nullopt;
            }

            std::vector<const Task*> TaskManager::filter(bool done) const {
                std::vector<const Task*> result;
                for (const auto& t : tasks_) {
                    if (t.done == done) result.push_back(&t);
                }
                return result;
            }

            std::vector<const Task*> TaskManager::overdue() const {
                std::vector<const Task*> result;
                for (const auto& t : tasks_) {
                    if (t.is_overdue()) result.push_back(&t);
                }
                return result;
            }

            std::vector<const Task*> TaskManager::search(const std::string& word) const {
                std::vector<const Task*> result;
                std::string needle = word;
                std::transform(needle.begin(), needle.end(), needle.begin(),
                               [](unsigned char c) { return std::tolower(c); });
                for (const auto& t : tasks_) {
                    std::string hay = t.title;
                    std::transform(hay.begin(), hay.end(), hay.begin(),
                                   [](unsigned char c) { return std::tolower(c); });
                    if (hay.find(needle) != std::string::npos) result.push_back(&t);
                }
                return result;
            }

            TaskManager::Stats TaskManager::stats() const {
                Stats s{};
                s.total = tasks_.size();
                for (const auto& t : tasks_) {
                    if (t.done) ++s.done;
                    else {
                        ++s.active;
                        if (t.is_overdue()) ++s.overdue;
                    }
                }
                return s;
            }

            void TaskManager::replace_all(std::vector<Task> tasks, int next_id) {
                tasks_ = std::move(tasks);
                next_id_ = next_id;
            }
            """,
        ),
        text(
            "Обратите внимание на тип возвращаемого значения у `filter`, "
            "`search` и `overdue`: `std::vector<const Task*>` — вектор указателей "
            "на существующие элементы, без копирования. Копировать задачи ради "
            "вывода расточительно, а менять их через результат фильтра не "
            "следует, поэтому указатель константный."
        ),
        heading("Хранение в файле"),
        text(
            "Формат файла выбирайте такой, который можно прочитать глазами. "
            "Для начала подойдёт простой текст: по одной задаче на строку, поля "
            "разделены символом `|`."
        ),
        example(
            "text",
            """
            1|Купить молоток|2|0|0
            2|Позвонить в сервис|3|1|1735689600
            """,
        ),
        example(
            "cpp",
            """
            // src/storage.cpp
            #include "storage.h"

            #include <fstream>
            #include <sstream>

            namespace {
            std::vector<std::string> split(const std::string& line, char sep) {
                std::vector<std::string> parts;
                std::istringstream iss(line);
                std::string part;
                while (std::getline(iss, part, sep)) parts.push_back(part);
                return parts;
            }
            }

            bool save_tasks(const std::vector<Task>& tasks, const std::string& path) {
                std::ofstream out(path, std::ios::trunc);
                if (!out) return false;

                for (const auto& t : tasks) {
                    out << t.id << '|' << t.title << '|'
                        << static_cast<int>(t.priority) << '|'
                        << (t.done ? 1 : 0) << '|'
                        << (t.due ? *t.due : 0) << '\\n';
                }
                return static_cast<bool>(out);
            }

            bool load_tasks(std::vector<Task>& tasks, int& next_id,
                            const std::string& path) {
                std::ifstream in(path);
                if (!in) return false;

                tasks.clear();
                std::string line;
                while (std::getline(in, line)) {
                    if (line.empty()) continue;
                    auto f = split(line, '|');
                    if (f.size() != 5) continue;   // битая строка — пропускаем

                    Task t;
                    t.id = std::stoi(f[0]);
                    t.title = f[1];
                    t.priority = static_cast<Priority>(std::stoi(f[2]));
                    t.done = std::stoi(f[3]) != 0;
                    auto due = std::stoll(f[4]);
                    if (due != 0) t.due = static_cast<std::time_t>(due);

                    next_id = std::max(next_id, t.id + 1);
                    tasks.push_back(std::move(t));
                }
                return true;
            }
            """,
        ),
        text(
            "Почему формат именно такой. Номер и приоритет — целые числа, "
            "их удобно читать и сравнивать. Флаг выполнения записан как `0` "
            "или `1`, потому что поток не умеет напрямую писать `bool` так, "
            "чтобы это потом читалось без `std::boolalpha`. Срок хранится "
            "как количество секунд — это компактно и не зависит от формата "
            "даты на конкретной машине.\n\n"
            "Разбор строки вынесен в функцию `split` внутри безымянного "
            "пространства имён: она нужна только этому файлу, и другие "
            "единицы трансляции её не видят. При загрузке битые строки "
            "пропускаются, а не обрушивают программу: файл мог быть испорчен "
            "или отредактирован вручную. `next_id` восстанавливается как "
            "максимальный существующий плюс один, иначе после перезапуска "
            "появятся дубликаты номеров."
        ),
        callout(
            "warning",
            "Формат с разделителем `|`",
            "Если в названии задачи встретится `|`, строка развалится при "
            "разборе. Для учебного проекта это допустимо, но в реальном коде "
            "либо запрещают символ во вводе, либо используют JSON. Всегда "
            "думайте, что произойдёт с данными, содержащими разделитель."
        ),
        heading("Меню и валидация ввода"),
        text(
            "Самая частая причина падения консольных программ — неверный ввод. "
            "Если пользователь вместо числа введёт букву, поток перейдёт в "
            "состояние ошибки, и все последующие чтения будут неудачными, пока "
            "ошибку не сбросят."
        ),
        example(
            "cpp",
            """
            #include <iostream>
            #include <limits>
            #include <string>

            int read_int(const std::string& prompt) {
                while (true) {
                    std::cout << prompt;
                    int value{};
                    if (std::cin >> value) {
                        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\\n');
                        return value;
                    }
                    std::cin.clear();
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\\n');
                    std::cout << "Нужно целое число, попробуйте снова\\n";
                }
            }

            std::string read_line(const std::string& prompt) {
                std::cout << prompt;
                std::string line;
                std::getline(std::cin, line);
                return line;
            }
            """,
        ),
        text(
            "Три действия обязательны при ошибке чтения: `clear()` сбрасывает "
            "флаг ошибки, `ignore()` выбрасывает остаток строки, и только потом "
            "можно читать снова. Без `ignore` следующее чтение сразу наткнётся "
            "на тот же неверный символ. Функция зациклена, пока не получит "
            "корректное значение, — так пользователь не сможет загнать "
            "программу в неверное состояние."
        ),
        example(
            "cpp",
            """
            // src/main.cpp
            #include "storage.h"
            #include "task_manager.h"

            #include <iostream>
            #include <string>

            void print_tasks(const std::vector<const Task*>& list) {
                if (list.empty()) {
                    std::cout << "Задач нет\\n";
                    return;
                }
                for (const auto* t : list) {
                    std::cout << "[" << t->id << "] " << t->title
                              << " | " << t->priority_name()
                              << " | " << (t->done ? "выполнена" : "активна");
                    if (t->is_overdue()) std::cout << " | ПРОСРОЧЕНА";
                    std::cout << '\\n';
                }
            }

            int main() {
                TaskManager tm;
                std::vector<Task> loaded;
                int next_id = 1;
                if (load_tasks(loaded, next_id, "data/tasks.txt")) {
                    tm.replace_all(std::move(loaded), next_id);
                }

                while (true) {
                    std::cout << "\\n1 добавить  2 все  3 активные  4 выполненные\\n"
                                 "5 просроченные  6 поиск  7 переключить  8 удалить\\n"
                                 "9 статистика  0 выход\\n";
                    int choice = read_int("Выбор: ");

                    switch (choice) {
                        case 0:
                            save_tasks(tm.all(), "data/tasks.txt");
                            std::cout << "До свидания\\n";
                            return 0;
                        case 1: {
                            auto title = read_line("Название: ");
                            if (title.empty()) {
                                std::cout << "Пустое название не добавлено\\n";
                                break;
                            }
                            int p = read_int("Приоритет 1-3: ");
                            if (p < 1 || p > 3) p = 2;
                            tm.add(std::move(title), static_cast<Priority>(p));
                            std::cout << "Добавлено\\n";
                            break;
                        }
                        case 2: print_tasks(tm.filter(false)); print_tasks(tm.filter(true)); break;
                        case 3: print_tasks(tm.filter(false)); break;
                        case 4: print_tasks(tm.filter(true)); break;
                        case 5: print_tasks(tm.overdue()); break;
                        case 6: print_tasks(tm.search(read_line("Слово: "))); break;
                        case 7: {
                            int id = read_int("Номер: ");
                            std::cout << (tm.toggle(id) ? "Изменено\\n" : "Не найдено\\n");
                            break;
                        }
                        case 8: {
                            int id = read_int("Номер: ");
                            std::cout << (tm.remove(id) ? "Удалено\\n" : "Не найдено\\n");
                            break;
                        }
                        case 9: {
                            auto s = tm.stats();
                            std::cout << "Всего " << s.total
                                      << ", выполнено " << s.done
                                      << ", активно " << s.active
                                      << ", просрочено " << s.overdue << '\\n';
                            break;
                        }
                        default:
                            std::cout << "Нет такого пункта\\n";
                    }
                }
            }
            """,
        ),
        text(
            "Стоит обратить внимание на строку `save_tasks(tm.all(), ...)` перед "
            "выходом. Сохранять после каждой операции тоже можно, но тогда при "
            "активной работе с программой файл перезаписывается десятки раз без "
            "нужды. Сохранение при выходе проще и предсказуемее; недостаток — "
            "при аварийном завершении последние изменения теряются. Для учебного "
            "проекта это приемлемый компромисс, и он явно назван, а не скрыт.\n\n"
            "Меню не знает, как устроено хранение, а `TaskManager` не знает, что "
            "существует консоль. Каждый слой занят своим делом, поэтому изменить "
            "формат файла или заменить меню на графическое можно независимо."
        ),
        heading("Сборка через CMake"),
        text(
            "Компилировать четыре файла вручную каждый раз утомительно. "
            "**CMake** описывает сборку один раз и создаёт файлы для нужной "
            "системы сборки."
        ),
        example(
            "cmake",
            """
            cmake_minimum_required(VERSION 3.20)
            project(task_manager LANGUAGES CXX)

            set(CMAKE_CXX_STANDARD 20)
            set(CMAKE_CXX_STANDARD_REQUIRED ON)
            set(CMAKE_CXX_EXTENSIONS OFF)

            add_executable(task_manager
                src/main.cpp
                src/task.cpp
                src/task_manager.cpp
                src/storage.cpp
            )

            target_include_directories(task_manager PRIVATE include)

            if (MSVC)
                target_compile_options(task_manager PRIVATE /W4)
            else()
                target_compile_options(task_manager PRIVATE -Wall -Wextra -pedantic)
            endif()
            """,
        ),
        example(
            "bash",
            """
            mkdir -p build && cd build
            cmake ..
            cmake --build .

            ./task_manager

            # без CMake, одной командой
            # g++ -std=c++20 -Wall -Wextra -Iinclude src/*.cpp -o task_manager
            """,
        ),
        text(
            "Каталог `build/` держите вне системы контроля версий: там лежат "
            "сгенерированные файлы. Флаги `-Wall -Wextra -pedantic` включают "
            "предупреждения; на Windows у MSVC аналог — `/W4`."
        ),
        heading("Порядок работы над проектом"),
        text(
            "Большой проект не пишут целиком за один раз. Двигайтесь шагами, "
            "после каждого шага программа должна собираться и запускаться."
        ),
        numbered(
            "Создайте каталоги и пустые файлы, соберите пустой `main` с приветствием.",
            "Опишите `Task` и добавьте в `main` пару задач в `std::vector`, выведите их.",
            "Перенесите операции в `TaskManager` и подключите его к меню.",
            "Добавьте сохранение в файл и загрузку при старте.",
            "Добавьте фильтры, поиск и статистику.",
            "Реализуйте валидацию ввода и проверьте ошибочные сценарии: пустое название, буква вместо номера, отсутствующий файл.",
            "Прогоните чек-лист качества и напишите `README.md`.",
        ),
        heading("Чек-лист качества"),
        bullets(
            "проект собирается без предупреждений при `-Wall -Wextra -pedantic`;",
            "нет ручных `new` и `delete` — все ресурсы под управлением RAII;",
            "данные сохраняются после выхода и восстанавливаются при следующем запуске;",
            "повторный запуск не дублирует задачи и не теряет номера;",
            "ввод буквы вместо номера не ломает программу;",
            "отсутствующий файл данных воспринимается как пустой список, а не как ошибка;",
            "каждый файл содержит только свои обязанности;",
            "есть `README.md` с командами сборки и запуска.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Всё в одном `main.cpp`",
                    "Файл на тысячу строк, меню переплетено с логикой и файлами.",
                    "Разделить на `task`, `task_manager`, `storage`, `main`.",
                ],
                [
                    "Забыли `std::cin.ignore` после `>>`",
                    "Следующий `getline` читает пустую строку.",
                    "Сбрасывать остаток строки после чтения числа.",
                ],
                [
                    "Не сбросили поток после ошибки ввода",
                    "Все последующие чтения тоже неудачны, цикл крутится бесконечно.",
                    "`clear()` и `ignore()` при неудаче.",
                ],
                [
                    "`next_id` не восстанавливается при загрузке",
                    "После перезапуска новые задачи получают существующие номера.",
                    "`next_id = max(next_id, id + 1)` при чтении.",
                ],
                [
                    "Ссылка на элемент вектора сохраняется дольше одной операции",
                    "После `push_back` ссылка может указывать на освобождённую память.",
                    "Не хранить ссылки между изменениями размера вектора.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Соберите проект по шагам из раздела «Порядок работы». "
            "Ниже — минимальный набор проверок, который нужно пройти перед сдачей."
        ),
        numbered(
            "Добавьте три задачи, выйдите и запустите программу снова — задачи должны остаться.",
            "Отметьте одну задачу выполненной и проверьте, что она появляется в списке выполненных и исчезает из активных.",
            "Введите букву вместо номера задачи — программа должна попросить число заново, а не завершиться.",
            "Удалите файл `data/tasks.txt` и запустите программу — она должна работать с пустым списком.",
            "Добавьте задачу со сроком в прошлом и проверьте, что она попадает в список просроченных.",
            "Введите название с пробелами и убедитесь, что оно сохранилось полностью.",
        ),
        text("Пример ожидаемого результата для первой проверки:"),
        example(
            "text",
            "[1] Купить молоток | обычный | активна\n[2] Позвонить в сервис | высокий | активна\n[3] Дочитать урок | низкий | выполнена",
        ),
        callout(
            "success",
            "Критерий готовности",
            "Все шесть проверок проходят. Программа собирается без предупреждений. "
            "В коде нет `new` и `delete`, нет `using namespace std;` в заголовках, "
            "и ни один файл не превышает двухсот строк."
        ),
        heading("Проверьте себя"),
        numbered(
            "Почему меню и работу с файлами держат в разных файлах?",
            "Зачем `is_overdue()` объявлен методом задачи, а не функцией в `main`?",
            "Почему `filter` возвращает указатели, а не копии задач?",
            "Что произойдёт, если не восстановить `next_id` при загрузке?",
            "Какие три действия нужны после неудачного чтения числа?",
            "Почему формат с разделителем `|` может сломаться?",
        ),
        heading("Ответы", 3),
        numbered(
            "Чтобы менять формат хранения или интерфейс независимо, а также чтобы логику можно было тестировать без клавиатуры.",
            "Правило «просрочена ли задача» относится к самой задаче и используется в нескольких местах; в одном методе его невозможно случайно рассинхронизировать.",
            "Копирование задач ради вывода тратит память и время, а константный указатель не позволяет случайно изменить список через результат фильтра.",
            "Новые задачи получат номера, которые уже есть в файле, и операции по номеру будут попадать не в ту задачу.",
            "`clear()` сбросить флаг ошибки, `ignore()` удалить остаток строки, затем предложить ввод снова.",
            "Если разделитель встретится внутри названия, строка разобьётся на большее число частей и разбор полей поедет.",
        ),
        heading("Итоги"),
        bullets(
            "Проект начинается с плана: требования, данные, обязанности файлов, потом код.",
            "Каждый класс отвечает за одно: `Task` — за одну задачу, `TaskManager` — за коллекцию, `storage` — за файл.",
            "Логика живёт рядом с данными: `is_overdue()` внутри `Task`.",
            "`std::optional` выражает необязательное значение лучше, чем нулевой указатель или магическое число.",
            "Файловое хранение отделено интерфейсом, поэтому формат можно заменить.",
            "Ввод валидируют в одном месте; при ошибке поток очищают и повторяют запрос.",
            "CMake описывает сборку один раз и работает на всех платформах.",
            "Готовность проверяют запуском: сохранение, восстановление, неверный ввод, отсутствующий файл.",
        ),
        heading("Что дальше"),
        text(
            "Первый уровень завершён: вы пишете программы на C++, собираете их из "
            "нескольких файлов и умеете довести проект до рабочего состояния. "
            "Второй уровень начинается с обзора современного C++: стандарты, "
            "инструменты, источники знаний и то, как писать код, который легко "
            "поддерживать."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "CMake Tutorial — cmake.org/cmake/help/latest/guide/tutorial/",
            "C++ Core Guidelines — isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines",
            "cppreference: std::optional — en.cppreference.com/w/cpp/utility/optional",
            "cppreference: std::filesystem — en.cppreference.com/w/cpp/filesystem",
            "nlohmann/json — header-only JSON для следующей версии проекта",
            "Catch2 — фреймворк модульных тестов для проверки `TaskManager`",
        ),
    ],
}
