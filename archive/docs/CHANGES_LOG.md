# Кернифи - Лог изменений (2026-11-10)

## Обзор
Полная ревизия и исправление багов проекта kernify, оптимизация темной темы, добавление логотипов языков.

---

## 🔴 КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ (Race Conditions & Data Integrity)

### 1. Race Condition в начислении XP
**Файлы:** `learning/services.py` (новый), `learning/views.py`
- Создан `LessonCompletionService` с `select_for_update()` и атомарными `F()` выражениями
- Устранено двойное начисление XP при одновременных запросах
- Объединена дублирующаяся логика `LessonCompleteView` и `LessonNextView`

### 2. Soft Delete не работал для PublishedModel
**Файлы:** `core/models.py`, `learning/models.py`, `practice/models.py`
- Добавлен `PublishedActiveManager` (фильтрует по `status=PUBLISHED` И `is_deleted=False`)
- Создан базовый класс `PublishedSoftDeleteTimeStampedModel`
- Все модели обучения теперь используют мягкое удаление корректно

### 3. Баг в `TopicProgress.update_status()`
**Файл:** `progress/models.py`
- Исправлен порядок условий: статус `NOT_MASTERED` стал достижим
- Ранее `elif self.test_score > 0` никогда не выполнялся

### 4. Race Condition в практике
**Файл:** `practice/views.py` (`TaskSubmitView`)
- Добавлен `select_for_update()` + атомарные `F()` выражения в транзакции

---

## 🟠 СЕРЬЕЗНЫЕ ИСПРАВЛЕНИЯ

### 5. SM-2 алгоритм (Spaced Repetition)
**Файл:** `progress/models.py` (`ErrorHistory.schedule_next_review`)
- Исправлена формула ease factor согласно стандарту SM-2
- При `quality < 3` теперь правильно сбрасывается `count = 1`

### 6. N+1 запросы в дашборде
**Файлы:** `accounts/views.py`
- `user_progress_totals()` теперь использует агрегацию БД (`Sum`, `Max`)
- Добавлены `select_related` для связанных объектов

### 7. Инкремент версии урока
**Файл:** `learning/models.py` (`Lesson.save`)
- Версия увеличивается только при изменении значимых полей (content, name, starter_code, hints, xp_reward, difficulty, tags, estimated_minutes)

### 8. UNIQUE constraint при импорте
- Импорт работает с флагом `--clear`

---

## 🟡 ТЕМНАЯ ТЕМА И UI ИСПРАВЛЕНИЯ

### 9. Rate Limiting на AI эндпоинты
**Файл:** `ai/views.py`
- Добавлен `@method_decorator(ratelimit(key='user', rate='30/m', method='POST', block=True))` к `AskAssistantView`
- Добавлен `@method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True))` к `CodeReviewSubmitView`

### 10. Индексы БД (`db_index=True`)
**Файлы:** `learning/models.py`, `practice/models.py`, `progress/models.py`
- Добавлены ко всем часто используемым FK

### 11. Хардкод путей в `align_lessons.py`
- `REF_DIR` теперь через `os.environ.get('REF_DIR', BASE_DIR / 'reference_structure')`

### 12. Дублирование констант
- Вынесено в `learning/import_config.py`

### 13. Пустые заглушки реализованы
- `HeatmapView` — показывает активность за 365 дней
- `ExportProgressView` — экспорт JSON прогресса пользователя

---

## 🎨 ТЕМНАЯ ТЕМА - ПОЛНАЯ ПЕРЕРАБОТКА

### 14. Прогресс-бары с цветами языков
**Файлы:** `templates/accounts/dashboard.html`, `static/css/style.css`
- Прогресс-бары используют цвет языка (`progress.language.color`)
- В темной теме: светлые оттенки цветов языков + свечение

### 15. Карточки прогресса - черный текст в темной теме
**Файл:** `static/css/style.css`
- Секция `#progress` — черный текст (`#000000`) на темном фоне карточек
- Заголовки таблиц `/progress/` — черный текст на темном фоне

### 16. Общий текст в темной теме - белый
**Файл:** `static/css/style.css`
- Все текст использует CSS переменные (`var(--text-primary)` = `#ffffff`)
- Вторичный/приглушенный текст — светло-серый (`#94a3b8` / `#e2e8f0`)
- **Исключение:** секция прогресса сохраняет черный текст

### 17. Названия курсов в "Мои курсы" - белые в темной теме
**Файл:** `templates/learning/my_courses.html`
- Добавлен класс `text-theme` к названиям курсов

---

## 🖼️ ЛОГОТИПЫ ЯЗЫКОВ ПРОГРАММИРОВАНИЯ

### 18. Добавлены логотипы всем 6 языкам
**Файлы:** `templates/learning/my_courses.html`, `assign_logos.py`

| Язык | Файл логотипа | Источник |
|------|---------------|----------|
| Python | `python.webp` | Создан (emoji 🐍 на фоне #3776AB) |
| C++ | `C.webp` | Из папки logo |
| JavaScript | `JavaScript.png` | Из папки logo |
| Rust | `Rust.webp` | Из папки logo |
| CSS | `CSS.webp` | Из папки logo |
| C# | `C.png` | Из папки logo |

**Приоритет отображения в шаблоне:**
1. Логотип (`progress.language.logo`)
2. Эмодзи-иконка (`progress.language.icon`)
3. Дефолтная иконка CPU

---

## 📦 МИГРАЦИИ И ТЕСТЫ

### 19. Исправлены зависимости миграций
- `progress/migrations/0002_remove_current_subtopic.py` теперь зависит от `learning.0001_initial`

### 20. Тесты
**Файл:** `tests/test_basic.py`
- 16 тестов покрывают: модели, сервисы, SM-2, прогресс
- Все тесты проходят: **16/16 passed**

---

## 📋 ПРОВЕРКИ КАЧЕСТВА

```
python manage.py check          → 0 issues
python -m pytest tests/test_basic.py -v  → 16/16 passed
python manage.py test           → OK
```

---

## 📁 ИЗМЕНЕННЫЕ ФАЙЛЫ (Итоговый список)

### Core / Models / Services
- `core/models.py` — `PublishedActiveManager`, `PublishedSoftDeleteTimeStampedModel`
- `learning/models.py` — наследование от `PublishedSoftDeleteTimeStampedModel`, `Lesson.save()`
- `learning/services.py` — **НОВЫЙ** `LessonCompletionService`
- `learning/import_config.py` — **НОВЫЙ** общие константы
- `practice/models.py` — наследование от `PublishedSoftDeleteTimeStampedModel`
- `progress/models.py` — `TopicProgress.update_status()`, `ErrorHistory.schedule_next_review()`, индексы FK

### Views
- `learning/views.py` — использование `LessonCompletionService`
- `accounts/views.py` — оптимизация N+1, агрегация
- `practice/views.py` — `TaskSubmitView` с `select_for_update()`
- `ai/views.py` — rate limiting
- `progress/views.py` — реализация `HeatmapView`, `ExportProgressView`

### Templates
- `templates/accounts/dashboard.html` — прогресс-бары с цветами языков, черный текст в `#progress`
- `templates/learning/my_courses.html` — логотипы языков, `text-theme` для названий курсов
- `templates/progress/dashboard.html` — таблица прогресса (CSS для темной темы)

### Static
- `static/css/style.css` — полная переработка темной темы, прогресс-бары, таблицы, карточки
- `logo/python.webp` — новый логотип Python
- `logo/*.webp, *.png` — существующие логотипы

### Tests / Config
- `tests/test_basic.py` — 16 тестов
- `pytest.ini` — `--no-migrations`
- `progress/migrations/0002_remove_current_subtopic.py` — исправлена зависимость

### Scripts
- `assign_logos.py` — назначение логотипов
- `check_langs.py` — проверка логотипов
- `learning/management/commands/import_lessons.py` — импорт уроков
- `align_lessons.py` — вынесение констант в `import_config.py`

---

*Сгенерировано автоматически 2026-11-10*