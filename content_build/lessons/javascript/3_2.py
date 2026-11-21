"""Урок 3.2 курса JavaScript: объекты и прототипы."""

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
    "language": "javascript",
    "program_order": 3,
    "topic_order": 2,
    "name": "3.2. Объекты и прототипы",
    "slug": "javascript-3-2-объекты-и-прототипы",
    "short_description": (
        "Дескрипторы свойств, цепочка прототипов, синтаксис классов как её надстройка, "
        "Reflect, Proxy с инвариантами и приватные поля на уровне спецификации."
    ),
    "topic_name": "Объекты и прототипы",
    "topic_description": (
        "Глубокий разбор объектной модели JavaScript: внутренние слоты [[Prototype]] и [[OwnPropertyKeys]], "
        "атрибуты свойств, алгоритм разрешения имён по цепочке прототипов, метапрограммирование через "
        "Reflect и Proxy и нативная приватность через поля, начинающиеся со знака решётки."
    ),
    "learning_objectives": [
        "Читать и изменять дескрипторы свойств, различать свойства-данные и свойства-аксессоры",
        "Объяснять поиск свойства по цепочке прототипов и роль прототипа в производительности",
        "Строить наследование через Object.create и понимать, во что разворачивается синтаксис class",
        "Использовать Reflect для вызова внутренних методов объекта без потери receiver",
        "Писать Proxy с соблюдением инвариантов и осознавать цену перехвата операций",
        "Применять приватные поля класса и выбирать между ними, замыканиями и WeakMap",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "javascript",
        "объекты",
        "прототипы",
        "proxy",
        "reflect",
        "дескрипторы",
    ],
    "starter_code": code(
        """
        const base = {
          greet() {
            return `Привет, ${this.name}`;
          },
        };

        const user = Object.create(base);
        user.name = "Анна";

        console.log(user.greet());
        console.log(Object.hasOwn(user, "greet"));
        console.log(Object.hasOwn(user, "name"));
        console.log(Object.getPrototypeOf(user) === base);
        """
    ),
    "hints": [
        "Перед изменением свойства проверьте его дескриптор через Object.getOwnPropertyDescriptor. В обычном литерале свойство создаётся изменяемым, перечисляемым и настраиваемым.",
        "Помните, что для чтения свойства интерпретатор проходит всю цепочку прототипов, а для записи создаёт собственное свойство на получателе. Поэтому запись в объект, унаследовавший аксессор, вызывает сеттер.",
        "В ловушках Proxy всегда передавайте аргумент receiver в Reflect.get и Reflect.set. Иначе аксессоры родительского класса получат в this исходную цель, а не сам Proxy.",
        "Приватные поля защищает не движок таблицей свойств, а класс, в котором они объявлены. Наследник не видит приватное поле родителя и не может получить к нему доступ.",
    ],
    "content": [
        text(
            "Объект в JavaScript — это коллекция свойств, у каждого из которых есть имя (ключ) "
            "и значение, а также набор скрытых атрибутов. Почти всё в языке построено "
            "на объектах: массивы, функции, экземпляры классов. Внутренняя операция, которая "
            "извлекает свойство, называется внутренним методом [[Get]], а объект, через который "
            "объекты участвуют в наследовании, называется прототипом, или `[[Prototype]]`.\n\n"
            "Повседневный код редко требует заглядывать в эти слои. Но на продвинутом уровне "
            "именно они объясняют поведение, которое казалось случайным: почему запись "
            "в неизменяемое свойство молча игнорируется, почему метод, скопированный в другой "
            "объект, теряет зависимость от родителя, почему экземпляр класса из другого окна "
            "не проходит проверку instanceof. Урок разбирает объектную модель от дескрипторов "
            "свойств до приватных полей и показывает, как Reflect и Proxy опираются на неё.\n\n"
            "Материал рассчитан на разработчиков, которые уже уверенно пишут классы. Примеры "
            "написаны под стандарт ES2022."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "читать и изменять дескрипторы свойств, различая свойства-данные и свойства-аксессоры;",
            "объяснять поиск свойства по цепочке прототипов и роль этой цепочки в производительности;",
            "строить наследование через `Object.create` и понимать, во что разворачивается синтаксис `class`;",
            "использовать Reflect как программный эквивалент внутренних методов и сохранять `receiver`;",
            "писать Proxy с соблюдением инвариантов и осознавать цену перехвата;",
            "применять приватные поля и выбирать между ними, замыканиями и WeakMap;",
            "избегать ошибок: ложного `instanceof`, копирования методов и деоптимизации из-за `setPrototypeOf`.",
        ),
        heading("Свойства и их атрибуты"),
        text(
            "Свойство описывается дескриптором, property descriptor. В стандарте это "
            "спецификационная запись; `Object.getOwnPropertyDescriptor` возвращает её копию "
            "как обычный объект. Дескриптор свойства-данных, data descriptor, "
            "состоит из `value` и трёх флагов: `writable` — можно ли заменить значение, "
            "`enumerable` — видно ли свойство в `for...in`, `Object.keys` и JSON, "
            "`configurable` — можно ли удалить свойство и изменить дескриптор. Дескриптор свойства-аксессора, или "
            "accessor descriptor, вместо значения содержит функции `get` и `set` и только два "
            "флага, `enumerable` и `configurable`.\n\n"
            "Смешивать оба вида в одном дескрипторе нельзя: попытка передать одновременно `value` "
            "и `get` приводит к TypeError. Флаг `configurable` необратим: после установки false "
            "дескриптор не изменить. Единственное исключение — перевод `writable` из true "
            "в false. Свойства из литерала получают все три флага равными true."
        ),
        example(
            "javascript",
            """
            const config = { retries: 3 };
            console.log(Object.getOwnPropertyDescriptor(config, "retries"));

            Object.defineProperty(config, "endpoint", {
              value: "https://api.example.com",
              writable: false,
              enumerable: false,
              configurable: false,
            });

            config.endpoint = "https://evil.example.com";
            console.log(config.endpoint);
            console.log(Object.keys(config));
            console.log(Object.getOwnPropertyNames(config));
            console.log(Object.getOwnPropertyDescriptor(config, "endpoint").writable);
            """,
        ),
        text(
            "Вывод: объект дескриптора с value: 3, writable: true, enumerable: true, configurable: true; "
            "затем неизменённый адрес https://api.example.com, ключи [\"retries\"], полный список "
            "имён [\"retries\", \"endpoint\"] и false для writable."
        ),
        callout(
            "warning",
            "Молчаливый отказ и строгий режим",
            "Запись в неизменяемое свойство в нестрогом режиме молча игнорируется, а в модуле или классе "
            "та же операция выбрасывает TypeError. Поэтому одна и та же ошибка может не проявляться "
            "в одном файле и падать в другом."
        ),
        heading("Аксессоры и ловушки this"),
        text(
            "Свойство-аксессор не хранит значение, а вычисляет его при каждом чтении и записи. "
            "`defineProperty` даёт полный контроль: можно создать свойство только для чтения, "
            "передав лишь `get`. Геттер получает в `this` объект, "
            "с которого свойство было прочитано. Это объясняет неожиданности с наследованием "
            "и с Proxy.\n\n"
            "Встроенные объекты тоже используют аксессоры. Так устроен `__proto__`: это свойство "
            "на `Object.prototype` с геттером и сеттером, которые читают и меняют слот "
            "`[[Prototype]]`. Приём устарел, а код, где ключом может стать строка "
            "`\"__proto__\"`, уязвим к загрязнению прототипа. Используйте "
            "`Object.getPrototypeOf` и `Object.setPrototypeOf`."
        ),
        example(
            "javascript",
            """
            const temperature = {
              _celsius: 20,
              get celsius() {
                return this._celsius;
              },
              set celsius(value) {
                if (value < -273.15) throw new RangeError("Ниже абсолютного нуля");
                this._celsius = value;
              },
              get fahrenheit() {
                return (this._celsius * 9) / 5 + 32;
              },
            };

            temperature.celsius = 25;
            console.log(temperature.celsius, temperature.fahrenheit);
            console.log(
              Object.getOwnPropertyDescriptor(temperature, "celsius")
            );
            console.log(Object.keys(temperature));
            """,
        ),
        text(
            "Вывод: 25 77; дескриптор с полями get и set как функциями и флагами enumerable: true "
            "и configurable: true; список ключей [\"_celsius\", \"celsius\", \"fahrenheit\"], "
            "потому что аксессоры в литерале тоже перечисляемы."
        ),
        heading("Цепочка прототипов"),
        text(
            "У каждого объекта есть внутренний слот `[[Prototype]]`, значение которого — другой "
            "объект или null. Когда интерпретатор выполняет чтение `obj.key`, он запускает "
            "внутренний метод `[[Get]]`: сначала ищет собственное свойство объекта, а при неудаче "
            "повторяет поиск на прототипе, затем на прототипе прототипа и так до объекта, "
            "у которого прототип равен null. Эта последовательность называется цепочкой "
            "прототипов, а поиск по ней — prototype chain lookup. Запись же устроена иначе: "
            "внутренний метод `[[Set]]` сначала ищет свойство по цепочке, чтобы найти сеттер, "
            "и если сеттера нет, создаёт собственное свойство на объекте-получателе. "
            "Свойства прототипа никогда не изменяются через экземпляр.\n\n"
            "Оператор `in` и цикл `for...in` проверяют всю цепочку, а `Object.hasOwn` "
            "— только сам объект. Первый пример урока показывает разницу: у `user` есть "
            "собственное name, но `greet` живёт на прототипе. Функция `Object.create(null)` "
            "создаёт объект без прототипа — удобный словарь, у которого нет ни одного "
            "унаследованного ключа."
        ),
        example(
            "javascript",
            """
            const animal = { breathe() { return "дышит"; } };
            const dog = Object.create(animal);
            dog.name = "Рекс";

            console.log(dog.breathe());
            console.log(Object.hasOwn(dog, "breathe"));
            console.log("breathe" in dog);
            console.log(Object.getPrototypeOf(dog) === animal);

            const dictionary = Object.create(null);
            dictionary.toString = 1;
            console.log(Object.getPrototypeOf(dictionary));
            console.log("toString" in dictionary);
            """,
        ),
        text(
            "Вывод: дышит; false; true; true; null; true. В последней строке `in` находит "
            "имя toString только потому, что оно было задано явно: у словаря нет прототипа, "
            "и унаследованного метода с таким именем у него нет."
        ),
        heading("Создание объектов и Object.create"),
        text(
            "Литерал `{}` — самый короткий способ создать объект, но он всегда даёт прототип "
            "`Object.prototype`. Функция `Object.create` позволяет задать прототип явно и "
            "дополнительно перечислить собственные свойства через дескрипторы. На ней строится "
            "паттерн дифференциального наследования, differential inheritance: объект описывает "
            "только отличия от прототипа.\n\n"
            "`Object.assign` копирует собственные перечисляемые свойства, а `Object.fromEntries` "
            "собирает объект из пар ключ-значение. `structuredClone` сохраняет данные, но не "
            "функции и не прототип. Полезно помнить, какие операции при создании объекта "
            "вы контролируете: прототип, дескрипторы, перечисляемость."
        ),
        table(
            ["Способ", "Прототип", "Контроль дескрипторов", "Особенность"],
            [
                ["`{ a: 1 }`", "`Object.prototype`", "нет, все флаги true", "коротко"],
                ["`Object.create(proto)`", "задаётся явно, бывает null", "через второй аргумент", "чистое наследование"],
                ["`new Fn()`", "`Fn.prototype`", "нет", "меняет this"],
                ["`Object.assign({}, src)`", "`Object.prototype`", "нет", "только перечисляемые"],
                ["`Object.fromEntries(iter)`", "`Object.prototype`", "нет", "из пар и Map"],
            ],
        ),
        example(
            "javascript",
            """
            const worker = {
              role: "сотрудник",
              describe() {
                return `${this.name} — ${this.role}`;
              },
            };

            const manager = Object.create(worker, {
              role: { value: "руководитель", enumerable: true },
              name: { value: "Ирина", enumerable: true, writable: true },
            });

            console.log(manager.describe());
            console.log(Object.keys(manager));
            console.log(Object.getPrototypeOf(manager) === worker);
            console.log(Object.hasOwn(manager, "describe"));
            """,
        ),
        text(
            "Вывод: Ирина — руководитель; ключи [\"role\", \"name\"]; true; false. Обратите внимание: "
            "без флага writable свойство name создалось бы неизменяемым, а без enumerable "
            "не попало бы в Object.keys."
        ),
        heading("Классы как надстройка над прототипами"),
        text(
            "Синтаксис `class` описывает ту же модель прототипов другой записью. "
            "Методы класса не копируются в экземпляры: они записываются в `Dog.prototype` "
            "с флагами writable и configurable, но не enumerable. Вызов `new Dog()` создаёт "
            "объект, чей `[[Prototype]]` равен `Dog.prototype`, и вызывает конструктор с этим "
            "объектом в `this`. Наследование через `extends` устанавливает два прототипа: "
            "`Dog.prototype` наследует от `Animal.prototype`, а функция Dog — от функции Animal, "
            "чтобы работали статические методы.\n\n"
            "Ключевое слово `super` в методах ищет свойство начиная с прототипа того объекта, "
            "где метод объявлен, а не с прототипа `this`. В конструкторе `super(...)` вызывает "
            "родительский конструктор, а `super.method()` — родительский метод с тем же `this`. "
            "Тело класса всегда выполняется в строгом режиме."
        ),
        example(
            "javascript",
            """
            class Animal {
              constructor(name) {
                this.name = name;
              }
              speak() {
                return `${this.name} издаёт звук`;
              }
              static kind() {
                return "животное";
              }
            }

            class Dog extends Animal {
              #breed;
              constructor(name, breed) {
                super(name);
                this.#breed = breed;
              }
              speak() {
                return `${super.speak()} — гав`;
              }
              get breed() {
                return this.#breed;
              }
            }

            const rex = new Dog("Рекс", "лабрадор");
            console.log(rex.speak());
            console.log(Dog.kind());
            console.log(Object.getPrototypeOf(Dog.prototype) === Animal.prototype);
            console.log(Object.getPrototypeOf(Dog) === Animal);
            console.log(Object.keys(rex));
            """,
        ),
        text(
            "Вывод: Рекс издаёт звук — гав; животное; true; true; [\"name\"]. Свойство breed "
            "не появилось в списке ключей: приватное поле не является обычным свойством и "
            "в перечисление не входит. Два последних значения true подтверждают двойную связь "
            "между наследником и родителем — на уровне прототипов экземпляров и на уровне "
            "статических членов."
        ),
        callout(
            "info",
            "Что именно создаёт extends",
            "`class Dog extends Animal` делает три вещи: устанавливает `Dog.prototype` так, что "
            "его прототип — `Animal.prototype`; устанавливает прототип самой функции Dog в Animal "
            "для наследования статики; и записывает в `Dog.prototype.constructor` ссылку на Dog. "
            "Ручная имитация через `Object.create` должна повторить всё это, иначе instanceof, "
            "super и статические методы работать не будут."
        ),
        heading("Reflect: внутренние методы как функции"),
        text(
            "Reflect — объект из стандарта ES2015, дающий доступ к внутренним методам "
            "объекта в виде обычных функций. `Reflect.get`, `Reflect.set`, `Reflect.has`, "
            "`Reflect.deleteProperty`, `Reflect.defineProperty`, `Reflect.getPrototypeOf`, "
            "`Reflect.ownKeys`, `Reflect.apply` и `Reflect.construct` повторяют операции языка. "
            "Reflect возвращает удобные для проверки значения: `Reflect.set` и "
            "`Reflect.deleteProperty` дают логическое значение вместо исключения или "
            "молчаливого отказа. Важнее другое: часть методов принимает аргумент receiver, "
            "который становится `this` для аксессоров по всей цепочке прототипов.\n\n"
            "`Reflect.ownKeys` возвращает все собственные ключи, включая неперечисляемые "
            "и символьные. `Reflect.construct` позволяет создать объект с заданным `new.target`. "
            "Reflect — естественный спутник Proxy: внутри ловушек вызывают "
            "`Reflect.<метод>` с теми же аргументами, и поведение по умолчанию сохраняется."
        ),
        example(
            "javascript",
            """
            const target = { count: 0 };
            Object.defineProperty(target, Symbol.toStringTag, {
              value: "Counter",
              enumerable: false,
            });

            console.log(Reflect.get(target, "count"));
            console.log(Reflect.set(target, "count", 5));
            console.log(Reflect.has(target, "count"));
            console.log(Reflect.ownKeys(target).length);
            console.log(Reflect.deleteProperty(target, "count"));
            console.log(Reflect.has(target, "count"));

            class Point {
              constructor(x) {
                this.x = x;
              }
            }
            const p = Reflect.construct(Point, [7]);
            console.log(p.x, p instanceof Point);
            """,
        ),
        text(
            "Вывод: 0; true; true; 2 (строка count и символ в Symbol.toStringTag); true; false; "
            "7 true. Обратите внимание, что Object.keys вернул бы только count, а "
            "Reflect.ownKeys видит и неперечисляемый символьный ключ."
        ),
        heading("Proxy: перехват операций"),
        text(
            "Proxy — объект, который оборачивает цель, target, и перехватывает обращения "
            "к ней через набор функций, называемых ловушками, или traps. Ловушки существуют "
            "для тех же операций, что и методы Reflect: `get`, `set`, `has`, `deleteProperty`, "
            "`defineProperty`, `getOwnPropertyDescriptor`, `ownKeys`, `getPrototypeOf`, "
            "`setPrototypeOf`, `isExtensible`, `preventExtensions`, а для функций ещё "
            "`apply` и `construct`. Если ловушки нет, операция передаётся цели без изменений.\n\n"
            "Вызов метода через прокси передаёт в `this` сам прокси, а не цель. Это почти "
            "всегда желаемое поведение, поэтому внутри ловушек используют "
            "`Reflect.get(target, prop, receiver)` и "
            "`Reflect.set(target, prop, value, receiver)`. Аргумент `receiver` — это объект, "
            "с которого шло обращение."
        ),
        example(
            "javascript",
            """
            function observable(target, onChange) {
              return new Proxy(target, {
                set(t, prop, value, receiver) {
                  const old = t[prop];
                  const ok = Reflect.set(t, prop, value, receiver);
                  if (ok && old !== value) onChange(prop, old, value);
                  return ok;
                },
              });
            }

            const state = observable({ count: 0 }, (prop, oldValue, value) => {
              console.log(`${prop}: ${oldValue} -> ${value}`);
            });

            state.count = 1;
            state.count = 1;
            state.count = 5;
            console.log(state.count);
            """,
        ),
        text(
            "Вывод: count: 0 -> 1; count: 1 -> 5; 5. Второе присваивание не вызвало обработчик, "
            "потому что значение не изменилось. Ловушка `set` работает, а ловушки `get` здесь "
            "нет, поэтому чтение `state.count` идёт напрямую к цели."
        ),
        heading("Инварианты Proxy"),
        text(
            "Прокси не может безнаказанно нарушать состояние цели: стандарт задаёт инварианты, "
            "invariants, которые интерпретатор проверяет после каждой ловушки. Если инвариант "
            "нарушен, движок выбрасывает TypeError. Ловушка `get` не может вернуть "
            "другое значение для неконфигурируемого свойства с флагом `writable: false`: "
            "такой объект фактически заморожен. Ловушка `ownKeys` обязана вернуть все "
            "неконфигурируемые собственные ключи цели, `isExtensible` — то же значение, что "
            "`Reflect.isExtensible(target)`, а `preventExtensions` должна действительно "
            "сделать цель нерасширяемой, если вернула true.\n\n"
            "Смысл инвариантов прост: сквозь прокси нельзя обмануть систему безопасности, "
            "которая полагается на замороженные объекты, и нельзя утаить существование "
            "такого свойства. Прокси не позволяет подменить гарантии, которые язык даёт "
            "для цели."
        ),
        example(
            "javascript",
            """
            const frozen = Object.freeze({ version: 1 });
            const liar = new Proxy(frozen, {
              get() {
                return 999;
              },
            });

            try {
              console.log(liar.version);
            } catch (error) {
              console.log(error.name, error.message);
            }

            const open = { a: 1 };
            const selector = new Proxy(open, {
              ownKeys(target) {
                return Reflect.ownKeys(target).filter((key) => key !== "a");
              },
            });

            try {
              Object.keys(selector);
            } catch (error) {
              console.log(error.name);
            }
            """,
        ),
        text(
            "Вывод: TypeError — прокси не может вернуть иное значение для неконфигурируемого "
            "свойства только для чтения; затем снова TypeError. В первом случае нарушен инвариант "
            "ловушки get, во втором ownKeys утаила ключ a, который после Object.freeze "
            "остаётся неконфигурируемым."
        ),
        callout(
            "warning",
            "Цена Proxy",
            "Движок не может применять к прокси те оптимизации, которые применяет к обычным объектам: "
            "форму, скрытые классы и встроенные кэши чтения свойств. Каждое обращение проходит через "
            "ловушку, что замедляет доступ. Прокси уместны на границах систем — наблюдаемость, "
            "валидация, мембраны изоляции, ленивое вычисление, — но не в горячих циклах обработки данных."
        ),
        heading("Приватные поля и выбор инкапсуляции"),
        text(
            "До ES2022 приватность в JavaScript достигалась замыканиями или соглашением о "
            "подчёркивании в имени. В ES2022 появились приватные поля, private fields: имя, "
            "начинающееся со знака решётки, например `#count`. Такое поле не является "
            "обычным свойством: у него нет дескриптора, его не видно в `Object.keys` "
            "и `Reflect.ownKeys`, а синтаксис `obj.#count` вне класса, где поле объявлено, "
            "не парсится. Приватность привязана к объявлению класса: если родитель и наследник "
            "объявят `#secret`, это будут два разных поля.\n\n"
            "Приватные поля можно объявлять со словом `static`. Proxy не перехватывает "
            "доступ к ним: они хранятся не в таблице свойств, а в особом слоте, который "
            "связывает объект с классом. Метод, вызванный через прокси, получит в `this` прокси "
            "и не сможет прочитать приватное поле цели."
        ),
        table(
            ["Подход", "Настоящая приватность", "Память", "Наследование и instanceof"],
            [
                ["`#private`", "да, на уровне класса", "поле на экземпляр", "у каждого класса свой слот"],
                ["Замыкание", "да, на уровне фабрики", "копия методов", "классов нет"],
                ["`WeakMap`", "да, ключ — объект", "запись на экземпляр", "доступ через карту"],
                ["`_underscore`", "нет, соглашение", "обычное свойство", "поле видно и копируется"],
            ],
        ),
        example(
            "javascript",
            """
            class Base {
              #secret = "база";
              readBase() {
                return this.#secret;
              }
            }

            class Derived extends Base {
              #secret = "наследник";
              readBoth() {
                return [this.#secret, super.readBase()];
              }
            }

            class Counter {
              static #active = 0;
              #value = 0;
              constructor() {
                Counter.#active += 1;
              }
              inc() {
                this.#value += 1;
                return this.#value;
              }
              static active() {
                return Counter.#active;
              }
            }

            const d = new Derived();
            console.log(d.readBoth());
            const c = new Counter();
            c.inc();
            c.inc();
            console.log(Counter.active());
            console.log(Object.keys(c));
            console.log("#value" in c);
            """,
        ),
        text(
            "Вывод: [\"наследник\", \"база\"]; 1; []; false. Пустой список ключей и false "
            "в последней строке показывают, что приватное поле не видно извне ни через "
            "перечисление, ни через оператор in."
        ),
        heading("Производительность прототипов"),
        text(
            "Наследование по прототипам — это поиск по цепочке, цена которого зависит "
            "от глубины. За глубину платят не только временем: движки хранят для каждой позиции "
            "доступа информацию о форме объекта и при изменении прототипа сбрасывают кэш. "
            "Поэтому `Object.setPrototypeOf` после создания объекта считается дорогим: "
            "функция, в которой это происходит, может перестать компилироваться в машинный код.\n\n"
            "Практические правила просты. Прототип задавайте при создании через `Object.create` "
            "или через класс. Держите цепочки короткими: обычно один-два уровня над "
            "экземпляром. Не добавляйте свойства в литерал после того, как он уже используется "
            "как прототип. Для методов коллекций не трогайте prototype: храните функции "
            "в объекте или модуле."),
        example(
            "javascript",
            """
            const proto = { base: true };

            const fast = Object.create(proto);
            const slow = {};
            Object.setPrototypeOf(slow, proto);

            console.log(fast.base, slow.base);

            let chain = Object.create(null);
            chain.base = true;
            const deep = Object.create(chain);
            const leaf = Object.create(deep);
            console.log(leaf.base);
            console.log(Object.hasOwn(leaf, "base"));
            """,
        ),
        text(
            "Вывод: true true; true; false. Первые два объекта ведут себя одинаково при чтении, "
            "разница только во внутреннем устройстве и скорости. В последних строках значение "
            "base найдено на втором шаге поиска, но leaf его не содержит: `hasOwn` проверяет "
            "только сам объект."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["Метод скопирован и вызван отдельно", "this равен undefined, выбрасывается TypeError", "Вызывайте `obj.method()` или привяжите `method.bind(obj)`"],
                ["`Object.setPrototypeOf` после создания", "Сбрасываются кэши форм, функция теряет оптимизацию", "Задавайте прототип заранее: `Object.create`, литерал или `class`"],
                ["В ловушке Proxy забыли `receiver`", "Наследуемый геттер получает неверный this", "Передавайте `receiver` в `Reflect.get` и `Reflect.set`"],
                ["`delete` без проверки configurable", "В строгом режиме TypeError", "Используйте `Reflect.deleteProperty` для явного результата"],
                ["Ожидание, что Proxy перехватит `#field`", "Доступ к приватному полю не проходит через ловушки", "Выносите работу с полем в публичный метод"],
            ],
        ),
        heading("Практика"),
        text(
            "Задания выполняются в Node.js или в консоли браузера. Запускайте код после каждого шага."),
        numbered(
            "Создайте объект с тремя свойствами: неизменяемым и неконфигурируемым `version`, неперечисляемым `debug` и вычисляемым геттером `label`, возвращающим строку вида `app v1.0`. Проверьте `Object.keys`, `Object.getOwnPropertyNames` и попытку изменения `version` в строгом режиме.",
            "Постройте цепочку из трёх уровней через `Object.create`: `vehicle` описывает метод `move`, `car` добавляет `wheels`, экземпляр `myCar` — марку. Убедитесь, что `Object.hasOwn` и оператор `in` дают разные ответы для метода.",
            "Создайте класс `Temperature` с приватным полем `#celsius`, геттером `fahrenheit` и сеттером `celsius`, который бракует значения ниже −273.15. Проверьте, что попытка прочитать `#celsius` вне класса невозможна.",
            "Напишите Proxy с ловушками `get` и `has`, который запрещает чтение свойств, начинающихся с подчёркивания, и возвращает `false` для `'_secret' in proxy`. Поясните, какие инварианты пришлось учесть.",
            "Заморозьте объект конфигурации через `Object.freeze`, оберните его в Proxy, который пробует вернуть другое значение, и объясните, почему возникает TypeError.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем отличается свойство-данные от свойства-аксессора?",
            "Что делает флаг configurable и почему его называют необратимым?",
            "Почему запись `obj.x = 1` не изменяет унаследованное свойство прототипа?",
            "Зачем Reflect-методам нужен аргумент receiver?",
            "Какие операции нельзя обойти инвариантами Proxy?",
            "Почему приватное поле, объявленное в базовом и в производном классе с одним именем, даёт два разных значения?",
        ),
        heading("Ответы", 3),
        numbered(
            "Свойство-данные хранит значение с флагом writable; свойство-аксессор хранит функции get и set и вычисляет значение при обращении. Одновременно value и get в одном дескрипторе передавать нельзя.",
            "configurable позволяет удалить свойство и менять его дескриптор. После установки false это состояние нельзя вернуть, потому что менять дескриптор уже не разрешено.",
            "Внутренний метод [[Set]] ищет описание свойства по цепочке ради сеттера, а значение записывает в собственное свойство получателя. Само унаследованное свойство не меняется.",
            "receiver задаёт this для геттеров и сеттеров по всей цепочке прототипов. Без него прокси-обёртка теряла бы this внутри наследуемых аксессоров.",
            "Значение неконфигурируемого свойства с writable: false, список неконфигурируемых собственных ключей в ownKeys, соответствие isExtensible и preventExtensions, перечисляемость существующих ключей в getOwnPropertyDescriptor.",
            "Приватность привязана к объявлению класса, а не к экземпляру. Каждое объявление создаёт отдельный слот, поэтому методы родителя видят только слот родителя, а методы наследника — свой.",
        ),
        heading("Итоги"),
        bullets(
            "Свойство описывается дескриптором: value, writable, enumerable, configurable для данных и get, set, enumerable, configurable для аксессоров.",
            "Чтение проходит по всей цепочке прототипов, запись создаёт собственное свойство получателя, а сеттер на прототипе перехватывает присваивание.",
            "Object.create задаёт прототип явно, class делает то же самое плюс связывает функции конструкторов для наследования статики.",
            "Reflect повторяет внутренние методы, возвращает логические результаты и передаёт receiver, что критично для аксессоров и Proxy.",
            "Proxy перехватывает фундаментальные операции через ловушки, обязан соблюдать инварианты и замедляет доступ из-за отсутствия кэшей.",
            "Приватные поля обеспечивают настоящую приватность на уровне класса, не попадают в перечисление и не проходят через Proxy.",
            "Object.setPrototypeOf после создания объекта дорог: он сбрасывает кэши форм, поэтому прототип задают заранее.",
        ),
        heading("Что дальше"),
        text(
            "Объектная модель объясняет, что происходит после того, как метод найден. Но чтобы "
            "полностью управлять поведением функций, нужно понять лексическое окружение, "
            "правила связывания this, методы call, apply и bind, а также генераторы "
            "и итераторы. Этому посвящён следующий урок «Функции»."),
        heading("Если хотите углубиться"),
        bullets(
            "ECMA-262: раздел 10.1 «Ordinary Object Internal Methods and Internal Slots» — спецификация [[Get]], [[Set]] и дескрипторов",
            "MDN: Object.defineProperty — developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty",
            "MDN: Proxy и инварианты — developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Global_Objects/Proxy",
            "MDN: Приватные поля классов — developer.mozilla.org/ru/docs/Web/JavaScript/Reference/Classes/Private_properties",
            "Axel Rauschmayer, Exploring ES6, глава о прокси — exploringjs.com/es6/ch_proxies.html",
            "V8 Blog: «Fast properties» и оптимизация форм объекта — v8.dev/blog/fast-properties",
        ),
    ],
}
