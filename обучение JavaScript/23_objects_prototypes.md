# Урок 23: Objects & Prototypes — Property Descriptors, Prototype Inheritance, Reflect, Proxy, Private Fields

## 🎯 Цели урока
- Глубоко понять Property Descriptors и Object.defineProperty / Object.getOwnPropertyDescriptors
- Освоить прототипное наследование: `[[Prototype]]`, `Object.create`, `class extends`
- Изучить Reflect API — программные аналоги внутренних операций
- Понять Proxy — перехват фундаментальных операций объекта
- Разобрать Private Fields (`#field`), Private Methods, Private Static Members

---

## 1. Property Descriptors (Атрибуты свойств) — Clause 9.1.6, 10.1.5

### 1.1 Data Property Descriptor
```javascript
// Data Property Descriptor = {
//   [[Value]]: any,
//   [[Writable]]: boolean,
//   [[Enumerable]]: boolean,
//   [[Configurable]]: boolean
// }

// Получение дескриптора:
const obj = { a: 1 };
Object.getOwnPropertyDescriptor(obj, 'a');
// { value: 1, writable: true, enumerable: true, configurable: true }

// Все дескрипторы сразу:
Object.getOwnPropertyDescriptors(obj);
// { a: { value: 1, writable: true, enumerable: true, configurable: true } }

// Установка:
Object.defineProperty(obj, 'b', {
  value: 2,
  writable: false,      // нельзя перезаписать
  enumerable: false,    // не видно в for..in, Object.keys
  configurable: false   // нельзя delete, нельзя изменить дескриптор
});
```

### 1.2 Accessor Property Descriptor
```javascript
// Accessor Property Descriptor = {
//   [[Get]]: function | undefined,
//   [[Set]]: function | undefined,
//   [[Enumerable]]: boolean,
//   [[Configurable]]: boolean
// }

const obj = {
  _value: 0,
  get value() { return this._value; },
  set value(v) { this._value = v * 2; }
};

Object.getOwnPropertyDescriptor(obj, 'value');
// { get: [Function: get value], set: [Function: set value], enumerable: true, configurable: true }

// Нельзя смешивать Data и Accessor дескрипторы!
// Object.defineProperty(obj, 'x', { value: 1, get: () => 2 }) // TypeError
```

### 1.3 Атрибуты детально

| Атрибут | Data | Accessor | Описание |
|---------|------|----------|----------|
| `[[Value]]` | ✅ | ❌ | Значение свойства |
| `[[Writable]]` | ✅ | ❌ | Можно ли изменить `[[Value]]` присваиванием |
| `[[Get]]` | ❌ | ✅ | Функция-геттер (вызывается при чтении) |
| `[[Set]]` | ❌ | ✅ | Функция-сеттер (вызывается при записи) |
| `[[Enumerable]]` | ✅ | ✅ | Видно ли в `for..in`, `Object.keys`, `JSON.stringify` |
| `[[Configurable]]` | ✅ | ✅ | Можно ли `delete`, изменить дескриптор, превратить в accessor |

> **Важно**: `[[Configurable]]: false` — **необратимо** (кроме `[[Writable]]: true → false`)

### 1.4 Object.defineProperties / Object.create с дескрипторами
```javascript
// Массовое определение:
Object.defineProperties(obj, {
  x: { value: 1, writable: true },
  y: { value: 2, writable: false }
});

// Object.create(proto, descriptors) — второй аргумент = descriptors:
const child = Object.create(parent, {
  ownProp: { value: 'mine', enumerable: true }
});
```

---

## 2. Prototype Inheritance (Прототипное наследование)

### 2.1 `[[Prototype]]` internal slot
```javascript
// У каждого объекта есть внутренний слот [[Prototype]] (null или Object)
// Доступ: Object.getPrototypeOf(obj) / obj.__proto__ (legacy, но везде)

// Цепочка прототипов:
const a = { x: 1 };
const b = Object.create(a); // b.[[Prototype]] = a
const c = Object.create(b); // c.[[Prototype]] = b

c.x; // 1 — поиск по цепочке: c → b → a → null
c.hasOwnProperty('x'); // false
'a' in c; // true (включает прототип)
```

### 2.2 Object.create — чистое прототипное наследование
```javascript
// Паттерн "Differential Inheritance"
const animal = {
  breathe() { console.log('breathing'); }
};

const dog = Object.create(animal, {
  bark: { value() { console.log('woof'); }, enumerable: true },
  name: { value: 'Rex', writable: true, enumerable: true }
});

dog.breathe(); // из прототипа
dog.bark();    // собственное
```

### 2.3 `class` syntax — syntactic sugar над прототипами
```javascript
class Animal {
  constructor(name) { this.name = name; }
  speak() { console.log(`${this.name} makes a sound`); }
  static species = 'Animal';
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name);           // вызывает Animal.call(this, name)
    this.breed = breed;
  }
  speak() {
    super.speak();         // вызывает Animal.prototype.speak.call(this)
    console.log(`${this.name} barks`);
  }
  static species = 'Dog';
}

// Что происходит "под капотом":
// Dog.prototype = Object.create(Animal.prototype)
// Dog.prototype.constructor = Dog
// Object.setPrototypeOf(Dog, Animal) // static inheritance
```

### 2.4 `Object.setPrototypeOf` / `Object.getPrototypeOf` vs `__proto__`
```javascript
// Современный способ:
Object.setPrototypeOf(obj, proto); // может быть медленным (инвалидация inline caches)
Object.getPrototypeOf(obj);

// Устаревший, но везде работающий:
obj.__proto__; // getter/setter на Object.prototype

// В class: super — это ссылка на прототип родителя (HomeObject.[[Prototype]])
```

---

## 3. Reflect API — Clause 26.1

### 3.1 Зачем нужен Reflect?
- **Программные аналоги внутренних методов** (`[[Get]]`, `[[Set]]`, `[[HasProperty]]`, `[[DefineOwnProperty]]`, `[[Delete]]`, `[[OwnPropertyKeys]]`, `[[GetPrototypeOf]]`, `[[SetPrototypeOf]]`, `[[IsExtensible]]`, `[[PreventExtensions]]`, `[[Apply]]`, `[[Construct]]`)
- **Возвращают boolean/Completion вместо выбрасывания исключений** (кроме `Reflect.apply/construct`)
- **Правильный `this` для `Proxy` traps**

### 3.2 Основные методы Reflect
```javascript
const obj = { x: 1, y: 2 };

// Property access:
Reflect.get(obj, 'x');           // 1 — как obj.x
Reflect.get(obj, 'x', receiver); // с receiver для proxy
Reflect.set(obj, 'x', 10);       // true/false — как obj.x = 10
Reflect.has(obj, 'x');           // true — как 'x' in obj
Reflect.deleteProperty(obj, 'x'); // true/false — как delete obj.x

// Property definition:
Reflect.defineProperty(obj, 'z', { value: 3, configurable: true });
Reflect.getOwnPropertyDescriptor(obj, 'z');

// Prototype:
Reflect.getPrototypeOf(obj);
Reflect.setPrototypeOf(obj, newProto); // true/false

// Extensibility:
Reflect.isExtensible(obj);
Reflect.preventExtensions(obj); // true/false

// Keys:
Reflect.ownKeys(obj); // ['x', 'y', Symbol(...)] — ВСЕ ключи (включая Symbols, non-enumerable)

// Function calls:
function sum(a, b) { return a + b; }
Reflect.apply(sum, null, [1, 2]); // 3 — как sum.apply(null, [1,2])

// Constructors:
class C { constructor(x) { this.x = x; } }
Reflect.construct(C, [10]); // new C(10) — правильный new.target
```

### 3.3 Reflect + Proxy = правильный `this`
```javascript
const target = { x: 1 };
const handler = {
  get(target, prop, receiver) {
    console.log(`Getting ${prop}`);
    // ВАЖНО: используем Reflect.get для правильного receiver
    return Reflect.get(target, prop, receiver);
  },
  set(target, prop, value, receiver) {
    console.log(`Setting ${prop} = ${value}`);
    return Reflect.set(target, prop, value, receiver);
  }
};

const proxy = new Proxy(target, handler);
proxy.x;     // Getting x → 1
proxy.x = 2; // Setting x = 2 → true
```

---

## 4. Proxy — Clause 26.2

### 4.1 Структура Proxy
```javascript
const proxy = new Proxy(target, handler);

// handler — объект с "traps" (ловушками):
const handler = {
  // Fundamental traps (перехватывают внутренние методы):
  get(target, prop, receiver) { /* ... */ },
  set(target, prop, value, receiver) { /* ... */ },
  has(target, prop) { /* ... */ },              // 'prop' in proxy
  deleteProperty(target, prop) { /* ... */ },   // delete proxy.prop
  defineProperty(target, prop, descriptor) { /* ... */ },
  getOwnPropertyDescriptor(target, prop) { /* ... */ },
  ownKeys(target) { /* ... */ },                // Object.keys, for..in, Reflect.ownKeys
  
  // Prototype traps:
  getPrototypeOf(target) { /* ... */ },
  setPrototypeOf(target, proto) { /* ... */ },
  
  // Extensibility traps:
  isExtensible(target) { /* ... */ },
  preventExtensions(target) { /* ... */ },
  
  // Function traps (только если target — функция):
  apply(target, thisArg, args) { /* ... */ },
  construct(target, args, newTarget) { /* ... */ }
};
```

### 4.2 Invariants (Инварианты) — Proxy не может нарушать
```javascript
// 1. Нельзя вернуть other для non-configurable non-writable свойства:
// target = Object.freeze({ x: 1 });
// handler.get = () => 2; // TypeError!

// 2. ownKeys должен включать все non-configurable own keys
// 3. setPrototypeOf: если target non-extensible, proto должен быть тем же
// 4. preventExtensions: если вернул true, target должен стать non-extensible
// И т.д. — см. Spec 10.5 "Proxy Object Internal Methods and Internal Slots"
```

### 4.3 Практические паттерны Proxy

#### Валидация / наблюдаемые объекты
```javascript
function createObservable(target, onChange) {
  return new Proxy(target, {
    set(target, prop, value, receiver) {
      const oldValue = target[prop];
      const result = Reflect.set(target, prop, value, receiver);
      if (result && oldValue !== value) {
        onChange(prop, value, oldValue);
      }
      return result;
    }
  });
}

const state = createObservable({ count: 0 }, (prop, val, old) => {
  console.log(`${prop}: ${old} → ${val}`);
});
state.count = 1; // count: 0 → 1
```

#### Negative array indices (как в Python)
```javascript
const arr = [1, 2, 3, 4, 5];
const proxy = new Proxy(arr, {
  get(target, prop, receiver) {
    if (typeof prop === 'string' && /^-?\d+$/.test(prop)) {
      const index = Number(prop);
      if (index < 0) prop = String(target.length + index);
    }
    return Reflect.get(target, prop, receiver);
  }
});

proxy[-1]; // 5
proxy[-2]; // 4
```

#### Private fields protection
```javascript
class Secret {
  #password = 'secret123';
  
  check(pwd) { return pwd === this.#password; }
}

const secret = new Secret();
// secret.#password // SyntaxError: Private field
// Proxy НЕ может перехватить доступ к private полям!
```

---

## 5. Private Fields (`#field`) — ES2022 (Class Fields)

### 5.1 Синтаксис и семантика
```javascript
class Counter {
  #count = 0;           // Private instance field
  static #instances = 0; // Private static field
  
  constructor() {
    Counter.#instances++;
  }
  
  increment() { this.#count++; }
  getCount() { return this.#count; }
  static getInstances() { return Counter.#instances; }
}

const c = new Counter();
c.increment();
c.getCount(); // 1
Counter.getInstances(); // 1

// c.#count // SyntaxError: Private field '#count' must be declared in an enclosing class
// Counter.#instances // SyntaxError
```

### 5.2 Private Methods и Accessors
```javascript
class Widget {
  #privateMethod() { return 'internal'; }
  #privateGetter = 42;
  
  get #privateAccessor() { return this.#privateGetter; }
  set #privateAccessor(v) { this.#privateGetter = v; }
  
  publicMethod() {
    return this.#privateMethod(); // OK внутри класса
  }
}
```

### 5.3 Private Static Members
```javascript
class Config {
  static #apiKey = 'default';
  static #cache = new Map();
  
  static setApiKey(key) { Config.#apiKey = key; }
  static getApiKey() { return Config.#apiKey; }
  
  static #compute(key) { /* heavy */ }
  static getCached(key) {
    if (!Config.#cache.has(key)) {
      Config.#cache.set(key, Config.#compute(key));
    }
    return Config.#cache.get(key);
  }
}
```

### 5.4 Private Fields vs Closures vs WeakMap
| Подход | Плюсы | Минусы |
|--------|-------|--------|
| `#private` | Синтаксис, нативная поддержка, работает с `extends`, `instanceof` | Только в классах, нельзя добавить динамически |
| Closures | Работает везде, настоящая приватность | Каждый экземпляр = свои функции (память), нет наследования |
| WeakMap | Настоящая приватность, работает с любыми объектами | Verbose, нужно хранить WeakMap где-то |

### 5.5 Private Fields и наследование
```javascript
class Base {
  #private = 'base';
  getPrivate() { return this.#private; }
}

class Derived extends Base {
  #private = 'derived'; // Отдельный слот!
  getBoth() { return [this.#private, super.getPrivate()]; }
}

const d = new Derived();
d.getBoth(); // ['derived', 'base'] — два разных #private!
```

> **Ключевой момент**: `#private` привязан к **классу**, где объявлен, не к экземпляру. Родитель и ребёнок могут иметь `#x` — это разные слоты.

### 5.6 Private Fields и Proxy
```javascript
class WithPrivate {
  #secret = 42;
  getSecret() { return this.#secret; }
}

const obj = new WithPrivate();
const proxy = new Proxy(obj, {
  get(target, prop) {
    console.log('get', prop);
    return Reflect.get(target, prop);
  }
});

proxy.getSecret(); // 42 — proxy НЕ видит #secret
proxy.#secret;     // SyntaxError (на этапе парсинга)
```

---

## 6. Browser vs Node.js Differences

| Feature | Браузер | Node.js |
|---------|---------|---------|
| **Private Fields** | Full support (ES2022) | Full support (Node 12+) |
| **Proxy** | Full support | Full support |
| **Reflect** | Full support | Full support |
| **Object.getOwnPropertyDescriptors** | Full support | Full support |
| **`__proto__`** | Annex B (required) | Annex B (required) |
| **`Object.setPrototypeOf`** | Full support | Full support |

> Node.js имеет `vm` модуль для изоляции, где `Proxy` и `Reflect` работают одинаково.

---

## 7. Advanced Patterns

### 7.1 Membrane Pattern (Proxy wrapper для изоляции)
```javascript
function createMembrane(target) {
  const membrane = new Proxy(target, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      // Оборачиваем возвращаемые объекты в membrane
      return typeof value === 'object' && value !== null
        ? createMembrane(value)
        : value;
    }
  });
  return membrane;
}
```

### 7.2 Proxy для lazy loading / virtualization
```javascript
function createLazyObject(loader) {
  let initialized = false;
  let target = null;
  
  return new Proxy({}, {
    get(target, prop, receiver) {
      if (!initialized) {
        target = loader();
        initialized = true;
      }
      return Reflect.get(target, prop, receiver);
    }
  });
}

const heavy = createLazyObject(() => {
  console.log('Loading...');
  return { data: [1,2,3], process() { return this.data.map(x => x*2); } };
});

heavy.data; // Loading... → [1,2,3]
```

---

## 8. Упражнения

### Упражнение 1: Property Descriptors
```javascript
// Создайте объект с:
// - readonly свойством (нельзя изменить, нельзя удалить)
// - hidden свойством (не в Object.keys, но доступно)
// - computed свойством (getter без setter)
const config = /* ваш код */;
```

### Упражнение 2: Proxy Invariants
```javascript
// Попробуйте создать Proxy, который нарушает инвариант:
// const frozen = Object.freeze({ x: 1 });
// new Proxy(frozen, { get() { return 2; } }); // TypeError?
// Объясните почему.
```

### Упражнение 3: Private Fields Inheritance
```javascript
// Создайте класс Base с #secret и методом getSecret()
// Создайте класс Derived extends Base с собственным #secret
// Проверьте, что у каждого класса свой #secret
```

---

## 9. Дополнительные ресурсы

- **MDN: Proxy** — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy
- **MDN: Reflect** — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Reflect
- **MDN: Private class fields** — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Private_class_fields
- **Exploring ES6: Proxies** — http://exploringjs.com/es6/ch_proxies.html
- **TC39 Proposal: Class Fields** — https://github.com/tc39/proposal-class-fields

---

## 10. Контрольные вопросы

1. В чём разница между `[[Writable]]: false` и `[[Configurable]]: false`?
2. Почему `Reflect.set` возвращает boolean, а `obj.x = 1` возвращает значение?
3. Как `super` работает в классе с Proxy-наследнике?
4. Может ли Proxy перехватить доступ к `#private` полю? Почему?
5. Что такое "membrane pattern" и зачем он нужен?

---

## 📝 Саммари

| Концепция | Ключевой момент |
|-----------|-----------------|
| **Property Descriptors** | Контролируют поведение свойств: value/writable/enumerable/configurable |
| **Prototype Chain** | `[[Prototype]]` → поиск свойств вверх по цепочке до `null` |
| **Reflect** | Программные аналоги внутренних методов, правильный `receiver` для Proxy |
| **Proxy** | Перехват фундаментальных операций, должен соблюдать инварианты |
| **Private Fields (`#`)** | Привязаны к классу объявления, нативная приватность, не перехватываются Proxy |

---

*Следующий урок: 24 — Functions: lexical environments, this, call/apply/bind, generators, iterators*