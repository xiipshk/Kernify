# Урок 22: ECMAScript / Runtime — Спецификация, типы, абстрактные операции, контексты исполнения, записи окружения

## 🎯 Цели урока
- Понять структуру спецификации ECMAScript и как читать алгоритмы
- Изучить все типы ECMAScript (включая Spec Types: Reference, Completion, Property Descriptor, Environment Record)
- Освоить абстрактные операции (Abstract Operations) — ядро семантики языка
- Глубоко разобрать Execution Contexts, Execution Context Stack, Environment Records
- Понять различия между браузерной и Node.js реализацией runtime

---

## 1. Структура спецификации ECMAScript

### 1.1 Как читать спецификацию
Спецификация ECMAScript (ECMA-262) — это формальное описание языка. Ключевые разделы:
- **Clause 4-5**: Overview, Notation
- **Clause 6**: ECMAScript Data Types and Values
- **Clause 7**: Abstract Operations
- **Clause 8**: Executable Code and Execution Contexts
- **Clause 9**: Ordinary and Exotic Objects Behaviours
- **Clause 10-15**: Built-in Objects, Functions, Modules, etc.

> **Совет**: Используйте [tc39.es/ecma262](https://tc39.es/ecma262/) — актуальная HTML-версия с поиском.

### 1.2 Нотация алгоритмов
Спецификация использует псевдокод с особыми соглашениями:
```javascript
// Пример: ToBoolean(argument) — 7.1.2
// 1. If argument is true, return true.
// 2. Return false.

// Completion Records: { [[Type]]: normal | break | continue | return | throw, [[Value]], [[Target]] }
// ? ReturnIfAbrupt(x) — если x — abrupt completion, вернуть его
// ! Assert — внутреннее утверждение (не проверяется в runtime)
```

---

## 2. Система типов ECMAScript (Clause 6)

### 2.1 ECMAScript Language Types (языковые типы)
```javascript
// Primitive Types (неизменяемые):
undefined, null, boolean, number, bigint, string, symbol

// Object Type (ссылочный, изменяемый):
object

// ES2023+: Symbols as WeakMap keys, #private fields
```

### 2.2 Specification Types (спецификационные типы) — **критически важны для понимания runtime**

| Тип | Назначение | Примеры использования |
|-----|------------|----------------------|
| **Reference** | Результат evaluation identifier/super/import.meta | `x`, `obj.prop`, `super.method()` |
| **Completion Record** | Результат выполнения любого кода | `return`, `throw`, `break`, `continue` |
| **Property Descriptor** | Атрибуты свойства объекта | `[[Value]]`, `[[Writable]]`, `[[Get]]`, `[[Set]]` |
| **Environment Record** | Хранение переменных (лексическое окружение) | `let`, `const`, `function`, `var` |
| **Abstract Closure** | Функция + её лексическое окружение | Замыкания, стрелочные функции |

### 2.3 Reference Type (Ссылочный тип) — ключ к пониманию `this`, `delete`, `typeof`
```javascript
// Reference = { [[Base]]: value | Environment Record, [[ReferencedName]]: string, [[Strict]]: boolean }

// Примеры:
x                    // Reference { base: globalEnv, name: "x", strict: false }
obj.prop             // Reference { base: obj, name: "prop", strict: false }
delete obj.prop      // Использует [[Base]] и [[ReferencedName]]
typeof x             // Special case: не выбрасывает ReferenceError если base = unresolvable
```

---

## 3. Абстрактные операции (Abstract Operations) — Clause 7

### 3.1 Type Conversion (преобразование типов)
```javascript
// ToPrimitive(input, preferredType?) — 7.1.1
// 1. If input is Object, call input[Symbol.toPrimitive](hint)
// 2. Else if preferredType = number: valueOf() -> toString()
// 3. Else: toString() -> valueOf()

// ToNumber(argument) — 7.1.3
// ToString(argument) — 7.1.4
// ToBoolean(argument) — 7.1.2
// ToObject(argument) — 7.1.13 (throws на null/undefined)

// ES2023: ToNumeric (для BigInt support)
```

### 3.2 Property Operations
```javascript
// OrdinaryGetPrototypeOf(O) — 10.1.1
// OrdinarySetPrototypeOf(O, V) — 10.1.2
// OrdinaryGetOwnProperty(O, P) — 10.1.5
// OrdinaryDefineOwnProperty(O, P, Desc) — 10.1.6
// OrdinaryHasProperty(O, P) — 10.1.7
// OrdinaryGet(O, P, Receiver) — 10.1.8
// OrdinarySet(O, P, V, Receiver) — 10.1.9
// OrdinaryDelete(O, P) — 10.1.10
// OrdinaryOwnPropertyKeys(O) — 10.1.11
```

### 3.3 Environment Record Operations (7.3)
```javascript
// Declarative Environment Records (function, block, catch)
//   HasBinding, CreateMutableBinding, CreateImmutableBinding,
//   InitializeBinding, SetMutableBinding, GetBindingValue,
//   DeleteBinding, HasThisBinding, HasSuperBinding, WithBaseObject

// Object Environment Records (with, global)
//   Same + bindings stored in object properties

// Global Environment Record (8.1.1.4)
//   VarNames, LexicalNames, objectRecord, declarativeRecord
```

---

## 4. Execution Contexts (Clause 8)

### 4.1 Структура Execution Context
```javascript
// Execution Context = {
//   [[Function]]: null | function object,        // код, выполняющийся сейчас
//   [[Realm]]: Realm Record,                     // глобальное окружение
//   [[ScriptOrModule]]: Script | Module Record,  // исходный код
//   [[LexicalEnvironment]]: Environment Record,  // для разрешения идентификаторов
//   [[VariableEnvironment]]: Environment Record, // для var/function declarations
//   [[PrivateEnvironment]]: PrivateEnvironment | null, // для #private fields
//   [[Generator]]: GeneratorObject | null,       // для generators
//   [[AsyncContext]]: AsyncContext | null        // для async functions
// }
```

### 4.2 Execution Context Stack (Call Stack)
```javascript
// При запуске скрипта:
// 1. Create Realm -> Global Environment Record -> Global Execution Context
// 2. Push на стек
// 3. При вызове функции: PrepareForOrdinaryCall -> New Execution Context -> Push
// 4. При return/throw: Pop, restore previous context

// Важно: каждый async function / generator имеет свой Execution Context,
// но они могут приостанавливаться (suspend) и возобновляться (resume)
```

### 4.3 LexicalEnvironment vs VariableEnvironment
```javascript
function example() {
  var a = 1;      // VariableEnvironment (Function Environment Record)
  let b = 2;      // LexicalEnvironment (Block Environment Record)
  const c = 3;    // LexicalEnvironment
  
  if (true) {
    var d = 4;    // VariableEnvironment (тоже function-scoped!)
    let e = 5;    // Новый Block Environment Record (child of current LexicalEnvironment)
  }
  
  // d доступна, e — нет
}
```

### 4.4 Environment Records детально

#### Declarative Environment Record (Function, Block, Catch, Module)
```javascript
// Хранит bindings в внутренних слотах, не в объекте
// CreateMutableBinding(name, deletable) — let/const/function
// CreateImmutableBinding(name, strict) — const
// InitializeBinding(name, value) — инициализация (TDZ для const/let)
// SetMutableBinding(name, value, strict) — присваивание
// GetBindingValue(name, strict) — чтение (бросает ReferenceError если uninitialized)
```

#### Object Environment Record (With, Global - legacy)
```javascript
// Bindings хранятся как свойства объекта (bindingObject)
// WithBaseObject() возвращает объект для with
```

#### Global Environment Record (Специальный комбинированный)
```javascript
// Два под-рекорда:
// - objectRecord: var, function declarations (legacy, configurable)
// - declarativeRecord: let, const, class (non-configurable, TDZ)

// GlobalThis — ссылка на global object (window, global, self)
// В браузере: window === globalThis
// В Node.js: global === globalThis (но global !== global object в модулях!)
```

---

## 5. Realm (Реальм) — изолированное глобальное окружение

### 5.1 Структура Realm Record
```javascript
// Realm Record = {
//   [[Intrinsics]]: %ObjectPrototype%, %ArrayPrototype%, ... (встроенные объекты)
//   [[GlobalObject]]: globalThis,
//   [[GlobalEnv]]: Global Environment Record,
//   [[TemplateMap]]: Map для template literals (кэш)
// }

// Важно: каждый iframe / Worker / vm.Context в Node.js — отдельный Realm
// instanceof проверяет прототип в ТЕКУЩЕМ Realm'е
```

### 5.2 Cross-realm взаимодействие
```javascript
// iframe.contentWindow.Array !== Array (разные Realm)
// Array.isArray() работает cross-realm (использует [[Realm]] internal slot)
// Symbol.for() — глобальный реестр символов (cross-realm)
// structuredClone() — клонирование между realms
```

---

## 6. Браузер vs Node.js: ключевые различия Runtime

| Аспект | Браузер | Node.js |
|--------|---------|---------|
| **Global Object** | `window` (WindowProxy) | `global` (но в модулях — `globalThis`) |
| **Global Scope** | `var`/`function` → `window` | `var`/`function` → `global` (но модули изолированы) |
| **Module System** | ES Modules (`.mjs`, `type: module`) | CommonJS (`require`) + ES Modules |
| **Event Loop** | HTML Spec (microtask/macrotask) | libuv (phases: timers, I/O, check, close) |
| **Realm Isolation** | iframe, Worker | `vm` module, Worker Threads |
| **Process/Exit** | `window.close()`, navigation | `process.exit()`, signals |
| **Console** | DevTools Console | `process.stdout/stderr`, TTY detection |

### 6.1 Node.js Module Execution Context
```javascript
// В Node.js (CommonJS) каждый модуль оборачивается:
// (function(exports, require, module, __filename, __dirname) { ... });

// В ES Modules (Node.js 14+):
// - Каждый модуль — отдельный Module Record
// - Свой Module Environment Record
// - import.meta.url доступен
```

---

## 7. Практические примеры и отладка

### 7.1 Визуализация Execution Context Stack
```javascript
function traceContext(label) {
  const stack = new Error().stack;
  console.log(`[${label}] Stack depth: ${stack.split('\n').length - 1}`);
}

function a() { traceContext('a'); b(); }
function b() { traceContext('b'); c(); }
function c() { traceContext('c'); }

a();
// Output показывает вложенность контекстов
```

### 7.2 Проверка TDZ (Temporal Dead Zone)
```javascript
{
  // console.log(x); // ReferenceError: Cannot access 'x' before initialization
  let x = 1;
  console.log(x); // OK
}

// typeof в TDZ:
typeof undeclaredVar; // "undefined" (не выбрасывает)
typeof tdzVar;        // ReferenceError в блоке до let/const
// let tdzVar;
```

### 7.3 Realm detection
```javascript
function isSameRealm(obj, constructor) {
  return obj instanceof constructor; // false если разные realms
}

// Cross-realm array check:
const arr = [];
// В iframe: iframe.contentWindow.Array.isArray(arr) === true
```

---

## 8. ES2023+ изменения в Runtime

### 8.1 Hashbang Grammar (ES2023)
```javascript
#!/usr/bin/env node
// Теперь валидный синтаксис в модулях и скриптах
```

### 8.2 Symbols as WeakMap Keys (ES2023)
```javascript
const wm = new WeakMap();
const sym = Symbol('key');
wm.set(sym, 'value'); // Теперь работает!
```

### 8.3 Array.findLast / findLastIndex (ES2023)
```javascript
// Не меняют runtime, но полезны для алгоритмов
```

---

## 9. Упражнения

### Упражнение 1: Reference Type
```javascript
// Предскажите результат и объясните через Reference Type:
const obj = { foo: 1 };
const ref = obj.foo;
delete obj.foo;
console.log(ref); // ?

// Ответ: 1 (Reference запомнил base и name, но значение прочитано до delete)
```

### Упражнение 2: Environment Records
```javascript
// Создайте функцию, которая возвращает объект с методами
// для чтения/записи переменной, недоступной снаружи
function createPrivateCounter() {
  // Используйте лексическое окружение
}

// Проверьте: counter.get() === 0, counter.increment(), counter.get() === 1
```

### Упражнение 3: Realm Isolation
```javascript
// В браузере: создайте iframe, передайте массив, проверьте instanceof
// В Node.js: используйте vm.createContext()
```

---

## 10. Дополнительные ресурсы

- **ECMA-262 Spec**: https://tc39.es/ecma262/
- **ECMAScript Spec Annotated**: https://github.com/tc39/ecma262
- **JavaScript Engine Fundamentals** (V8, SpiderMonkey, JavaScriptCore): статьи на v8.dev/blog
- **"JavaScript: The Definitive Guide" 7th ed.** — Chapter 3, 8, 13
- **"You Don't Know JS: Scope & Closures"** — Chapter 2, 3, 5

---

## 11. Контрольные вопросы

1. В чём разница между `LexicalEnvironment` и `VariableEnvironment`?
2. Почему `typeof undeclared` не бросает ошибку, а `let x; typeof x;` в TDZ бросает?
3. Что такое Completion Record и зачем он нужен?
4. Как работает `super` в методах классов через лексическое окружение?
5. В чём разница между Realm в браузере (iframe) и Node.js (vm module)?

---

## 📝 Саммари

| Концепция | Суть |
|-----------|------|
| **Specification Types** | Reference, Completion, Property Descriptor, Environment Record — не существуют в runtime, но определяют семантику |
| **Execution Context** | Контейнер для выполнения кода: код + окружение + realm + приватные поля |
| **Environment Record** | Где живут переменные: Declarative (function/block) vs Object (with/global) |
| **Realm** | Изолированный мир с собственными встроенными объектами и globalThis |
| **Abstract Operations** | Атомарные шаги семантики: Get, Set, HasProperty, ToNumber, ToPrimitive... |

---

*Следующий урок: 23 — Objects/Prototypes: property descriptors, prototype inheritance, Reflect, Proxy, private fields*