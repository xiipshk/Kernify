"""Урок 1.8 курса JavaScript: работа с DOM."""

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
    "program_order": 1,
    "topic_order": 8,
    "name": "1.8. Работа с DOM",
    "slug": "javascript-1-8-работа-с-dom",
    "short_description": (
        "Как устроено дерево DOM, как находить и изменять элементы страницы, "
        "работать с атрибутами и классами, а также обрабатывать события и "
        "использовать делегирование."
    ),
    "topic_name": "Работа с DOM",
    "topic_description": (
        "Введение в Document Object Model: структура дерева документа, поиск "
        "элементов, создание и удаление узлов, работа с атрибутами, классами, "
        "стилями и событиями, а также безопасная вставка данных на страницу."
    ),
    "learning_objectives": [
        "Объяснять, что такое DOM и как браузер строит дерево документа из HTML",
        "Находить элементы через querySelector, querySelectorAll и getElementById",
        "Перемещаться по дереву: родители, дети и соседние элементы",
        "Создавать, вставлять, заменять и удалять элементы, использовать DocumentFragment",
        "Работать с атрибутами, data-атрибутами, классами через classList и inline-стилями",
        "Подписываться на события, различать фазы всплытия и перехвата, применять делегирование",
        "Безопасно вставлять пользовательские данные через textContent и избегать XSS",
    ],
    "estimated_minutes": 30,
    "xp_reward": 10,
    "difficulty": "beginner",
    "tags": [
        "javascript",
        "dom",
        "браузер",
        "события",
        "querySelector",
        "делегирование",
    ],
    "starter_code": code(
        """
        // Откройте страницу в браузере и выполните код в консоли
        const button = document.querySelector('#counter');
        const output = document.querySelector('#output');
        let count = 0;

        button.addEventListener('click', () => {
          count += 1;
          output.textContent = `Нажатий: ${count}`;
        });
        """
    ),
    "hints": [
        "querySelectorAll возвращает NodeList — статичный список. Чтобы получить массив, используйте [...nodes] или Array.from(nodes).",
        "Свойство textContent вставляет строку как текст и экранирует HTML, а innerHTML интерпретирует строку как разметку — это риск XSS.",
        "Чтобы поймать клики по динамически добавленным элементам, повесьте один слушатель на родителя и используйте e.target.closest('li').",
        "Если элемент не находится, querySelector вернёт null, и обращение к его свойству выбросит TypeError. Проверяйте результат или используйте необязательную цепочку.",
    ],
    "content": [
        text(
            "До этого момента весь код выполнялся в отрыве от страницы: переменные, "
            "функции и объекты жили только в памяти интерпретатора. Настоящая сила "
            "JavaScript в браузере проявляется, когда код начинает читать и изменять "
            "HTML-документ. За этот мост отвечает DOM — объектная модель документа.\n\n"
            "DOM (Document Object Model) — это программный интерфейс, через который "
            "скрипт получает доступ к содержимому страницы. Браузер разбирает HTML-текст "
            "и строит из него дерево объектов: каждый тег становится узлом, текст внутри "
            "тега — тоже узлом. JavaScript видит это дерево как набор вложенных объектов "
            "с методами и свойствами, а любой вызов вроде изменения текста или класса "
            "немедленно отражается на экране.\n\n"
            "В этом уроке вы научитесь находить нужные элементы, изменять их содержимое "
            "и оформление, добавлять новые узлы и реагировать на действия пользователя. "
            "Мы также разберём, как устроены события и почему один слушатель на родителе "
            "часто лучше сотни слушателей на дочерних элементах."
        ),
        heading("Чему вы научитесь"),
        bullets(
            "объяснять, что такое DOM и как браузер строит дерево документа из HTML;",
            "находить элементы через querySelector, querySelectorAll и getElementById;",
            "перемещаться по дереву: родители, дети и соседние элементы;",
            "создавать, вставлять, заменять и удалять элементы, использовать DocumentFragment;",
            "работать с атрибутами, data-атрибутами, классами через classList и inline-стилями;",
            "подписываться на события, различать фазы всплытия и перехвата, применять делегирование;",
            "безопасно вставлять пользовательские данные через textContent и избегать XSS.",
        ),
        heading("Что такое DOM"),
        text(
            "DOM — это представление HTML-документа в виде дерева узлов. Каждому тегу "
            "соответствует узел типа Element, тексту внутри тега — узел типа Text, "
            "комментарию — узел Comment. Корнем дерева служит объект document, от него "
            "идут html, внутри него head и body, а дальше — остальная разметка."
        ),
        example(
            "html",
            """
            <!DOCTYPE html>
            <html>
            <head><title>Страница</title></head>
            <body>
              <h1 id="title">Привет</h1>
              <p class="text">Текст <span>внутри</span></p>
            </body>
            </html>
            """,
        ),
        text(
            "Ниже показана та же разметка в виде дерева: отступы обозначают уровень "
            "вложенности, а стрелка — текстовое содержимое узла."
        ),
        example(
            "text",
            """
            document
            └── html
                ├── head
                │   └── title → "Страница"
                └── body
                    ├── h1#title → "Привет"
                    └── p.text
                        ├── text: "Текст "
                        └── span → "внутри"
            """,
        ),
        text(
            "Важная деталь: текст внутри элемента — отдельный узел, а не значение "
            "свойства. При обходе дерева через childNodes легко встретить пустые "
            "текстовые узлы от переносов строк в исходном HTML. Поэтому чаще нужны "
            "свойства, возвращающие только элементы: children, firstElementChild, "
            "nextElementSibling. DocumentFragment — лёгкий контейнер, который не "
            "отображается на странице и служит для подготовки группы узлов перед "
            "вставкой. Все типы узлов наследуются от базового интерфейса Node, поэтому "
            "у них есть общие методы вроде appendChild и removeChild."
        ),
        table(
            ["Тип узла", "Что описывает", "Пример"],
            [
                ["Document", "Корень документа, глобальный объект document", "document.body"],
                ["Element", "HTML-тег со своими атрибутами и детьми", "div, span, h1"],
                ["Text", "Текстовое содержимое внутри элемента", "«Привет» в теге h1"],
                ["Comment", "Комментарий в разметке, невидим на странице", "<!-- черновик -->"],
                ["DocumentFragment", "Ненастоящий контейнер для группы узлов", "Батч-вставка списка"],
            ],
        ),
        heading("Поиск элементов"),
        text(
            "Первый шаг работы с DOM — найти нужный узел. querySelector принимает "
            "CSS-селектор и возвращает первый подходящий элемент или null. Синтаксис "
            "тот же, что в CSS: #id для идентификатора, .class для класса, тег без "
            "префикса, [attr] для атрибута. querySelectorAll возвращает все совпадения "
            "в виде NodeList.\n\n"
            "getElementById ищет только по идентификатору и работает чуть быстрее, "
            "потому что не разбирает селектор. getElementsByClassName и "
            "getElementsByTagName возвращают HTMLCollection."
        ),
        example(
            "javascript",
            """
            // Возвращает первый подходящий элемент или null
            const title = document.querySelector('#title');
            const firstText = document.querySelector('.text');
            const heading1 = document.querySelector('h1');
            const withAttr = document.querySelector('[data-id]');
            const nested = document.querySelector('article > h2');

            // Возвращает все совпадения — NodeList
            const items = document.querySelectorAll('.item');
            console.log(items.length); // например, 3

            // Быстрые методы по идентификатору, классу и тегу
            const byId = document.getElementById('title');
            const byClass = document.getElementsByClassName('text');
            const byTag = document.getElementsByTagName('p');
            console.log(byTag.length);
            """,
        ),
        text(
            "Вывод в консоли показывает количество найденных узлов. Если элементов с "
            "классом item на странице три, а абзацев четыре, консоль выведет 3 и 4."
        ),
        example(
            "text",
            """
            Вывод:
            3
            4
            """,
        ),
        callout(
            "info",
            "HTMLCollection и NodeList — не массивы",
            "querySelectorAll возвращает статичный NodeList: снимок состояния в момент вызова. "
            "У него есть метод forEach, но нет map, filter и reduce. Чтобы получить массив, "
            "используйте [...nodes] или Array.from(nodes). HTMLCollection от getElementsByClassName "
            "и getElementsByTagName наоборот «живой»: он обновляется при изменении DOM, но "
            "у него нет даже forEach — только обычный цикл for или Array.from.",
        ),
        heading("Навигация по дереву"),
        text(
            "От найденного элемента обычно нужно перейти к родителю, детям или соседям. "
            "Для каждого направления есть пара свойств: одно обходит все узлы, включая "
            "текстовые, другое — только элементы. parentNode вернёт родителя любого "
            "типа, вплоть до document, а parentElement — только Element или null. "
            "childNodes и firstChild включают текстовые узлы, children и "
            "firstElementChild их пропускают. В большинстве случаев нужны именно "
            "«элементные» варианты.\n\n"
            "Метод closest поднимается от текущего элемента вверх и возвращает ближайшего "
            "предка, подходящего под селектор. Сам элемент тоже проверяется, поэтому "
            "closest может вернуть исходный узел."
        ),
        example(
            "javascript",
            """
            const el = document.querySelector('.item');

            // Родители
            console.log(el.parentElement.tagName);   // UL
            console.log(el.closest('.container')?.id); // container
            console.log(el.closest('.missing'));       // null

            // Дети (только элементы)
            console.log(el.children.length);
            console.log(el.firstElementChild?.textContent);
            console.log(el.lastElementChild?.textContent);
            console.log(el.childElementCount);

            // Соседи-элементы
            console.log(el.previousElementSibling?.textContent);
            console.log(el.nextElementSibling?.textContent);

            // Все узлы, включая текстовые
            console.log(el.childNodes.length);
            """,
        ),
        text(
            "Для разметки, где список из двух пунктов лежит внутри контейнера, а каждый "
            "пункт содержит span с текстом, результат будет таким."
        ),
        example(
            "text",
            """
            Вывод:
            UL
            container
            null
            1
            Первый
            Первый
            1
            null
            Второй
            3
            """,
        ),
        heading("Создание и вставка элементов"),
        text(
            "Новые элементы создаются методом document.createElement и до вставки в "
            "документ никак не отображаются. Пока узел не добавлен к дереву, браузер "
            "не выделяет ему место на странице и не пересчитывает вёрстку — это "
            "позволяет спокойно заполнить элемент содержимым.\n\n"
            "Для вставки есть несколько групп методов. Методы append и prepend добавляют "
            "узлы или строки внутрь элемента, в конец или начало. Методы before и after "
            "вставляют рядом с элементом — перед ним или после. Обратите внимание: "
            "append принимает сколько угодно аргументов и понимает строки, автоматически "
            "превращая их в текстовые узлы. Похожий по названию appendChild умеет работать "
            "только с одним узлом и строку не примет.\n\n"
            "Замена выполняется через replaceWith, удаление — через метод remove, вызванный "
            "на самом элементе. А вот его соседи before и after\n"
            "в отличие от себя самого не требуют доступа к родителю."
        ),
        example(
            "javascript",
            """
            const parent = document.querySelector('#parent');
            const child = document.createElement('div');
            child.textContent = 'Новый блок';

            const span = document.createElement('span');
            span.textContent = 'вставка';

            // Внутрь элемента
            parent.append(child, ' - просто текст', span);
            parent.prepend(document.createTextNode('Начало. '));

            // Рядом с элементом
            parent.before(document.createComment('перед родителем'));
            parent.after(document.createElement('hr'));

            // Замена и удаление
            span.replaceWith(document.createTextNode('замена'));
            child.remove();

            console.log(parent.childNodes.length);
            console.log(parent.textContent);
            """,
        ),
        text(
            "После вставки строки «- просто текст», узла span и замены span на текстовый "
            "узел внутри родителя остаются: текстовый узел «Начало. », удалённый элемент "
            "child уже не в счёт, и оставшиеся узлы."
        ),
        example(
            "text",
            """
            Вывод:
            3
            Начало.  - просто текстзамена
            """,
        ),
        callout(
            "info",
            "DocumentFragment для пакетной вставки",
            "Каждое изменение DOM может вызвать пересчёт стилей и вёрстки. Если добавить "
            "сто узлов по одному, браузер может перерисовать страницу сотню раз. "
            "DocumentFragment решает это: соберите узлы в фрагмент, а затем одной операцией "
            "list.append(fragment) вставьте всё сразу — фрагмент при этом опустошится, "
            "а его дети перейдут в список.",
        ),
        example(
            "javascript",
            """
            const list = document.querySelector('#list');
            const fragment = document.createDocumentFragment();

            for (let i = 1; i <= 100; i += 1) {
              const li = document.createElement('li');
              li.textContent = `Пункт ${i}`;
              fragment.append(li);
            }

            list.append(fragment); // одна операция вставки вместо ста
            console.log(list.children.length); // 100
            console.log(fragment.childNodes.length); // 0 — фрагмент опустел
            """,
        ),
        text(
            "Вывод демонстрирует, что все сто пунктов оказались в списке, а фрагмент "
            "после вставки стал пустым. Такой приём особенно полезен при рендеринге "
            "больших таблиц и списков.\n\n"
            "Отдельно стоит упомянуть тег template. Его содержимое не отображается и не "
            "исполняется, но хранится в свойстве content как готовый фрагмент. "
            "Клонируя его через cloneNode(true), можно быстро создавать повторяющиеся "
            "блоки разметки и заполнять их данными."
        ),
        example(
            "javascript",
            """
            // В разметке: <template id="card"><article class="card"><h2></h2></article></template>
            const template = document.querySelector('#card');
            const card = template.content.cloneNode(true); // true — копировать всё поддерево
            card.querySelector('h2').textContent = 'Заголовок карточки';
            document.body.append(card);

            console.log(document.querySelectorAll('.card').length);
            """,
        ),
        example(
            "text",
            """
            Вывод:
            1
            """,
        ),
        heading("Атрибуты, данные и классы"),
        text(
            "У элемента есть два способа работы с атрибутами: свойства объекта и "
            "универсальные методы setAttribute, getAttribute, hasAttribute, "
            "removeAttribute. Для стандартных атрибутов удобнее свойства: img.src, "
            "img.alt, el.id, el.hidden. Они типизированы — например, hidden возвращает "
            "логическое значение, а не строку. Универсальные методы нужны для "
            "нестандартных атрибутов и для случаев, когда имя известно только в "
            "виде строки.\n\n"
            "Для пользовательских данных есть отдельный механизм — data-атрибуты. "
            "Атрибут data-user-name доступен через свойство dataset.userName: дефисы "
            "в имени превращаются в camelCase. Это удобный способ хранить в разметке "
            "идентификаторы и параметры, не смешивая их с классами.\n\n"
            "Классы изменяют через свойство classList. Оно ведёт себя как набор и "
            "предлагает методы add, remove, toggle, replace, contains. "
            "В отличие от присваивания classList не стирает остальные классы, "
            "а toggle возвращает новое состояние — удобно для переключателей."
        ),
        example(
            "javascript",
            """
            const card = document.querySelector('.card');

            // Стандартные атрибуты как свойства
            card.id = 'main-card';
            card.hidden = true;

            // Универсальные методы
            card.setAttribute('aria-label', 'Карточка');
            console.log(card.getAttribute('aria-label')); // Карточка
            console.log(card.hasAttribute('hidden'));      // true
            card.removeAttribute('hidden');

            // data-атрибуты
            card.dataset.userName = 'alex'; // в разметке data-user-name="alex"
            card.dataset.id = '42';
            console.log(card.dataset.id);   // 42
            console.log(card.dataset.userName); // alex

            // Классы
            card.classList.add('active', 'visible');
            console.log(card.classList.contains('active')); // true
            card.classList.toggle('visible');                // false
            card.classList.toggle('visible');                // true
            card.classList.replace('active', 'selected');
            console.log(card.className);
            """,
        ),
        text(
            "Обратите внимание на последний вывод: класс active заменён на selected, "
            "видимость включена повторным toggle, а hidden вместе с атрибутом был удалён "
            "ещё раньше — в className его нет. Свойство className всегда возвращает всю "
            "строку целиком, и присваивание ей значения стирает прежние классы."
        ),
        example(
            "text",
            """
            Вывод:
            Карточка
            true
            42
            alex
            true
            false
            true
            card selected visible
            """,
        ),
        callout(
            "warning",
            "className стирает всё",
            "el.className = 'active' удаляет все прежние классы элемента. Если нужно добавить "
            "класс, используйте el.classList.add('active') — он сохранит остальные. Присваивание "
            "полной строки уместно только тогда, когда вы осознанно заменяете набор классов целиком.",
        ),
        heading("Текст, HTML и стили"),
        text(
            "Содержимое элемента меняют тремя свойствами. textContent задаёт текст: "
            "строки вроде <b>привет</b> попадут на страницу как есть, без интерпретации. "
            "innerHTML разбирает строку как HTML и создаёт из неё элементы. "
            "innerText учитывает отображение и работает медленнее, потому что требует "
            "пересчёта вёрстки.\n\n"
            "Разница между textContent и innerHTML — не косметическая. Если строку "
            "прислал пользователь и вы вставили её через innerHTML, браузер выполнит "
            "любую разметку из неё, включая тег img со скриптом в атрибуте onerror. "
            "Такой класс атак называется XSS (cross-site scripting, межсайтовый "
            "скриптинг). Правило простое: текст пользователя — только через textContent "
            "или createTextNode, а innerHTML оставьте для статичной разметки, которую "
            "вы контролируете сами.\n\n"
            "Для оформления применяют два подхода. Inline-стили через el.style меняют "
            "конкретное свойство: имена в camelCase, значения в виде строк с единицами "
            "измерения. Вычисленные значения, в которых уже учтены все CSS-правила, "
            "читают через getComputedStyle. Второй подход — переключение классов: "
            "стили лежат в CSS-файле, а скрипт лишь добавляет или убирает класс. "
            "Так код проще поддерживать, потому что оформление не размазано по JavaScript."
        ),
        example(
            "javascript",
            """
            const message = document.querySelector('#message');
            const userInput = '<img src=x onerror=alert(1)>';

            // Безопасно: строка останется текстом
            message.textContent = userInput;
            console.log(message.children.length); // 0

            // Опасно при работе с данными пользователя
            message.innerHTML = userInput;
            console.log(message.children.length); // 1 — появился элемент img

            // Стили
            message.style.color = 'crimson';
            message.style.fontSize = '18px';
            message.style.setProperty('--accent', '#0a7');
            message.style.cssText = 'color: navy; font-size: 20px';

            const color = getComputedStyle(message).color;
            console.log(color); // rgb(0, 0, 128)
            """,
        ),
        text(
            "Вывод показывает, что textContent не создал дочерних элементов, а innerHTML "
            "создал тег img. Вычисленный цвет вернулся уже в нормализованном виде rgb."
        ),
        example(
            "text",
            """
            Вывод:
            0
            1
            rgb(0, 0, 128)
            """,
        ),
        heading("События и addEventListener"),
        text(
            "Событие — это сигнал о том, что на странице что-то произошло: клик, нажатие "
            "клавиши, отправка формы, загрузка изображения. Источником служит элемент "
            "или сам документ. Чтобы реагировать на событие, на нём регистрируют "
            "слушатель методом addEventListener: первым аргументом идёт имя события, "
            "вторым — функция-обработчик, третьим — необязательный объект настроек.\n\n"
            "У настроек есть три полезных флага. once: true удаляет слушатель после "
            "первого вызова. passive: true обещает браузеру, что обработчик не вызовет "
            "preventDefault, и позволяет прокрутке не ждать выполнения JavaScript. "
            "Аргумент signal принимает AbortSignal, чтобы отписать обработчик одной "
            "операцией отмены — это удобный способ массово снять слушатели при закрытии "
            "модального окна или уничтожении компонента.\n\n"
            "Обработчик получает объект события. В нём полезны тип события, цель target, "
            "элемент с зарегистрированным слушателем currentTarget и методы управления "
            "поведением по умолчанию."
        ),
        example(
            "javascript",
            """
            const button = document.querySelector('#save');

            const onClick = (event) => {
              console.log(event.type);          // click
              console.log(event.target.id);     // save
              console.log(event.currentTarget.id); // save
              console.log(event.bubbles);       // true
              console.log(event.isTrusted);     // true для клика пользователя
            };

            button.addEventListener('click', onClick);
            button.removeEventListener('click', onClick);

            // Обработчик, который снимается после первого срабатывания
            button.addEventListener('click', () => console.log('только один раз'), {
              once: true,
            });

            // Отписка через AbortController
            const controller = new AbortController();
            button.addEventListener('mouseover', () => console.log('наведение'), {
              signal: controller.signal,
            });
            controller.abort(); // все слушатели с этим сигналом удалены
            """,
        ),
        text(
            "Если пользователь нажал кнопку, консоль выведет строки ниже. Слушатель с once "
            "сработает единожды, а слушатель mouseover будет ждать наведения курсора."
        ),
        example(
            "text",
            """
            Вывод:
            click
            save
            save
            true
            true
            только один раз
            """,
        ),
        heading("Фазы события и делегирование"),
        text(
            "Событие не появляется прямо на элементе-цели. Сначала оно проходит фазу "
            "перехвата: от window вниз по дереву до цели. Затем достигает фазы цели. "
            "Наконец идёт фаза всплытия: от цели обратно вверх до window. Слушатель, "
            "зарегистрированный обычным образом, срабатывает на всплытии, а с флагом "
            "capture: true — на перехвате. Порядок для вложенных элементов поэтому такой: "
            "обработчик перехвата родителя, обработчик цели, обработчик всплытия родителя.\n\n"
            "Всплытие позволяет применять делегирование. Вместо того чтобы вешать "
            "обработчик на каждый из ста пунктов списка, слушатель ставят один раз на "
            "родительский ul. Внутри обработчика по event.target определяют, по какому "
            "конкретному узлу кликнули, а метод closest помогает подняться до нужного "
            "пункта, даже если клик пришёлся на вложенный span с иконкой.\n\n"
            "Делегирование экономит память и, что важнее, автоматически работает для "
            "элементов, добавленных в DOM позже. При этом не забывайте проверять, что "
            "найденный пункт действительно принадлежит этому списку: событие могло "
            "прийти из вложенного списка с похожей разметкой."
        ),
        example(
            "javascript",
            """
            const list = document.querySelector('#list');

            // Один слушатель на весь список вместо слушателя на каждом li
            list.addEventListener('click', (event) => {
              const item = event.target.closest('li');
              if (!item || !list.contains(item)) return;

              const id = item.dataset.id;
              console.log(`Кликнули по пункту с id=${id}`);
              item.classList.toggle('done');
            });

            // Порядок фаз для вложенного элемента
            const parent = document.querySelector('#parent');
            const child = document.querySelector('#child');

            parent.addEventListener('click', () => console.log('capture'), { capture: true });
            parent.addEventListener('click', () => console.log('bubble'));
            child.addEventListener('click', () => console.log('target'));
            child.click();
            """,
        ),
        text(
            "Клик по второму пункту списка и программный клик по child дадут такую "
            "последовательность сообщений. Обратите внимание: обработчик цели "
            "зарегистрирован на child без флага capture, но всё равно срабатывает "
            "между перехватом и всплытием родителя."
        ),
        example(
            "text",
            """
            Вывод:
            Кликнули по пункту с id=1
            capture
            target
            bubble
            """,
        ),
        callout(
            "warning",
            "stopPropagation и stopImmediatePropagation",
            "preventDefault отменяет действие браузера по умолчанию: переход по ссылке, отправку "
            "формы, прокрутку. stopPropagation прекращает движение события вверх, но остальные "
            "слушатели на том же элементе продолжают работу. stopImmediatePropagation останавливает "
            "и их. Используйте эти методы осознанно: они ломают делегирование на родителях.",
        ),
        heading("Полезные события браузера"),
        text(
            "Большинство событий слушаются так же, как click, но у некоторых есть "
            "особенности. Событие DOMContentLoaded срабатывает, когда браузер разобрал "
            "HTML и построил дерево, но ещё не загрузил картинки и стили. Событие load "
            "у window наступает позже, когда загружены все ресурсы. Если скрипт подключён "
            "в конце body, обычно можно работать сразу, без ожидания DOMContentLoaded.\n\n"
            "Для полей ввода используют события keydown и keyup для отдельных клавиш, "
            "input для любого изменения значения и submit для отправки формы. "
            "События resize и scroll происходят очень часто, поэтому их обработчики "
            "стоит либо ограничивать по частоте, либо помечать passive: true, если они "
            "не меняют поведение по умолчанию. События focus и blur не всплывают, "
            "а focusin и focusout всплывают — при делегировании нужны именно они.\n\n"
            "События online и offline на window сообщают о состоянии сети, а "
            "visibilitychange на document — о том, что вкладка была скрыта или снова "
            "показана. Во многих браузерах клики по аудио и видео в фоновой вкладке "
            "также обрабатываются с задержкой, поэтому пауза воспроизведения при "
            "скрытии вкладки — частая практика."
        ),
        example(
            "javascript",
            """
            document.addEventListener('DOMContentLoaded', () => {
              console.log('DOM построен');
            });

            window.addEventListener('load', () => {
              console.log('Все ресурсы загружены');
            });

            const input = document.querySelector('#search');
            input.addEventListener('keydown', (event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                console.log(`Поиск: ${input.value}`);
              }
            });

            window.addEventListener('scroll', () => {
              console.log('прокрутка');
            }, { passive: true });

            document.addEventListener('visibilitychange', () => {
              console.log(document.hidden ? 'вкладка скрыта' : 'вкладка видна');
            });
            """,
        ),
        text(
            "При загрузке страницы и нажатии Enter в поле ввода консоль выведет строки "
            "в таком порядке — load наступает позже DOMContentLoaded, а ввод выводом "
            "подтверждает значение поля."
        ),
        example(
            "text",
            """
            Вывод:
            DOM построен
            Все ресурсы загружены
            вкладка видна
            Поиск: javascript
            """,
        ),
        heading("Собственные события"),
        text(
            "Иногда компоненту нужно сообщить о событии, которого нет в браузере: "
            "например, «товар добавлен в корзину». Для этого служит CustomEvent. "
            "В объекте настроек флаг bubbles делает событие всплывающим, а свойство "
            "detail хранит произвольные данные. Событие отправляют методом dispatchEvent, "
            "а слушают так же, как обычные. Такой приём позволяет слабо связывать "
            "модули приложения: кнопка не знает о корзине, она лишь объявляет событие."
        ),
        example(
            "javascript",
            """
            document.addEventListener('product-added', (event) => {
              console.log(`Добавлен товар ${event.detail.name}, цена ${event.detail.price}`);
            });

            const event = new CustomEvent('product-added', {
              bubbles: true,
              cancelable: true,
              detail: { name: 'Клавиатура', price: 4500 },
            });

            document.dispatchEvent(event);
            """,
        ),
        example(
            "text",
            """
            Вывод:
            Добавлен товар Клавиатура, цена 4500
            """,
        ),
        heading("Типичные ошибки"),
        table(
            ["Ошибка", "Что происходит", "Как правильно"],
            [
                ["el.innerHTML = userInput", "Пользовательская строка исполняется как HTML, открывая путь к XSS", "el.textContent = userInput или createElement с textContent"],
                ["els.map(...) у результата querySelectorAll", "У NodeList нет метода map, возникает TypeError", "[...els].map(...) или Array.from(els)"],
                ["el.className = 'active'", "Стираются все ранее установленные классы", "el.classList.add('active')"],
                ["Слушатель на каждом li в большом списке", "Много обработчиков и утечки памяти при пересоздании списка", "Один слушатель на ul плюс e.target.closest('li')"],
                ["e.target вместо e.currentTarget", "При клике по вложенному span возвращается span, а не кнопка-слушатель", "e.currentTarget или closest нужного тега"],
                ["document.querySelector('.item').textContent", "При отсутствии элемента получаем TypeError: null", "Проверить результат на null или использовать ?."],
                ["for...in по NodeList", "Перебираются индексы и служебные свойства, а не элементы", "for...of или forEach"],
            ],
        ),
        heading("Практика"),
        text(
            "Выполняйте задания по порядку в отдельном HTML-файле, открывая страницу в "
            "браузере и проверяя результат в консоли разработчика. Скрипт подключайте "
            "через тег script в конце body."
        ),
        numbered(
            "Счётчик: создайте на странице кнопку и элемент вывода. По клику увеличивайте число на единицу и обновляйте текст через textContent.",
            "Список задач: по кнопке добавляйте новый пункт в список через createElement, а по делегированному клику на пункт переключайте класс done.",
            "Безопасный вывод: сделайте поле ввода и предпросмотр. Выводите введённый текст через textContent, а затем сравните поведение с innerHTML на строке <b>тест</b>.",
            "Пакетная вставка: сгенерируйте 50 пунктов списка в DocumentFragment и вставьте их одной операцией. Измерьте время через performance.now() до и после и сравните со вставкой в цикле.",
            "Фильтр по data-атрибуту: добавьте пунктам data-category, выведите кнопки категорий и по клику скрывайте неподходящие пункты, переключая класс hidden через classList.",
        ),
        text(
            "Для четвёртого задания ожидаемый вывод в консоли выглядит примерно так — "
            "точные миллисекунды зависят от машины и браузера."
        ),
        example(
            "text",
            """
            Вывод:
            Вставлено одним фрагментом: 50, 1.2 мс
            Вставлено в цикле: 50, 4.7 мс
            """,
        ),
        callout(
            "success",
            "Подсказка к заданию 5",
            "Для фильтрации переберите [...list.children] циклом for...of и вызовите item.classList.toggle('hidden', item.dataset.category !== category). Второй аргумент toggle задаёт нужное состояние явно.",
        ),
        heading("Проверьте себя"),
        numbered(
            "Чем querySelector отличается от getElementById?",
            "Что вернёт el.closest('.card'), если сам элемент el уже имеет класс card?",
            "В чём разница между querySelectorAll и getElementsByClassName?",
            "Зачем нужен DocumentFragment?",
            "Почему innerHTML опасен для пользовательских данных?",
            "Как сделать так, чтобы один обработчик обслуживал все пункты списка?",
        ),
        heading("Ответы", 3),
        numbered(
            "querySelector принимает любой CSS-селектор и возвращает первый элемент или null, а getElementById ищет только по идентификатору и обычно работает быстрее.",
            "Сам элемент el: closest проверяет текущий узел, потом поднимается вверх по предкам.",
            "querySelectorAll возвращает статичный NodeList, а getElementsByClassName — живой HTMLCollection, который обновляется вместе с DOM.",
            "Фрагмент позволяет собрать группу узлов вне документа и вставить их одной операцией, избегая множественных перерисовок.",
            "innerHTML разбирает строку как разметку, поэтому пользователь может внедрить теги и скрипты, что приводит к XSS. Для текста используют textContent.",
            "Повесить один слушатель на родительский список и внутри обработчика найти нужный пункт через event.target.closest('li').",
        ),
        heading("Итоги"),
        bullets(
            "DOM — дерево объектов, которое браузер строит из HTML; узлы бывают Element, Text, Comment и Document.",
            "Поиск: querySelector и querySelectorAll принимают CSS-селектор, getElementById ищет по идентификатору; NodeList и HTMLCollection — не массивы.",
            "Навигация: parentElement, children, firstElementChild, nextElementSibling для элементов и closest для поиска предка.",
            "Создание и вставка: createElement, append и prepend, before и after, replaceWith, remove, DocumentFragment для пакетных операций.",
            "Атрибуты: свойства и setAttribute, data-атрибуты через dataset, классы через classList без риска стереть остальные.",
            "Содержимое: textContent безопасен, innerHTML разбирает разметку и опасен для данных пользователя.",
            "События проходят фазы перехвата, цели и всплытия; делегирование через closest даёт один слушатель на родителей.",
            "Регистрация и снятие слушателей: addEventListener с настройками once и signal, removeEventListener, AbortController для массовой отписки.",
        ),
        heading("Что дальше"),
        text(
            "Вы научились читать и изменять страницу напрямую. Следующий шаг — работать "
            "с деревом DOM так же организованно, как с обычными структурами данных: "
            "перебирать найденные коллекции, обрабатывать формы и собирать данные с "
            "помощью массивов и объектов. В следующих уроках разберём формы и валидацию, "
            "а затем перейдём к асинхронности, чтобы часть DOM можно было заполнять "
            "данными с сервера."
        ),
        heading("Если хотите углубиться"),
        bullets(
            "MDN: Document Object Model — developer.mozilla.org/ru/docs/Web/API/Document_Object_Model",
            "MDN: Introduction to events — developer.mozilla.org/ru/docs/Learn/JavaScript/Building_blocks/Events",
            "javascript.info: Документ — javascript.info/dom-nodes",
            "Спецификация DOM — dom.spec.whatwg.org",
            "MDN: DocumentFragment — developer.mozilla.org/ru/docs/Web/API/DocumentFragment",
        ),
    ],
}
