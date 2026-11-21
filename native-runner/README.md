# Нативный раннер кода (замена Piston)

Лёгкий локальный сервис запуска кода для Kernify. Код пользователя выполняется
в контейнере, изолированном по времени и памяти (но это не полноценная песочница
уровня nsjail — для локальной разработки достаточно).

Поддерживаемые языки: **Python, JavaScript, C++, Rust**.
C# и CSS помечены в интерфейсе как неисполняемые.

## Запуск

```bash
# 1. Собрать образ (нужен работающий Docker)
docker build -t kernify-runner -f native-runner/Dockerfile native-runner

# 2. Запустить (слушает только 127.0.0.1:2000)
docker run -d --name kernify-runner --restart unless-stopped \
    -p 127.0.0.1:2000:2000 kernify-runner
```

Проверка:

```bash
curl http://127.0.0.1:2000/api/v2/runtimes
curl -X POST http://127.0.0.1:2000/api/v2/execute \
    -H 'Content-Type: application/json' \
    -d '{"language":"python","version":"3","files":[{"name":"main.py","content":"print(1+1)"}]}'
```

Django обращается к нему по адресу из настройки `PISTON_API_URL`
(по умолчанию `http://127.0.0.1:2000/api/v2`) и через `CODE_RUNNER_ENABLED=true`.

## Как это связано с кодом

- `native-runner/server.py` — HTTP-сервис (только stdlib), эндпоинты
  `GET /api/v2/runtimes` и `POST /api/v2/execute` (совместимо с Piston).
- `native-runner/Dockerfile` — образ Ubuntu 24.04 с python3/nodejs/g++/rustc.
- `runner/code_runner.py` — клиент, который Django вызывает из
  `/api/code/run/`; маппинг языков Kernify → раннер.

## Почему не Piston

Официальный образ `ghcr.io/engineer-man/piston` — только amd64, а пакеты языков
весят по 200–700 МБ и качаются с GitHub. На Apple Silicon это работает через
эмуляцию и крайне медленно. Нативный arm64-раннер выполняет ту же задачу
быстро и без внешних зависимостей.
