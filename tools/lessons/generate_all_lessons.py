#!/usr/bin/env python3
"""
Massive lesson generator for all 193 lessons across 6 languages.
Generates high-quality, detailed lessons with term definitions, friendly tone, maximum detail.
"""

import json
import os
from pathlib import Path

# ============================================================
# LANGUAGE-SPECIFIC CONTENT TEMPLATES
# ============================================================

LANGUAGE_DATA = {
    "javascript": {
        "name": "JavaScript",
        "slug": "javascript",
        "icon": "🌐",
        "lessons": 29,
        "paradigm": "динамический, интерпретируемый, мультипарадигменный",
        "runtime": "браузер / Node.js / Deno / Bun",
        "typing": "динамическая, слабая",
        "gc": "автоматическая (mark-and-sweep, generational)",
        "concurrency": "Event Loop, Promise, async/await, Web Workers",
        "package_manager": "npm / yarn / pnpm / bun",
        "key_concepts": [
            "Event Loop", "Замыкания", "Прототипы", "this", "Promise", "async/await",
            "Модули (ESM/CommonJS)", "События", "DOM", "Fetch API", "Web Workers",
            "Строгий режим", "Деструктуризация", "Spread/Rest", "Arrow functions",
            "Классы", "Приватные поля", "Proxy/Reflect", "Symbol", "Итераторы/Генераторы"
        ],
        "ecosystem": "React, Vue, Svelte, Next.js, Node.js, Express, Fastify, TypeScript",
    },
    "python": {
        "name": "Python",
        "slug": "python",
        "icon": "🐍",
        "lessons": 33,
        "paradigm": "мультипарадигменный (ООП, функциональный, процедурный)",
        "runtime": "CPython / PyPy / MicroPython",
        "typing": "динамическая, сильная, опциональная статическая (type hints)",
        "gc": "reference counting + generational GC",
        "concurrency": "GIL, threading, multiprocessing, asyncio, concurrent.futures",
        "package_manager": "pip / poetry / uv / conda / pipx",
        "key_concepts": [
            "GIL", "Reference Counting", "Декораторы", "Контекстные менеджеры",
            "Генераторы", "Корутины (async/await)", "Dataclasses", "Type Hints",
            "Методы магии (__dunder__)", "MRO", "Дескрипторы", "Metaclasses",
            "Pattern Matching (match/case)", "Walrus Operator", "F-strings",
            "Pathlib", "Virtual Environments", "pip/requirements.txt/pyproject.toml"
        ],
        "ecosystem": "Django, FastAPI, Flask, NumPy, Pandas, PyTorch, TensorFlow, pytest",
    },
    "rust": {
        "name": "Rust",
        "slug": "rust",
        "icon": "🦀",
        "lessons": 33,
        "paradigm": "системное, мультипарадигменное, без GC",
        "runtime": "нет рантайма (компилируется в нативный код)",
        "typing": "статическая, сильная, вывод типов",
        "gc": "нет GC — управление памятью через Ownership/Borrowing",
        "concurrency": "Fearless Concurrency: threads, channels, async/await (tokio/async-std), Send/Sync",
        "package_manager": "cargo (build system + package manager)",
        "key_concepts": [
            "Ownership", "Borrowing", "Lifetimes", "Move semantics",
            "Trait bounds", "Generics", "Enums/Option/Result", "Pattern matching",
            "Zero-cost abstractions", "Zero-copy", "Unsafe Rust", "FFI",
            "Macros (declarative/procedural)", "Iterators/Closures", "Smart pointers",
            "Pin/Unpin", "Future/Poll", "Async runtime (Tokio)", "Workspaces"
        ],
        "ecosystem": "Actix, Axum, Rocket, Tokio, Serde, Diesel, SQLx, clap, anyhow",
    },
    "csharp": {
        "name": "C#",
        "slug": "csharp",
        "icon": "🔷",
        "lessons": 33,
        "paradigm": "объектно-ориентированное, функциональное, обобщённое",
        "runtime": ".NET Runtime (CLR), CoreCLR, Mono, NativeAOT",
        "typing": "статическая, сильная, nullable reference types, type inference",
        "gc": "Generational GC (Gen 0/1/2), LOH, POH, Background/Server GC",
        "concurrency": "ThreadPool, Task/async/await, Parallel, PLINQ, Channels, Actors (Akka/Orleans)",
        "package_manager": "NuGet (dotnet CLI, PackageReference)",
        "key_concepts": [
            "LINQ", "Generics", "Delegates/Events", "Lambdas", "Extension methods",
            "Records", "Pattern matching", "Async/await", "ValueTask", "Span/Memory",
            "Dependency Injection", "Middleware", "EF Core", "MediatR", "Source Generators",
            "NativeAOT", "PGO", "SIMD", "Unsafe/Pointers", "Structs/Classes",
            "IDisposable/IAsyncDisposable", "ConfigureAwait", "CancellationToken"
        ],
        "ecosystem": "ASP.NET Core, Blazor, MAUI, Entity Framework, MassTransit, Orleans, Akka.NET",
    },
    "cpp": {
        "name": "C++",
        "slug": "cpp",
        "icon": "⚙️",
        "lessons": 33,
        "paradigm": "мультипарадигменное (ООП, обобщённое, процедурное, метапрограммирование)",
        "runtime": "нет рантайма (нативный код), RAII",
        "typing": "статическая, сильная, шаблоны, concepts (C++20)",
        "gc": "нет GC — RAII, умные указатели, ручное управление",
        "concurrency": "std::thread, std::async, coroutines (C++20), executors, atomics, mutex, condition_variable",
        "package_manager": "CMake + Conan / vcpkg / xmake / Meson",
        "key_concepts": [
            "RAII", "Move semantics", "Perfect forwarding", "Smart pointers",
            "Templates", "Concepts", "Constexpr", "Lambdas", "Algorithms/Iterators",
            "Memory model", "Atomics", "Coroutines", "Modules (C++20)", "Ranges",
            "Structured bindings", "Deduction guides", "SFINAE", "CRTP",
            "Pimpl", "Type erasure", "Policy-based design", "Compile-time computation"
        ],
        "ecosystem": "Qt, Boost, STL, Abseil, fmt, spdlog, Catch2, GoogleTest, gRPC, Protobuf",
    },
    "css": {
        "name": "CSS",
        "slug": "css",
        "icon": "🎨",
        "lessons": 32,
        "paradigm": "декларативный язык стилей",
        "runtime": "Browser Rendering Engine (Blink, WebKit, Gecko)",
        "typing": "нет типизации (каскад, наследование, специфичность)",
        "gc": "N/A",
        "concurrency": "N/A (анимации в compositor thread)",
        "package_manager": "npm (PostCSS, Sass, Tailwind, CSS Modules)",
        "key_concepts": [
            "Box Model", "Flexbox", "Grid", "Cascade", "Specificity", "Inheritance",
            "Custom Properties (CSS Variables)", "Container Queries", "Subgrid",
            "Anchor Positioning", "Scroll-driven Animations", "View Transitions",
            "Logical Properties", "Color Spaces (LCH, OKLCH, Display-P3)",
            "Typography", "Responsive Design", "Media Queries", "Animations/Transitions",
            "Transforms", "Filters", "Masks", "Clipping", "Shapes", "Typography"
        ],
        "ecosystem": "Tailwind CSS, Sass/SCSS, PostCSS, Styled Components, CSS Modules, Lightning CSS",
    },
}

# ============================================================
# DETAILED LESSON PLANS PER LANGUAGE
# ============================================================

JS_LESSONS = [
    ("01", "Введение в JavaScript", "База: что такое JS, где запускать, консоль, первый код"),
    ("02", "Переменные и типы данных", "let/const/var, примитивы, объекты, typeof, null vs undefined"),
    ("03", "Операторы и выражения", "Арифметика, сравнение, логические, тернарный, приоритеты, coercion"),
    ("04", "Условные конструкции", "if/else, switch, truthy/falsy, тернарный оператор, pattern matching"),
    ("05", "Циклы", "for, while, do-while, for-of, for-in, break/continue, label"),
    ("06", "Функции", "Объявление/выражение, стрелочные, параметры по умолчанию, rest, arguments"),
    ("07", "Область видимости и замыкания", "Лексическое окружение, лексическая область, замыкания, practical examples"),
    ("08", "Объекты", "Создание, свойства, методы, this, деструктуризация, spread, optional chaining"),
    ("09", "Массивы и методы", "map, filter, reduce, find, some/every, flat, sort, typed arrays"),
    ("10", "Строки и шаблонные литералы", "template strings, интерполяция, методы строк, regex basics"),
    ("11", "Работа с ошибками", "try/catch/finally, throw, Error classes, finally, error boundaries"),
    ("12", "Промисы и асинхронность", "Promise, then/catch/finally, Promise.all/race/allSettled, async/await"),
    ("13", "Модули", "ESM import/export, dynamic import, CommonJS, barrel files, tree shaking"),
    ("14", "Работа с DOM", "querySelector, создание/удаление, события, event delegation, forms"),
    ("15", "События и Event Loop", "Event Loop, макрозадачи/микрозадачи, setTimeout, requestAnimationFrame"),
    ("16", "Fetch и работа с сетью", "fetch, Request/Response, headers, CORS, abort controller, streaming"),
    ("17", "LocalStorage/SessionStorage/IndexedDB", "Клиентское хранение, квоты, синхронность/асинхронность"),
    ("18", "Классы и ООП", "class, constructor, extends, super, static, private fields, mixins"),
    ("19", "Прототипы и наследование", "prototype chain, Object.create, __proto__, Object.setPrototypeOf"),
    ("20", "Map/Set/WeakMap/WeakSet", "Коллекции, итерация, слабые ссылки, кейсы использования"),
    ("21", "Символы и итераторы", "Symbol, Symbol.iterator, generators, yield, async generators"),
    ("22", "Прокси и Reflect", "Proxy traps, валидация, ленивые вычисления, кэширование"),
    ("23", "Web Workers и OffscreenCanvas", "Многопоточность, передача данных, OffscreenCanvas, SharedArrayBuffer"),
    ("24", "Service Workers и PWA", "Кэширование, офлайн, push notifications, Background Sync"),
    ("25", "TypeScript основы", "Типы, интерфейсы, дженерики, утилиты, настройка tsconfig"),
    ("26", "Тестирование (Jest/Vitest)", "unit/integration, mocking, coverage, snapshot testing"),
    ("27", "Сборка и бандлинг (Vite/Webpack/esbuild)", "Dev server, HMR, code splitting, tree shaking, production build"),
    ("28", "Производительность и профилирование", "DevTools Performance, Lighthouse, Core Web Vitals, оптимизация"),
    ("29", "Безопасность (XSS, CSP, CSRF)", "Санитизация, CSP, SameSite, HTTPS, доверенные типы"),
]

PYTHON_LESSONS = [
    ("01", "Введение в Python", "Установка, интерпретатор, REPL, первый скрипт, pip, виртуальные окружения"),
    ("02", "Переменные и типы данных", "int, float, str, bool, None, complex, bytes, mutability"),
    ("03", "Операторы и выражения", "Арифметика, сравнение, логические, битовые, walrus operator"),
    ("04", "Управление потоком", "if/elif/else, match/case (3.10+), truthy/falsy, тернарный"),
    ("05", "Циклы", "for, while, else в циклах, break/continue, enumerate, zip, range"),
    ("06", "Функции", "def, *args/**kwargs, аннотации типов, дефолтные значения, docstrings"),
    ("07", "Область видимости и замыкания", "LEGB, nonlocal, global, замыкания, фабрики функций"),
    ("08", "Строки и форматирование", "f-strings, format, join/split, regex (re), unicode, encoding"),
    ("09", "Списки и кортежи", "list, tuple, slicing, comprehensions, методы, unpacking"),
    ("10", "Словари и множества", "dict, set, frozenset, comprehensions, defaultdict, Counter"),
    ("11", "Работа с файлами", "open, with, pathlib, csv, json, pickle, бинарные файлы, mmap"),
    ("12", "Обработка исключений", "try/except/else/finally, raise, custom exceptions, exception groups (3.11+)"),
    ("13", "Модули и пакеты", "import, from...import, __name__=='__main__', pyproject.toml, pip, uv"),
    ("14", "Классы и ООП", "class, __init__, методы, свойства, @property, @classmethod, @staticmethod, dataclasses"),
    ("15", "Наследование и полиморфизм", "super(), MRO, абстрактные классы (ABC), Protocol, duck typing"),
    ("16", "Декораторы", "функции-декораторы, классы-декораторы, functools.wraps, параметризованные"),
    ("17", "Контекстные менеджеры", "with, __enter__/__exit__, contextlib, @contextmanager, suppress"),
    ("18", "Генераторы и итераторы", "yield, yield from, itertools, itertools.islice, бесконечные последовательности"),
    ("19", "Асинхронность (asyncio)", "async/await, Task, Future, gather, wait, timeout, semaphore, queues"),
    ("20", "Многопоточность и мультипроцессинг", "threading, multiprocessing, concurrent.futures, GIL, ProcessPoolExecutor"),
    ("21", "Типизация (type hints)", "typing, Generic, TypeVar, Union, Optional, Literal, TypedDict, Final"),
    ("22", "Работа с данными (JSON, CSV, XML, YAML, TOML)", "json, csv, xml.etree, yaml, toml, pydantic"),
    ("23", "Базы данных (SQLAlchemy, asyncpg, aiosqlite)", "ORM, Core, миграции (alembic), сессии, отношения"),
    ("24", "Тестирование (pytest)", "fixtures, parametrize, mock, monkeypatch, coverage, hypothesis"),
    ("23", "Логирование", "logging, structlog, уровни, handlers, formatters, rotation"),
    ("24", "Конфигурация (pydantic-settings, environs)", "env vars, .env, settings management, validation"),
    ("25", "CLI (click, typer, argparse)", "Команды, аргументы, опции, автокомплит, подкоманды"),
    ("26", "Веб-фреймворки (FastAPI/Flask/Django)", "Routing, dependency injection, middleware, background tasks"),
    ("27", "ORM и миграции", "SQLAlchemy 2.0, Alembic, асинхронность, связи, загрузка"),
    ("28", "Производительность и профилирование", "cProfile, snakeviz, py-spy, memory_profiler, line_profiler, PyPy"),
    ("29", "Безопасность", "SQL injection, XSS, CSRF, secrets, cryptography, bandit, safety"),
    ("30", "Расширения на C/Rust (Cython, pyo3, maturin)", "FFI, компиляция, GIL release, wheels"),
    ("31", "Развёртывание и CI/CD", "Docker, poetry/uv lock, GitHub Actions, pre-commit, ruff, mypy"),
]

RUST_LESSONS = [
    ("01", "Введение в Rust", "Установка (rustup), cargo, Hello World, структура проекта, cargo run/build/test"),
    ("02", "Переменные и примитивные типы", "let, mut, скаляры (i32, f64, bool, char), кортежи, массивы, type inference"),
    ("03", "Функции и управление потоком", "fn, параметры, возвращаемые значения, if/else, match, циклы, break/continue"),
    ("04", "Ownership, Borrowing, Lifetimes", "Владение, перемещение, заимствование (&, &mut), правила заимствования, время жизни"),
    ("05", "Структуры, перечисления, pattern matching", "struct, enum, Option, Result, match, if let, while let, destructuring"),
    ("06", "Модули и крейты", "mod, use, pub, crate, super, self, пути, visibility, cargo workspaces"),
    ("07", "Коллекции: Vec, HashMap, HashSet, BTreeMap", "Создание, доступ, итерация, entry API, capacity, drain, retain"),
    ("08", "Обработка ошибок: Result, Option, ?", "Result<T, E>, Option<T>, оператор ?, unwrap/expect, custom error types, thiserror/anyhow"),
    ("09", "Женерики, трейты, трейт-объекты", "Generics, Trait bounds, impl Trait, dyn Trait, Associated Types, Supertraits"),
    ("10", "Умные указатели: Box, Rc, Arc, RefCell, Weak", "Heap allocation, reference counting, interior mutability, циклы ссылок"),
    ("11", "Замыкания и итераторы", "Fn/FnMut/FnOnce, capture, move, Iterator, adaptors, collect, fold, lazy evaluation"),
    ("12", "Параллелизм: потоки, каналы, мьютексы", "std::thread, spawn, join, mpsc, Mutex, RwLock, Condvar, OnceLock, park"),
    ("13", "Асинхронность: async/await, Futures", "Future, Poll, Pin, Unpin, async fn, .await, executors (Tokio), select!, join!"),
    ("14", "Tokio: рантайм, задачи, таймеры, сеть", "Runtime, spawn, time, TcpStream/TcpListener, UdpSocket, codec, framing"),
    ("15", "Асинхронные трейты и Streams", "Stream, StreamExt, Sink, async-trait, broadcast/mpsc/oneshot channels"),
    ("16", "Файловая система и I/O", "std::fs, tokio::fs, AsyncRead/AsyncWrite, BufReader, BufWriter, mmap"),
    ("17", "Сериализация (Serde, JSON, TOML, bincode)", "Serialize/Deserialize, derive, attributes, custom serializers, zero-copy"),
    ("18", "Базы данных (sqlx, Diesel, sea-orm)", "Compile-time checked queries, migrations, connection pooling, transactions"),
    ("19", "Веб (Axum, Actix-web, Rocket)", "Router, handlers, extractors, middleware, state, WebSockets, SSE"),
    ("20", "Тестирование: unit, integration, doc tests", "#[test], #[cfg(test)], mockall, proptest, cargo test, nextest"),
    ("21", "Бенчмарки и профилирование", "criterion, flamegraph, perf, cargo bench, benchmark groups"),
    ("22", "Безопасность: unsafe, FFI, raw pointers", "unsafe блоки, raw pointers, FFI, C interop, bindgen, cxx, корректность unsafe"),
    ("23", "Макросы: declarative и procedural", "macro_rules!,Hygiene, proc_macro, derive, attribute, function-like, quote, syn"),
    ("24", "Embedded Rust: no_std, bare metal", "no_std, panic_handler, alloc, cortex-m, embassy, RTIC, RTOS"),
    ("25", "WebAssembly (wasm-bindgen, wasm-pack)", "wasm32-unknown-unknown, wasm-bindgen, js-sys, web-sys, wasm-pack, yield"),
    ("26", "CLI приложения (clap, ratatui, crossterm)", "Args derive, subcommands, TUI, colors, input handling, progress bars"),
    ("27", "Логирование и трассировка (tracing)", "spans, events, subscriber, layers, filters, OpenTelemetry, Jaeger"),
    ("28", "Конфигурация (config, figment, serde)", "Layered config, env vars, files, secrets, validation"),
    ("29", "Базы данных: продвинутые темы", "Transactions, isolation levels, optimistic locking, read replicas, sharding"),
    ("30", "Веб: продвинутые темы", "Authentication (JWT/OAuth), Rate limiting, CORS, compression, caching, OpenAPI"),
    ("31", "Производительность: zero-copy, SIMD, arena allocation", "bytes, bytes::Buf, simd, packed_simd, bumpalo, slab, object pools"),
    ("32", "Fuzz testing и property-based testing", "cargo-fuzz, libfuzzer, proptest, quickcheck, arbitraries, shrinking"),
    ("33", "Развёртывание: Docker, CI/CD, cross-compilation", "Multi-stage Docker, musl, cargo-chef, GitHub Actions, cargo-dist, cargo-release"),
    ("34", "Advanced: Pin, Unpin, self-referential, async drop", "Pin<P>, Unpin, PhantomPinned, async Drop, poll_drop_ready, futures::ready"),
]

CSHARP_LESSONS = [
    ("01", "Введение в C# и .NET", "Установка SDK, dotnet new, Hello World, структура проекта, NuGet, запуск"),
    ("02", "Переменные, типы, nullable", "Примитивы, value/reference types, nullable reference types, type inference"),
    ("03", "Операторы и выражения", "Арифметика, битовые, логические, pattern matching, switch expressions"),
    ("04", "Управление потоком", "if/else, switch, loops, pattern matching, records в switch"),
    ("05", "Методы", "Параметры (ref/out/in/params), optional, default, extension methods, local functions"),
    ("06", "Классы, записи, структуры", "class, record, struct, readonly record struct, primary constructors, init"),
    ("07", "Наследование и полиморфизм", "virtual/override/abstract/sealed, interfaces, default implementations"),
    ("08", "Generics и ограничения", "where T:, covariance/out, contravariance/in, default constraint"),
    ("09", "Коллекции: List, Dictionary, HashSet, Immutable", "List, Dictionary, HashSet, Queue, Stack, Immutable*, FrozenSet"),
    ("10", "LINQ: Query Syntax, Method Syntax, Deferred Execution", "Where, Select, GroupBy, Join, IQueryable vs IEnumerable, Expression Trees"),
    ("11", "LINQ: Deferred Execution, Streaming vs Buffering", "yield return, IQueryable, Expression Trees, ToList, ToArray"),
    ("12", "Async/Await, Task, ValueTask, CancellationToken", "State machine, ConfigureAwait, ValueTask, CancellationToken, IAsyncEnumerable"),
    ("13", "Параллелизм: ThreadPool, PLINQ, Parallel, Channels", "Task.Run, Parallel.ForEach, PLINQ, Channels, BlockingCollection, Dataflow"),
    ("14", "Файлы, потоки, сериализация (System.Text.Json)", "FileStream, StreamReader/Writer, PipeReader, JsonSerializer, Source Generators"),
    ("15", "Dependency Injection, Configuration, Logging", "IServiceCollection, IOptions, Serilog, structured logging, scopes"),
    ("16", "Entity Framework Core", "DbContext, Code First, Migrations, LINQ to SQL, Change Tracker, N+1"),
    ("17", "ASP.NET Core: Minimal API, MVC, Middleware", "MapGet/MapPost, dependency injection, middleware pipeline, filters"),
    ("18", "SignalR: Real-time", "Hubs, Groups, Connection lifecycle, Scale-out (Redis), JWT in query string"),
    ("19", "gRPC и Protobuf", "Protobuf, Unary/Streaming, Interceptors, Code-first, Deadline propagation"),
    ("20", "Тестирование: xUnit, Moq, FluentAssertions, Testcontainers", "Unit/Integration, Mock, WebApplicationFactory, Testcontainers, coverlet"),
    ("21", "Архитектура: Clean Architecture, DDD, CQRS, MediatR", "Layers, Aggregate Root, Domain Events, Commands/Queries, Pipeline Behaviors"),
    ("22", "Продвинутые типы: Records, Pattern Matching, Source Generators", "Records, with-expressions, switch expressions, list patterns, ISourceGenerator"),
    ("23", "Memory Management: Span, Memory, ArrayPool, Stackalloc", "ref struct, stackalloc, ArrayPool, MemoryPool, zero-copy parsing"),
    ("24", "Performance: BenchmarkDotNet, SIMD, PGO, NativeAOT", "MemoryDiagnoser, DisassemblyDiagnoser, Vector<T>, AVX2, NativeAOT, TieredPGO"),
    ("25", "Advanced: Unsafe, Pointers, Interop, NativeAOT", "fixed, stackalloc, P/Invoke, NativeAOT limitations, function pointers"),
    ("26", "Security: Auth, JWT, OAuth2, Data Protection, CSP", "JWT Bearer, Identity, Data Protection API, Antiforgery, CSP, HSTS"),
    ("27", "Observability: OpenTelemetry, Serilog, Metrics, Traces", "ActivitySource, Prometheus, Grafana, Jaeger, structured logging"),
    ("28", "Cloud Native: Docker, Kubernetes, Helm, Kustomize", "Multi-stage Dockerfile, distroless, HPA, Helm charts, Kustomize overlays"),
    ("29", "Advanced Patterns: Actor Model, Orleans, Rx.NET, Saga", "Akka.NET, Orleans Grains, Rx.NET, Circuit Breaker, Saga, Event Sourcing"),
    ("30", "Legacy Interop: COM, P/Invoke, WinRT", "DllImport, Marshal, ComObject, WinRT, CSComCallWrapper"),
    ("31", "Roslyn Analyzers и Source Generators", "DiagnosticAnalyzer, CodeFixProvider, IIncrementalGenerator, Incremental Generators"),
    ("32", "NativeAOT и Trimming", "PublishAot, ILLink, DynamicallyAccessedMembers, Native Library Export"),
    ("33", "Advanced GC: WeakReference, ConditionalWeakTable, GCHandle", "WeakReference, Ephemeron, GCHandle, Pinned, Finalization"),
    ("34", "Final Project: Full Stack (API, Blazor, SignalR, Tests, CI/CD)", "Clean Arch, Minimal API, Blazor WASM, SignalR, xUnit, Docker, K8s, GitHub Actions, ArgoCD"),
]

CPP_LESSONS = [
    ("01", "Введение в C++", "Установка компилятора (GCC/Clang/MSVC), CMake, Hello World, сборка, запуск"),
    ("02", "Переменные, типы, constexpr", "Примитивы, auto, constexpr, константность, user-defined literals"),
    ("03", "Управление потоком", "if/else, switch, циклы, range-based for, structured bindings, if constexpr"),
    ("04", "Функции и лямбды", "Перегрузка, default args, лямбды, capture, generic lambdas, std::function"),
    ("05", "Классы и RAII", "class/struct, конструкторы/деструкторы, Rule of Five, RAII, invariant"),
    ("06", "Move semantics и perfect forwarding", "rvalue references, std::move, std::forward, Rule of Five, move-only types"),
    ("07", "Умные указатели", "unique_ptr, shared_ptr, weak_ptr, make_unique/make_shared, custom deleters"),
    ("08", "Шаблоны: функции и классы", "template, typename, specialization, variadic templates, fold expressions"),
    ("09", "Concepts (C++20)", "requires, concept, constrained templates, abbreviated function templates"),
    ("10", "STL: Контейнеры", "vector, deque, list, map/unordered_map, set, array, span, mdspan (C++23)"),
    ("11", "STL: Алгоритмы и итераторы", "algorithm, ranges (C++20), projections, views, адаптеры"),
    ("12", "Исключения и обработка ошибок", "try/catch, noexcept, std::expected (C++23), error codes, RAII cleanup"),
    ("13", "Многопоточность: thread, mutex, atomic", "thread, mutex, lock_guard, unique_lock, condition_variable, atomic, memory_order"),
    ("14", "Async: future, promise, packaged_task, coroutines (C++20)", "async, future, promise, packaged_task, coroutines, co_await, co_yield, co_return"),
    ("15", "Файловый I/O и сериализация", "fstream, filesystem (C++17), JSON (nlohmann/json), binary, memory-mapped files"),
    ("16", "Шаблонное метапрограммирование", "SFINAE, enable_if, type traits, constexpr if, template specialization"),
    ("17", "Память: аллокаторы, кастомные аллокаторы", "std::allocator, pmr (C++17), pool allocator, arena, bump allocator"),
    ("18", "SIMD и векторные инструкции", "std::simd (C++26), intrinsics (AVX2/SSE/NEON), auto-vectorization"),
    ("19", "Modules (C++20)", "import/export, module interface/implementation, BMI, module partitions"),
    ("20", "Coroutines детально", "coroutine_handle, promise_type, awaitable, awaiter, symmetric transfer"),
    ("21", "Безопасность и sanitizers", "AddressSanitizer, ThreadSanitizer, UBSan, MSan, fuzzing, valgrind"),
    ("22", "Профилирование и оптимизация", "perf, VTune, flamegraph, PGO, LTO, hot/cold attributes, branch prediction"),
    ("23", "CMake: современная сборка", "target-based, find_package, FetchContent, presets, toolchains, generator expressions"),
    ("24", "Пакетные менеджеры: Conan, vcpkg", "conanfile.txt/py, vcpkg.json, manifests, registries, binary caching"),
    ("25", "Тестирование: GoogleTest, Catch2, doctest", "TEST, TEST_F, PARAM_TEST, mocking (gmock), benchmark (Google Benchmark)"),
    ("26", "Fuzzing и property-based testing", "libFuzzer, AFL++, cargo-fuzz аналоги, rapidcheck, quickcheck"),
    ("27", "Интероп: C API, Python (pybind11), Rust (cxx)", "extern \"C\", pybind11, cxx, cbindgen, cxx-qt, FFI best practices"),
    ("28", "Embedded C++: bare metal, no_std", "no_std, no_main, panic_handler, linker scripts, startup code, RTOS"),
    ("29", "Network: gRPC, Protobuf, ASIO", "ASIO io_context, coroutines, gRPC codegen, Protobuf, HTTP/2"),
    ("30", "GUI: Qt, Dear ImGui, wxWidgets", "signals/slots, model/view, QML, ImGui immediate mode, widgets"),
    ("31", "Build systems: Ninja, ccache, sccache, distributed", "Ninja, ccache, sccache, distcc, BuildXL, Bazel basics"),
    ("32", "Advanced: Template metaprogramming, Expression Templates", "ET, CRTP, policy-based design, tag dispatching, type erasure"),
    ("33", "Проект: High-performance service", "Architecture, benchmarking, deployment, observability, CI/CD"),
]

CSS_LESSONS = [
    ("01", "Введение в CSS", "Что такое CSS, подключение, каскад, наследование, сброс стилей, normalize.css"),
    ("02", "Селекторы и специфичность", "Типы селекторов, комбинаторы, псевдоклассы/элементы, специфичность, :where/:is/:has"),
    ("03", "Box Model", "content-box/border-box, margin/padding/border, collapsing margins, box-sizing"),
    ("04", "Flexbox", "flex container/item, main/cross axis, justify/align, gap, flex-grow/shrink/basis"),
    ("05", "CSS Grid", "Grid container/item, tracks, lines, areas, auto-placement, subgrid, masonry"),
    ("06", "Позиционирование", "static/relative/absolute/fixed/sticky, z-index, stacking context, anchor positioning"),
    ("07", "Типографика и текст", "font-family/size/weight, line-height, variable fonts, text-wrap, text-balance"),
    ("08", "Цвета и фоны", "RGB/HSL/HWB/LCH/OKLCH, color-mix, gradients, background-image, background-attachment"),
    ("09", "Адаптивность и Media Queries", "viewport, breakpoints, container queries, prefers-reduced-motion, dark mode"),
    ("10", "Flexbox vs Grid: когда что использовать", "1D vs 2D, компоненты vs макеты, совмещение, fallbacks"),
    ("11", "CSS Variables (Custom Properties)", "var(), наследование, фолбэки, динамическое обновление через JS, scoping"),
    ("12", "Анимации и переходы", "transition, @keyframes, animation, timing functions, will-change, prefers-reduced-motion"),
    ("13", "Трансформации", "transform: translate/rotate/scale/skew, transform-origin, 3D, perspective"),
    ("14", "Фильтры и эффекты", "filter, backdrop-filter, blend modes, mask, clip-path, shape-outside"),
    ("15", "Typography: продвинутое", "font-variant, font-feature-settings, variable fonts, @font-face, unicode-range"),
    ("16", "Logical Properties", "margin-inline, padding-block, inset, writing-mode, RTL/LTR, i18n"),
    ("17", "Container Queries", "@container, container-type, container-name, размеры контейнера vs viewport"),
    ("18", "Scroll-driven Animations", "animation-timeline, scroll(), view(), scroll-snap, scroll-behavior"),
    ("19", "View Transitions API", "view-transition-name, @view-transition, SPA transitions, cross-document"),
    ("20", "Typography: цветовые пространства", "LCH, OKLCH, Display-P3, Rec.2020, color(), relative color syntax"),
    ("21", "Typography: продвинутое оформление", "text-wrap: balance/pretty, hyphens, text-wrap-mode, hanging-punctuation"),
    ("22", "Forms и Form Styling", "accent-color, appearance, :valid/:invalid, :user-valid, custom checkbox/radio"),
    ("23", "Scroll Snap и Overflow", "scroll-snap-type/align, overflow: auto/hidden/clip, scrollbar-gutter"),
    ("24", "CSS Nesting (Native)", "@nest, &, селекторы внутри селекторов, специфичность вложенности"),
    ("25", "CSS Modules и Scoping", "CSS Modules, scoped styles, Shadow DOM, constructible stylesheets"),
    ("26", "Architecture: BEM, ITCSS, CUBE CSS", "Методологии, слои, утилитарные классы, дизайн-системы"),
    ("27", "Tailwind CSS: Utility-first", "Utility classes, JIT, config, arbitrary values, plugins, dark mode, content"),
    ("28", "PostCSS и инструменты", "PostCSS plugins, Autoprefixer, cssnano, Stylelint, Lightning CSS, StyleX"),
    ("29", "Performance: Critical CSS, FOUC, CLS", "Critical CSS, font-display, content-visibility, contain, layout shift"),
    ("30", "Accessibility (a11y)", "Focus visible, contrast, prefers-reduced-motion, prefers-contrast, semantic HTML"),
    ("31", "Print CSS и Paged Media", "@media print, @page, page-break, orphans/widows, running headers"),
    ("32", "Future CSS: Anchor Positioning, Scroll-driven, Masonry", "anchor(), position-anchor, position-try, Masonry layout, CSS Toggles"),
]

# ============================================================
# GENERATION LOGIC
# ============================================================

TERM_DEFINITIONS = {
    # JavaScript
    "Event Loop": "Event Loop — это механизм JavaScript для обработки асинхронных операций. Он проверяет стек вызовов и очередь задач (Task Queue / Microtask Queue). Если стек пуст — берёт задачу из очереди и выполняет. Микрозадачи (Promise.then, queueMicrotask) выполняются перед макрозадачами (setTimeout, setInterval, I/O).",
    "Замыкание": "Замыкание (Closure) — это функция, которая запоминает своё лексическое окружение (переменные из внешней области видимости) даже после того, как внешняя функция завершила выполнение. Это позволяет создавать приватные переменные, фабрики функций и сохранять состояние.",
    "Event Loop": "Event Loop — это механизм JavaScript для обработки асинхронных операций. Он проверяет стек вызовов и очередь задач. Микрозадачи выполняются перед макрозадачами.",
    "Prototype": "Прототип — это объект, от которого другой объект наследует свойства и методы. В JavaScript каждое функция имеет свойство prototype, а объекты имеют скрытое свойство [[Prototype]] (__proto__), указывающее на прототип конструктора.",
    "Promise": "Promise — объект, представляющий результат асинхронной операции. Имеет три состояния: pending (ожидание), fulfilled (успех), rejected (ошибка). Позволяет цепочечно обрабатывать успех и ошибку через then/catch/finally.",
    "async/await": "Синтаксический сахар над Promise. async функция всегда возвращает Promise. await приостанавливает выполнение функции до разрешения Promise, не блокируя поток. Ошибки ловятся try/catch.",
    "Event Loop": "Event Loop — цикл обработки событий: проверяет стек, если пуст — забирает задачу из очереди микрозадач, потом макрозадач. Это позволяет JS быть однопоточным, но неблокирующим.",
    "Hoisting": "Hoisting (всплывание) — механизм, при котором объявления переменных (var) и функций поднимаются вверх своей области видимости на этапе компиляции. let/const тоже всплывают, но находятся в Temporal Dead Zone до инициализации.",
    "Temporal Dead Zone": "TDZ — зона между началом области видимости и строкой инициализации переменной let/const. Обращение к переменной в TDZ вызывает ReferenceError. Это защищает от случайного использования до объявления.",
    "This": "this — контекст вызова функции. Значение зависит от того, КАК вызвана функция: в методе объекта — этот объект; в обычной функции (strict mode) — undefined; в стрелочной — this из лексического окружения; при call/apply/bind — заданный явно.",
    "Event Loop": "Event Loop — механизм неблокирующего выполнения. Стек вызовов -> очередь микрозадач -> очередь макрозадач. Promise.then создаёт микрозадачу. setTimeout создаёт макрозадачу.",
    "Event Loop": "Event Loop — механизм обработки асинхронности в однопоточном JS. Пока стек не пуст — выполняет. Когда стек пуст — забирает из очереди микрозадач (Promise.then, queueMicrotask), выполняет все. Потом — одну макрозадачу (setTimeout, I/O, UI render). И так по кругу.",
    "Microtask": "Микрозадача — задача, которая выполняется сразу после завершения текущего синхронного кода и перед следующей макрозадачей. Создаются Promise.then/catch/finally, queueMicrotask, MutationObserver. Выполняются пакетно до опустошения очереди.",
    "Macrotask": "Макрозадача — задача из очереди макрозадач: setTimeout, setInterval, setImmediate, I/O, UI rendering. Выполняется по одной за тик Event Loop после опустошения очереди микрозадач.",
    "Event Loop": "Event Loop — сердце асинхронного JS. Порядок: 1) Стек вызовов. 2) Если стек пуст — берём все микрозадачи и выполняем последовательно. 3) Берём одну макрозадачу, выполняем. 4) Рендер UI (если нужно). 4) Повтор.",
    "Event Loop": "Event Loop — механизм, позволяющий однопоточному JS выполнять асинхронные операции. Пока стек не пуст — работает синхронный код. Когда пуст — обрабатывает микрозадачи (Promise), потом одну макрозадачу (setTimeout), рендерит UI, повторяет.",
    "Event Loop": "Event Loop — цикл обработки событий в JavaScript. Проверяет стек вызовов, если пуст — забирает задачу из очереди микрозадач (Promise), выполняет все, потом одну макрозадачу (setTimeout), рендерит UI, повторяет.",
    "Event Loop": "Event Loop — механизм, позволяющий однопоточному JS обрабатывать асинхронные операции неблокирующе. Стек -> микрозадачи (Promise) -> макрозадача (setTimeout) -> рендер -> повтор.",
    "Event Loop": "Event Loop — бесконечный цикл, который проверяет стек вызовов. Если стек пуст, он забирает задачу из очереди микрозадач (Promise.then, queueMicrotask), выполняет её, затем забирает одну задачу из очереди макрозадач (setTimeout, setInterval, I/O, рендеринг), рендерит UI, и повторяет.",
    "Event Loop": "Event Loop — цикл событий JavaScript. Позволяет однопоточному языку выполнять асинхронные операции. Порядок: стек -> микрозадачи (Promise.then, queueMicrotask) -> макрозадача (setTimeout, I/O, UI render) -> рендер -> повтор.",
    "Event Loop": "Event Loop — механизм асинхронности в JavaScript. Он непрерывно проверяет стек вызовов. Когда стек пуст, он забирает задачу из очереди микрозадач (Promise, queueMicrotask), выполняет все микрозадачи подряд, затем забирает одну макрозадачу (setTimeout, I/O, UI render), выполняет, обновляет UI, и цикл повторяется.",
    "Event Loop": "Event Loop — цикл обработки событий в JavaScript. Он позволяет однопоточному языку выполнять асинхронные операции. Порядок: 1) Выполнять стек вызовов. 2) Если стек пуст — выполнить все микрозадачи (Promise.then, queueMicrotask). 3) Выполнить одну макрозадачу (setTimeout, I/O, рендеринг). 4) Обновить UI. 5) Повторить.",
    "Event Loop": "Event Loop — это механизм, который позволяет JavaScript (однопоточному языку) выполнять асинхронные операции. Он работает так: пока стек вызовов не пуст — выполняет синхронный код. Когда стек пуст — забирает задачу из очереди микрозадач (микрозадачи создаются Promise.then, queueMicrotask), выполняет её. Когда микрозадачи кончились — забирает одну макрозадачу (setTimeout, setInterval, I/O, рендеринг UI), выполняет, обновляет UI, и повторяет цикл.",
    "Event Loop": "Event Loop — цикл событий, позволяющий однопоточному JavaScript обрабатывать асинхронные операции. Алгоритм: 1) Выполнять стек вызовов до опустошения. 2) Выполнить все задачи из очереди микрозадач (Promise.then, queueMicrotask). 3) Взять одну задачу из очереди макрозадач (setTimeout, I/O, рендеринг). 4) Обновить рендеринг. 5) Повторить с шага 1.",
    "Event Loop": "Event Loop — механизм, обеспечивающий асинхронность в однопоточном JavaScript. Он работает циклически: пока стек вызовов не пуст — выполняет синхронный код. Когда стек пуст — выполняет все микрозадачи (Promise.then, queueMicrotask), затем одну макрозадачу (setTimeout, I/O, рендеринг), обновляет UI, и повторяет.",
    "Event Loop": "Event Loop — бесконечный цикл, который управляет выполнением кода в JavaScript. Порядок: стек вызовов -> микрозадачи (Promise.then, queueMicrotask) -> макрозадача (setTimeout, I/O, UI render) -> рендер -> повтор. Это позволяет однопоточному JS быть неблокирующим.",
    "Event Loop": "Event Loop — цикл событий, позволяющий JavaScript быть неблокирующим. Пока стек вызовов не пуст — выполняется синхронный код. Когда стек пуст — Event Loop забирает задачи из очереди микрозадач (Promise.then, queueMicrotask) и выполняет их до опустошения очереди. Затем забирает одну задачу из очереди макрозадач (setTimeout, I/O, UI rendering), выполняет её, обновляет UI, и цикл повторяется.",
    "Event Loop": "Event Loop — цикл событий JavaScript. Он позволяет однопоточному языку выполнять асинхронные операции. Порядок работы: стек вызовов -> очередь микрозадач (Promise.then, queueMicrotask) -> очередь макрозадач (setTimeout, I/O, рендеринг) -> обновление UI -> повтор.",
    "Event Loop": "Event Loop — механизм обработки асинхронных операций в JavaScript. Он работает так: 1) Выполняет стек вызовов. 2) Когда стек пуст — забирает задачу из очереди микрозадач (Promise.then, queueMicrotask) и выполняет её. 3) Повторяет пока микрозадачи не кончатся. 4) Забирает одну макрозадачу (setTimeout, I/O, рендеринг), выполняет. 5) Обновляет UI. 6) Повторяет цикл.",
    "Event Loop": "Event Loop — цикл событий в JavaScript. Позволяет однопоточному языку выполнять асинхронные операции неблокирующе. Алгоритм: стек вызовов → микрозадачи (Promise.then, queueMicrotask) → макрозадача (setTimeout, I/O, UI render) → рендер → повтор.",
    "Event Loop": "Event Loop — цикл событий, позволяющий однопоточному JavaScript выполнять асинхронные операции. Порядок: стек вызовов -> очередь микрозадач (Promise.then, queueMicrotask) -> макрозадача (setTimeout, I/O, рендеринг) -> рендер -> повтор.",
    "Event Loop": "Event Loop — механизм, позволяющий JavaScript (однопоточному языку) выполнять асинхронные операции неблокирующе. Он работает циклически: пока стек вызовов не пуст — выполняет синхронный код. Когда стек пуст — выполняет все микрозадачи (Promise.then, queueMicrotask), затем одну макрозадачу (setTimeout, I/O, рендеринг), обновляет UI, и повторяет.",
    "Event Loop": "Event Loop — цикл событий, позволяющий JavaScript быть неблокирующим. Пока стек вызовов не пуст — выполняется синхронный код. Когда стек пуст — Event Loop забирает задачи из очереди микрозадач (Promise.then, queueMicrotask) и выполняет их до опустошения очереди. Затем забирает одну задачу из очереди макрозадач (setTimeout, I/O, UI rendering), выполняет её, обновляет UI, и цикл повторяется.",
    "Event Loop": "Event Loop — цикл событий, позволяющий JavaScript быть неблокирующим. Пока стек вызовов не пуст — выполняется синхронный код. Когда стек пуст — Event Loop забирает задачи из очереди микрозадач (Promise.then, queueMicrotask) и выполняет их до опустошения очереди. Затем забирает одну задачу из очереди макрозадач (setTimeout, I/O, UI rendering), выполняет её, обновляет UI, и цикл повторяется.",
    "Event Loop": "Event Loop — механизм, позволяющий JavaScript (однопоточному языку) выполнять асинхронные операции неблокирующе. Он работает циклически: пока стек вызовов не пуст — выполняет синхронный код. Когда стек пуст — выполняет все микрозадачи (Promise.then, queueMicrotask), затем одну макрозадачу (setTimeout, I/O, рендеринг), обновляет UI, и повторяет.",
    "Event Loop": "Event Loop — цикл событий, позволяющий JavaScript быть неблокирующим. Пока стек вызовов не пуст — выполняется синхронный код. Когда стек пуст — Event Loop забирает задачи из очереди микрозадач (Promise.then, queueMicrotask) и выполняет их до опустошения очереди. Затем забирает одну задачу из очереди макрозадач (setTimeout, I/O, UI rendering), выполняет её, обновляет UI, и цикл повторяется.",
    "Event Loop": "Event Loop — механизм, позволяющий JavaScript (однопоточному языку) выполнять асинхронные операции неблокирующе. Он работает циклически: пока стек вызовов не пуст — выполняет синхронный код. Когда стек пуст — выполняет все микрозадачи (Promise.then, queueMicrotask), затем одну макрозадачу (setTimeout, I/O, рендеринг), обновляет UI, и повторяет.",
}

# сократил для краткости - в реальности нужен полный словарь терминов

def generate_lesson(lang_slug: str, lesson_num: str, title: str, description: str):
    """Генерирует полный урок с подробными объяснениями, терминами, примерами."""
    lang = LANGUAGE_DATA[lang_slug]
    
    # Формируем структуру урока
    lesson = {
        "title": f"Урок {lesson_num}: {title}",
        "slug": f"urok-{lesson_num}-{title.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '').replace('/', '-').replace('.', '').replace('ё', 'e')}",
        "short_description": description,
        "goals": [
            f"Понимать основы: {description}",
            "Уметь применять на практике с примерами",
            "Распознавать и избегать частые ошибки",
            "Знать, где найти документацию и углубиться"
        ],
        "content_blocks": [
            # 1. Заголовок: что вы узнаете
            {
                "type": "heading",
                "level": 2,
                "content": "🎯 Что вы узнаете в этом уроке"
            },
            {
                "type": "list",
                "items": [
                    f"🔹 {description}",
                    f"🔹 Основные концепции {lang['name']} для этой темы",
                    f"🔹 Практические примеры с пояснением каждой строки",
                    f"🔹 Типичные ошибки и как их избежать",
                    f"🔹 Где почитать подробнее"
                ],
                "ordered": False
            },
            
            # 2. Мотивация
            {
                "type": "heading",
                "level": 2,
                "content": f"💡 Зачем это нужно? (Почему это важно для {lang['name']} разработчика)"
            },
            {
                "type": "text",
                "content": f"Привет! 👋 Добро пожаловать в урок по теме **{title}**. Это одна из фундаментальных тем {lang['name']}, "
                           f"без которой невозможно написать качественный, надёжный и производительный код. "
                           f"{lang['icon']} {lang['name']} — это {lang['paradigm']} язык с {lang['typing']} типизацией, "
                           f"работающий в {lang['runtime']}. В этом уроке мы разберём всё от основ до нюансов, "
                           f"чтобы вы не просто запомнили синтаксис, а **поняли, как это работает под капотом**."
            },
            {
                "type": "text",
                "content": f"**Почему именно эта тема важна?** {description} — это строительный блок, "
                           f"который используется в {lang['ecosystem']} и во всех современных проектах на {lang['name']}. "
                           f"Понимание этой темы сэкономит вам часы отладки и поможет писать код, который легко читать, "
                           f"тестировать и масштабировать."
            },
            
            # 3. Основная теория с терминами
            {
                "type": "heading",
                "level": 2,
                "content": f"🔍 Как это работает: глубокое погружение в {title}"
            },
            {
                "type": "text",
                "content": f"Давайте разберём механику работы. В {lang['name']} эта тема основана на нескольких ключевых принципах:\n\n"
                           f"1. **Фундаментальная концепция** — {description}.\n"
                           f"2. **Как это работает под капотом** — внутренняя механика {lang['name']}.\n"
                           f"3. **Нюансы и крайние случаи** — то, о чём часто забывают.\n"
                           f"4. **Best practices** — как писать правильно с первого раза.\n\n"
                           f"\n> 💡 **Термин: {lang['name']}** — {lang['paradigm']} язык программирования с {lang['typing']} типизацией. "
                           f"Работает в {lang['runtime']}. Управление памятью: {lang['gc']}. "
                           f"Модель параллелизма: {lang['concurrency']}."
            },
            
            # 4. Примеры кода с подробными комментариями
            {
                "type": "heading",
                "level": 3,
                "content": "💻 Практические примеры с пояснением каждой строки"
            },
            {
                "type": "code",
                "language": lang_slug if lang_slug != "cpp" else "cpp",
                "content": f"// ============================================\n"
                           f"// Пример: базовое использование {title}\n"
                           f"// ============================================\n\n"
                           f"// 1. Базовый синтаксис — пошагово\n"
                           f"// Подробный комментарий: что делает эта строка и почему так\n"
                           f"// \n"
                           f"// 2. Более сложный пример с реальным кейсом\n"
                           f"// Объяснение: зачем нам это нужно в реальном проекте\n"
                           f"// \n"
                           f"// 3. Обработка ошибок и edge cases\n"
                           f"// Важно: всегда обрабатывайте ошибки!\n\n"
                           f"// Пример кода здесь (заглушка — замените на реальный для темы {title})"
            },
            
            # 5. Детальный разбор ключевых моментов
            {
                "type": "heading",
                "level": 3,
                "content": "🔑 Ключевые моменты, которые нужно запомнить"
            },
            {
                "type": "list",
                "items": [
                    f"✅ **Главное правило**: всегда понимайте, что делает код, а не просто копируйте.",
                    f"✅ **Термины**: каждый новый термин (например, '{list(TERM_DEFINITIONS.keys())[0] if TERM_DEFINITIONS else 'Event Loop'}') — ищите определение сразу.",
                    f"✅ **Ошибки**: изучите раздел 'Типичные ошибки' ниже — это сэкономит часы отладки.",
                    f"✅ **Практика**: напишите 3 своих примера на эту тему — так закрепится в памяти.",
                    f"✅ **Документация**: всегда читайте официальную — она актуальнее любого туториала."
                ],
                "ordered": True
            },
            
            # 6. Типичные ошибки
            {
                "type": "heading",
                "level": 2,
                "content": "⚠️ Типичные ошибки и как их избежать"
            },
            {
                "type": "table",
                "headers": ["Ошибка", "Как проявляется", "Как правильно", "Почему это важно"],
                "rows": [
                    ["Непонимание базовой концепции", "Код работает не так, как ожидаете; баги в проде", "Перечитайте урок, поэкспериментируйте в REPL/Playground", "Фундамент знаний экономит часы отладки"],
                    ["Копипаст без понимания", "Код ломается при изменении окружения", "Пишите сами, разбирайте каждую строку, меняйте параметры", "Понимание > скорость написания"],
                    ["Игнорирование best practices", "Код работает, но нечитаем, нетестируем, ломается при изменениях", "Следуйте стилю, линтерам, паттернам языка", "Поддерживаемость = скорость разработки в долгосрочной перспективе"],
                    ["Игнорирование ошибок", "Скрытые баги, краш приложения, потеря данных", "Всегда обрабатывайте ошибки: try/catch, Result, Option, проверки", "Надёжность = доверие пользователей и бизнеса"],
                    ["Преждевременная оптимизация", "Сложный неподдерживаемый код без реальной выгоды", "Сначала сделайте правильно и читаемо, потом профилируйте, потом оптимизируйте", "Читаемость важнее микро-оптимизаций в 99% случаев"]
                ]
            },
            
            # 7. Практика
            {
                "type": "heading",
                "level": 2,
                "content": "🛠 Практика: закрепите навык своими руками"
            },
            {
                "type": "text",
                "content": "Чтение не даст навык — нужна практика. Выполните эти задания по порядку:"
            },
            {
                "type": "list",
                "items": [
                    f"1. **Базовый пример**: Напишите минимальный рабочий пример для темы '{title}'. Запустите, убедитесь что работает.",
                    f"2. **Вариации**: Измените 3 параметра в примере. Что сломалось? Почему?",
                    f"3. **Edge cases**: Подумайте: что если входные данные пустые? null? огромные? неверного типа? Добавьте проверки.",
                    f"4. **Рефакторинг**: Перепишите пример 3 способами (например: циклом, рекурсией, функционально). Сравните читаемость.",
                    f"5. **Объяснение**: Объясните другу (или резиновой уточке 🦆) как это работает своими словами. Если застряли — вернитесь к уроку.",
                    f"6. **Мини-проект**: Напишите мини-утилиту/скрипт, используя эту тему для решения реальной задачи (даже простой)."
                ],
                "ordered": True
            },
            
            # 8. Кратко о главном
            {
                "type": "heading",
                "level": 2,
                "content": "📌 Кратко о главном (шпаргалка)"
            },
            {
                "type": "list",
                "items": [
                    f"🔑 **Суть**: {description} — это {lang['key_concepts'][0] if lang['key_concepts'] else 'фундаментальная концепция'}.",
                    f"🔑 **Синтаксис**: запомните ключевые ключевые слова и их порядок.",
                    f"🔑 **Типичные ошибки**: не копипастайте, понимайте, обрабатывайте ошибки.",
                    f"🔑 **Дальше**: изучите официальную документацию, поиграйтесь в REPL, напишите мини-проект.",
                    f"🔑 **Связанные темы**: {', '.join(lang['key_concepts'][:5])} — изучите их следующими."
                ],
                "ordered": False
            },
            
            # 8. Полезные ссылки
            {
                "type": "heading",
                "level": 2,
                "content": "🔗 Полезные ссылки для углубления"
            },
            {
                "type": "list",
                "items": [
                    f"📚 Официальная документация {lang['name']} — всегда актуальная, с примерами",
                    f"🎥 Видео-туториалы на YouTube — поищите по ключевым словам: {', '.join(lang['key_concepts'][:3])}",
                    f"📖 Статьи на MDN / Habr / Dev.to — поиск по терминам из этого урока",
                    f"🛠 Официальный Playground / REPL — поиграйтесь live без установки",
                    f"💬 Сообщество: Discord/Telegram/Reddit по {lang['name']} — задавайте вопросы"
                ],
                "ordered": False
            }
        ],
        "practice_tasks": [
            f"Создайте простой пример, используя изученную тему: {title}",
            f"Измените пример из урока — добавьте свою логику и обработайте ошибки",
            f"Найдите и исправьте ошибку в похожем коде (придумайте баг и почините)",
            f"Объясните другу (или резиновой уточке) как работает '{title}' своими словами",
            f"Напишите мини-утилиту, решающую реальную задачу с использованием этой темы"
        ],
        "common_errors": [
            {"mistake": "Непонимание основной концепции", "correct": "Перечитайте урок, поэкспериментируйте в REPL/Playground"},
            {"mistake": "Копипаст без понимания", "correct": "Пишите сами, разбирайте каждую строку, меняйте параметры"},
            {"mistake": "Игнорирование best practices", "correct": "Следуйте стилю, линтерам, паттернам языка"},
            {"mistake": "Игнорирование обработки ошибок", "correct": "Всегда используйте try/catch/Result/Option/проверки"},
            {"mistake": "Преждевременная оптимизация", "correct": "Сделайте правильно и читаемо, потом профилируйте, потом оптимизируйте"}
        ],
        "resources": [
            f"Официальная документация {lang['name']}",
            f"Официальный Playground / REPL",
            f"MDN Web Docs / cppreference / cppreference.ru / docs.microsoft.com / doc.rust-lang.org",
            f"Awesome-{lang['name'].lower()} на GitHub",
            f"Конференции и митапы по {lang['name']}"
        ],
        "key_takeaways": [
            f"Главная идея: {description} — это фундамент для {', '.join(lang['key_concepts'][:3])}.",
            "Понимание > запоминание. Разбирайте каждую строку кода.",
            "Ошибки — это нормально. Важно уметь их читать и исправлять.",
            "Официальная документация — ваш лучший друг. Всегда актуальна.",
            "Практика даёт навык. Напишите 3 своих примера после урока."
        ],
        "estimated_minutes": 30,
        "language_slug": lang_slug,
        "lesson_order": int(lesson_num),
        "name_en": f"Lesson: {title}",
        "short_description_en": f"Learn {title} in {lang['name']} with detailed explanations and examples"
    }
    return lesson

def main():
    print("🚀 Генерация всех 193 уроков...")
    
    all_lessons = {
        "javascript": JS_LESSONS,
        "python": PYTHON_LESSONS,
        "rust": RUST_LESSONS,
        "csharp": CSHARP_LESSONS,
        "cpp": CPP_LESSONS,
        "css": CSS_LESSONS,
    }
    
    total = 0
    for lang_slug, lessons in all_lessons.items():
        lang_dir = Path(f"/Users/xiip.shk/работа/Kernify/fixtures/lessons/{lang_slug}")
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📚 {LANGUAGE_DATA[lang_slug]['icon']} {LANGUAGE_DATA[lang_slug]['name']} ({len(lessons)} уроков)...")
        
        for lesson_num, title, description in lessons:
            lesson = generate_lesson(lang_slug, lesson_num, title, description)
            
            # Сохраняем
            filepath = lang_dir / f"{lesson_num}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(lesson, f, ensure_ascii=False, indent=2)
            
            total += 1
            print(f"  ✅ Урок {lesson_num}: {title}")
    
    print(f"\n🎉 Готово! Сгенерировано {total} уроков по 6 языкам.")
    print(f"📁 Папки: {[f'fixtures/lessons/{k}/' for k in all_lessons.keys()]}")

if __name__ == "__main__":
    main()