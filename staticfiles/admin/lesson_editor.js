/* Visual lesson editor for the Django admin.
 *
 * The editor works on a JSON block list (the same structure the lesson page
 * renders) and saves it through the admin endpoint with fetch(). No build
 * step, no dependencies.
 */
(function () {
    'use strict';

    var payloadEl = document.getElementById('le-payload');
    var app = document.getElementById('leApp');
    if (!payloadEl || !app) {
        return;
    }

    var payload = {};
    try {
        payload = JSON.parse(payloadEl.textContent || '{}');
    } catch (error) {
        payload = {};
    }

    var SAVE_URL = app.getAttribute('data-save-url');
    var LESSON_ID = app.getAttribute('data-lesson-id');
    var CAN_CHANGE = app.getAttribute('data-can-change') === '1';
    var DRAFT_KEY = 'kernify.lesson-editor.draft.' + LESSON_ID;
    var choices = payload.choices || {};

    var BLOCK_LABELS = {
        heading: { label: 'Заголовок', icon: 'H' },
        text: { label: 'Текст', icon: '¶' },
        code: { label: 'Код', icon: '</>' },
        list: { label: 'Список', icon: '≡' },
        table: { label: 'Таблица', icon: '▤' },
        callout: { label: 'Врезка', icon: '!' },
        blockquote: { label: 'Цитата', icon: '❝' },
        image: { label: 'Изображение', icon: '▣' },
        video: { label: 'Видео', icon: '▶' },
        divider: { label: 'Разделитель', icon: '—' }
    };

    var CALLOUT_LABELS = {
        info: 'Справка',
        success: 'Совет',
        warning: 'Внимание',
        danger: 'Ошибка'
    };

    var SAMPLE_LANGUAGE = 'python';

    // ---------------------------------------------------------------- state

    var state = {
        content: Array.isArray(payload.content) ? deepClone(payload.content) : [],
        display: Object.assign({ font: 'sans', size: 17, line_height: 1.7, width: 68 }, payload.display || {}),
        meta: {
            name: payload.name || '',
            short_description: payload.short_description || '',
            status: payload.status || 'draft',
            difficulty: payload.difficulty || 'beginner',
            lesson_type: payload.lesson_type || 'text',
            xp_reward: payload.xp_reward == null ? 10 : payload.xp_reward,
            estimated_minutes: payload.estimated_minutes == null ? 15 : payload.estimated_minutes
        },
        preview: false,
        dirty: false,
        saving: false,
        collapsed: {}
    };

    var dragIndex = null;

    // ------------------------------------------------------------- elements

    var blocksRoot = document.getElementById('leBlocks');
    var outlineRoot = document.getElementById('leOutline');
    var emptyNode = document.getElementById('leEmpty');
    var addBar = document.getElementById('leAddBar');
    var previewRoot = document.getElementById('lePreview');
    var previewBtn = document.getElementById('lePreviewBtn');
    var saveBtn = document.getElementById('leSaveBtn');
    var saveState = document.getElementById('leSaveState');
    var versionChip = document.getElementById('leVersionChip');
    var statsNode = document.getElementById('leStats');
    var blockCountNode = document.getElementById('leBlockCount');
    var toastNode = document.getElementById('leToast');
    var carryNode = document.getElementById('leCarry');
    var titleNode = document.getElementById('leTitle');

    // --------------------------------------------------------------- helpers

    function deepClone(value) {
        return JSON.parse(JSON.stringify(value));
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function el(tag, className, text) {
        var node = document.createElement(tag);
        if (className) {
            node.className = className;
        }
        if (text != null) {
            node.textContent = text;
        }
        return node;
    }

    function clamp(value, min, max, fallback) {
        var number = Number(value);
        if (!isFinite(number)) {
            number = fallback;
        }
        return Math.min(max, Math.max(min, number));
    }

    function splitLines(value) {
        return String(value == null ? '' : value).split('\n');
    }

    function firstLine(block) {
        if (block.type === 'divider') {
            return 'Горизонтальная линия';
        }
        if (block.type === 'video') {
            return block.url || 'Ссылка на видео';
        }
        if (block.type === 'image') {
            return block.alt || block.caption || block.url || 'Изображение';
        }
        if (block.type === 'table') {
            return (block.headers || []).join(' · ') || 'Таблица';
        }
        if (block.type === 'list') {
            return (block.items || []).filter(Boolean)[0] || 'Список';
        }
        return String(block.content || '').split('\n')[0] || 'Пустой блок';
    }

    function plainText(block) {
        var parts = [];
        ['content', 'title'].forEach(function (key) {
            if (typeof block[key] === 'string') {
                parts.push(block[key]);
            }
        });
        if (Array.isArray(block.items)) {
            parts.push(block.items.join(' '));
        }
        if (Array.isArray(block.headers)) {
            parts.push(block.headers.join(' '));
        }
        if (Array.isArray(block.rows)) {
            block.rows.forEach(function (row) {
                if (Array.isArray(row)) {
                    parts.push(row.join(' '));
                }
            });
        }
        return parts.join(' ');
    }

    function getCookie(name) {
        var parts = document.cookie ? document.cookie.split(';') : [];
        for (var i = 0; i < parts.length; i += 1) {
            var pair = parts[i].trim();
            if (pair.indexOf(name + '=') === 0) {
                return decodeURIComponent(pair.slice(name.length + 1));
            }
        }
        return '';
    }

    // ------------------------------------------------------------ draft/dirty

    var draftTimer = null;

    function markDirty() {
        state.dirty = true;
        setSaveState('Не сохранено', 'dirty');
        scheduleDraft();
        updateStats();
        if (state.preview) {
            renderPreview();
        }
    }

    function scheduleDraft() {
        if (!CAN_CHANGE) {
            return;
        }
        window.clearTimeout(draftTimer);
        draftTimer = window.setTimeout(saveDraft, 800);
    }

    function saveDraft() {
        try {
            window.localStorage.setItem(DRAFT_KEY, JSON.stringify({
                content: state.content,
                meta: state.meta,
                display: state.display,
                savedAt: Date.now()
            }));
        } catch (error) {
            /* localStorage can be disabled — the editor still works */
        }
    }

    function clearDraft() {
        try {
            window.localStorage.removeItem(DRAFT_KEY);
        } catch (error) {
            /* ignore */
        }
    }

    function setSaveState(text, kind) {
        saveState.textContent = text;
        saveState.className = 'le-save-state' + (kind ? ' is-' + kind : '');
    }

    function toast(message, kind) {
        toastNode.textContent = message;
        toastNode.className = 'le-toast' + (kind ? ' is-' + kind : '');
        toastNode.hidden = false;
        window.clearTimeout(toast._timer);
        toast._timer = window.setTimeout(function () {
            toastNode.hidden = true;
        }, 3200);
    }

    // -------------------------------------------------------------- defaults

    function defaultBlock(type) {
        switch (type) {
        case 'heading':
            return { type: 'heading', level: 2, content: '' };
        case 'code':
            return { type: 'code', language: SAMPLE_LANGUAGE, content: '' };
        case 'list':
            return { type: 'list', ordered: false, items: [''] };
        case 'table':
            return { type: 'table', headers: ['Колонка 1', 'Колонка 2'], rows: [['', '']] };
        case 'callout':
            return { type: 'callout', style: 'info', title: '', content: '' };
        case 'blockquote':
            return { type: 'blockquote', content: '' };
        case 'image':
            return { type: 'image', url: '', alt: '', caption: '' };
        case 'video':
            return { type: 'video', url: '' };
        case 'divider':
            return { type: 'divider' };
        default:
            return { type: 'text', content: '' };
        }
    }

    function convertBlock(block, newType) {
        var next = defaultBlock(newType);
        if (['text', 'blockquote', 'heading', 'callout'].indexOf(newType) !== -1 &&
                ['text', 'blockquote', 'heading', 'callout'].indexOf(block.type) !== -1) {
            next.content = block.content || '';
        }
        if (newType === 'code' && block.type === 'code') {
            next.content = block.content || '';
            next.language = block.language || SAMPLE_LANGUAGE;
        }
        if (newType === 'list' && block.type !== 'list') {
            next.items = splitLines(block.content || '').filter(function (line) { return line.trim(); });
            if (!next.items.length) {
                next.items = [''];
            }
        }
        return next;
    }

    // ------------------------------------------------------------ block cards

    function makeInput(value, onInput, options) {
        var input = el('input', 'le-input');
        input.type = (options && options.type) || 'text';
        input.value = value == null ? '' : value;
        if (options && options.placeholder) {
            input.placeholder = options.placeholder;
        }
        if (options && options.list) {
            input.setAttribute('list', options.list);
        }
        input.addEventListener('input', function () {
            onInput(input.value);
        });
        return input;
    }

    function makeTextarea(value, onInput, options) {
        var area = el('textarea', 'le-input' + (options && options.code ? ' le-code-input' : ''));
        area.value = value == null ? '' : value;
        area.rows = (options && options.rows) || 6;
        if (options && options.placeholder) {
            area.placeholder = options.placeholder;
        }
        if (options && options.code) {
            area.spellcheck = false;
            area.addEventListener('keydown', function (event) {
                if (event.key === 'Tab') {
                    event.preventDefault();
                    insertAtCursor(area, '    ');
                }
            });
        }
        area.addEventListener('input', function () {
            onInput(area.value);
        });
        return area;
    }

    function field(labelText, control, className) {
        var wrap = el('label', 'le-field' + (className ? ' ' + className : ''));
        wrap.appendChild(el('span', null, labelText));
        wrap.appendChild(control);
        return wrap;
    }

    function insertAtCursor(area, text) {
        var start = area.selectionStart;
        var end = area.selectionEnd;
        var value = area.value;
        area.value = value.slice(0, start) + text + value.slice(end);
        area.selectionStart = area.selectionEnd = start + text.length;
        area.dispatchEvent(new Event('input'));
    }

    function wrapSelection(area, before, after, placeholder) {
        var start = area.selectionStart;
        var end = area.selectionEnd;
        var value = area.value;
        var selected = value.slice(start, end) || placeholder || '';
        area.value = value.slice(0, start) + before + selected + after + value.slice(end);
        area.focus();
        area.selectionStart = start + before.length;
        area.selectionEnd = start + before.length + selected.length;
        area.dispatchEvent(new Event('input'));
    }

    function formatToolbar(area) {
        var bar = el('div', 'le-toolbar');
        var actions = [
            { label: 'Ж', title: 'Жирный: **текст**', before: '**', after: '**', placeholder: 'текст' },
            { label: 'К', title: 'Курсив: *текст*', before: '*', after: '*', placeholder: 'текст', italic: true },
            { label: '‹/›', title: 'Код в строке: `код`', before: '`', after: '`', placeholder: 'код' },
            { label: 'Ссылка', title: 'Ссылка: [текст](https://…)', before: '[', after: '](https://)', placeholder: 'текст' }
        ];
        actions.forEach(function (action) {
            var button = el('button', 'le-icon-btn', action.label);
            button.type = 'button';
            button.title = action.title;
            if (action.italic) {
                button.style.fontStyle = 'italic';
            }
            button.addEventListener('click', function () {
                wrapSelection(area, action.before, action.after, action.placeholder);
            });
            bar.appendChild(button);
        });
        return bar;
    }

    function renderFields(block, index) {
        var body = el('div', 'le-block-body');

        if (block.type === 'heading') {
            var headingRow = el('div', 'le-row');
            var level = el('select', 'le-input');
            [1, 2, 3, 4, 5, 6].forEach(function (number) {
                var option = el('option', null, 'H' + number);
                option.value = String(number);
                level.appendChild(option);
            });
            level.value = String(block.level || 2);
            level.addEventListener('change', function () {
                block.level = Number(level.value) || 2;
                markDirty();
                updateOutline();
            });
            headingRow.appendChild(field('Уровень', level));
            headingRow.appendChild(field('Текст заголовка', makeInput(block.content, function (value) {
                block.content = value;
                markDirty();
                updateOutline();
            }, { placeholder: 'Например: Переменные и типы данных' })));
            body.appendChild(headingRow);

        } else if (block.type === 'text') {
            var textArea = makeTextarea(block.content, function (value) {
                block.content = value;
                markDirty();
                updateOutline();
            }, { rows: 7, placeholder: 'Абзац текста. Пустая строка начинает новый абзац.' });
            body.appendChild(formatToolbar(textArea));
            body.appendChild(textArea);
            body.appendChild(el('p', 'le-hint', 'Поддерживается **жирный**, *курсив*, `код` и [ссылка](https://example.com). Пустая строка разделяет абзацы.'));

        } else if (block.type === 'code') {
            var codeRow = el('div', 'le-row');
            var language = makeInput(block.language || SAMPLE_LANGUAGE, function (value) {
                block.language = value.trim().toLowerCase() || 'text';
                markDirty();
            }, { placeholder: 'python', list: 'leLanguages' });
            codeRow.appendChild(field('Язык (подсветка)', language));
            body.appendChild(codeRow);
            body.appendChild(field('Код', makeTextarea(block.content, function (value) {
                block.content = value;
                markDirty();
                updateOutline();
            }, { rows: 10, code: true, placeholder: 'print("Привет")' })));
            body.appendChild(el('p', 'le-hint', 'Tab добавляет отступ в 4 пробела. Код выводится моноширинным шрифтом с подсветкой синтаксиса.'));

        } else if (block.type === 'list') {
            var ordered = el('input');
            ordered.type = 'checkbox';
            ordered.checked = !!block.ordered;
            ordered.addEventListener('change', function () {
                block.ordered = ordered.checked;
                markDirty();
            });
            var orderedLabel = el('label', 'le-checkbox');
            orderedLabel.appendChild(ordered);
            orderedLabel.appendChild(el('span', null, 'Нумерованный список (1, 2, 3)'));
            body.appendChild(orderedLabel);
            body.appendChild(field('Пункты (каждый с новой строки)', makeTextarea((block.items || []).join('\n'), function (value) {
                block.items = splitLines(value);
                markDirty();
                updateOutline();
            }, { rows: 5, placeholder: 'Первый пункт\nВторой пункт' })));

        } else if (block.type === 'table') {
            body.appendChild(field('Заголовки колонок (каждый с новой строки)', makeTextarea((block.headers || []).join('\n'), function (value) {
                block.headers = splitLines(value);
                markDirty();
                updateOutline();
            }, { rows: 2, placeholder: 'Оператор\nЧто делает' })));
            var rowsText = (block.rows || []).map(function (row) {
                return (row || []).join(' | ');
            }).join('\n');
            body.appendChild(field('Строки таблицы (колонки через |)', makeTextarea(rowsText, function (value) {
                block.rows = splitLines(value).filter(function (line) {
                    return line.trim() !== '';
                }).map(function (line) {
                    return line.split('|').map(function (cell) {
                        return cell.trim();
                    });
                });
                markDirty();
                updateOutline();
            }, { rows: 6, placeholder: '+ | сложение\n- | вычитание' })));
            body.appendChild(el('p', 'le-hint', 'Пример строки: <b>len() | длина строки или списка</b>. Разделитель колонок — вертикальная черта.'));

        } else if (block.type === 'callout') {
            var styleRow = el('div', 'le-row');
            var styleSelect = el('select', 'le-input');
            Object.keys(CALLOUT_LABELS).forEach(function (key) {
                var option = el('option', null, CALLOUT_LABELS[key]);
                option.value = key;
                styleSelect.appendChild(option);
            });
            styleSelect.value = block.style || 'info';
            styleSelect.addEventListener('change', function () {
                block.style = styleSelect.value;
                markDirty();
            });
            styleRow.appendChild(field('Вид', styleSelect));
            styleRow.appendChild(field('Заголовок (необязательно)', makeInput(block.title, function (value) {
                block.title = value;
                markDirty();
                updateOutline();
            }, { placeholder: 'Например: Частая ошибка' })));
            body.appendChild(styleRow);
            var calloutArea = makeTextarea(block.content, function (value) {
                block.content = value;
                markDirty();
                updateOutline();
            }, { rows: 4, placeholder: 'Текст врезки' });
            body.appendChild(formatToolbar(calloutArea));
            body.appendChild(calloutArea);

        } else if (block.type === 'blockquote') {
            var quoteArea = makeTextarea(block.content, function (value) {
                block.content = value;
                markDirty();
                updateOutline();
            }, { rows: 4, placeholder: 'Цитата или определение' });
            body.appendChild(formatToolbar(quoteArea));
            body.appendChild(quoteArea);

        } else if (block.type === 'image') {
            body.appendChild(field('Ссылка на изображение', makeInput(block.url, function (value) {
                block.url = value;
                markDirty();
                updateOutline();
            }, { placeholder: 'https://… или /media/…' })));
            var imageRow = el('div', 'le-row');
            imageRow.appendChild(field('Alt-текст', makeInput(block.alt, function (value) {
                block.alt = value;
                markDirty();
            }, { placeholder: 'Что изображено' })));
            imageRow.appendChild(field('Подпись', makeInput(block.caption, function (value) {
                block.caption = value;
                markDirty();
                updateOutline();
            }, { placeholder: 'Подпись под изображением' })));
            body.appendChild(imageRow);
            body.appendChild(el('p', 'le-hint', 'Alt-текст нужен для доступности: его читают скринридеры и показывают, если картинка не загрузилась.'));

        } else if (block.type === 'video') {
            body.appendChild(field('Ссылка на встраиваемое видео', makeInput(block.url, function (value) {
                block.url = value;
                markDirty();
                updateOutline();
            }, { placeholder: 'https://www.youtube.com/embed/…' })));
            body.appendChild(el('p', 'le-hint', 'Нужна ссылка формата embed, а не обычная страница просмотра.'));

        } else if (block.type === 'divider') {
            body.appendChild(el('p', 'le-hint', 'Горизонтальная линия, которая визуально разделяет части урока.'));

        } else {
            body.appendChild(el('p', 'le-hint', 'Неизвестный тип блока «' + escapeHtml(block.type || '?') + '». Его можно отредактировать как JSON.'));
            body.appendChild(makeTextarea(JSON.stringify(block, null, 2), function (value) {
                var parsed;
                try {
                    parsed = JSON.parse(value);
                } catch (error) {
                    return; /* keep typing until the JSON is valid */
                }
                if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
                    return;
                }
                Object.keys(block).forEach(function (key) {
                    delete block[key];
                });
                Object.keys(parsed).forEach(function (key) {
                    block[key] = parsed[key];
                });
                markDirty();
                updateOutline();
            }, { rows: 8, code: true }));
        }

        return body;
    }

    function renderBlockCard(block, index) {
        var card = el('div', 'le-block' + (state.collapsed[index] ? ' le-collapsed' : ''));
        card.setAttribute('data-index', String(index));
        card.setAttribute('data-type', block.type || 'text');

        var head = el('div', 'le-block-head');
        head.draggable = true;

        head.appendChild(el('span', 'le-grip', '⠿'));

        var typeSelect = el('select', 'le-type-select');
        Object.keys(BLOCK_LABELS).forEach(function (type) {
            var option = el('option', null, BLOCK_LABELS[type].label);
            option.value = type;
            typeSelect.appendChild(option);
        });
        typeSelect.value = block.type;
        typeSelect.addEventListener('change', function () {
            state.content[index] = convertBlock(block, typeSelect.value);
            renderAll();
            markDirty();
        });
        head.appendChild(typeSelect);

        head.appendChild(el('span', 'le-block-index', '#' + (index + 1)));

        var tools = el('div', 'le-block-tools');

        function tool(label, title, handler, danger) {
            var button = el('button', 'le-icon-btn' + (danger ? ' le-danger' : ''), label);
            button.type = 'button';
            button.title = title;
            button.addEventListener('click', handler);
            tools.appendChild(button);
        }

        tool('↑', 'Выше', function () { moveBlock(index, index - 1); });
        tool('↓', 'Ниже', function () { moveBlock(index, index + 1); });
        tool('⧉', 'Дублировать', function () {
            state.content.splice(index + 1, 0, deepClone(state.content[index]));
            renderAll();
            markDirty();
        });
        tool(state.collapsed[index] ? '▸' : '▾', 'Свернуть', function () {
            state.collapsed[index] = !state.collapsed[index];
            renderAll();
        });
        tool('✕', 'Удалить блок', function () {
            var typeLabel = BLOCK_LABELS[block.type] ? BLOCK_LABELS[block.type].label : block.type;
            if (!window.confirm('Удалить блок «' + typeLabel + '»?')) {
                return;
            }
            state.content.splice(index, 1);
            renderAll();
            markDirty();
        }, true);

        head.appendChild(tools);
        card.appendChild(head);
        card.appendChild(renderFields(block, index));

        head.addEventListener('dragstart', function (event) {
            dragIndex = index;
            card.classList.add('is-dragging');
            try {
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', String(index));
            } catch (error) {
                /* ignore */
            }
        });
        head.addEventListener('dragend', function () {
            dragIndex = null;
            card.classList.remove('is-dragging');
            clearDropTargets();
        });
        card.addEventListener('dragover', function (event) {
            if (dragIndex == null || dragIndex === index) {
                return;
            }
            event.preventDefault();
            card.classList.add('le-drop-target');
        });
        card.addEventListener('dragleave', function () {
            card.classList.remove('le-drop-target');
        });
        card.addEventListener('drop', function (event) {
            event.preventDefault();
            card.classList.remove('le-drop-target');
            if (dragIndex == null || dragIndex === index) {
                dragIndex = null;
                return;
            }
            var moved = state.content.splice(dragIndex, 1)[0];
            var target = dragIndex < index ? index - 1 : index;
            state.content.splice(target, 0, moved);
            dragIndex = null;
            renderAll();
            markDirty();
        });

        return card;
    }

    function clearDropTargets() {
        var nodes = blocksRoot.querySelectorAll('.le-drop-target');
        for (var i = 0; i < nodes.length; i += 1) {
            nodes[i].classList.remove('le-drop-target');
        }
    }

    function moveBlock(from, to) {
        if (to < 0 || to >= state.content.length) {
            return;
        }
        var moved = state.content.splice(from, 1)[0];
        state.content.splice(to, 0, moved);
        renderAll();
        markDirty();
    }

    function renderBlocks() {
        blocksRoot.innerHTML = '';
        state.content.forEach(function (block, index) {
            blocksRoot.appendChild(renderBlockCard(block, index));
        });
        emptyNode.hidden = state.content.length > 0;
    }

    function renderOutline() {
        outlineRoot.innerHTML = '';
        state.content.forEach(function (block, index) {
            var item = el('button', 'le-outline-item');
            item.type = 'button';
            var label = BLOCK_LABELS[block.type];
            item.appendChild(el('span', 'le-outline-type', label ? label.icon : '?'));
            var text = el('span', 'le-outline-text', (index + 1) + '. ' + firstLine(block));
            item.appendChild(text);
            item.title = label ? label.label : block.type;
            item.addEventListener('click', function () {
                var card = blocksRoot.querySelector('[data-index="' + index + '"]');
                if (card) {
                    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    card.classList.add('le-drop-target');
                    window.setTimeout(function () {
                        card.classList.remove('le-drop-target');
                    }, 900);
                }
            });
            outlineRoot.appendChild(item);
        });
        blockCountNode.textContent = '(' + state.content.length + ')';
    }

    function updateOutline() {
        renderOutline();
    }

    function updateStats() {
        var words = 0;
        state.content.forEach(function (block) {
            words += plainText(block).split(/\s+/).filter(Boolean).length;
        });
        statsNode.textContent = state.content.length + ' блоков · ' + words + ' слов';
    }

    function renderAll() {
        renderBlocks();
        renderOutline();
        updateStats();
        if (state.preview) {
            renderPreview();
        }
    }

    function addBlock(type) {
        state.content.push(defaultBlock(type));
        state.collapsed[state.content.length - 1] = false;
        renderAll();
        markDirty();
        var cards = blocksRoot.querySelectorAll('.le-block');
        var last = cards[cards.length - 1];
        if (last) {
            last.scrollIntoView({ behavior: 'smooth', block: 'center' });
            var input = last.querySelector('input, textarea, select');
            if (input) {
                input.focus();
            }
        }
    }

    function renderAddBar() {
        addBar.innerHTML = '';
        addBar.appendChild(el('div', 'le-addbar-title', 'Добавить блок'));
        Object.keys(BLOCK_LABELS).forEach(function (type) {
            var button = el('button', 'le-add-btn');
            button.type = 'button';
            var meta = BLOCK_LABELS[type];
            button.appendChild(el('span', 'le-outline-type', meta.icon));
            button.appendChild(el('span', null, meta.label));
            button.addEventListener('click', function () {
                addBlock(type);
            });
            addBar.appendChild(button);
        });
    }

    // -------------------------------------------------------------- preview

    function mdInline(text) {
        var codes = [];
        var out = String(text).replace(/`([^`\n]+)`/g, function (match, code) {
            codes.push(code);
            return '\u0000' + (codes.length - 1) + '\u0000';
        });
        out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        out = out.replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,!?:;]|$)/g, '$1<em>$2</em>');
        out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
        out = out.replace(/\u0000(\d+)\u0000/g, function (match, index) {
            return '<code>' + codes[Number(index)] + '</code>';
        });
        return out;
    }

    function richParagraphs(text) {
        return String(text || '').split(/\n\s*\n/).map(function (paragraph) {
            return '<p>' + paragraph.split('\n').map(mdInline).join('<br>') + '</p>';
        }).join('');
    }

    function previewBlock(block) {
        if (block.type === 'heading') {
            var level = clamp(block.level, 1, 6, 2);
            return '<h' + level + '>' + mdInline(escapeHtml(block.content)) + '</h' + level + '>';
        }
        if (block.type === 'text') {
            return '<div>' + richParagraphs(escapeHtml(block.content)) + '</div>';
        }
        if (block.type === 'code') {
            return '<div class="le-preview-code">' +
                '<div class="le-preview-code-label"><span>' + escapeHtml(block.language || 'text') + '</span><span>код</span></div>' +
                '<pre><code>' + escapeHtml(block.content) + '</code></pre></div>';
        }
        if (block.type === 'list') {
            var tag = block.ordered ? 'ol' : 'ul';
            var items = (block.items || []).map(function (item) {
                return '<li>' + mdInline(escapeHtml(item)) + '</li>';
            }).join('');
            return '<' + tag + '>' + items + '</' + tag + '>';
        }
        if (block.type === 'table') {
            var head = '';
            if ((block.headers || []).length) {
                head = '<thead><tr>' + block.headers.map(function (header) {
                    return '<th>' + mdInline(escapeHtml(header)) + '</th>';
                }).join('') + '</tr></thead>';
            }
            var body = '<tbody>' + (block.rows || []).map(function (row) {
                return '<tr>' + (row || []).map(function (cell) {
                    return '<td>' + mdInline(escapeHtml(cell)) + '</td>';
                }).join('') + '</tr>';
            }).join('') + '</tbody>';
            return '<table>' + head + body + '</table>';
        }
        if (block.type === 'callout') {
            var callout = '<div class="le-preview-callout is-' + escapeHtml(block.style || 'info') + '">';
            if (block.title) {
                callout += '<div class="le-preview-callout-title">' + mdInline(escapeHtml(block.title)) + '</div>';
            }
            callout += '<div>' + mdInline(escapeHtml(block.content)) + '</div></div>';
            return callout;
        }
        if (block.type === 'blockquote') {
            return '<blockquote>' + mdInline(escapeHtml(block.content)) + '</blockquote>';
        }
        if (block.type === 'image') {
            if (!block.url) {
                return '<p><em>Изображение без ссылки</em></p>';
            }
            var figure = '<figure><img src="' + escapeHtml(block.url) + '" alt="' + escapeHtml(block.alt || '') + '">';
            if (block.caption) {
                figure += '<figcaption>' + escapeHtml(block.caption) + '</figcaption>';
            }
            return figure + '</figure>';
        }
        if (block.type === 'video') {
            if (!block.url) {
                return '<p><em>Видео без ссылки</em></p>';
            }
            return '<div style="margin:1.5rem 0;"><iframe class="le-preview-frame" src="' + escapeHtml(block.url) + '" allowfullscreen loading="lazy"></iframe></div>';
        }
        if (block.type === 'divider') {
            return '<hr>';
        }
        return '<p><em>Неизвестный блок: ' + escapeHtml(block.type || '?') + '</em></p>';
    }

    function displayStyle() {
        var fonts = {
            sans: "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
            serif: "Georgia, 'Times New Roman', 'Iowan Old Style', serif",
            mono: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
            humanist: 'Verdana, Geneva, Tahoma, sans-serif',
            rounded: "ui-rounded, 'SF Pro Rounded', 'Segoe UI', sans-serif"
        };
        var display = state.display;
        return 'font-family:' + (fonts[display.font] || fonts.sans) +
            ';font-size:' + clamp(display.size, 12, 28, 17) + 'px' +
            ';line-height:' + clamp(display.line_height, 1.2, 2.4, 1.7) +
            ';max-width:' + clamp(display.width, 40, 120, 68) + 'ch';
    }

    function renderPreview() {
        previewRoot.innerHTML = '<div class="le-preview-inner" style="' + displayStyle() + '">' +
            state.content.map(previewBlock).join('') + '</div>';
    }

    function togglePreview(force) {
        state.preview = typeof force === 'boolean' ? force : !state.preview;
        previewBtn.classList.toggle('is-active', state.preview);
        previewBtn.textContent = state.preview ? 'Вернуться к редактору' : 'Предпросмотр';
        blocksRoot.hidden = state.preview;
        addBar.hidden = state.preview;
        emptyNode.hidden = state.preview || state.content.length > 0;
        previewRoot.hidden = !state.preview;
        if (state.preview) {
            renderPreview();
            previewRoot.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // ----------------------------------------------------------- meta/display

    function fillSelect(select, options, value) {
        select.innerHTML = '';
        (options || []).forEach(function (pair) {
            var option = el('option', null, pair[1]);
            option.value = pair[0];
            select.appendChild(option);
        });
        select.value = value;
    }

    function syncMetaForm() {
        document.getElementById('leName').value = state.meta.name;
        document.getElementById('leShort').value = state.meta.short_description;
        document.getElementById('leXp').value = state.meta.xp_reward;
        document.getElementById('leMinutes').value = state.meta.estimated_minutes;
        titleNode.textContent = state.meta.name || 'Без названия';

        fillSelect(document.getElementById('leStatus'), choices.status || [], state.meta.status);
        fillSelect(document.getElementById('leType'), choices.lesson_type || [], state.meta.lesson_type);
        fillSelect(document.getElementById('leDifficulty'), choices.difficulty || [], state.meta.difficulty);
    }

    function bindMeta() {
        var nameInput = document.getElementById('leName');
        var shortInput = document.getElementById('leShort');
        var statusSelect = document.getElementById('leStatus');
        var typeSelect = document.getElementById('leType');
        var difficultySelect = document.getElementById('leDifficulty');
        var xpInput = document.getElementById('leXp');
        var minutesInput = document.getElementById('leMinutes');

        syncMetaForm();

        function textHandler(key) {
            return function () {
                state.meta[key] = this.value;
                if (key === 'name') {
                    titleNode.textContent = this.value || 'Без названия';
                    document.title = (this.value || 'Урок') + ' — редактор';
                }
                markDirty();
            };
        }

        nameInput.addEventListener('input', textHandler('name'));
        shortInput.addEventListener('input', textHandler('short_description'));
        statusSelect.addEventListener('change', function () {
            state.meta.status = statusSelect.value;
            markDirty();
        });
        typeSelect.addEventListener('change', function () {
            state.meta.lesson_type = typeSelect.value;
            markDirty();
        });
        difficultySelect.addEventListener('change', function () {
            state.meta.difficulty = difficultySelect.value;
            markDirty();
        });
        xpInput.addEventListener('input', function () {
            state.meta.xp_reward = clamp(xpInput.value, 0, 10000, 10);
            markDirty();
        });
        minutesInput.addEventListener('input', function () {
            state.meta.estimated_minutes = clamp(minutesInput.value, 1, 600, 15);
            markDirty();
        });
    }

    function syncDisplayForm() {
        document.getElementById('leSize').value = state.display.size;
        document.getElementById('leLh').value = state.display.line_height;
        document.getElementById('leWidth').value = state.display.width;
        document.getElementById('leSizeVal').textContent = state.display.size;
        document.getElementById('leLhVal').textContent = state.display.line_height;
        document.getElementById('leWidthVal').textContent = state.display.width;
        fillSelect(document.getElementById('leFont'), choices.font || [], state.display.font);
    }

    function bindDisplay() {
        var fontSelect = document.getElementById('leFont');
        var sizeInput = document.getElementById('leSize');
        var lhInput = document.getElementById('leLh');
        var widthInput = document.getElementById('leWidth');
        var sizeValue = document.getElementById('leSizeVal');
        var lhValue = document.getElementById('leLhVal');
        var widthValue = document.getElementById('leWidthVal');
        var resetButton = document.getElementById('leResetDisplay');

        syncDisplayForm();

        fontSelect.addEventListener('change', function () {
            state.display.font = fontSelect.value;
            markDirty();
        });

        sizeInput.addEventListener('input', function () {
            state.display.size = clamp(sizeInput.value, 12, 28, 17);
            sizeValue.textContent = state.display.size;
            markDirty();
        });
        lhInput.addEventListener('input', function () {
            state.display.line_height = Math.round(clamp(lhInput.value, 1.2, 2.4, 1.7) * 100) / 100;
            lhValue.textContent = state.display.line_height;
            markDirty();
        });
        widthInput.addEventListener('input', function () {
            state.display.width = clamp(widthInput.value, 40, 120, 68);
            widthValue.textContent = state.display.width;
            markDirty();
        });

        resetButton.addEventListener('click', function () {
            state.display = { font: 'sans', size: 17, line_height: 1.7, width: 68 };
            fontSelect.value = 'sans';
            sizeInput.value = 17;
            lhInput.value = 1.7;
            widthInput.value = 68;
            sizeValue.textContent = '17';
            lhValue.textContent = '1.7';
            widthValue.textContent = '68';
            markDirty();
        });
    }

    // ------------------------------------------------------------------ save

    function save() {
        if (!CAN_CHANGE || state.saving) {
            return;
        }
        state.saving = true;
        saveBtn.disabled = true;
        setSaveState('Сохранение…', 'saving');

        fetch(SAVE_URL, {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                meta: state.meta,
                content: state.content,
                display: state.display
            })
        }).then(function (response) {
            return response.json().catch(function () {
                return { ok: false, error: 'Сервер вернул некорректный ответ' };
            }).then(function (data) {
                if (!response.ok || !data.ok) {
                    throw new Error(data.error || ('Ошибка HTTP ' + response.status));
                }
                return data;
            });
        }).then(function (data) {
            state.dirty = false;
            clearDraft();
            if (data.version) {
                versionChip.textContent = 'v' + data.version;
            }
            setSaveState('Сохранено в ' + (data.saved_at || '…'), 'saved');
            toast('Сохранено: ' + data.blocks + ' блоков, версия ' + (data.version || '—'), 'ok');
        }).catch(function (error) {
            setSaveState('Ошибка сохранения', 'error');
            toast('Не удалось сохранить: ' + error.message, 'error');
        }).then(function () {
            state.saving = false;
            saveBtn.disabled = false;
        });
    }

    function offerDraft() {
        var raw;
        try {
            raw = window.localStorage.getItem(DRAFT_KEY);
        } catch (error) {
            return;
        }
        if (!raw) {
            return;
        }
        var draft;
        try {
            draft = JSON.parse(raw);
        } catch (error) {
            clearDraft();
            return;
        }
        if (!draft || !Array.isArray(draft.content)) {
            clearDraft();
            return;
        }
        var sameContent = JSON.stringify(draft.content) === JSON.stringify(state.content);
        var sameMeta = JSON.stringify(draft.meta) === JSON.stringify(state.meta);
        var sameDisplay = JSON.stringify(draft.display) === JSON.stringify(state.display);
        if (sameContent && sameMeta && sameDisplay) {
            return;
        }

        carryNode.innerHTML = '';
        var banner = el('div', 'le-banner');
        var savedAt = draft.savedAt ? new Date(draft.savedAt) : new Date();
        banner.appendChild(el('span', null, 'Найден несохранённый черновик от ' + savedAt.toLocaleString('ru-RU') + '.'));
        var restore = el('button', 'le-btn le-btn-small', 'Восстановить черновик');
        restore.type = 'button';
        restore.addEventListener('click', function () {
            state.content = deepClone(draft.content);
            state.meta = Object.assign({}, state.meta, draft.meta || {});
            state.display = Object.assign({}, state.display, draft.display || {});
            syncMetaForm();
            syncDisplayForm();
            renderAll();
            markDirty();
            carryNode.innerHTML = '';
            toast('Черновик восстановлен. Не забудьте сохранить.', 'ok');
        });
        var discard = el('button', 'le-btn le-btn-small', 'Удалить черновик');
        discard.type = 'button';
        discard.addEventListener('click', function () {
            clearDraft();
            carryNode.innerHTML = '';
        });
        banner.appendChild(restore);
        banner.appendChild(discard);
        carryNode.appendChild(banner);
    }

    // ------------------------------------------------------------------ init

    bindMeta();
    bindDisplay();
    renderAddBar();
    renderAll();
    setSaveState(payload.version ? 'Версия ' + payload.version : 'Готово', null);
    document.title = (state.meta.name || 'Урок') + ' — редактор';

    saveBtn.addEventListener('click', save);

    previewBtn.addEventListener('click', function () {
        togglePreview();
    });

    document.addEventListener('keydown', function (event) {
        if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 's') {
            event.preventDefault();
            save();
        }
        if (event.key === 'Escape' && state.preview) {
            togglePreview(false);
        }
    });

    window.addEventListener('beforeunload', function (event) {
        if (!state.dirty) {
            return undefined;
        }
        event.preventDefault();
        event.returnValue = '';
        return '';
    });

    offerDraft();
}());
