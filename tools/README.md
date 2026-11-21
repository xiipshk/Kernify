# Служебные скрипты и архив

Всё, что не нужно для запуска сайта, разложено по темам.

## Корень проекта (рабочие файлы)

Запуск и установка: `run.sh`, `install.sh`, `Запуск.command`, `Установка.command`,
`start.bat`, `install.bat`.
Проект: `manage.py`, `requirements.txt`, `pytest.ini`, `db.sqlite3`, `.env`.
Docker: `Dockerfile`, `docker-compose.yml`, `nginx.conf`. Документация: `README.md`.

## tools/ — одноразовые скрипты

| Папка | Что внутри |
|---|---|
| `lessons/` | генераторы и переработка уроков (`create_*.py`, `generate_*.py`, `recreate_*.py`, `rewrite_*`) |
| `fixes/` | правки и форматирование (`fix_*.py`, `cleanup_*.py`, `format_*.py`, `style_text*`) |
| `i18n/` | переводы и локализация (`translate_*`, `localize_*`, `compile_po.py`) |
| `content/` | наполнение контента (`fill_*.py`, `enhance_*.py`, `inline_*`, `apply_pedagogical.py`) |
| `checks/` | диагностика (`audit_*`, `check_*`, `scan_*`, `dump_*`) |
| `data/` | `solutions.py`, `generate_tasks.py` — данные для генерации задач |
| `_незавершённые/` | 14 скриптов с синтаксическими ошибками (недописанные черновики, были сломаны изначально) |

> **Важно:** скрипты содержат относительные импорты (например, `from solutions import ...`).
> Запускать их нужно из корня проекта: `python tools/data/generate_tasks.py`,
> а скриптам, импортирующим друг друга, может понадобиться
> `PYTHONPATH=tools/data`.

## archive/

| Папка | Что внутри |
|---|---|
| `logs/` | старые логи и отчёты (`runserver.log`, `*_output.txt`, отчёты) |
| `docs/` | исторические документы (`AUDIT_REPORT.md`, `CHANGES_LOG.md`, `PROGRESS_PLAN.md`) |

## backups/db/

Резервные копии базы `db.sqlite3.bak-*`. Текущая рабочая база — в корне проекта.

## Основное приложение

Папки Django: `config/`, `core/`, `accounts/`, `learning/`, `practice/`,
`progress/`, `ai/`, `runner/`, плюс `templates/`, `static/`, `locale/`, `venv/`.
Материалы: `Kernify-lesson/`, `задачи kernify/`, `Документация/`, `логи/`,
`основная информация/`. Раннер кода: `native-runner/`.
