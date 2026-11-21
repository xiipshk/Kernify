"""Урок 3.2 курса Python: C-расширения и Cython."""

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
    "language": "python",
    "program_order": 3,
    "topic_order": 2,
    "name": "3.2. Расширения на C и Cython",
    "slug": "python-3-2-расширения-на-c-и-cython",
    "short_description": (
        "Ускорение Python через C-расширения, Cython, ctypes, cffi, PyO3/Rust "
        "и Numba. Когда и как выходить за границы интерпретатора."
    ),
    "topic_name": "Расширения на C и Cython",
    "topic_description": (
        "Инструменты для написания высокопроизводительного кода: Python C API, "
        "Cython с типизацией и nogil, FFI через ctypes/cffi, современный Rust/PyO3 "
        "и JIT-компиляция Numba."
    ),
    "learning_objectives": [
        "Понимать, когда оправдано использование C-расширений",
        "Создавать минимальное расширение на C через Python C API",
        "Писать типизированный код на Cython с cdef, memoryview и nogil",
        "Использовать ctypes и cffi для вызова C-библиотек без написания C-кода",
        "Создавать расширения на Rust через PyO3/maturin",
        "Применять Numba для JIT-компиляции численных функций",
        "Выбирать подходящий инструмент для задачи",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "c-расширения",
        "cython",
        "ctypes",
        "cffi",
        "pyo3",
        "rust",
        "numba",
        "производительность",
    ],
    "starter_code": code(
        """
        # Cython: типизированная функция Фибоначчи
        # fast.pyx
        def fib(int n):
            cdef int a = 0, b = 1, i
            for i in range(n):
                a, b = b, a + b
            return a
        """
    ),
    "hints": [
        "Cython требует компиляции: pip install cython && python setup.py build_ext --inplace",
        "Ключевое слово nogil работает только в контексте prange или явном with nogil:",
        "Для ctypes всегда указывайте argtypes и restype — иначе UB.",
        "PyO3/maturin: cargo install maturin && maturin new --bindings pyo3 mylib",
    ],
    "content": [
        text(
            "Python удобен и выразителен, но интерпретатор, динамическая типизация и GIL "
            "делают его медленным для CPU-bound задач: тяжелых вычислений, обработки "
            "больших массивов, криптографии, парсинга. Когда профилирование показывает, "
            "что горячий путь лежит в чистом Python, и алгоритмические оптимизации "
            "исчерпаны — пора выходить за границы интерпретатора. В этом уроке разберём "
            "основные способы: ручной C API, Cython, FFI (ctypes/cffi), Rust/PyO3 и Numba."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "определять, когда нужен C-код, а когда достаточно алгоритмических улучшений;",
            "создавать расширение на C через Python C API и собирать его через setuptools;",
            "писать .pyx файлы с типизацией (cdef, cpdef), memoryview и освобождением GIL;",
            "вызывать функции из .so/.dll библиотек через встроенный ctypes;",
            "использовать cffi для более удобного и безопасного FFI;",
            "создавать Python-модули на Rust через PyO3 и maturin;",
            "применять @jit от Numba для автоматической JIT-компиляции численных функций;",
            "сравнивать подходы по сложности, скорости и накладным расходам.",
        ),
        heading("Зачем выходить за границы Python"),
        text(
            "Три главных ограничения чистого Python:\n"
            "1. **GIL (Global Interpreter Lock)** — только один поток выполняет байт-код. "
            "Многопоточность не ускоряет CPU-bound код.\n"
            "2. **Динамическая типизация** — каждая операция требует проверки типов, "
            "поиска методов в MRO, аллокации объектов.\n"
            "3. **Интерпретатор** — байт-код выполняется в виртуальной машине, а не "
            "напрямую на железе."
        ),
        table(
            ["Сценарий", "Решение в чистом Python", "Когда нужен C/Rust"],
            [
                ["Веб-бэкенд, HTTP, БД", "asyncio, aiohttp, пулы соединений", "Редко (только если парсинг/сериализация — узкое место)"],
                ["Обработка изображений", "Pillow, OpenCV (уже на C)", "Если нужны кастомные фильтры"],
                ["Научные вычисления", "NumPy, Pandas (вектор化)", "Кастомные алгоритмы, не выражаемые через ufunc"],
                ["Криптография, хэширование", "hashlib, cryptography (уже на C)", "Свои алгоритмы или интеграция с C-библиотекой"],
                ["Real-time / игровой цикл", "Сложно гарантировать задержки", "Часто необходимо"],
            ],
        ),
        callout(
            "info",
            "Правило: сначала профилируйте",
            "90% случаев «медленного Python» решаются: лучшим алгоритмом, NumPy, "
            "кэшированием, asyncio для I/O. C-расширения — последнее средство, "
            "а не первое. Они усложняют сборку, отладку, деплой и поддержку.",
        ),
        heading("Python C API: ручное написание расширений"),
        text(
            "Python C API — самый низкий уровень. Вы пишете C-код, который напрямую "
            "взаимодействует с объектами Python: увеличивает/уменьшает счётчики ссылок, "
            "создаёт кортежи, списки, строки, вызывает методы. Это даёт максимальный "
            "контроль, но требует глубокого понимания модели памяти CPython."
        ),
        heading("Минимальное расширение", 3),
        example(
            "c",
            """
            // mymodule.c
            #include <Python.h>

            static PyObject* hello(PyObject* self, PyObject* args) {
                const char* name;
                if (!PyArg_ParseTuple(args, "s", &name))
                    return NULL;
                return PyUnicode_FromFormat("Hello, %s!", name);
            }

            static PyMethodDef methods[] = {
                {"hello", hello, METH_VARARGS, "Greet someone"},
                {NULL, NULL, 0, NULL}
            };

            static struct PyModuleDef module = {
                PyModuleDef_HEAD_INIT,
                "mymodule",
                "Example module",
                -1,
                methods
            };

            PyMODINIT_FUNC PyInit_mymodule(void) {
                return PyModule_Create(&module);
            }
            """,
        ),
        text(
            "Ключевые моменты:\n"
            "- `PyArg_ParseTuple` — парсит позиционные аргументы из кортежа Python в C. "
            "Форматная строка `'s'` — строка (const char*).\n"
            "- `PyUnicode_FromFormat` — создаёт объект строки Python из C-строки.\n"
            "- `PyMethodDef` — таблица методов модуля. `METH_VARARGS` — обычные "
            "позиционные аргументы.\n"
            "- `PyModuleDef` — описание модуля. `PyInit_<name>` — точка входа, "
            "которую ищет импортёр."
        ),
        heading("Сборка через setuptools", 3),
        example(
            "python",
            """
            # setup.py
            from setuptools import setup, Extension

            module = Extension('mymodule', sources=['mymodule.c'])

            setup(
                name='mymodule',
                version='1.0',
                ext_modules=[module],
            )
            """,
        ),
        example(
            "bash",
            """
            pip install -e .
            # или
            python setup.py build_ext --inplace
            """,
        ),
        example(
            "python",
            """
            import mymodule
            print(mymodule.hello("World"))  # Hello, World!
            """,
        ),
        text(
            "Флаг `-e` (editable) ставит пакет в режим разработки: изменения в .c "
            "после пересборки (`python setup.py build_ext --inplace`) сразу видны. "
            "Для продакшена лучше собирать wheel: `pip wheel .` и устанавливать его."
        ),
        heading("Счётчики ссылок: главная ловушка", 3),
        text(
            "Каждый Python-объект имеет `ob_refcnt`. Правила:\n"
            "- Функции, **создающие** новый объект (PyUnicode_FromFormat, PyList_New, "
            "PyLong_FromLong) возвращают **новую ссылку** (new reference) — вы "
            "владеете ею и должны вызвать `Py_DECREF`, когда объект больше не нужен.\n"
            "- Функции, **возвращающие** существующий объект (PyList_GetItem, "
            "PyDict_GetItem, PyTuple_GetItem) возвращают **заимствованную ссылку** "
            "(borrowed reference) — её не нужно декрементировать, но и нельзя "
            "хранить после возможного изменения контейнера.\n"
            "- `Py_INCREF(obj)` — увеличивает счётчик, когда вы сохраняете указатель "
            "на долгий срок."
        ),
        callout(
            "warning",
            "Утечки и use-after-free",
            "Забытый Py_DECREF — утечка памяти. Двойной Py_DECREF или доступ после "
            "Py_DECREF — краш интерпретатора. Всегда парируйте INCREF/DECREF. "
            "Инструменты: `tracemalloc`, `valgrind --tool=memcheck`, "
            "`PYTHONMALLOC=debug`.",
        ),
        heading("Cython: Python с типизацией"),
        text(
            "Cython — надмножество Python, компилируемое в C. Вы пишете код, похожий "
            "на Python, добавляете статические типы через `cdef`/`cpdef`, и Cython "
            "генерирует эффективный C-код, вызывающий Python C API. Это золотой "
            "баланс: читаемость Python, скорость C."
        ),
        heading("Установка и первый файл", 3),
        example(
            "bash",
            """
            pip install cython
            """,
        ),
        example(
            "cython",
            """
            # fast.pyx
            def fib(int n):
                cdef int a = 0, b = 1, i
                for i in range(n):
                    a, b = b, a + b
                return a
            """,
        ),
        example(
            "python",
            """
            # setup.py
            from setuptools import setup
            from Cython.Build import cythonize

            setup(
                ext_modules=cythonize("fast.pyx", compiler_directives={'language_level': 3})
            )
            """,
        ),
        example(
            "bash",
            """
            python setup.py build_ext --inplace
            # Создаёт fast.cpython-*.so
            """,
        ),
        example(
            "python",
            """
            import fast
            print(fast.fib(10))  # 55
            """,
        ),
        heading("Ключевые ключевые слова типизации", 3),
        table(
            ["Ключевое слово", "Значение", "Пример"],
            [
                ["`cdef`", "C-переменная или C-функция (не видна из Python)", "`cdef int x = 5` / `cdef int add(int a, int b): return a+b`"],
                ["`cpdef`", "C-функция + Python-обёртка (видна из Python)", "`cpdef int add(int a, int b): return a+b`"],
                ["`cdef class`", "Extension type (C-структура, быстрее обычного класса)", "`cdef class Point: cdef int x, y`"],
                ["`cimport`", "Импорт C-уровня из .pxd файлов (без накладных расходов Python)", "`cimport numpy as np`"],
                ["`nogil`", "Блок/функция без GIL (только C-типы, без Python-объектов)", "`with nogil: ...` / `cpdef int f() nogil: ...`"],
            ],
        ),
        heading("memoryview: быстрый доступ к буферам", 3),
        text(
            "`memoryview` (в Cython — синтаксис `type[:]`) даёт прямой доступ к "
            "памяти массива без копирования и проверок границ в Python. Работает с "
            "bytes, bytearray, array.array, numpy.ndarray, любым объектом, "
            "поддерживающим buffer protocol."
        ),
        example(
            "cython",
            """
            # sum_buffer.pyx
            def sum_buffer(int[:] buf):
                cdef int total = 0
                cdef int i
                for i in range(buf.shape[0]):
                    total += buf[i]
                return total
            """,
        ),
        example(
            "python",
            """
            import sum_buffer
            import array
            import numpy as np

            data = array.array('i', range(1_000_000))
            print(sum_buffer.sum_buffer(data))

            arr = np.arange(1_000_000, dtype=np.int32)
            print(sum_buffer.sum_buffer(arr))
            """,
        ),
        text(
            "Многомерные буферы: `int[:, :]` (2D), `double[:, :, :]` (3D). "
            "Стрыды (strides) доступны через `buf.strides`. `memoryview` можно "
            "срезать: `buf[::2]` — каждый второй элемент без копирования."
        ),
        heading("nogil и prange: параллелизм без GIL", 3),
        text(
            "Блок `with nogil:` или атрибут `nogil` у функции говорит Cython: "
            "здесь не используется Python C API, GIL можно отпустить. Внутри можно "
            "использовать только C-типы (int, double, memoryview, указатели), "
            "но **не** Python-объекты (list, dict, str, вызовы Python-функций)."
        ),
        example(
            "cython",
            """
            # parallel.pyx
            from cython.parallel import prange

            def parallel_sum(int[:] data):
                cdef int total = 0
                cdef int i
                # prange автоматически распараллеливает цикл через OpenMP
                for i in prange(data.shape[0], nogil=True):
                    total += data[i]
                return total
            """,
        ),
        text(
            "Требует компилятора с поддержкой OpenMP (GCC, Clang, MSVC). На macOS "
            "GCC из Homebrew (`brew install gcc`) или Clang с флагом `-fopenmp`. "
            "В `setup.py` добавьте `extra_compile_args=['-fopenmp'], "
            "extra_link_args=['-fopenmp']`."
        ),
        heading("NumPy интеграция", 3),
        example(
            "cython",
            """
            # numpy_fast.pyx
            import numpy as np
            cimport numpy as np

            def process(np.ndarray[np.int32_t, ndim=1] arr):
                cdef int n = arr.shape[0]
                cdef int i, total = 0
                for i in range(n):
                    total += arr[i]
                return total
            """,
        ),
        text(
            "`cimport numpy as np` подключает C-API NumPy. Аннотация "
            "`np.ndarray[np.int32_t, ndim=1]` проверяет dtype и размерность "
            "при вызове и даёт Cythonу информацию для оптимизаций. "
            "Всегда используйте `cimport` для NumPy в .pyx файлах."
        ),
        heading("Cython аннотации: профилирование горячих линий", 3),
        example(
            "bash",
            """
            cython -a fast.pyx
            # Генерирует fast.html: жёлтые строки — обращения к Python API,
            # белые — чистый C. Цель: минимизировать жёлтое в горячих циклах.
            """,
        ),
        heading("ctypes: встроенный FFI"),
        text(
            "`ctypes` в стандартной библиотеке позволяет вызывать функции из "
            "динамических библиотек (.so, .dll, .dylib) без написания C-кода. "
            "Удобно для системных библиотек (libc, WinAPI) и простых своих."
        ),
        heading("Базовое использование", 3),
        example(
            "python",
            """
            import ctypes
            import platform

            if platform.system() == "Windows":
                lib = ctypes.CDLL("./mylib.dll")
            else:
                lib = ctypes.CDLL("./mylib.so")

            # C: int add(int a, int b)
            lib.add.argtypes = [ctypes.c_int, ctypes.c_int]
            lib.add.restype = ctypes.c_int

            result = lib.add(2, 3)  # 5
            print(result)
            """,
        ),
        text(
            "`argtypes` — список типов аргументов (ctypes.c_int, ctypes.c_double, "
            "ctypes.c_char_p, ctypes.POINTER(Type)). `restype` — тип возвращаемого "
            "значения. **Всегда указывайте их** — без этого ctypes передаёт/читает "
            "сырые слова памяти, что ведёт к UB, крашам и неверным результатам."
        ),
        heading("Структуры и указатели", 3),
        example(
            "python",
            """
            class Point(ctypes.Structure):
                _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

            # C: double distance(Point* a, Point* b)
            lib.distance.argtypes = [ctypes.POINTER(Point), ctypes.POINTER(Point)]
            lib.distance.restype = ctypes.c_double

            p1 = Point(0, 0)
            p2 = Point(3, 4)
            print(lib.distance(ctypes.byref(p1), ctypes.byref(p2)))  # 5.0
            """,
        ),
        text(
            "`ctypes.Structure` задаёт layout в памяти. `ctypes.byref(obj)` — "
            "указатель на существующий объект. `ctypes.POINTER(Type)` — тип указателя. "
            "`ctypes.pointer(obj)` — создаёт новый объект-указатель."
        ),
        heading("Callback функции", 3),
        example(
            "python",
            """
            CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int)

            def py_compare(a, b):
                return a - b

            cmp_func = CMPFUNC(py_compare)
            # C: void qsort(void* base, size_t nmemb, size_t size, 
            #               int (*compar)(const void*, const void*))
            lib.qsort(array, len(array), ctypes.sizeof(ctypes.c_int), cmp_func)
            """,
        ),
        text(
            "`CFUNCTYPE` создаёт C-совместимый указатель на Python-функцию. "
            "Важно: `cmp_func` должен жить, пока C-код его использует — сохраняйте "
            "ссылку в Python-переменной, иначе GC удалит callback."
        ),
        callout(
            "warning",
            "ctypes ловушки",
            "1. Без argtypes/restype — UB.\n"
            "2. Передача Python-строки в `char*` — `ctypes.c_char_p(b'str')`, "
            "но строка должна жить до конца вызова.\n"
            "3. Структуры с выравниванием — проверяйте `ctypes.alignment`.\n"
            "4. 64-битные указатели на 32-битных системах — используйте `ctypes.c_void_p`.",
        ),
        heading("cffi: удобный и безопасный FFI"),
        text(
            "`cffi` (pip install cffi) — надстройка над libffi, проще и безопаснее "
            "ctypes. Два режима: ABI (динамическая загрузка) и API (генерация C-кода)."
        ),
        heading("ABI mode", 3),
        example(
            "python",
            """
            from cffi import FFI

            ffi = FFI()
            ffi.cdef('''
                int add(int a, int b);
                double distance(double x1, double y1, double x2, double y2);
            ''')

            lib = ffi.dlopen("./mylib.so")  # или .dll/.dylib
            print(lib.add(2, 3))
            """,
        ),
        heading("API mode (рекомендуемый)", 3),
        example(
            "python",
            """
            # build.py
            from cffi import FFI

            ffi = FFI()
            ffi.set_source("_mylib",
                '#include "mylib.h"',
                libraries=['mylib'],
                library_dirs=['.'],
            )
            ffi.cdef('''
                int add(int a, int b);
            ''')

            if __name__ == "__main__":
                ffi.compile()
            """,
        ),
        example(
            "bash",
            """
            python build.py
            # Создаёт _mylib.cpython-*.so
            """,
        ),
        example(
            "python",
            """
            from _mylib import ffi, lib
            print(lib.add(2, 3))
            """,
        ),
        text(
            "API mode генерирует C-код, компилирует его и создаёт нативный модуль. "
            "Это быстрее (нет libffi накладных расходов), безопаснее (проверка "
            "сигнатур на этапе компиляции C) и позволяет использовать макросы, "
            "inline-функции и константы из заголовков."
        ),
        heading("PyO3: Rust + Python"),
        text(
            "PyO3 — современные биндинги Rust ↔ Python. Rust даёт гарантии безопасности "
            "памяти без GC, отсутствие GIL (по умолчанию), удобный Cargo, отличную "
            "экосистему крейтов. `maturin` — инструмент сборки: `maturin develop` "
            "компилирует Rust и ставит модуль в Python."
        ),
        heading("Создание проекта", 3),
        example(
            "bash",
            """
            pip install maturin
            # Или: cargo install maturin

            maturin new --bindings pyo3 my_rust_lib
            cd my_rust_lib
            """,
        ),
        heading("Cargo.toml", 3),
        example(
            "toml",
            """
            [package]
            name = "my_rust_lib"
            version = "0.1.0"
            edition = "2021"

            [lib]
            name = "my_rust_lib"
            crate-type = ["cdylib"]

            [dependencies]
            pyo3 = { version = "0.20", features = ["extension-module"] }
            """,
        ),
        heading("Rust код", 3),
        example(
            "rust",
            """
            // src/lib.rs
            use pyo3::prelude::*;

            #[pyfunction]
            fn fib(n: usize) -> usize {
                let mut a = 0;
                let mut b = 1;
                for _ in 0..n {
                    let tmp = a + b;
                    a = b;
                    b = tmp;
                }
                a
            }

            #[pymodule]
            fn my_rust_lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
                m.add_function(wrap_pyfunction!(fib, m)?)?;
                Ok(())
            }
            """,
        ),
        heading("Сборка и использование", 3),
        example(
            "bash",
            """
            maturin develop --release
            """,
        ),
        example(
            "python",
            """
            import my_rust_lib
            print(my_rust_lib.fib(10))  # 55
            """,
        ),
        heading("Параллелизм без GIL через Rayon", 3),
        example(
            "rust",
            """
            use pyo3::prelude::*;
            use rayon::prelude::*;

            #[pyfunction]
            fn parallel_sum(data: Vec<usize>) -> usize {
                data.par_iter().sum()  // Rayon использует все ядра!
            }
            """,
        ),
        text(
            "Rust-функция по умолчанию выполняется без GIL. PyO3 захватывает GIL "
            "только для преобразования аргументов/результата. Rayon распараллеливает "
            "на все ядра — идеально для CPU-bound задач."
        ),
        heading("Numba: JIT-компиляция для NumPy"),
        text(
            "Numba (pip install numba) — JIT-компилятор, основанный на LLVM. "
            "Декоратор `@jit(nopython=True)` компилирует функцию в машинный код "
            "при первом вызове. Работает с NumPy массивами, циклами, математикой. "
            "Не работает с Python-объектами (list, dict, классы) в nopython режиме."
        ),
        example(
            "python",
            """
            from numba import jit, prange
            import numpy as np

            @jit(nopython=True)
            def fast_fib(n):
                a, b = 0, 1
                for _ in range(n):
                    a, b = b, a + b
                return a

            @jit(nopython=True, parallel=True)
            def parallel_sum(arr):
                total = 0
                for i in prange(arr.shape[0]):
                    total += arr[i]
                return total

            arr = np.arange(10_000_000, dtype=np.int64)
            print(parallel_sum(arr))  # использует все ядра
            """,
        ),
        text(
            "`prange` + `parallel=True` — автоматическая параллелизация через OpenMP. "
            "Numba отлично подходит для численных ядер, где переписывание на Cython/Rust "
            "занимает слишком много времени."
        ),
        heading("Сравнение подходов"),
        table(
            ["Подход", "Сложность", "Макс. скорость", "GIL", "Зависимости", "Когда выбирать"],
            [
                ["C API", "Очень высокая", "Максимальная", "Ручное", "Нет", "Нужно полное управление, встраивание в CPython"],
                ["Cython", "Средняя", "Высокая", "nogil", "Cython", "Большинство CPU-bound задач, NumPy-интеграция"],
                ["ctypes", "Низкая", "Средняя", "Да", "Встроен", "Быстрый вызов системной библиотеки, прототипирование"],
                ["cffi (API)", "Низкая", "Высокая", "Да", "cffi", "Серьёзный FFI, нужны заголовки, безопасность"],
                ["PyO3/Rust", "Средняя", "Максимальная", "Нет (по умолчанию)", "Rust toolchain", "Новые модули, параллелизм, безопасность памяти"],
                ["Numba", "Очень низкая", "Высокая (числ.)", "Нет (nogil)", "LLVM", "Быстрый JIT для NumPy-ядров, эксперименты"],
            ],
        ),
        heading("Профилирование C/Cython/Rust кода"),
        text(
            "Обычные Python-профайлеры (cProfile, py-spy) не видят внутрь нативного кода. "
            "Инструменты:\n"
            "- **perf (Linux)**: `perf record -g python script.py && perf report` — "
            "показывает C/Rust стеки.\n"
            "- **cython -a**: `cython -a file.pyx` — HTML с аннотацией жёлтых линий.\n"
            "- **gdb/lldb**: отладка сегфолтов в расширениях.\n"
            "- **valgrind**: `valgrind --tool=memcheck python script.py` — утечки в C.\n"
            "- **scalene**: `python -m scalene script.py` — показывает CPU/память по "
            "строкам, включая Cython (через tracemalloc)."
        ),
        heading("Распространённые паттерны и лучшие практики"),
        bullets(
            "**Минимизируйте границу Python↔C**: передавайте большие массивы целиком, "
            "а не по элементу. Каждый вызов через границу — накладные расходы.",
            "**Используйте memoryview / NumPy buffer protocol**: никаких копий, "
            "прямой доступ к памяти.",
            "**Освобождайте GIL там, где нет Python API**: `with nogil:` в Cython, "
            "по умолчанию в PyO3, `prange` / `parallel=True`.",
            "**Пишите тесты на Python**: логику проверяйте на Python, нативный код — "
            "только горячие ядра. Property-based testing (hypothesis) ловит edge cases.",
            "**CI/CD**: собирайте wheels для целевых платформ (cibuildwheel для "
            "Cython/cffi, maturin для PyO3). Тестируйте на Linux/macOS/Windows.",
            "**Версионирование**: расширения привязаны к ABI Python (stable ABI "
            "начиная с 3.2 помогает, но не всегда). Указывайте `python_requires`.",
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Последствия", "Как правильно"],
            [
                ["Cython без типов (cdef)", "Код работает как обычный Python, никакого ускорения", "Добавляйте типы аргументов, локальных переменных, возвращаемых значений"],
                ["Забыли nogil=True в prange", "GIL не отпустится, параллелизм не работает", "Всегда указывайте nogil=True при prange и в with nogil:"],
                ["ctypes без argtypes/restype", "UB, краши, неверные результаты", "Всегда задавайте argtypes (список) и restype"],
                ["Передача Python-объектов в C без incref", "Утечки памяти / use-after-free / краш", "Py_INCREF при сохранении, Py_DECREF при освобождении"],
                ["Смешивание аллокаторов (malloc/free vs PyMem)", "Heap corruption", "Используйте PyMem_Malloc/PyMem_Free для объектов Python"],
                ["Rust: неправильные lifetime в PyO3", "Ошибки компиляции или UB", "Следуйте PyO3 гайду: Bound<'py>, Py<PyAny>, GILGuard"],
                ["Numba: использование Python-объектов в nopython", "Fallback в object mode — медленно", "Только NumPy массивы, примитивы, простые циклы"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Для компиляции Cython/Rust нужны установленные "
            "инструменты (см. hints)."
        ),
        numbered(
            "Cython: напишите пузырьковую сортировку `bubble_sort(int[:] arr)` с типизацией и `nogil`. Сравните скорость с `list.sort()` на 10000 элементов.",
            "ctypes: вызовите `libc.strlen` (или `msvcrt.strlen` на Windows) для подсчёта длины строки. Сравните с `len(bytes)`.",
            "cffi (API mode): оберните простую C-функцию `int hash32(const char* data, size_t len)` (реализуйте её в отдельном .c файле) и вызовите из Python.",
            "PyO3: создайте проект `maturin new --bindings pyo3 parser`, реализуйте параллельный парсер строк в числа (`Vec<f64> -> Vec<f64>`) через Rayon.",
            "Numba: напишите `@jit(nopython=True, parallel=True)` функцию Монте-Карло для оценки π (генерация случайных точек в квадрате, подсчёт в круге).",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "Python list.sort(): 0.008s\n"
            "Cython bubble_sort: 0.045s\n"
            "(пузырьковая сортировка O(n^2) медленнее, но показывает ускорение vs чистый Python)",
        ),
        callout(
            "success",
            "Подсказка к заданию 1",
            "В setup.py добавьте `extra_compile_args=['-fopenmp'], extra_link_args=['-fopenmp']` "
            "для OpenMP. На macOS: `brew install libomp` и флаги `-Xpreprocessor -fopenmp -lomp`. "
            "Используйте `cython.parallel.prange` с `nogil=True`.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Какие три основных ограничения Python для CPU-bound задач?",
            "Чем `cdef` отличается от `cpdef` в Cython?",
            "Зачем нужен `memoryview` (`int[:]`) в Cython?",
            "Почему в ctypes критически важны `argtypes` и `restype`?",
            "В чём главное преимущество PyO3/Rust перед Cython для параллелизма?",
            "Когда Numba — лучший выбор, а когда Cython/Rust?",
        ),
        heading("Ответы", 3),
        numbered(
            "GIL, динамическая типизация, интерпретатор байт-кода.",
            "`cdef` — только C-уровень (не видно из Python), `cpdef` — C-функция + Python-обёртка (видна из Python).",
            "Прямой доступ к памяти буфера без копирования и проверок границ Python. Работает с любым объектом, поддерживающим buffer protocol.",
            "Без них ctypes передаёт/читает сырые машинные слова — неопределённое поведение, краши, неверные результаты.",
            "Rust-функции по умолчанию выполняются без GIL. Rayon распараллеливает на все ядра без дополнительных усилий. Безопасность памяти гарантируется компилятором.",
            "Numba — для быстрых экспериментов с NumPy, JIT без сборки. Cython — для продакшен-модулей с NumPy, нужной типизацией. Rust — для новых модулей, где важна безопасность, параллелизм, долгая поддержка.",
        ),
        heading("Итоги"),
        bullets(
            "C-расширения оправданы только после профилирования и исчерпания алгоритмических оптимизаций.",
            "Python C API — максимальный контроль, но ручное управление refcount и высокая сложность.",
            "Cython — баланс: Python-синтаксис + статические типы (cdef/cpdef) + memoryview + nogil/prange.",
            "ctypes — встроенный FFI для простых вызовов системных библиотек. Всегда указывайте argtypes/restype.",
            "cffi — безопаснее и удобнее ctypes. API mode генерирует нативный модуль.",
            "PyO3/Rust — современный стандарт: безопасность памяти, нет GIL, Cargo, Rayon для параллелизма. maturin develop — один командой.",
            "Numba — JIT для NumPy-ядер: @jit(nopython=True, parallel=True) + prange.",
            "Выбор: Numba (эксперименты) → Cython (продакшен NumPy) → Rust/PyO3 (новые модули, параллелизм) → C API (экзотические случаи).",
            "Профилируйте нативный код: perf, cython -a, valgrind, scalene.",
        ),
        heading("Что дальше"),
        text(
            "Теперь вы умеете ускорять Python на порядки. В следующем уроке разберём "
            "архитектуру приложений: как структурировать крупные проекты, разделение "
            "на слои, dependency injection, event-driven архитектура и микросервисы."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Cython Docs — cython.readthedocs.io/",
            "Python C API — docs.python.org/3/c-api/",
            "cffi Docs — cffi.readthedocs.io/",
            "PyO3 Guide — pyo3.rs/",
            "Numba Docs — numba.readthedocs.io/",
            "Extending Python with C/C++ — docs.python.org/3/extending/",
            "maturin — www.maturin.rs/",
            "Rayon — docs.rs/rayon/",
        ),
    ],
}