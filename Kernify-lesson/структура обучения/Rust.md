# Курс Rust

## 1. Новичок

1.  **Введение:** Rust, installation, Cargo, first program, compilation
    diagnostics.
2.  **Переменные/типы:** `let`, `mut`, numbers, bool, char, tuples,
    arrays, constants.
3.  **Control flow:** `if`, `loop`, `while`, `for`, `break`,
    expressions.
4.  **Функции:** parameters, return types, statements/expressions.
5.  **Ownership/references:** ownership, moves, borrowing,
    mutable/immutable references.
6.  **Strings/collections:** `String`, `&str`, `Vec`, `HashMap`, slices.
7.  **Structs/enums:** `struct`, `impl`, `enum`, `match`, `Option`.
8.  **Errors:** `Result`, `?`, panic, error handling.
9.  **Modules/Cargo:** visibility, packages/crates, dependencies, docs.
10. **Traits/generics basics:** implement traits, generic functions,
    bounds.
11. **Проект:** console app, files, tests, compiler diagnostics.

## 2. Средний уровень

1.  **Ownership глубже:** lifetimes, borrowing, aliasing rules, lifetime
    annotations.
2.  **Типы:** advanced enums, pattern matching, `Option`/`Result`,
    newtype.
3.  **Generics/traits:** bounds, associated types, `where`, trait
    objects.
4.  **Iterators/functional style:** Iterator, adapters/consumers,
    closures, `collect`.
5.  **Architecture:** crates, public APIs, workspaces, dependencies,
    library design.
6.  **Smart pointers:** `Box`, `Rc`, `Arc`, `RefCell`, `Cell`, `Cow`,
    reference cycles.
7.  **Testing:** unit/integration/doc tests, Clippy, debugging, edge
    cases.
8.  **Files/network/serialization:** filesystem, buffered I/O,
    serialization, HTTP clients.
9.  **Async Rust:** `Future`, `async/await`, runtime/executor, async
    I/O, cancellation.
10. **Concurrency:** `Send`, `Sync`, threads, channels, `Mutex`,
    `RwLock`, `Arc`.
11. **Проект:** modular app with network or filesystem capabilities.

## 3. Углублённый уровень

1.  **Memory/ownership:** lifetime elision, variance, Drop, Pin,
    self-referential constraints.
2.  **Advanced traits:** coherence/orphan rules, blanket impls, trait
    objects, GATs, specialization limits.
3.  **Type system:** bounds, PhantomData, marker traits, type-level
    patterns, safe API design.
4.  **Unsafe Rust:** unsafe blocks/functions, raw pointers, safety
    invariants, FFI, Miri.
5.  **Async internals:** Future, poll/waker, Pin, executor/runtime,
    async traits and APIs.
6.  **Concurrency:** memory model, synchronization, atomics, lock-free
    concepts, shared state.
7.  **Macros:** declarative/procedural, derive, token streams,
    debugging.
8.  **Systems programming:** data layout, C FFI, system calls, embedded
    constraints.
9.  **Cargo ecosystem:** workspaces, features, cross-compilation, crate
    publishing, versioning.
10. **Performance/reliability:** benchmarks, allocation profiling,
    unsafe validation, fuzz/property tests.
11. **Проект:** library, systems tool or network service with safety
    guarantees, tests and docs.

**Методика:** pin toolchain/crate versions; explain borrow-checker
diagnostics; separately justify and test unsafe code.
