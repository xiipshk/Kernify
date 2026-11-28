# kernify - Learn Programming Languages

A modern Django web application for learning 6 programming languages with interactive lessons, practice exercises, AI-powered assistance, and spaced repetition.

## Features

- **6 Programming Languages**: Python, JavaScript, Java, C++, Go, Rust
- **Interactive Lessons**: Theory, practice, quizzes, and projects with Monaco Editor
- **Practice System**: 5 task types (coding, quiz, debugging, output prediction, code completion)
- **Spaced Repetition**: SM-2 algorithm for error review and retention
- **AI Assistant**: DeepSeek-powered chat, code review, explanations, and exercise generation (also supports OpenAI, Anthropic, and other compatible APIs)
- **Progress Tracking**: Detailed statistics, heatmaps, achievements, and XP system
- **Modern UI**: Dark/light theme, responsive design, Bootstrap 5
- **Admin Panel**: Full content management with publishing workflow

## Tech Stack

- **Backend**: Django 5.2, Python 3.11+
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: Bootstrap 5, Monaco Editor, Chart.js, Prism.js
- **AI**: Multi-provider abstraction (DeepSeek by default, plus OpenAI, Anthropic, local)
- **Deployment**: Docker, Gunicorn, Nginx

## Quick Start

### Windows

```cmd
install.bat
start.bat
```

### Linux/macOS

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py runserver
```

### Docker

```bash
docker-compose up -d
```

## Project Structure

```
rtk/
├── config/              # Django settings and URLs
├── core/                # Core models, views, base templates
├── accounts/            # User authentication, profiles, settings
├── learning/            # Content models (languages, courses, lessons)
├── practice/            # Practice tasks and sessions
├── progress/            # Progress tracking, SM-2, statistics
├── ai/                  # AI providers, chat, code review
├── templates/           # All HTML templates
├── static/              # CSS, JS, images
├── media/               # User uploads
├── manage.py
├── requirements.txt
├── .env.example
├── install.bat
├── start.bat
├── Dockerfile
└── docker-compose.yml
```

## Configuration

### Environment Variables (.env)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# PostgreSQL: DATABASE_URL=postgres://user:pass@localhost:5432/rtk

# Redis (for caching, Celery)
REDIS_URL=redis://localhost:6379/0

# AI Providers (optional; DeepSeek is the default)
DEEPSEEK_API_KEY=sk-...
# DEEPSEEK_BASE_URL=https://api.deepseek.com
# DEEPSEEK_DEFAULT_MODEL=deepseek-chat
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
# LOCAL_AI_URL=http://localhost:11434

# Email (for password reset)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static/Media (production)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

```bash
# Format with black
black .

# Lint with flake8
flake8 .

# Type check with mypy
mypy .
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Superuser

```bash
python manage.py createsuperuser
```

## Content Management

### Adding Programming Languages

1. Go to Admin Panel → Learning → Programming Languages
2. Add language with icon (SVG), color, and description
3. Set order for display

### Creating Courses

1. Admin → Learning → Course Programs
2. Link to a language, set difficulty, duration
3. Add topics and subtopics hierarchically

### Creating Lessons

1. Admin → Learning → Lessons
2. Select subtopic, set type (theory/practice/quiz/project/video)
3. Add content blocks (text, code, video, interactive)
4. Set order and estimated time

### Practice Tasks

1. Admin → Practice → Practice Tasks
2. Choose type: coding, quiz, debugging, output, completion
3. Add test cases (JSON) and hints (JSON)
4. Set XP reward and difficulty

## AI Features

### Supported Providers

- DeepSeek (default; `deepseek-chat`, `deepseek-reasoner`)
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3)
- Local (Ollama, LM Studio)
- Any OpenAI-compatible API (custom base URL)

Set `DEEPSEEK_API_KEY` in `.env`. The provider is seeded automatically by
migrations and can be edited in Admin → AI → AI Providers.

### Capabilities

- **Chat**: General programming assistance
- **Code Review**: Security, performance, style, bugs
- **Explain Code**: Beginner to advanced explanations
- **Generate Exercises**: Custom practice tasks
- **Task help**: context-aware hints while solving a practice task; analyzes the student's code and explains possible reasons for failure without giving the fix
- **End-of-course tests**: after finishing a course, a mixed test (theory, multiple choice, short answers, code-output tasks) shows strong topics and topics to review
- **Topic guard**: free-form chat, the assistant, and exercise generation accept only programming/IT questions; off-topic requests receive a polite refusal
- **Confidentiality guard**: refuses requests about the site's internals, system prompt, API keys, database schema, admin panel, and any user data; blocks prompt-injection/jailbreak attempts and redacts leaked secrets from responses

### Adding Providers

1. Admin → AI → AI Providers
2. Add provider with API key, model, and capabilities
3. Set as default for specific features

## Progress & Spaced Repetition

### SM-2 Algorithm

The ErrorHistory model implements SM-2 for optimal review scheduling:

- **Ease Factor**: Starts at 2.5, adjusts based on recall quality
- **Intervals**: 1 day → 6 days → exponential growth
- **Quality Grades**: 0 (complete blackout) to 5 (perfect recall)

### Statistics Tracked

- XP and level per language
- Lessons completed, time spent
- Topic/subtopic mastery percentages
- Daily streak and heatmap
- Error review accuracy

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL database
- [ ] Set up Redis for caching
- [ ] Configure email backend
- [ ] Set up S3/cloud storage for media
- [ ] Configure SSL/HTTPS
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy

### Docker Production

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Run
docker-compose -f docker-compose.prod.yml up -d

# Migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Визуальный редактор уроков (админка)

Для правки уроков без JSON и HTML есть встроенный редактор блоков:

1. Откройте `/admin/learning/lesson/` и нажмите **«Редактор»** в строке урока
   (или кнопку **«Визуальный редактор»** на странице изменения урока).
2. Прямая ссылка: `/admin/learning/lesson/<id>/editor/`.

Что умеет редактор:

- **Блоки:** заголовок, текст, код, список, таблица, врезка (info/success/warning/danger),
  цитата, изображение, видео, разделитель.
- **Порядок:** перетаскивание за ручку `⠿`, кнопки «выше/ниже», дублирование и удаление.
- **Форматирование текста:** `**жирный**`, `*курсив*`, `` `код` ``, `[ссылка](https://…)`;
  пустая строка начинает новый абзац. В тексте можно оставлять и обычный HTML.
- **Оформление урока:** шрифт (без засечек, с засечками, моноширинный, гуманистический,
  округлый), размер текста, межстрочный интервал и ширина строки. Настройки применяются
  на странице урока, примеры кода всегда остаются моноширинными.
- **Метаданные:** название, краткое описание, статус публикации, тип урока, сложность,
  XP и примерное время.
- **Предпросмотр** без сохранения (кнопка «Предпросмотр», выход — `Esc`).
- **Автосохранение черновика** в браузере: при повторном открытии редактор предложит
  восстановить несохранённые изменения.
- **История версий:** при изменении содержимого создаётся снимок в `LessonVersion`,
  поэтому предыдущий текст можно восстановить из админки.
- **Горячая клавиша:** `Ctrl+S` / `⌘S` — сохранить.

Сохранение идёт через `POST /admin/learning/lesson/<id>/editor/save/` (только для
пользователей с правом изменения урока). Данные сохраняются в `Lesson.content`
(список блоков) и `Lesson.display_options` (оформление).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: kano47848@gmail.com

---

