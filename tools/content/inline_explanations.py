#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Встраивает объяснения терминов прямо в текст при первом упоминании.
"""

import json
import re
from pathlib import Path
from typing import Set, Dict, List, Tuple

# Термины с краткими объяснениями для встраивания
TERM_DEFINITIONS: Dict[str, str] = {
    # Базовые типы
    "class": " (класс — ссылочный тип, шаблон для создания объектов, поддерживает наследование)",
    "struct": " (struct — значимый тип, хранится в стеке, копируется при присваивании, для маленьких неизменяемых данных)",
    "record": " (record — ссылочный тип с автоматической проверкой на равенство, неизменяемостью и with-выражениями, C# 9+)",
    "interface": " (interface — контракт, описывает ЧТО делает тип, только сигнатуры без реализации, класс может реализовывать много интерфейсов)",
    "abstract": " (abstract — модификатор: абстрактный класс нельзя инстанцировать, абстрактный метод обязан быть переопределен в наследнике)",
    "virtual": " (virtual — метод можно переопределить в наследнике через override)",
    "override": " (override — переопределение виртуального/абстрактного метода в наследнике, полиморфизм)",
    "sealed": " (sealed — класс нельзя наследовать, метод нельзя переопределять дальше)",
    "static": " (static — член принадлежит типу, а не объекту; вызов через ИмяТипа.Метод())",
    "readonly": " (readonly — поле можно задать только в конструкторе или при объявлении, ссылка неизменна)",
    "const": " (const — константа времени компиляции, значение задается в коде, неявно static)",
    "property": " (свойство — метод доступа к данным, выглядит как поле: get — чтение, set — запись)",
    "interface": " (interface — контракт, только сигнатуры без реализации, класс может реализовывать много интерфейсов)",
    "abstract class": " (abstract class — класс, от которого нельзя создать объект, только наследовать; может иметь реализацию)",
    "virtual": " (virtual — метод можно переопределить в наследнике через override)",
    "override": " (override — переопределение виртуального/абстрактного метода в наследнике, полиморфизм)",
    "sealed": " (sealed — класс нельзя наследовать, метод нельзя переопределять дальше)",
    "static": " (static — член принадлежит ТИПУ, а не объекту; вызов через ИмяТипа.Метод())",
    "readonly": " (readonly — поле можно задать только в конструкторе или при объявлении, ссылка неизменна)",
    "const": " (const — константа времени компиляции, значение задается в коде, неявно static)",
    "property": " (свойство — метод доступа к данным, выглядит как поле: get — чтение, set — запись)",
    "indexer": " (indexer — позволяет обращаться к экземпляру как к массиву: obj[i])",
    "operator overloading": " (operator overloading — перегрузка операторов для своих типов: +, -, ==, != и др.)",
    "extension method": " (extension method — метод расширения для существующего типа, this перед первым параметром)",
    "LINQ": " (LINQ — интегрированный язык запросов, отложенное выполнение, синтаксис запроса или методы расширения)",
    "IEnumerable": " (IEnumerable<T> — интерфейс для перебора последовательности, база для LINQ и foreach)",
    "yield return": " (yield return — возвращает элемент и приостанавливает выполнение, для ленивых последовательностей)",
    "IQueryable": " (IQueryable<T> — запросы, транслируемые в SQL, для EF Core/БД)",
    "Entity Framework": " (Entity Framework — ORM для .NET, маппит классы на таблицы БД, LINQ в SQL)",
    "DI": " (Dependency Injection — зависимости получаются извне через конструктор, контейнер управляет жизненным циклом)",
    "SOLID": " (SOLID — 5 принципов ООП: SRP, OCP, LSP, ISP, DIP)",
    "DRY": " (DRY — Don't Repeat Yourself, не дублируй код)",
    "KISS": " (KISS — Keep It Simple, Stupid, пиши простой код)",
    "YAGNI": " (YAGNI — You Aren't Gonna Need It, не пиши код \"на будущее\")",
    "ref": " (ref — передача по ссылке, чтение и запись, переменная должна быть инициализирована ДО вызова)",
    "out": " (out — передача по ссылке только для записи, переменная инициализируется ВНУТРИ метода)",
    "in": " (in — передача по ссылке ТОЛЬКО для чтения, защита от изменения, для больших struct)",
    "params": " (params — параметр-массив, переменное число аргументов: Print(params string[] names))",
    "optional parameters": " (optional parameters — параметры со значениями по умолчанию: void Greet(string name, string greeting = \"Hello\"))",
    "named arguments": " (named arguments — передача по имени: Greet(name: \"Alex\", greeting: \"Hi\"))",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "boxing": " (boxing — упаковка value type в object, создает объект в куче, расходует память)",
    "unboxing": " (unboxing — извлечение value type из object: int x = (int)obj)",
    "value type": " (value type — значимый тип: struct, enum, примитивы; хранится в стеке, копируется при присваивании)",
    "reference type": " (reference type — ссылочный тип: class, interface, delegate, array, string; в куче, по ссылке)",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "struct": " (struct — значимый тип, хранится в стеке, копируется при присваивании, для маленьких неизменяемых данных)",
    "class": " (class — ссылочный тип, шаблон для объектов, поддерживает наследование, в куче)",
    "record": " (record — ссылочный тип с value-based equality, неизменяемостью, with-выражениями, C# 9+)",
    "interface": " (interface — контракт, только сигнатуры без реализации, класс может реализовывать много интерфейсов)",
    "abstract": " (abstract — класс нельзя инстанцировать, метод обязан переопределить в наследнике)",
    "virtual": " (virtual — метод можно переопределить в наследнике через override)",
    "override": " (override — переопределение виртуального/абстрактного метода в наследнике, полиморфизм)",
    "sealed": " (sealed — класс нельзя наследовать, метод нельзя переопределять дальше)",
    "static": " (static — член принадлежит ТИПУ, а не объекту; вызов через ИмяТипа.Метод())",
    "readonly": " (readonly — поле можно задать только в конструкторе или при объявлении, ссылка неизменна)",
    "const": " (const — константа времени компиляции, значение в коде, неявно static)",
    "property": " (свойство — метод доступа к данным, выглядит как поле: get — чтение, set — запись)",
    "indexer": " (indexer — позволяет обращаться к экземпляру как к массиву: obj[i])",
    "operator overloading": " (operator overloading — перегрузка операторов для своих типов: +, -, ==, !=)",
    "extension method": " (extension method — метод расширения для существующего типа, this перед первым параметром)",
    "LINQ": " (LINQ — интегрированный язык запросов, отложенное выполнение, синтаксис запроса или методы расширения)",
    "IEnumerable": " (IEnumerable<T> — интерфейс для перебора последовательности, база для LINQ и foreach)",
    "yield return": " (yield return — возвращает элемент и приостанавливает выполнение, для ленивых последовательностей)",
    "IQueryable": " (IQueryable<T> — запросы, транслируемые в SQL, для EF Core/БД)",
    "Entity Framework": " (Entity Framework — ORM для .NET, маппит классы на таблицы БД, LINQ в SQL)",
    "DI": " (Dependency Injection — зависимости получаются извне через конструктор, контейнер управляет жизненным циклом)",
    "SOLID": " (SOLID — 5 принципов ООП: SRP, OCP, LSP, ISP, DIP)",
    "DRY": " (DRY — Don't Repeat Yourself, не дублируй код)",
    "KISS": " (KISS — Keep It Simple, Stupid, пиши простой код)",
    "YAGNI": " (YAGNI — You Aren't Gonna Need It, не пиши код \"на будущее\")",
    "ref": " (ref — передача по ссылке, чтение и запись, переменная должна быть инициализирована ДО вызова)",
    "out": " (out — передача по ссылке только для записи, переменная инициализируется ВНУТРИ метода)",
    "in": " (in — передача по ссылке ТОЛЬКО для чтения, readonly, для больших struct)",
    "params": " (params — параметр-массив, переменное число аргументов: Print(params string[] names))",
    "optional parameters": " (optional parameters — параметры со значениями по умолчанию: void Greet(string name, string greeting = \"Hello\"))",
    "named arguments": " (named arguments — передача по имени: Greet(name: \"Alex\", greeting: \"Hi\"))",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "boxing": " (boxing — упаковка value type в object, создает объект в куче, расходует память)",
    "unboxing": " (unboxing — извлечение value type из object: int x = (int)obj)",
    "value type": " (value type — значимый тип: struct, enum, примитивы; в стеке, копируется при присваивании)",
    "reference type": " (reference type — ссылочный тип: class, interface, delegate, array, string; в куче, по ссылке)",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "struct": " (struct — значимый тип, хранится в стеке, копируется при присваивании, для маленьких неизменяемых данных)",
    "class": " (class — ссылочный тип, шаблон для объектов, поддерживает наследование, в куче)",
    "record": " (record — ссылочный тип с value-based equality, неизменяемостью, with-выражениями, C# 9+)",
    "interface": " (interface — контракт, только сигнатуры без реализации, класс может реализовывать много интерфейсов)",
    "abstract": " (abstract — класс нельзя инстанцировать, метод обязан переопределить в наследнике)",
    "virtual": " (virtual — метод можно переопределить в наследнике через override)",
    "override": " (override — переопределение виртуального/абстрактного метода в наследнике, полиморфизм)",
    "sealed": " (sealed — класс нельзя наследовать, метод нельзя переопределять дальше)",
    "static": " (static — член принадлежит ТИПУ, а не объекту; вызов через ИмяТипа.Метод())",
    "readonly": " (readonly — поле можно задать только в конструкторе или при объявлении, ссылка неизменна)",
    "const": " (const — константа времени компиляции, значение в коде, неявно static)",
    "property": " (свойство — метод доступа к данным, выглядит как поле: get — чтение, set — запись)",
    "indexer": " (indexer — позволяет обращаться к экземпляру как к массиву: obj[i])",
    "operator overloading": " (operator overloading — перегрузка операторов для своих типов: +, -, ==, !=)",
    "extension method": " (extension method — метод расширения для существующего типа, this перед первым параметром)",
    "LINQ": " (LINQ — интегрированный язык запросов, отложенное выполнение, синтаксис запроса или методы расширения)",
    "IEnumerable": " (IEnumerable<T> — интерфейс для перебора последовательности, база для LINQ и foreach)",
    "yield return": " (yield return — возвращает элемент и приостанавливает выполнение, для ленивых последовательностей)",
    "IQueryable": " (IQueryable<T> — запросы, транслируемые в SQL, для EF Core/БД)",
    "Entity Framework": " (Entity Framework — ORM для .NET, маппит классы на таблицы БД, LINQ в SQL)",
    "DI": " (Dependency Injection — зависимости получаются извне через конструктор, контейнер управляет жизненным циклом)",
    "SOLID": " (SOLID — 5 принципов ООП: SRP, OCP, LSP, ISP, DIP)",
    "DRY": " (DRY — Don't Repeat Yourself, не дублируй код)",
    "KISS": " (KISS — Keep It Simple, Stupid, пиши простой код)",
    "YAGNI": " (YAGNI — You Aren't Gonna Need It, не пиши код \"на будущее\")",
    "ref": " (ref — передача по ссылке, чтение и запись, переменная должна быть инициализирована ДО вызова)",
    "out": " (out — передача по ссылке только для записи, переменная инициализируется ВНУТРИ метода)",
    "in": " (in — передача по ссылке ТОЛЬКО для чтения, readonly, для больших struct)",
    "params": " (params — параметр-массив, переменное число аргументов: Print(params string[] names))",
    "optional parameters": " (optional parameters — параметры со значениями по умолчанию: void Greet(string name, string greeting = \"Hello\"))",
    "named arguments": " (named arguments — передача по имени: Greet(name: \"Alex\", greeting: \"Hi\"))",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "boxing": " (boxing — упаковка value type в object, создает объект в куче, расходует память)",
    "unboxing": " (unboxing — извлечение value type из object: int x = (int)obj)",
    "value type": " (value type — значимый тип: struct, enum, примитивы; в стеке, копируется при присваивании)",
    "reference type": " (reference type — ссылочный тип: class, interface, delegate, array, string; в куче, по ссылке)",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "struct": " (struct — значимый тип, хранится в стеке, копируется при присваивании, для маленьких неизменяемых данных)",
    "class": " (class — ссылочный тип, шаблон для объектов, поддерживает наследование, в куче)",
    "record": " (record — ссылочный тип с value-based equality, неизменяемостью, with-выражениями, C# 9+)",
    "interface": " (interface — контракт, только сигнатуры без реализации, класс может реализовывать много интерфейсов)",
    "abstract": " (abstract — класс нельзя инстанцировать, метод обязан переопределить в наследнике)",
    "virtual": " (virtual — метод можно переопределить в наследнике через override)",
    "override": " (override — переопределение виртуального/абстрактного метода в наследнике, полиморфизм)",
    "sealed": " (sealed — класс нельзя наследовать, метод нельзя переопределять дальше)",
    "static": " (static — член принадлежит ТИПУ, а не объекту; вызов через ИмяТипа.Метод())",
    "readonly": " (readonly — поле можно задать только в конструкторе или при объявлении, ссылка неизменна)",
    "const": " (const — константа времени компиляции, значение в коде, неявно static)",
    "property": " (свойство — метод доступа к данным, выглядит как поле: get — чтение, set — запись)",
    "indexer": " (indexer — позволяет обращаться к экземпляру как к массиву: obj[i])",
    "operator overloading": " (operator overloading — перегрузка операторов для своих типов: +, -, ==, !=)",
    "extension method": " (extension method — метод расширения для существующего типа, this перед первым параметром)",
    "LINQ": " (LINQ — интегрированный язык запросов, отложенное выполнение, синтаксис запроса или методы расширения)",
    "IEnumerable": " (IEnumerable<T> — интерфейс для перебора последовательности, база для LINQ и foreach)",
    "yield return": " (yield return — возвращает элемент и приостанавливает выполнение, для ленивых последовательностей)",
    "IQueryable": " (IQueryable<T> — запросы, транслируемые в SQL, для EF Core/БД)",
    "Entity Framework": " (Entity Framework — ORM для .NET, маппит классы на таблицы БД, LINQ в SQL)",
    "DI": " (Dependency Injection — зависимости получаются извне через конструктор, контейнер управляет жизненным циклом)",
    "SOLID": " (SOLID — 5 принципов ООП: SRP, OCP, LSP, ISP, DIP)",
    "DRY": " (DRY — Don't Repeat Yourself, не дублируй код)",
    "KISS": " (KISS — Keep It Simple, Stupid, пиши простой код)",
    "YAGNI": " (YAGNI — You Aren't Gonna Need It, не пиши код \"на будущее\")",
    "ref": " (ref — передача по ссылке, чтение и запись, переменная должна быть инициализирована ДО вызова)",
    "out": " (out — передача по ссылке только для записи, переменная инициализируется ВНУТРИ метода)",
    "in": " (in — передача по ссылке ТОЛЬКО для чтения, readonly, для больших struct)",
    "params": " (params — параметр-массив, переменное число аргументов: Print(params string[] names))",
    "optional parameters": " (optional parameters — параметры со значениями по умолчанию: void Greet(string name, string greeting = \"Hello\"))",
    "named arguments": " (named arguments — передача по имени: Greet(name: \"Alex\", greeting: \"Hi\"))",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "boxing": " (boxing — упаковка value type в object, создает объект в куче, расходует память)",
    "unboxing": " (unboxing — извлечение value type из object: int x = (int)obj)",
    "value type": " (value type — значимый тип: struct, enum, примитивы; в стеке, копируется при присваивании)",
    "reference type": " (reference type — ссылочный тип: class, interface, delegate, array, string; в куче, по ссылке)",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "struct": " (struct — значимый тип, хранится в стеке, копируется при присваивании, для маленьких неизменяемых данных)",
    "class": " (class — ссылочный тип, шаблон для объектов, поддерживает наследование, в куче)",
    "record": " (record — ссылочный тип с value-based equality, неизменяемостью, with-выражениями, C# 9+)",
    "interface": " (interface — контракт, только сигнатуры без реализации, класс может реализовывать много интерфейсов)",
    "abstract": " (abstract — класс нельзя инстанцировать, метод обязан переопределить в наследнике)",
    "virtual": " (virtual — метод можно переопределить в наследнике через override)",
    "override": " (override — переопределение виртуального/абстрактного метода в наследнике, полиморфизм)",
    "sealed": " (sealed — класс нельзя наследовать, метод нельзя переопределять дальше)",
    "static": " (static — член принадлежит ТИПУ, а не объекту; вызов через ИмяТипа.Метод())",
    "readonly": " (readonly — поле можно задать только в конструкторе или при объявлении, ссылка неизменна)",
    "const": " (const — константа времени компиляции, значение в коде, неявно static)",
    "property": " (свойство — метод доступа к данным, выглядит как поле: get — чтение, set — запись)",
    "indexer": " (indexer — позволяет обращаться к экземпляру как к массиву: obj[i])",
    "operator overloading": " (operator overloading — перегрузка операторов для своих типов: +, -, ==, !=)",
    "extension method": " (extension method — метод расширения для существующего типа, this перед первым параметром)",
    "LINQ": " (LINQ — интегрированный язык запросов, отложенное выполнение, синтаксис запроса или методы расширения)",
    "IEnumerable": " (IEnumerable<T> — интерфейс для перебора последовательности, база для LINQ и foreach)",
    "yield return": " (yield return — возвращает элемент и приостанавливает выполнение, для ленивых последовательностей)",
    "IQueryable": " (IQueryable<T> — запросы, транслируемые в SQL, для EF Core/БД)",
    "Entity Framework": " (Entity Framework — ORM для .NET, маппит классы на таблицы БД, LINQ в SQL)",
    "DI": " (Dependency Injection — зависимости получаются извне через конструктор, контейнер управляет жизненным циклом)",
    "SOLID": " (SOLID — 5 принципов ООП: SRP, OCP, LSP, ISP, DIP)",
    "DRY": " (DRY — Don't Repeat Yourself, не дублируй код)",
    "KISS": " (KISS — Keep It Simple, Stupid, пиши простой код)",
    "YAGNI": " (YAGNI — You Aren't Gonna Need It, не пиши код \"на будущее\")",
    "ref": " (ref — передача по ссылке, чтение и запись, переменная должна быть инициализирована ДО вызова)",
    "out": " (out — передача по ссылке только для записи, переменная инициализируется ВНУТРИ метода)",
    "in": " (in — передача по ссылке ТОЛЬКО для чтения, readonly, для больших struct)",
    "params": " (params — параметр-массив, переменное число аргументов: Print(params string[] names))",
    "optional parameters": " (optional parameters — параметры со значениями по умолчанию: void Greet(string name, string greeting = \"Hello\"))",
    "named arguments": " (named arguments — передача по имени: Greet(name: \"Alex\", greeting: \"Hi\"))",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "boxing": " (boxing — упаковка value type в object, создает объект в куче, расходует память)",
    "unboxing": " (unboxing — извлечение value type из object: int x = (int)obj)",
    "value type": " (value type — значимый тип: struct, enum, примитивы; в стеке, копируется при присваивании)",
    "reference type": " (reference type — ссылочный тип: class, interface, delegate, array, string; в куче, по ссылке)",
    "null": " (null — отсутствие значения, источник NullReferenceException)",
    "nullable": " (nullable — T? обертка над value type, позволяющая хранить null: int? x = null)",
    "boxing": " (boxing — упаковка value type в object, создает объект в куче, расходует память)",
    "unboxing": " (unboxing — извлечение value type из object: int x = (int)obj)",
    "value type": " (value type — значимый тип: struct, enum, примитивы; в стеке, копируется при присваивании)",
    "reference type": " (reference type — ссылочный тип: class, interface, delegate, array, string; в куче, по ссылке)",
}

def inject_explanations(text: str, explained: Set[str]) -> Tuple[str, Set[str]]:
    """Вставляет объяснения после первого упоминания термина."""
    # Сортируем термины по длине (сначала длинные), чтобы не ловить подстроки
    sorted_terms = sorted(TERM_DEFINITIONS.keys(), key=len, reverse=True)
    
    result = text
    newly_explained = set()
    
    for term in sorted_terms:
        if term in explained:
            continue
        # Ищем термин как целое слово (границы слова)
        pattern = r'\b' + re.escape(term) + r'\b'
        match = re.search(pattern, result, re.IGNORECASE)
        if match:
            # Вставляем объяснение после первого вхождения
            explanation = TERM_DEFINITIONS[term]
            start, end = match.span()
            # Проверяем, не в коде ли это (простая эвристика: не внутри ```)
            before = result[:start]
            code_blocks = before.count('```')
            if code_blocks % 2 == 0:  # не внутри кода
                result = result[:end] + explanation + result[end:]
                explained.add(term.lower())
                newly_explained.add(term.lower())
    
    return result, newly_explained


def process_lesson_content(lesson: dict) -> dict:
    explained: Set[str] = set()
    new_blocks = []
    
    for block in lesson.get('content_blocks', []):
        if block.get('type') in ('text', 'heading'):
            content = block.get('content', '')
            enriched, new_explained = inject_explanations(content, explained)
            explained.update(new_explained)
            block = {**block, 'content': enriched}
        new_blocks.append(block)
    
    lesson['content_blocks'] = new_blocks
    return lesson


def process_lesson_file(lesson_path: Path):
    with open(lesson_path, 'r', encoding='utf-8') as f:
        lesson = json.load(f)
    
    lesson = process_lesson_content(lesson)
    
    with open(lesson_path, 'w', encoding='utf-8') as f:
        json.dump(lesson, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Обработан: {lesson_path.name}')


if __name__ == '__main__':
    lessons_dir = Path('fixtures/lessons/csharp')
    for lesson_file in sorted(lessons_dir.glob('*.json')):
        process_lesson_file(lesson_file)
    print('Все 33 урока обновлены с инлайн-объяснениями!')