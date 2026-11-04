# Урок 24: Functions — Lexical Environments, this, call/apply/bind, Generators, Iterators

## 🎯 Цели урока
- Глубоко понять Lexical Environments и замыкания (closures)
- Освоить `this` binding: implicit, explicit, new, arrow functions
- Разобрать `call`, `apply`, `bind` и их внутреннюю реализацию
- Изучить Generators (`function*`), `yield`, `yield*`, async generators
- Понять Iterator и Iterable протоколы, Symbol.iterator

---

## 1. Lexical Environments и Closures (Замыкания)

### 1.1 Lexical Environment (Лексическое окружение) — Spec 8.1
```javascript
// Lexical Environment = {
//   EnvironmentRecord: DeclarativeEnvironmentRecord,
//   Outer: LexicalEnvironment | null
// }

// Каждый блок { }, функция, модуль создаёт новое лексическое окружение
// Outer указывает на родительское окружение (статическая вложенность)
```

### 1.2 Function Object структура
```javascript
// Function Object = {
//   [[Environment]]: LexicalEnvironment,    // замыкание — ссылка на окружение создания
//   [[FormalParameters]]: ParameterList,
//   [[ECMAScriptCode]]: FunctionBody,
//   [[ThisMode]]: lexical | strict | global,
//   [[Strict]]: boolean,
//   [[HomeObject]]: Object | undefined,    // для super
//   [[Call]]: internal method,
//   [[Construct]]: internal method (если не arrow)
// }
```

### 1.3 Замыкание (Closure) = функция + её [[Environment]]
```javascript
function outer(x) {
  const secret = x * 2;
  
  function inner(y) {
    return secret + y; // захватывает secret из outer EnvironmentRecord
  }
  
  return inner;
}

const fn = outer(5); // fn.[[Environment]] → outer's EnvironmentRecord
fn(3); // 13 = 10 + 3

// outer завершился, но его EnvironmentRecord жив, пока жив fn
```

### 1.4 Module Scope как Lexical Environment
```javascript
// module.mjs
export let counter = 0; // в Module Environment Record (Declarative)
export function increment() { counter++; }

// Другой модуль импортирует binding, а не значение!
import { counter, increment } from './module.mjs';
console.log(counter); // 0
increment();
console.log(counter); // 1 — live binding!
```

---

## 2. This Binding (Связывание this)

### 2.1 Четыре типа this binding (Spec 10.2.1)

| Тип | Пример | this value |
|-----|--------|------------|
| **Default** | `func()` | `globalThis` (sloppy) / `undefined` (strict) |
| **Implicit** | `obj.method()` | `obj` |
| **Explicit** | `func.call(obj)`, `func.bind(obj)` | `obj` (первый аргумент) |
| **New** | `new Func()` | свежий объект (`this = Object.create(Func.prototype)`) |

### 2.2 Arrow Functions — Lexical this
```javascript
// Arrow functions НЕ имеют собственного this
// this берётся из ближайшего лексического окружения (EnvironmentRecord)

const obj = {
  method() {
    const arrow = () => this; // this из method()
    return arrow();
  }
};

obj.method() === obj; // true

// Ошибка: нельзя использовать call/apply/bind для изменения this стрелочной функции
const arrow = () => this;
arrow.call({ x: 1 }); // this НЕ изменится!
```

### 2.3 ThisMode в Function Object
```javascript
// [[ThisMode]]: 
// - "lexical" — arrow functions, this из окружения
// - "strict" — strict mode functions, this как передано
// - "global" — sloppy mode functions, this = globalThis если undefined/null

function sloppy() { return this; }
function strict() { 'use strict'; return this; }
const arrow = () => this;

sloppy();        // globalThis
strict();        // undefined
arrow();         // лексическое this
```

---

## 3. call / apply / bind — Внутренняя реализация

### 3.1 Function.prototype.call (Spec 19.2.3.2)
```javascript
// Упрощённый алгоритм:
Function.prototype.call = function (thisArg, ...args) {
  // 1. Let func be this value
  // 2. If IsCallable(func) is false, throw TypeError
  // 3. PrepareForOrdinaryCall(func, undefined) — новый Execution Context
  // 4. Call(func, thisArg, args) — OrdinaryCallBindThis(func, thisArg)
  // 5. Return result
};

// OrdinaryCallBindThis(func, thisArg):
//   if func.[[ThisMode]] === "lexical" → throw TypeError (arrow)
//   if thisArg === undefined/null и func.[[ThisMode]] !== "strict" → globalThis
//   else → thisArg
```

### 3.2 Function.prototype.apply (Spec 19.2.3.1)
```javascript
// Разница с call: второй аргумент — array-like объект
Function.prototype.apply = function (thisArg, argsArray) {
  // 1. Let func be this value
  // 2. If argsArray is null/undefined → args = []
  // 3. Else args = CreateListFromArrayLike(argsArray)
  // 4. Call(func, thisArg, args)
};
```

### 3.3 Function.prototype.bind (Spec 19.2.3.3)
```javascript
// bind создаёт Bound Function Exotic Object
Function.prototype.bind = function (thisArg, ...boundArgs) {
  const target = this;
  if (!IsCallable(target)) throw TypeError;
  
  // Создаёт объект с внутренними слотами:
  // [[BoundTargetFunction]]: target
  // [[BoundThis]]: thisArg
  // [[BoundArguments]]: boundArgs
  
  // При вызове bound function:
  // Call(boundFunc, thisArg, args) →
  //   Call(target, boundThis, [...boundArgs, ...args])
  
  // new boundFunc() →
  //   Construct(target, [...boundArgs, ...args], newTarget)
};

// Важно: bind НЕ работает для arrow functions (у них [[ThisMode]]: lexical)
const arrow = () => this;
const bound = arrow.bind({ x: 1 });
bound(); // this всё равно лексическое!
```

### 3.4 Bound Function Exotic Object
```javascript
function add(a, b) { return a + b; }
const add5 = add.bind(null, 5);

add5(3); // 8 — как add(5, 3)
add5.call({x:1}, 3); // 8 — this игнорируется (boundThis = null)

// new add5(3) → new add(5, 3) → this = новый объект, a=5, b=3
```

---

## 4. Generators (function*)

### 4.1 Синтаксис и базовое поведение
```javascript
function* generator() {
  yield 1;
  yield 2;
  return 3; // значение при done: true
}

const gen = generator();
gen.next(); // { value: 1, done: false }
gen.next(); // { value: 2, done: false }
gen.next(); // { value: 3, done: true }
gen.next(); // { value: undefined, done: true }
```

### 4.2 Generator Object внутренняя структура
```javascript
// Generator Object = {
//   [[GeneratorState]]: "suspendedStart" | "suspendedYield" | "executing" | "completed"
//   [[GeneratorContext]]: ExecutionContext | null,  // сохранённый контекст
//   [[GeneratorBrand]]: "%Generator%",             // для instanceof
//   [[GeneratorPrototype]]: %GeneratorPrototype%
// }

// Generator.prototype = {
//   next(value),
//   return(value),
//   throw(exception),
//   [Symbol.iterator]() { return this; }
// }
```

### 4.3 yield и yield* (делегирование)
```javascript
function* inner() {
  yield 'a';
  yield 'b';
}

function* outer() {
  yield 1;
  yield* inner(); // делегирует к inner
  yield 2;
}

[...outer()]; // [1, 'a', 'b', 2]

// yield* работает с любым iterable:
function* gen() {
  yield* [1, 2, 3];
  yield* new Map([[4, 5]]); // итерирует по entries
}
```

### 4.4 next(value) — передача значения в генератор
```javascript
function* gen() {
  const a = yield 1; // первый next() игнорирует аргумент
  const b = yield a * 2;
  return b * 2;
}

const g = gen();
g.next();     // { value: 1, done: false } — paused на yield 1
g.next(10);   // { value: 20, done: false } — a = 10, yield 20
g.next(5);    // { value: 10, done: true }  — b = 5, return 10
```

### 4.5 return() и throw() — управление генератором
```javascript
function* gen() {
  try {
    yield 1;
    yield 2;
    yield 3;
  } finally {
    console.log('cleanup'); // выполняется при return/throw
  }
}

const g = gen();
g.next();    // { value: 1, done: false }
g.return(99); // { value: 99, done: true } — finally выполнится!
// Output: cleanup

const g2 = gen();
g2.next();
g2.throw(new Error('oops')); // throw внутри генератора на месте yield
// finally тоже выполнится
```

---

## 5. Iterators и Iterables (Протоколы итерации)

### 5.1 Iterator Protocol
```javascript
// Iterator = объект с методом next() возвращающим IteratorResult
// IteratorResult = { value: any, done: boolean }

const iterator = {
  next() {
    if (this.i++ < 3) return { value: this.i, done: false };
    return { value: undefined, done: true };
  },
  i: 0
};
```

### 5.2 Iterable Protocol
```javascript
// Iterable = объект с методом [Symbol.iterator]() возвращающим Iterator

const iterable = {
  [Symbol.iterator]() {
    let i = 0;
    return {
      next() {
        return i < 3 ? { value: i++, done: false } : { value: undefined, done: true };
      }
    };
  }
};

for (const x of iterable) { console.log(x); } // 0, 1, 2
[...iterable]; // [0, 1, 2]
```

### 5.3 Built-in Iterables
```javascript
// Array, String, Map, Set, TypedArray, arguments, NodeList — все iterable
// Object — НЕ iterable (нет Symbol.iterator)

const map = new Map([[1, 'a'], [2, 'b']]);
for (const [k, v] of map) { /* ... */ } // итерирует по entries

// String итерирует по code points (не code units!)
'😀'.length; // 2 (UTF-16 code units)
[...'😀'].length; // 1 (code point)
```

### 5.4 Iterator Helpers (ES2025 / Stage 3)
```javascript
// Array.fromAsync, Iterator.from, iterator methods (map, filter, take, drop, flatMap)
// В Node.js 20+ / браузерах (под флагом или нативно скоро)

const nums = [1, 2, 3, 4, 5];
const doubled = nums.values().map(x => x * 2).toArray(); // [2, 4, 6, 8, 10]

// Lazy evaluation!
function* infinite() { let i = 0; while (true) yield i++; }
infinite().map(x => x * 2).filter(x => x > 10).take(3).toArray(); // [12, 14, 16]
```

---

## 6. Async Generators (ES2018)

### 6.1 Синтаксис
```javascript
async function* asyncGen() {
  yield 1;
  await sleep(100);
  yield 2;
  return 3;
}

const gen = asyncGen();
gen.next(); // Promise<{value: 1, done: false}>
await gen.next(); // { value: 1, done: false }
await gen.next(); // { value: 2, done: false } (после 100ms)
await gen.next(); // { value: 3, done: true }
```

### 6.2 for await...of
```javascript
async function* fetchPages(url) {
  let nextUrl = url;
  while (nextUrl) {
    const response = await fetch(nextUrl);
    const data = await response.json();
    yield data.items;
    nextUrl = data.nextPage;
  }
}

for await (const items of fetchPages('/api/items')) {
  process(items); // обрабатывает страницы по мере загрузки
}
```

### 6.3 Async Iterator Protocol
```javascript
// AsyncIterator = { next(): Promise<IteratorResult> }
// AsyncIterable = { [Symbol.asyncIterator](): AsyncIterator }

// Symbol.asyncIterator для асинхронных источников
```

---

## 7. Advanced Patterns

### 7.1 Coroutines с generators
```javascript
function run(generatorFunc) {
  const gen = generatorFunc();
  
  function step(value) {
    const result = gen.next(value);
    if (result.done) return result.value;
    return Promise.resolve(result.value).then(step);
  }
  
  return step();
}

// Использование:
run(function* () {
  const user = yield fetch('/user').then(r => r.json());
  const posts = yield fetch(`/posts/${user.id}`).then(r => r.json());
  return posts;
}).then(console.log);
```

### 7.2 Trampoline для хвостовой рекурсии
```javascript
function trampoline(fn) {
  return function (...args) {
    let result = fn(...args);
    while (typeof result === 'function') {
      result = result();
    }
    return result;
  };
}

const factorial = trampoline(function* (n, acc = 1) {
  if (n <= 1) return acc;
  yield () => factorial(n - 1, n * acc); // thunk
});

factorial(100000); // Не переполнит стек!
```

### 7.3 Iterable для lazy sequences
```javascript
const fibonacci = {
  [Symbol.iterator]() {
    let [prev, curr] = [0, 1];
    return {
      next() {
        [prev, curr] = [curr, prev + curr];
        return { value: prev, done: false };
      }
    };
  }
};

[...fibonacci].slice(0, 10); // [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

---

## 8. Browser vs Node.js Differences

| Feature | Браузер | Node.js |
|---------|---------|---------|
| **Generators** | Full support | Full support |
| **Async Generators** | Full support | Full support (Node 10+) |
| **for await...of** | Full support | Full support (Node 10+) |
| **Iterator Helpers** | Behind flags / новые версии | Behind flags / новые версии |
| **arguments object** | В sloppy функциях | В sloppy функциях |
| **Tail Call Optimization** | Только Safari (strict mode) | Нет (V8 не реализует) |

> Node.js: `require` не поддерживает top-level await в CommonJS, используйте `.mjs` или `"type": "module"`

---

## 9. Упражнения

### Упражнение 1: Closure & Lexical Environment
```javascript
// Создайте функцию createCounter(), которая возвращает объект
// с методами increment, decrement, getValue
// Используйте замыкание для приватного счётчика
```

### Упражнение 2: this binding
```javascript
const obj = {
  value: 42,
  getValue() { return this.value; }
};

const getValue = obj.getValue;
console.log(getValue()); // ? (strict vs sloppy)

const arrow = () => this.value;
console.log(arrow.call(obj)); // ?
```

### Упражнение 3: Generator delegation
```javascript
// Реализуйте flat() для массива любого уровня вложенности через generator
function* flatten(arr) {
  // ваш код
}

[...flatten([1, [2, [3, 4], 5]])]; // [1, 2, 3, 4, 5]
```

### Упражнение 4: Async iterator
```javascript
// Создайте async iterable, который генерирует числа с задержкой
// Используйте for await...of для потребления
```

---

## 10. Дополнительные ресурсы

- **MDN: Generators** — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Iterators_and_Generators
- **MDN: this** — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this
- **Exploring ES6: Generators** — http://exploringjs.com/es6/ch_generators.html
- **TC39: Iterator Helpers** — https://github.com/tc39/proposal-iterator-helpers
- **"JavaScript Allongé"** — про функции и замыкания

---

## 11. Контрольные вопросы

1. Почему `arrow.call(obj)` не меняет `this` в стрелочной функции?
2. В чём разница между `function*()` и `async function*()`?
3. Что возвращает `yield*` при делегировании к другому генератору?
4. Как работает `bind` с `new` (new boundFunc())?
5. Почему `for await...of` ждёт Promise от `next()`?

---

## 📝 Саммари

| Концепция | Ключевой момент |
|-----------|-----------------|
| **Lexical Environment** | Статическая вложенность, EnvironmentRecord + Outer ссылка |
| **Closure** | Функция + её [[Environment]] (ссылка на лексическое окружение создания) |
| **this** | Определяется в момент ВЫЗОВА (кроме arrow: лексическое) |
| **call/apply/bind** | Явное управление this; bind создаёт Bound Function Exotic Object |
| **Generators** | Приостанавливаемые функции, сохраняют Execution Context в [[GeneratorContext]] |
| **Iterators/Iterables** | Протоколы: next() / [Symbol.iterator](); lazy evaluation |

---

*Следующий урок: 25 — Async Internals: event loop, Promise resolution, cancellation, AbortController, workers, async iterators*