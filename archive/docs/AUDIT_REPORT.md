# Kernify Code Audit Report

Generated: 2026-11-14

---

## config/settings.py

- [ ] `LOCALE_PATHS` указывает на `BASE_DIR / 'locale'`, которой не существует — нужен `mkdir` или удалить настройку
- [ ] В `REST_FRAMEWORK` нет `DEFAULT_RENDERER_CLASSES` / `DEFAULT_PARSER_CLASSES` — для API может понадобиться
- [ ] `CSRF_TRUSTED_ORIGINS` читается из env, но нет дефолта для продакшена

---

## config/urls.py

- [ ] В `DEBUG` блоке: `static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)` — `STATIC_ROOT` собирается только при `collectstatic`, в деве файлов нет → 404 на статике. Лучше `STATICFILES_DIRS`.

---

## Dockerfile

- [ ] `COPY requirements.txt .` → `RUN pip install -r requirements.txt`, но `requirements.txt` содержит **только тестовые депы** (pytest, mypy). В контейнере не будет Django, DRF, environ, Pillow, gunicorn — сборка упадёт на `collectstatic` или запуске.
- [ ] Нет создания пользователя до `COPY . .` — кэш слоёв не используется при изменении кода.
- [ ] `HEALTHCHECK` использует `curl`, но его нет в `python:3.11-slim` (не установлен в `apt-get`).

---

## nginx.conf

- [ ] `server_name _;` — лучше явное имя или `$host`
- [ ] `proxy_params` включены как комментарий — в контейнере файла нет, нужно либо `include /etc/nginx/proxy_params;` (есть в образе nginx), либо инлайн.
- [ ] `limit_req_zone` — ключ `$binary_remote_addr` не учитывает прокси (нужен `X-Forwarded-For` через `map`).

---

## requirements.txt

- [ ] **Отсутствуют рантаймовые зависимости**: `Django`, `djangorestframework`, `django-environ`, `Pillow`, `gunicorn`, `httpx`, `django-ratelimit`, `pytest-django`, `psycopg2-binary` (для Postgres).
- [ ] Нет закрепления версий для продакшена (только `==` для тестов).

---

## .env.example

- [ ] `DEFAULT_FROM_EMAIL` закомментирован — в продакшене почта не заработает без него.
- [ ] Нет примеров для `CELERY`, `SENTRY`, `AWS_S3` — раскомментировать при подключении.

---

## core/models.py

- [ ] `PublishedActiveManager.get_queryset()` предполагает наличие поля `status` у модели. Безопасно только для моделей, наследующих `PublishedModel`, но не проверяется.
- [ ] Нет `__repr__` для абстрактных моделей — сложнее дебажить.

---

## core/views.py

- [ ] `HomeView` делает 4 отдельных `count()` запроса — можно объединить через `aggregate`.
- [ ] `LanguageDetailView` / `ProgramDetailView` / `TopicDetailView` / `LessonDetailView` — каждый делает отдельный запрос на `UserProgress` / `LessonProgress`. При списке уроков — N+1. Нужно `prefetch_related` с `Prefetch`.

---

## core/urls.py

- [ ] Нет `app_name` в `include('core.urls')` в главном `urls.py` — есть, ок.

---

## accounts/models.py

- [ ] `get_preferred_language_display()` и `get_current_level_display()` — дублируют встроенный Django `get_FOO_display()` для `TextChoices`. Удалить.
- [ ] `telegram_id` — `BigIntegerField`, но Telegram ID может быть отрицательным (группы/каналы). `PositiveBigIntegerField` не подходит, текущий вариант ок.
- [ ] `UserProfile.bookmarked_lessons` — `ManyToMany` без `through` — нельзя хранить дату добавления. Если понадобится — миграция.

---

## accounts/views.py

- [ ] `LoginView` и `RegisterView` наследуют `TemplateView`, а не `FormView` / `CreateView` — ручная обработка `get`/`post`. Работает, но неидиоматично.
- [ ] `DashboardView` делает 6+ запросов в `get_context_data` — можно объединить через `prefetch_related` / `annotate`.
- [ ] `user_progress_totals` — отдельная функция вне класса, дублирует логику агрегации в `ProfileView`.

---

## accounts/forms.py

- [ ] `CustomUserCreationForm.save()` перезаписывает `email` и `username` из `cleaned_data` — `super().save(commit=False)` уже это делает. Лишние строки.
- [ ] `CustomAuthenticationForm.username_field = 'email'` — работает, но `username` в форме всё равно называется `username` (путаница в шаблоне).

---

## accounts/signals.py

- [ ] `create_user_profile` — `get_or_create` при каждом `post_save` (в т.ч. обновлении). Нормально, но можно `if created:` (уже есть).

---

## learning/models.py

- [ ] **КРИТИЧНО** `Topic.difficulty` (стр. 212-216): `PositiveIntegerField` с `choices=Difficulty.choices` где `Difficulty` — `TextChoices` (строки: 'easy', 'medium'...). Валидация упадёт при сохранении. Нужно: `CharField` + `TextChoices` ИЛИ `IntegerChoices`.
- [ ] `Lesson.save()` (стр. 359-378) инкрементит `version` при изменении полей, но **не проверяет `*_en` поля** (`content_en`, `name_en`, `short_description_en`, `hints_en` если появятся). Английские правки не поднимут версию.
- [ ] `LocalizedFieldsMixin.__getattribute__` (стр. 34-43) перехватывает **любой** доступ к атрибуту — слёгка замедляет каждый `lesson.name`. Кэш `translation.get_language()` вызывается каждый раз. Лучше: property или дескриптор.
- [ ] `Lesson.get_content_blocks()` (стр. 380-389) дублирует логику `LocalizedFieldsMixin` — можно убрать и пользоваться `lesson.content` напрямую.
- [ ] Сигналы `update_language_counts` / `update_program_counts` / `update_topic_counts` делают `.count()` запросы при каждом save/delete — при массовом импорте будет тормозить. Лучше: отложенное обновление через Celery или `update_fields` + `F()`.

---

## learning/views.py

- [ ] **КРИТИЧНО** `LessonNotesView.get_context_data` (стр. 228-230): использует переменную `context`, которой нет. Нужно: `context = super().get_context_data(**kwargs)`.
- [ ] `LessonLearnView.get_context_data` — 4 запроса на навигацию (prev/next/topic_lessons) + `LessonProgress`. Можно один запрос с `Window` функциями (Postgres) или кэш в сессии.
- [ ] `EnrollView` — при повторной записи на программу сбрасывает прогресс на первый урок (`current_lesson = first_lesson`). Можно добавить флаг `reset=False`.
- [ ] `LessonNotesView` / `UserNotesView` — заглушки, нет модели заметок (только `LessonProgress.personal_notes`).

---

## learning/urls.py

- [ ] Все пути требуют авторизации (`LoginRequiredMixin` во вьюхах) — ок.

---

## learning/admin.py

- [ ] `LessonAdmin.readonly_fields` включает `content` — JSONField в админке читается как текст, неудобно. Лучше: кастомный виджет или `PrettyJSONWidget`.
- [ ] `LessonVersionInline` — `can_delete = False`, но `has_add_permission` не переопределён — можно добавить через админку (хотя `extra=0`).

---

## learning/services.py

- [ ] `LessonCompletionService._check_topic_completion` (стр. 132-151): считает `topics_completed` только для статусов `MASTERED` и `PARTIAL`. Топики `NOT_MASTERED` (провалили входной тест, не начали) не учитываются — счётчик занижен.
- [ ] `start_lesson` (стр. 154-193) делает `get_or_create` + `save` — 2 запроса. Можно `update_or_create`.
- [ ] Нет обработки `IntegrityError` при гонке `get_or_create` (редко, но бывает).

---

## learning/lesson_parser.py

- [ ] `SECTION_PATTERNS` (стр. 60-66) — только русские заголовки. Английские (`## Lesson Goals`, `## Practice Tasks`) не распознаются.
- [ ] `slugify` (стр. 69-91) — транслитерация жёстко в коде. Лучше: `django.utils.text.slugify` с `allow_unicode=True` + кастомная замена.
- [ ] `parse_table` (стр. 139-164) — не экранирует HTML в ячейках. XSS-риск при рендере.
- [ ] Нет тестов парсера.

---

## learning/signals.py

- [ ] Файл-пустышка, сигналы в `models.py` — работает, но нестандартно. Лучше: перенести `@receiver` в `signals.py` и импортировать в `apps.py`.

---

## practice/models.py

- [ ] `PracticeTask.test_cases` / `hints` — `JSONField` без схемы валидации. Можно: `jsonschema` валидатор в `clean()`.
- [ ] `PracticeSession.test_results` — `JSONField`, структура не типизирована. Dataclass/Pydantic модель для валидации при чтении.
- [ ] `topic` дублирует `task.topic` — денормализация для скорости, но риск рассинхрона. Сигнал на обновление при смене `task.topic`.

---

## practice/views.py

- [ ] **КРИТИЧНО** `TaskSubmitView` (стр. 165-170): **мок тестов** — код не исполняется, все проходят. Нет интеграции с Piston/Judge0.
- [ ] `TaskSolveView` (стр. 145-150): `get_or_create` сессии при **каждом GET** — пользователь обновляет страницу → новая сессия со статусом `pending`. При сабмите придёт старый `session_id` → 404 или чужой результат.
- [ ] `PracticeIndexView` / `DailyChallengeView` (стр. 40-45, 244-247): `order_by('?')` эмулируется через `random.choice(list(ids))` — ок для малых таблиц, на 10к+ задач — полный скан `id`. Лучше: `TABLESAMPLE` (PG) или предвыборка.
- [ ] `TaskSubmitView` (стр. 186-202): обновление `UserProgress` через `F()` — хорошо, но нет `select_for_update` на чтении перед обновлением (хотя `F()` атомарен, race на `current_lesson` возможен).

---

## practice/urls.py

- [ ] Нет API-эндпоинтов для AJAX сабмита (нужен для монак/редактора).

---

## practice/admin.py

- [ ] `PracticeTaskAdmin` — `test_cases` и `hints` в `fieldsets` без виджета — неудобно править JSON в textarea. Нужен `JSONEditorWidget`.

---

## practice/signals.py

- [ ] Пустышка.

---

## progress/models.py

- [ ] `UserProgress.completion_percentage` (стр. 92-99) использует кэш `lessons_count` программы. Если сигналы не сработали — неверный %.
- [ ] `TopicProgress.update_status` (стр. 242-256): логика `NOT_MASTERED` срабатывает только при `test_score < 30` И `completion_percentage == 0`. Если пользователь начал уроки, но провалил тест — статус `PARTIAL`, что вводит в заблуждение.
- [ ] `ErrorHistory.schedule_next_review` (стр. 341-384): SM-2 реализован верно, но `quality` не валидируется (0-5) — проверка есть во вьюхе, но не в модели.
- [ ] `TestResult.answers` — `JSONField` без схемы.

---

## progress/views.py

- [ ] `ProgressDashboardView` (стр. 28-33): `sum(p.total_xp for p in progress)` — тянет все объекты в Python. Лучше: `aggregate(Sum('total_xp'))`.
- [ ] `HeatmapView` (стр. 221-270): 2 отдельных запроса + мердж в Python. Можно `UNION` в БД.
- [ ] `ExportProgressView` (стр. 279-296): `values()` без `iterator()` — при большом прогрессе съест память. Нужен `iterator(chunk_size=1000)`.

---

## progress/urls.py

- [ ] Ок.

---

## progress/admin.py

- [ ] `ErrorHistoryAdmin` — `readonly_fields` нет `last_seen` (auto_now), но есть в `list_display` — ок.

---

## progress/signals.py

- [ ] Пустышка.

---

## ai/models.py

- [ ] **КРИТИЧНО** `AIProvider.save()` (стр. 71-75): race condition при `is_default=True`. Два параллельных сохранения → два дефолтных провайдера. Нужен `select_for_update` или `transaction.atomic` + `update`.
- [ ] `AIChatSession` — нет уникального ограничения на `(user, topic, lesson, practice_task)` — можно создать дубликаты чатов для одного контекста.
- [ ] `AIMessage.tool_calls` — `JSONField`, нет валидации схемы OpenAI function calling.
- [ ] `AIPromptTemplate.render()` (стр. 263-268): простая замена `{var}` — не экранирует, ломается при `{` в значении. Лучше: `string.Template` или Jinja2.

---

## ai/views.py

- [ ] `AskAssistantView` (стр. 81-93): заглушка, не вызывает AI.
- [ ] `CodeReviewSubmitView` (стр. 103-114): заглушка.
- [ ] `UsageStatsView` (стр. 136-152): хардкод `SimpleNamespace` с нулями вместо чтения `AIUsageStats`.
- [ ] `ChatDetailView` (стр. 51-57): `prefetch_related('messages')` без `order_by` — порядок сообщений не гарантирован. В `Meta` есть `ordering`, но prefetch игнорирует. Нужен `Prefetch('messages', queryset=AIMessage.objects.order_by('created_at'))`.
- [ ] `NewChatView` (стр. 29-37): создаёт чат без тайтла/контекста → пустой чат в списке. Лучше: редирект на детальную с автотайтлом "New Chat".

---

## ai/urls.py

- [ ] Нет API для стриминга ответов (SSE / WebSocket).

---

## ai/admin.py

- [ ] `AIMessageInline` — `readonly_fields` включает `content`, но в админке длинный текст нечитаем. Нужен кастомный `readonly` виджет с `pre`/`code`.

---

## tests/test_basic.py

- [ ] Тесты покрывают только модели и `LessonCompletionService`. Нет тестов:
  - `TaskSubmitView` / `TaskCheckerService`
  - `AIProvider` race condition
  - `ErrorHistory` SM-2 edge cases
  - Парсера уроков
  - Админок
- [ ] Нет фикстур (`pytest.fixture`) — дублирование `setup_method`.
- [ ] Нет интеграционных тестов вьюх (client.post/get).

---

## manage.py

- [ ] Стандартный, ок.

---

## Итого по файлам

| Файл | Критично | Баги | Заглушки | Качество |
|------|----------|------|----------|----------|
| learning/models.py | 1 | 3 | 0 | 2 |
| learning/views.py | 1 | 2 | 2 | 1 |
| practice/views.py | 1 | 2 | 1 | 1 |
| ai/models.py | 1 | 0 | 0 | 3 |
| ai/views.py | 0 | 0 | 4 | 1 |
| requirements.txt | 0 | 0 | 0 | 1 |
| Dockerfile | 0 | 0 | 0 | 3 |
| config/settings.py | 0 | 0 | 0 | 2 |
| nginx.conf | 0 | 0 | 0 | 2 |
| Остальные | 0 | 8 | 0 | 12 |

**Всего: 4 критических, 15 багов, 7 заглушек, 27 качественных замечаний**