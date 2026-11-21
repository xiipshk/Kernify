"""Урок 3.1 курса Python: метаклассы и дескрипторы."""

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
    "topic_order": 1,
    "name": "3.1. Метаклассы и дескрипторы",
    "slug": "python-3-1-метаклассы-и-дескрипторы",
    "short_description": (
        "Продвинутая объектная модель Python: метаклассы для кастомизации "
        "создания классов и дескрипторы для контроля доступа к атрибутам."
    ),
    "topic_name": "Метаклассы и дескрипторы",
    "topic_description": (
        "Как работают метаклассы (type, __new__, __init__, __prepare__) и "
        "дескрипторы (__get__, __set__, __delete__, __set_name__), и как их "
        "применять для решения архитектурных задач."
    ),
    "learning_objectives": [
        "Объяснять, что класс — это экземпляр метакласса type",
        "Создавать собственные метаклассы через наследование от type",
        "Использовать __new__, __init__ и __prepare__ для изменения создания класса",
        "Реализовывать дескрипторы: data и non-data, с __get__, __set__, __delete__",
        "Применять __set_name__ для автоматического получения имени атрибута",
        "Выбирать между метаклассом, дескриптором и __init_subclass__",
    ],
    "estimated_minutes": 40,
    "xp_reward": 20,
    "difficulty": "advanced",
    "tags": [
        "python",
        "метаклассы",
        "дескрипторы",
        "type",
        "__set_name__",
        "продвинутое ооп",
    ],
    "starter_code": code(
        """
        class MyClass:
            pass

        print(type(MyClass))
        print(isinstance(MyClass, type))
        """
    ),
    "hints": [
        "Класс — это объект, а значит у него есть свой класс: type.",
        "Метакласс перехватывает создание класса, дескриптор — доступ к атрибуту.",
        "__set_name__ вызывается автоматически при создании класса (Python 3.6+).",
    ],
    "content": [
        text(
            "К концу второго уровня вы умеете создавать классы, наследовать их и "
            "контролировать доступ к данным через property. Но Python даёт ещё более "
            "глубокие механизмы: **метаклассы** позволяют вмешиваться в сам процесс "
            "создания классов, а **дескрипторы** — перехватывать любое обращение к "
            "атрибуту экземпляра. Эти инструменты лежат в основе фреймворков вроде "
            "Django ORM, SQLAlchemy, Pydantic и dataclasses."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "понимать, что класс — это экземпляр метакласса type;",
            "создавать метаклассы и перехватывать создание классов через __new__ и __init__;",
            "использовать __prepare__ для кастомизации пространства имён класса;",
            "реализовывать дескрипторы с протоколом __get__, __set__, __delete__;",
            "различать data и non-data дескрипторы и понимать приоритет доступа;",
            "применять __set_name__ для автоматического связывания дескриптора с именем атрибута;",
            "выбирать между метаклассом, дескриптором и __init_subclass__ для конкретной задачи.",
        ),
        heading("Классы — это тоже объекты"),
        text(
            "В Python **всё — объект**, включая сами классы. У каждого объекта есть "
            "тип, который можно узнать через `type()`. Для обычных значений тип — это "
            "класс (int, str, list), а для классов тип — это **type**. То есть "
            "`type` — класс, экземплярами которого являются все классы. Это делает "
            "`type` **метаклассом** — классом классов."
        ),
        example(
            "python",
            """
            class MyClass:
                pass

            print(type(MyClass))           # <class 'type'>
            print(isinstance(MyClass, type))  # True
            print(type(type))              # <class 'type'>
            """,
        ),
        example("text", "<class 'type'>\nTrue\n<class 'type'>"),
        text(
            "Цепочка выглядит так: `MyClass` — экземпляр `type`, а `type` — "
            "экземпляр самого себя. Это не рекурсия, а замыкание системы типов. "
            "Понимание этого факта ключевое: если класс — объект, его можно "
            "создавать программно, менять его структуру до появления экземпляров "
            "и регистрировать в глобальных реестрах."
        ),
        heading("Как создаётся класс"),
        text(
            "Оператор `class` — это синтаксический сахар над вызовом `type`. "
            "Когда интерпретатор видит определение класса, он выполняет три шага: "
            "подготавливает пространство имён (словарь), выполняет тело класса в "
            "этом пространстве, а затем вызывает `type(name, bases, namespace)` "
            "для создания объекта-класса."
        ),
        example(
            "python",
            """
            # Явное создание класса через type
            Foo = type('Foo', (), {'attr': 42})

            print(Foo)
            print(Foo.attr)
            print(type(Foo))
            """,
        ),
        example("text", "<class '__main__.Foo'>\n42\n<class 'type'>"),
        text(
            "Аргументы `type`: имя класса (строка), кортеж базовых классов, словарь "
            "атрибутов. Это знание позволяет создавать классы динамически — "
            "например, на основе конфигурации или схемы базы данных."
        ),
        heading("Метаклассы: кастомизация создания классов"),
        text(
            "**Метакласс** — класс, наследуемый от `type`, который контролирует, "
            "как создаются классы, использующие этот метакласс. Главные точки "
            "вмешательства: `__new__` (создание объекта-класса), `__init__` "
            "(инициализация уже созданного класса), `__prepare__` (подготовка "
            "пространства имён до выполнения тела класса)."
        ),
        heading("Метод __new__"),
        text(
            "`__new__` вызывается **до** создания класса. Он получает метакласс "
            "(`mcs`), имя, базовые классы и словарь атрибутов. Здесь можно "
            "добавить, удалить или изменить атрибуты, а затем передать управление "
            "родительскому `type.__new__` для фактического создания класса."
        ),
        example(
            "python",
            """
            class VerboseMeta(type):
                def __new__(mcs, name, bases, namespace):
                    print(f"Создаём класс: {name}")
                    print(f"  Базовые классы: {bases}")
                    print(f"  Атрибуты: {list(namespace.keys())}")
                    # Добавляем атрибут ко всем классам с этим метаклассом
                    namespace['class_id'] = id(namespace)
                    return super().__new__(mcs, name, bases, namespace)

            class User(metaclass=VerboseMeta):
                name = "Аноним"

                def greet(self):
                    return f"Привет, {self.name}"

            print(f"class_id: {User.class_id}")
            """,
        ),
        example(
            "text",
            "Создаём класс: User\n"
            "  Базовые классы: ()\n"
            "  Атрибуты: ['__module__', '__qualname__', 'name', 'greet']\n"
            "class_id: 140123456789",
        ),
        heading("Метод __init__"),
        text(
            "`__init__` вызывается **после** создания класса. Класс уже существует, "
            "и можно выполнять дополнительные действия: регистрацию, проверки, "
            "настройку. В отличие от `__new__`, здесь `cls` — уже готовый класс."
        ),
        example(
            "python",
            """
            class RegistryMeta(type):
                registry = {}

                def __init__(cls, name, bases, namespace):
                    super().__init__(name, bases, namespace)
                    if name != 'BaseModel':
                        RegistryMeta.registry[name] = cls
                        print(f"Зарегистрирован: {name}")

            class BaseModel(metaclass=RegistryMeta):
                pass

            class User(BaseModel):
                pass

            class Order(BaseModel):
                pass

            print(RegistryMeta.registry)
            """,
        ),
        example(
            "text",
            "Зарегистрирован: User\n"
            "Зарегистрирован: Order\n"
            "{'User': <class '__main__.User'>, 'Order': <class '__main__.Order'>}",
        ),
        heading("Метод __prepare__ (Python 3+)"),
        text(
            "`__prepare__` вызывается **до** выполнения тела класса и возвращает "
            "объект, который станет пространством имён (namespace). По умолчанию это "
            "обычный `dict`, но можно вернуть `OrderedDict` для сохранения порядка "
            "объявления атрибутов или любой другой отображение. Это полезно для "
            "декларативных API, где порядок полей важен (формы, ORM, сериализация)."
        ),
        example(
            "python",
            """
            from collections import OrderedDict

            class OrderedFieldsMeta(type):
                @classmethod
                def __prepare__(mcs, name, bases):
                    return OrderedDict()

                def __new__(mcs, name, bases, namespace):
                    cls = super().__new__(mcs, name, bases, dict(namespace))
                    cls._field_order = [
                        k for k in namespace.keys()
                        if not k.startswith('__')
                    ]
                    return cls

            class Form(metaclass=OrderedFieldsMeta):
                username = "text"
                email = "email"
                age = "number"
                bio = "textarea"

            print(Form._field_order)
            """,
        ),
        example("text", "['username', 'email', 'age', 'bio']"),
        text(
            "Без `__prepare__` порядок атрибутов в обычном `dict` не гарантирован "
            "(хотя в CPython 3.7+ словарь сохраняет порядок вставки, полагаться на "
            "это в метаклассах непереносимо). `OrderedDict` даёт гарантию."
        ),
        heading("Практические примеры метаклассов"),
        heading("Singleton метакласс", 3),
        text(
            "Паттерн **Singleton** гарантирует, что у класса только один экземпляр. "
            "Метакласс перехватывает вызов класса (`__call__`) и возвращает уже "
            "созданный экземпляр, если он есть."
        ),
        example(
            "python",
            """
            class SingletonMeta(type):
                _instances = {}

                def __call__(cls, *args, **kwargs):
                    if cls not in cls._instances:
                        cls._instances[cls] = super().__call__(*args, **kwargs)
                    return cls._instances[cls]

            class Database(metaclass=SingletonMeta):
                def __init__(self):
                    self.connected = False
                    print("Инициализация подключения...")

                def connect(self):
                    self.connected = True

            db1 = Database()
            db2 = Database()
            print(f"Один объект: {db1 is db2}")
            db1.connect()
            print(f"db2 connected: {db2.connected}")
            """,
        ),
        example(
            "text",
            "Инициализация подключения...\n"
            "Один объект: True\n"
            "db2 connected: True",
        ),
        heading("Автоматическая регистрация плагинов", 3),
        text(
            "Метакласс может автоматически собирать все подклассы в реестр. Это "
            "база для плагинных систем, обработчиков команд, маршрутизаторов."
        ),
        example(
            "python",
            """
            class PluginMeta(type):
                plugins = {}

                def __new__(mcs, name, bases, namespace):
                    cls = super().__new__(mcs, name, bases, namespace)
                    if name != 'BasePlugin' and 'handle' in namespace:
                        PluginMeta.plugins[name] = cls
                    return cls

            class BasePlugin(metaclass=PluginMeta):
                pass

            class AuthPlugin(BasePlugin):
                def handle(self, request):
                    return f"Auth: {request}"

            class CachePlugin(BasePlugin):
                def handle(self, request):
                    return f"Cache: {request}"

            print("Плагины:", list(PluginMeta.plugins.keys()))
            for name, plugin_cls in PluginMeta.plugins.items():
                print(plugin_cls().handle("test"))
            """,
        ),
        example(
            "text",
            "Плагины: ['AuthPlugin', 'CachePlugin']\n"
            "Auth: test\n"
            "Cache: test",
        ),
        heading("Валидация атрибутов класса", 3),
        text(
            "Метакласс может проверять корректность объявления класса до того, как "
            "он будет создан. Если проверка не проходит — выбрасывается исключение "
            "на этапе импорта модуля."
        ),
        example(
            "python",
            """
            class ValidatedMeta(type):
                def __new__(mcs, name, bases, namespace):
                    for key, value in namespace.items():
                        if key.startswith('MAX_') and not isinstance(value, int):
                            raise TypeError(
                                f"{key} в классе {name} должен быть int, "
                                f"получен {type(value).__name__}"
                            )
                    return super().__new__(mcs, name, bases, namespace)

            class Config(metaclass=ValidatedMeta):
                MAX_USERS = 100
                MAX_CONNECTIONS = 50

            # class BadConfig(metaclass=ValidatedMeta):
            #     MAX_SIZE = "big"  # TypeError при импорте!
            """,
        ),
        heading("Дескрипторы: протокол доступа к атрибутам"),
        text(
            "**Дескриптор** — объект, реализующий хотя бы один из методов "
            "`__get__`, `__set__`, `__delete__`. Когда такой объект является "
            "атрибутом **класса** (не экземпляра), Python вызывает соответствующий "
            "метод при любом обращении к этому атрибуту через экземпляр. Это "
            "механизм, на котором строятся `property`, `classmethod`, "
            "`staticmethod` и поля ORM."
        ),
        heading("Базовый дескриптор", 3),
        text(
            "Методы протокола:\n"
            "- `__get__(self, obj, objtype=None)` — чтение атрибута. "
            "`obj` — экземпляр (или `None` при обращении через класс), "
            "`objtype` — класс экземпляра.\n"
            "- `__set__(self, obj, value)` — запись атрибута.\n"
            "- `__delete__(self, obj)` — удаление атрибута (`del obj.attr`)."
        ),
        example(
            "python",
            """
            class TracingDescriptor:
                def __init__(self, initial=None):
                    self.value = initial

                def __get__(self, obj, objtype=None):
                    print(f"  __get__: obj={obj}, type={objtype}")
                    return self.value

                def __set__(self, obj, value):
                    print(f"  __set__: obj={obj}, value={value}")
                    self.value = value

                def __delete__(self, obj):
                    print(f"  __delete__: obj={obj}")
                    del self.value

            class MyClass:
                attr = TracingDescriptor(10)

            obj = MyClass()
            print("Чтение:")
    print(obj.attr)
            print("Запись:")
    obj.attr = 42
            print("Удаление:")
    del obj.attr
            """,
        ),
        example(
            "text",
            "Чтение:\n"
            "  __get__: obj=<__main__.MyClass object at 0x...>, type=<class '__main__.MyClass'>\n"
            "10\n"
            "Запись:\n"
            "  __set__: obj=<__main__.MyClass object at 0x...>, value=42\n"
            "Удаление:\n"
            "  __delete__: obj=<__main__.MyClass object at 0x...>",
        ),
        heading("Метод __set_name__ (Python 3.6+)", 3),
        text(
            "`__set_name__(self, owner, name)` вызывается **автоматически** при "
            "создании класса для каждого дескриптора, найденного в теле класса. "
            "`owner` — класс-владелец, `name` — имя атрибута в классе. Это "
            "убирает необходимость передавать имя вручную и позволяет дескриптору "
            "генерировать уникальное имя для хранения в `obj.__dict__`."
        ),
        example(
            "python",
            """
            class ValidatedField:
                def __init__(self, validator=None):
                    self.validator = validator
                    self.name = None
                    self.storage_name = None

                def __set_name__(self, owner, name):
                    self.name = name
                    self.storage_name = f'_validated_{name}'

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self
                    return getattr(obj, self.storage_name, None)

                def __set__(self, obj, value):
                    if self.validator and not self.validator(value):
                        raise ValueError(
                            f"Невалидное значение для {self.name}: {value}"
                        )
                    setattr(obj, self.storage_name, value)

            class User:
                name = ValidatedField(lambda x: len(x) > 0)
                age = ValidatedField(lambda x: isinstance(x, int) and 0 <= x <= 150)

            u = User()
            u.name = "Анна"
            u.age = 25
            print(f"name: {u.name}, age: {u.age}")

            try:
                u.age = -5
            except ValueError as e:
                print(f"Ошибка: {e}")
            """,
        ),
        example(
            "text",
            "name: Анна, age: 25\n"
            "Ошибка: Невалидное значение для age: -5",
        ),
        text(
            "Обратите внимание: дескриптор хранит значение в `__dict__` экземпляра "
            "под сгенерированным именем (`_validated_name`, `_validated_age`). "
            "Если хранить значение в самом дескрипторе (`self.value`), оно станет "
            "общим для **всех** экземпляров класса — типичная ошибка."
        ),
        heading("Data и non-data дескрипторы", 3),
        text(
            "**Data descriptor** (дескриптор данных) — имеет `__set__` или "
            "`__delete__`. **Non-data descriptor** (не-данные) — только "
            "`__get__`. Разница в приоритете:\n"
            "1. Data descriptor в классе побеждает `__dict__` экземпляра.\n"
            "2. Non-data descriptor в классе проигрывает `__dict__` экземпляра — "
            "если в `__dict__` есть ключ с таким именем, дескриптор не вызывается.\n"
            "3. Обычный атрибут в `__dict__` экземпляра имеет высший приоритет "
            "над non-data дескриптором."
        ),
        example(
            "python",
            """
            class DataDescriptor:
                def __get__(self, obj, objtype=None):
                    return "data descriptor"

                def __set__(self, obj, value):
                    obj._value = value

            class NonDataDescriptor:
                def __get__(self, obj, objtype=None):
                    return "non-data descriptor"

            class Test:
                data = DataDescriptor()
                non_data = NonDataDescriptor()

            t = Test()
            t.data = 10
            t.non_data = "ignored"  # запишется в __dict__!

            print(f"data: {t.data}")
            print(f"non_data: {t.non_data}")
            print(f"__dict__: {t.__dict__}")

            # Перекрываем non-data через __dict__
            t.__dict__['non_data'] = "from dict"
            print(f"non_data после перекрытия: {t.non_data}")

            # Data descriptor НЕ перекрывается
            t.__dict__['data'] = "from dict"
            print(f"data после попытки перекрытия: {t.data}")
            """,
        ),
        example(
            "text",
            "data: data descriptor\n"
            "non_data: non-data descriptor\n"
            "__dict__: {'non_data': 'ignored', '_value': 10}\n"
            "non_data после перекрытия: from dict\n"
            "data после попытки перекрытия: data descriptor",
        ),
        text(
            "Именно поэтому `property` (data descriptor) всегда работает, а методы "
            "(non-data descriptors) можно перекрыть атрибутом экземпляра. "
            "`classmethod` и `staticmethod` тоже — non-data дескрипторы."
        ),
        heading("property — это дескриптор", 3),
        text(
            "Встроенный `property` реализован как дескриптор. Понимание этого "
            "позволяет писать свои аналоги с дополнительной логикой."
        ),
        example(
            "python",
            """
            class Property:
                def __init__(self, fget=None, fset=None, fdel=None, doc=None):
                    self.fget = fget
                    self.fset = fset
                    self.fdel = fdel
                    self.__doc__ = doc

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self
                    if self.fget is None:
                        raise AttributeError("unreadable attribute")
                    return self.fget(obj)

                def __set__(self, obj, value):
                    if self.fset is None:
                        raise AttributeError("can't set attribute")
                    self.fset(obj, value)

                def __delete__(self, obj):
                    if self.fdel is None:
                        raise AttributeError("can't delete attribute")
                    self.fdel(obj)

                def getter(self, fget):
                    return type(self)(fget, self.fset, self.fdel, self.__doc__)

                def setter(self, fset):
                    return type(self)(self.fget, fset, self.fdel, self.__doc__)

                def deleter(self, fdel):
                    return type(self)(self.fget, self.fset, fdel, self.__doc__)

            class Account:
                def __init__(self, balance):
                    self._balance = balance

                @Property
                def balance(self):
                    return self._balance

                @balance.setter
                def balance(self, value):
                    if value < 0:
                        raise ValueError("Баланс не может быть отрицательным")
                    self._balance = value

            acc = Account(100)
            print(acc.balance)
            acc.balance = 200
            print(acc.balance)
            try:
                acc.balance = -50
            except ValueError as e:
                print(e)
            """,
        ),
        example(
            "text",
            "100\n200\nБаланс не может быть отрицательным",
        ),
        heading("Продвинутые паттерны дескрипторов"),
        heading("Ленивая инициализация (кэширование)", 3),
        text(
            "Дескриптор может вычислить значение при первом доступе, сохранить его "
            "в `__dict__` экземпляра и при последующих обращениях возвращать "
            "уже готовое значение. Это полезно для дорогих вычислений."
        ),
        example(
            "python",
            """
            class LazyProperty:
                def __init__(self, func):
                    self.func = func
                    self.name = func.__name__

                def __set_name__(self, owner, name):
                    self.name = name

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self
                    value = self.func(obj)
                    setattr(obj, self.name, value)  # кэшируем, перекрываем себя
                    return value

            import time

            class Expensive:
                @LazyProperty
                def data(self):
                    print("Вычисляем...")
                    time.sleep(0.1)
                    return [i ** 2 for i in range(100000)]

            e = Expensive()
            print("Первый доступ:")
            start = time.time()
    _ = e.data
            print(f"  время: {time.time() - start:.3f}s")

            print("Второй доступ:")
            start = time.time()
    _ = e.data
            print(f"  время: {time.time() - start:.6f}s")
            """,
        ),
        example(
            "text",
            "Первый доступ:\n"
            "Вычисляем...\n"
            "  время: 0.102s\n"
            "Второй доступ:\n"
            "  время: 0.000001s",
        ),
        heading("Типизированные поля (как в dataclass)", 3),
        text(
            "Дескриптор может проверять тип при записи. Это основа библиотек вроде "
            "`attrs`, `pydantic`, `dataclasses` (где проверка типов добавляется "
            "через сторонние инструменты)."
        ),
        example(
            "python",
            """
            class TypedField:
                def __init__(self, type_, default=None):
                    self.type = type_
                    self.default = default
                    self.name = None
                    self.storage = None

                def __set_name__(self, owner, name):
                    self.name = name
                    self.storage = f'_typed_{name}'

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self
                    return getattr(obj, self.storage, self.default)

                def __set__(self, obj, value):
                    if not isinstance(value, self.type):
                        raise TypeError(
                            f"{self.name} должен быть {self.type.__name__}, "
                            f"не {type(value).__name__}"
                        )
                    setattr(obj, self.storage, value)

            class Person:
                name = TypedField(str)
                age = TypedField(int, default=0)
                email = TypedField(str, default="")

            p = Person()
            p.name = "Анна"
            p.age = 25
            print(f"{p.name}, {p.age}, email='{p.email}'")

            try:
                p.age = "двадцать пять"
            except TypeError as e:
                print(f"Ошибка: {e}")
            """,
        ),
        example(
            "text",
            "Анна, 25, email=''\n"
            "Ошибка: age должен быть int, не str",
        ),
        heading("Дескриптор только для чтения", 3),
        text(
            "Data descriptor без `__set__` (или с `__set__`, выбрасывающим ошибку) "
            "делает атрибут неизменяемым после инициализации. В отличие от `property` "
            "без сеттера, такой дескриптор можно переиспользовать."
        ),
        example(
            "python",
            """
            class ReadOnly:
                def __init__(self, value):
                    self.value = value

                def __get__(self, obj, objtype=None):
                    return self.value

                def __set__(self, obj, value):
                    raise AttributeError(
                        f"Атрибут только для чтения: {self.value!r}"
                    )

            class Config:
                VERSION = ReadOnly("1.0.0")
                DEBUG = ReadOnly(False)

            c = Config()
            print(f"VERSION: {c.VERSION}")
            print(f"DEBUG: {c.DEBUG}")

            try:
                c.VERSION = "2.0"
            except AttributeError as e:
                print(f"Ошибка: {e}")
            """,
        ),
        example(
            "text",
            "VERSION: 1.0.0\n"
            "DEBUG: False\n"
            "Ошибка: Атрибут только для чтения: '1.0.0'",
        ),
        heading("Наблюдаемые атрибуты (Observer pattern)", 3),
        text(
            "Дескриптор может вызывать коллбеки при изменении значения — основа "
            "реактивных систем, UI биндинга и валидации."
        ),
        example(
            "python",
            """
            class ObservedField:
                def __init__(self, default=None, on_change=None):
                    self.default = default
                    self.on_change = on_change
                    self.name = None
                    self.storage = None

                def __set_name__(self, owner, name):
                    self.name = name
                    self.storage = f'_observed_{name}'

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self
                    return getattr(obj, self.storage, self.default)

                def __set__(self, obj, value):
                    old = getattr(obj, self.storage, self.default)
                    setattr(obj, self.storage, value)
                    if self.on_change and old != value:
                        self.on_change(obj, self.name, old, value)

            class Model:
                def __init__(self):
                    self._changes = []

                def _log_change(self, obj, name, old, new):
                    self._changes.append((name, old, new))
                    print(f"  изменено: {name} = {old!r} -> {new!r}")

                status = ObservedField("draft", on_change=lambda s, n, o, v: s._log_change(s, n, o, v))
                count = ObservedField(0, on_change=lambda s, n, o, v: s._log_change(s, n, o, v))

            m = Model()
            m.status = "active"
            m.count = 5
            m.count = 10
            print("История:", m._changes)
            """,
        ),
        example(
            "text",
            "  изменено: status = 'draft' -> 'active'\n"
            "  изменено: count = 0 -> 5\n"
            "  изменено: count = 5 -> 10\n"
            "История: [('status', 'draft', 'active'), ('count', 0, 5), ('count', 5, 10)]",
        ),
        heading("Метаклассы vs дескрипторы vs __init_subclass__"),
        text(
            "Все три механизма решают задачи кастомизации классов, но на разных "
            "уровнях и для разных целей."
        ),
        table(
            ["Характеристика", "Метакласс", "Дескриптор", "__init_subclass__"],
            [
                ["Уровень действия", "Создание класса", "Доступ к атрибуту экземпляра", "Создание подкласса"],
                ["Когда срабатывает", "При объявлении class", "При obj.attr / obj.attr = x", "При создании наследника"],
                ["Типичные задачи", "Регистрация, валидация структуры, изменение namespace", "Контроль доступа, типизация, ленивость, наблюдение", "Авторегистрация подклассов, настройка наследников"],
                ["Сложность", "Высокая", "Средняя", "Низкая"],
                ["Примеры в stdlib", "abc.ABCMeta, Enum", "property, classmethod, staticmethod", "enum.Enum, typing.Generic"],
            ],
        ),
        text(
            "**Правило выбора:** если задачу можно решить через `__init_subclass__` — "
            "делайте это (проще, читаемее). Если нужно контролировать доступ к "
            "атрибуту экземпляра — дескриптор. Если нужно вмешаться в саму структуру "
            "класса до создания экземпляров — метакласс."
        ),
        heading("__init_subclass__ — альтернатива метаклассам (Python 3.6+)"),
        text(
            "Метод класса `__init_subclass__` вызывается автоматически при создании "
            "каждого подкласса. Это упрощённый способ регистрации наследников или "
            "настройки их поведения без полного метакласса."
        ),
        example(
            "python",
            """
            class BaseHandler:
                handlers = {}

                def __init_subclass__(cls, route=None, **kwargs):
                    super().__init_subclass__(**kwargs)
                    if route:
                        BaseHandler.handlers[route] = cls
                        print(f"Зарегистрирован {cls.__name__} для {route}")

            class HomeHandler(BaseHandler, route="/"):
                pass

            class ApiHandler(BaseHandler, route="/api"):
                pass

            class AdminHandler(BaseHandler, route="/admin"):
                pass

            print("Маршруты:", BaseHandler.handlers)
            """,
        ),
        example(
            "text",
            "Зарегистрирован HomeHandler для /\n"
            "Зарегистрирован ApiHandler для /api\n"
            "Зарегистрирован AdminHandler для /admin\n"
            "Маршруты: {'/': <class '__main__.HomeHandler'>, '/api': <class '__main__.ApiHandler'>, '/admin': <class '__main__.AdminHandler'>}",
        ),
        text(
            "`__init_subclass__` получает ключевые аргументы из объявления наследника "
            '(в примере `route="/"`) Это позволяет передавать метаданные без '
            "сложностей метаклассов."
        ),
        heading("Комбинирование метаклассов и дескрипторов"),
        text(
            "В реальных фреймворках метаклассы и дескрипторы работают вместе: "
            "метакласс собирает дескрипторы и настраивает их, дескрипторы "
            "контролируют доступ к данным экземпляров."
        ),
        example(
            "python",
            """
            class Field:
                def __init__(self, type_=str, required=False):
                    self.type = type_
                    self.required = required
                    self.name = None
                    self.storage = None

                def __set_name__(self, owner, name):
                    self.name = name
                    self.storage = f'_field_{name}'
                    # Регистрируемся в метаклассе владельца
                    if hasattr(owner, '_fields'):
                        owner._fields[name] = self

                def __get__(self, obj, objtype=None):
                    if obj is None:
                        return self
                    return getattr(obj, self.storage, None)

                def __set__(self, obj, value):
                    if not isinstance(value, self.type):
                        raise TypeError(
                            f"{self.name}: ожидается {self.type.__name__}, "
                            f"получено {type(value).__name__}"
                        )
                    setattr(obj, self.storage, value)

            class ModelMeta(type):
                def __new__(mcs, name, bases, namespace):
                    cls = super().__new__(mcs, name, bases, namespace)
                    cls._fields = {}
                    # Собираем поля из MRO
                    for base in cls.__mro__:
                        if hasattr(base, '_fields'):
                            cls._fields.update(base._fields)
                    return cls

            class Model(metaclass=ModelMeta):
                @classmethod
                def create(cls, **kwargs):
                    obj = cls()
                    for key, value in kwargs.items():
                        if key in cls._fields:
                            setattr(obj, key, value)
                        else:
                            raise ValueError(f"Неизвестное поле: {key}")
                    return obj

                def to_dict(self):
                    return {name: getattr(self, name) for name in self._fields}

            class User(Model):
                name = Field(str, required=True)
                age = Field(int)
                email = Field(str)

            u = User.create(name="Анна", age=25, email="anna@example.com")
            print(u.to_dict())

            try:
                User.create(name="Борис", age="много")
            except TypeError as e:
                print(f"Ошибка: {e}")
            """,
        ),
        example(
            "text",
            "{'name': 'Анна', 'age': 25, 'email': 'anna@example.com'}\n"
            "Ошибка: age: ожидается int, получено str",
        ),
        heading("Сравнение производительности"),
        text(
            "Дескрипторы добавляют накладные расходы на каждый доступ к атрибуту. "
            "Для горячих путей (миллионы обращений в секунду) это может быть "
            "заметно. Обычный атрибут в `__dict__` быстрее."
        ),
        example(
            "python",
            """
            import time

            class Descriptor:
                def __init__(self):
                    self.value = 0
                def __get__(self, obj, objtype=None):
                    return self.value
                def __set__(self, obj, value):
                    self.value = value

            class WithDescriptor:
                x = Descriptor()

            class WithDict:
                def __init__(self):
                    self.x = 0

            obj_desc = WithDescriptor()
            obj_dict = WithDict()
            n = 1_000_000

            start = time.time()
            for i in range(n):
                obj_desc.x = i
                _ = obj_desc.x
            print(f"Дескриптор: {time.time() - start:.3f}s")

            start = time.time()
            for i in range(n):
                obj_dict.x = i
                _ = obj_dict.x
            print(f"Обычный атрибут: {time.time() - start:.3f}s")
            """,
        ),
        example(
            "text",
            "Дескриптор: 0.156s\n"
            "Обычный атрибут: 0.062s",
        ),
        text(
            "Разница в 2-3 раза. Для бизнес-логики, валидации, ORM это "
            "незначительно. Для численных расчётов в цикле — избегайте "
            "дескрипторов на горячих атрибутах."
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                [
                    "Забыли super().__new__ в метаклассе",
                    "Класс не создаётся, теряется функциональность type.",
                    "Всегда вызывайте super().__new__(mcs, name, bases, namespace).",
                ],
                [
                    "Дескриптор хранит состояние в себе (self.value)",
                    "Значение становится общим для всех экземпляров класса.",
                    "Храните в obj.__dict__ под уникальным ключом (через __set_name__).",
                ],
                [
                    "__set_name__ не определён",
                    "Дескриптор не знает имя атрибута, нельзя сгенерировать storage_name.",
                    "Добавьте __set_name__(self, owner, name) (Python 3.6+).",
                ],
                [
                    "Конфликт data/non-data дескрипторов",
                    "Non-data дескриптор перекрывается __dict__ экземпляра.",
                    "Для контроля записи используйте data descriptor (с __set__).",
                ],
                [
                    "Метакласс для простой регистрации",
                    "Избыточная сложность, труднее отлаживать.",
                    "Используйте __init_subclass__ или декоратор класса.",
                ],
                [
                    "Множественное наследование с разными метаклассами",
                    "TypeError: metaclass conflict.",
                    "Объедините метаклассы в один через множественное наследование от type.",
                ],
                [
                    "Дескриптор на горячем пути в численных расчётах",
                    "Накладные расходы 2-3x медленнее прямого доступа.",
                    "Используйте обычные атрибуты или __slots__ для производительности.",
                ],
            ],
        ),
        heading("Практика"),
        text(
            "Выполните задания по порядку. Каждое проверяет понимание протоколов. "
            "Запускайте код и сверяйтесь с выводом."
        ),
        numbered(
            "Создайте дескриптор `PositiveNumber`, который позволяет записать только положительные числа (int или float). При попытке записать отрицательное или ноль — ValueError.",
            "Создайте метакласс `AutoReprMeta`, который автоматически добавляет `__repr__` ко всем классам: вывод должен быть `ClassName(attr1=value1, attr2=value2, ...)` для всех атрибутов, не начинающихся с подчёркивания.",
            "Реализуйте дескриптор `LazyProperty` (как в уроке) и примените его к методу, который читает большой файл или делает дорогой запрос. Проверьте, что повторное чтение мгновенно.",
            "Создайте метакласс `ValidatedMeta`, проверяющий, что у класса есть атрибут `VERSION` типа str. Если нет — TypeError при создании класса.",
            "Создайте базовый класс `EventEmitter` с `__init_subclass__`, который автоматически регистрирует все подклассы в `EventEmitter.events` (словарь имя_класса -> класс). Добавьте классметод `emit(event_name, data)`, создающий экземпляр соответствующего класса и вызывающий его `.handle(data)`.",
        ),
        text("Пример ожидаемого результата для первого задания:"),
        example(
            "text",
            "value = 42\n"
            "Ошибка: значение должно быть положительным",
        ),
        callout(
            "success",
            "Подсказка к заданию 2",
            "В __new__ метакласса после создания класса добавьте ему метод __repr__, "
            "который собирает атрибуты из self.__dict__ (фильтруя __module__, "
            "__qualname__ и другие служебные). Используйте setattr(cls, '__repr__', ...).",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем метакласс отличается от обычного класса?",
            "В какой момент вызывается __prepare__, __new__, __init__ метакласса?",
            "Чем data descriptor отличается от non-data descriptor?",
            "Почему дескриптор не должен хранить значение в self.value?",
            "Когда следует использовать __init_subclass__ вместо метакласса?",
            "Как дескриптор узнаёт имя атрибута, под которым он объявлен в классе?",
        ),
        heading("Ответы", 3),
        numbered(
            "Метакласс — класс, экземплярами которого являются классы. Обычный класс — экземпляр type, метакласс наследуется от type.",
            "__prepare__ — до выполнения тела класса (подготовка namespace). __new__ — создание объекта-класса. __init__ — инициализация уже созданного класса.",
            "Data descriptor имеет __set__ или __delete__ и побеждает __dict__ экземпляра. Non-data descriptor имеет только __get__ и проигрывает __dict__.",
            "self.value общий для всех экземпляров класса-владельца. Хранить нужно в obj.__dict__ под уникальным ключом.",
            "Когда нужно просто отреагировать на создание подкласса (регистрация, настройка). Метакласс нужен для вмешательства в создание самого класса.",
            "Через автоматический вызов __set_name__(self, owner, name) при создании класса (Python 3.6+).",
        ),
        heading("Итоги"),
        bullets(
            "Класс — объект, экземпляр метакласса type. type — метакласс по умолчанию.",
            "Метакласс (наследник type) перехватывает создание классов через __new__, __init__, __prepare__.",
            "__prepare__ возвращает namespace для тела класса (OrderedDict для порядка полей).",
            "Дескриптор — объект с __get__, __set__, __delete__, управляющий доступом к атрибуту.",
            "Data descriptor (с __set__) побеждает __dict__ экземпляра, non-data — проигрывает.",
            "__set_name__(self, owner, name) вызывается автоматически при создании класса (Python 3.6+).",
            "Значение дескриптора хранить в obj.__dict__ под уникальным ключом, а не в самом дескрипторе.",
            "property, classmethod, staticmethod — встроенные дескрипторы.",
            "__init_subclass__ — простая альтернатива метаклассам для реакции на наследование (Python 3.6+).",
            "Метаклассы и дескрипторы — основа ORM, валидации, реактивности, плагинных систем.",
        ),
        heading("Что дальше"),
        text(
            "Метаклассы и дескрипторы — фундамент для понимания того, как работают "
            "современные фреймворки. В следующем уроке разберём расширения Python "
            "на C и Cython: как писать модули на C, компилировать Python-код в C "
            "через Cython и использовать Rust через PyO3 для CPU-bound задач."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "Официальная документация: Metaclasses — docs.python.org/3/reference/datamodel.html#metaclasses",
            "Официальная документация: Descriptors — docs.python.org/3/howto/descriptor.html",
            "Real Python: Metaclasses — realpython.com/python-metaclasses/",
            "Real Python: Descriptors — realpython.com/python-descriptors/",
            "PEP 487 — Simpler customization of class creation — peps.python.org/pep-0487/",
            "Python MRO и метаклассы — blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/",
        ),
    ],
}