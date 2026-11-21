# Курс C++

## 1. Новичок

1.  **Введение:** язык, компилятор, сборка, `main`, консольный вывод.
2.  **Типы и переменные:** числа, `char`, `bool`, `std::string`,
    инициализация, `const`, conversions.
3.  **Операторы:** арифметика, сравнения, логика, приоритет.
4.  **Условия и циклы:** `if`, `switch`, `while`, `do while`, `for`,
    `break`, `continue`.
5.  **Функции:** declaration/definition, параметры, return, overloads,
    scope.
6.  **Массивы/строки:** arrays, `std::array`, `std::string`, индексы,
    перебор.
7.  **Контейнеры:** `std::vector`, `pair`, основы `map`/`set`.
8.  **Указатели/ссылки:** адреса, pointers, references, `nullptr`,
    базовая безопасность.
9.  **ООП:** классы, поля, методы, constructors, encapsulation,
    inheritance.
10. **Файлы/ошибки:** streams, file I/O, error handling, несколько
    исходников.
11. **Проект:** консольное приложение с функциями и классами.

## 2. Средний уровень

1.  **Современный C++ и ресурсы:** RAII, storage duration, smart
    pointers, rule of 3/5/0.
2.  **Move semantics:** lvalue/rvalue, `std::move`, move constructors,
    perfect forwarding.
3.  **ООП:** virtual functions, abstract classes, composition,
    правильное уничтожение.
4.  **Templates:** function/class templates, specialization,
    `constexpr`, concepts basics.
5.  **STL:** containers, iterators, algorithms, lambdas, `optional`,
    `variant`, `tuple`, `string_view`, `span`.
6.  **Ошибки:** exceptions, exception-safety guarantees, `expected` в
    подходящих стандартах.
7.  **Сборка:** headers, translation units, ODR, CMake, libraries.
8.  **Тестирование:** debugger, sanitizers, unit tests, UB, static
    analysis.
9.  **Многопоточность:** `std::thread`, mutexes, atomics, condition
    variables, data races.
10. **Алгоритмы/performance:** complexity, cache locality, profiling,
    лишние копии.
11. **Проект:** многомодульная программа с тестами и сборкой.

## 3. Углублённый уровень

1.  **Язык и компиляция:** translation phases, ODR, linkage, lifetime,
    undefined behavior, стандарт.
2.  **Метапрограммирование:** SFINAE, concepts/constraints, variadic
    templates, type traits, compile-time computation.
3.  **Object model:** layout, alignment, strict aliasing, placement new,
    object lifetime.
4.  **Resource semantics:** move/forwarding, exception safety, API
    design.
5.  **Продвинутая STL:** allocators, ranges/views, coroutines, iterator
    categories, time/format.
6.  **Memory model/concurrency:** happens-before, memory order,
    lock-free concepts, async models.
7.  **Build/ABI:** large CMake projects, ABI, symbols, modules,
    cross-compilation.
8.  **Optimization:** machine code, vectorization, cache, profiling,
    compile-time cost.
9.  **Security:** memory errors, overflow, fuzzing, sanitizers,
    analyzers.
10. **Large-scale architecture:** library design, module boundaries,
    stable APIs, compiler portability.
11. **Проект:** library/system app with tests, performance measurements
    and docs.

**Методика:** выбрать стандарт (например, C++20/23), проверять
компиляцию и предупреждения, уделять внимание ресурсам и UB.
