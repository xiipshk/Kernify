#!/usr/bin/env python3
"""Create Russian .po file with translations and compile to .mo."""
import struct
from pathlib import Path

LOCALE_DIR = Path("locale/ru/LC_MESSAGES")
LOCALE_DIR.mkdir(parents=True, exist_ok=True)

# Translation dictionary: English -> Russian
TRANSLATIONS = {
    # Navigation
    "Cabinet": "Кабинет",
    "Learning": "Обучение",
    "Practice": "Практика",
    "Progress": "Прогресс",
    "AI Assistant": "AI-помощник",
    "Profile": "Профиль",
    "Settings": "Настройки",
    "Logout": "Выйти",
    "Login": "Войти",
    "Register": "Регистрация",
    "Learn Programming Languages": "Изучение языков программирования",

    # Home page
    "Learn 6 Programming Languages": "Изучение 6 языков программирования",
    "Master Python, JavaScript, Java, C++, Go, and Rust with interactive lessons, coding practice, and AI-powered assistance.": "Освойте Python, JavaScript, Java, C++, Go и Rust с интерактивными уроками, практикой кодирования и помощью ИИ.",
    "New: AI Assistant & Spaced Repetition": "Новое: AI-помощник и интервальное повторение",
    "Master 6 Programming Languages": "Освойте 6 языков программирования",
    "One Platform": "Одна платформа",
    "Learn Python, JavaScript, Java, C++, Go, and Rust with structured courses, hands-on coding practice, AI-powered explanations, and scientifically-backed spaced repetition.": "Изучите Python, JavaScript, Java, C++, Go и Rust со структурированными курсами, практикой кодирования, объяснениями на базе ИИ и научно обоснованным интервальным повторением.",
    "Open Cabinet": "Открыть кабинет",
    "Browse Courses": "Посмотреть курсы",
    "Start Free": "Начать бесплатно",
    "Sign In": "Войти",

    "Self-paced learning": "Самостоятельное обучение",
    "AI-powered help": "Помощь на базе ИИ",
    "Choose Your Language": "Выберите язык",
    "View All": "Смотреть все",
    "course": "курса",
    "No languages available yet": "Языки пока недоступны",
    "Check back soon for new programming languages!": "Загляните позже за новыми языками программирования!",
    "Why Choose RTK?": "Почему выбирают RTK?",
    "Structured Curriculum": "Структурированная программа",
    "From basics to advanced topics — each language has a carefully designed learning path with prerequisites and clear progression.": "От основ до продвинутых тем — у каждого языка тщательно продуманный путь обучения с предварительными условиями и четкой прогрессией.",
    "Hands-on Practice": "Практика кодирования",
    "Write and run real code in the browser. Solve exercises, build projects, and get instant feedback with automated testing.": "Пишите и запускайте реальный код в браузере. Решайте упражнения, создавайте проекты и получайте мгновенную обратную связь с автоматизированным тестированием.",
    "AI-Powered Learning": "Обучение на базе ИИ",
    "Get explanations, hints, code reviews, and personalized guidance from multiple AI providers (OpenAI, Anthropic, and more).": "Получайте объяснения, подсказки, ревью кода и персонализированное руководство от нескольких провайдеров ИИ (OpenAI, Anthropic и др.).",
    "Spaced Repetition": "Интервальное повторение",
    "Never forget what you learned. SM-2 algorithm schedules reviews at optimal intervals for long-term retention.": "Никогда не забывайте то, что выучили. Алгоритм SM-2 запланирует повторения в оптимальные интервалы для долговременного запоминания.",
    "Progress Tracking": "Отслеживание прогресса",
    "Visualize your learning journey with detailed statistics, streak tracking, heatmaps, and achievement system.": "Визуализируйте свой путь обучения с подробной статистикой, отслеживанием серии, тепловыми картами и системой достижений.",
    "Community Ready": "Готово к сообществу",
    "Built for future social features: leaderboards, study groups, code sharing, and collaborative learning.": "Построено для будущих социальных функций: таблицы лидеров, учебные группы, обмен кодом и совместное обучение.",
    "Programming Languages": "Языков программирования",
    "Course Programs": "Учебных программ",
    "Interactive Lessons": "Интерактивных урока",
    "Practice Exercises": "Упражнения для практики",
    "Ready to Start Coding?": "Готовы начать кодить?",
    "Join thousands of learners mastering programming languages with RTK. Free forever, no credit card required.": "Присоединяйтесь к тысячам учащихся, осваивающих языки программирования с RTK. Бесплатно навсегда, кредитная карта не требуется.",
    "Continue Learning": "Продолжить обучение",
    "Create Free Account": "Создать бесплатный аккаунт",
    "Explore Languages": "Изучить языки",

    # Login
    "Welcome Back": "Добро пожаловать обратно",
    "Sign in to continue learning": "Войдите, чтобы продолжить обучение",
    "Email or Username": "Электронная почта или имя пользователя",
    "Password": "Пароль",
    "Remember me": "Запомнить меня",
    "Don't have an account?": "Еще нет аккаунта?",
    "Forgot password?": "Забыли пароль?",

    # Register
    "Create Account": "Создать аккаунт",
    "Join RTK and start learning 6 programming languages": "Присоединяйтесь к RTK и начните изучение 6 языков программирования",
    "Email": "Электронная почта",
    "Username": "Имя пользователя",
    "150 chars max. Letters, digits and @/./+/-/_ only.": "Максимум 150 символов. Только буквы, цифры и @/./+/-/_.",
    "At least 8 characters.": "Не менее 8 символов.",
    "Confirm Password": "Подтвердите пароль",
    "I agree to the": "Я соглашаюсь с",
    "Terms of Service": "Условиями обслуживания",
    "and": "и",
    "Privacy Policy": "Политикой конфиденциальности",
    "Already have an account?": "Уже есть аккаунт?",

    # Dashboard
    "Dashboard": "Панель управления",
    "Total XP": "Всего XP",
    "Day Streak": "Серия дней",
    "Cabinet Sections": "Разделы кабинета",
    "Overview": "Обзор",
    "Learning Path": "Путь обучения",
    "Achievements": "Достижения",
    "Languages Learning": "Изучаемые языки",
    "Lessons Completed": "Завершено уроков",
    "Exercises Solved": "Решено упражнений",
    "Current Level": "Текущий уровень",
    "Continue Learning": "Продолжить обучение",
    "No lessons in progress. Start learning!": "Нет уроков в процессе. Начните обучение!",
    "Recent Practice": "Недавняя практика",
    "No recent practice sessions.": "Недавно не было сессий практики.",
    "Start Practicing": "Начать практику",
    "ago": "назад",
    "Your Learning Path": "Ваш путь обучения",
    "topics": "тем",
    "Continue": "Продолжить",
    "No active course": "Нет активного курса",
    "Choose Course": "Выбрать курс",
    "No languages selected yet": "Языки пока не выбраны",
    "Select a language in settings to start your learning journey": "Выберите язык в настройках, чтобы начать свой путь обучения",
    "Open Settings": "Открыть настройки",
    "Recommended Practice": "Рекомендуемая практика",
    "All Exercises": "Все упражнения",
    "Practice recommendations coming soon": "Рекомендации по практике скоро будут доступны",
    "Based on your learning progress, we'll suggest relevant exercises": "На основе вашего прогресса мы подберем релевантные упражнения",
    "Daily Challenge": "Ежедневный вызов",
    "Progress Overview": "Обзор прогресса",
    "Full Statistics": "Полная статистика",
    "Lessons": "Уроки",
    "Topics": "Темы",
    "Exercises": "Упражнения",
    "Select a language to see progress": "Выберите язык, чтобы увидеть прогресс",
    "Achievements system coming soon": "Система достижений скоро будет доступна",
    "Earn badges for completing courses, streaks, and milestones": "Получайте значки за завершение курсов, серии и вехи",
    "Quick Settings": "Быстрые настройки",
    "Appearance": "Внешний вид",
    "Theme": "Тема",
    "Dark": "Тёмная",
    "Light": "Светлая",
    "Auto": "Авто",
    "Language": "Язык",
    "Russian": "Русский",
    "English": "Английский",
    "Learning Preferences": "Предпочтения в обучении",
    "Primary Language": "Основной язык",
    "Select language": "Выбрать язык",
    "Streak reminders": "Напоминания о серии",
    "AI Assistant": "AI-помощник",
    "Open Chat": "Открыть чат",
    "Your Personal Coding Assistant": "Ваш личный помощник по кодированию",
    "Get help with code explanations, debugging, exercise hints, and learning guidance. Powered by multiple AI providers.": "Получайте помощь с объяснением кода, отладкой, подсказками к упражнениям и руководством по обучению. Работает на нескольких провайдерах ИИ.",
    "Start Chatting": "Начать чат",

    # Profile
    "Edit Profile": "Редактировать профиль",
    "Total XP": "Всего XP",
    "Level": "Уровень",
    "Lessons Done": "Завершено уроков",
    "Languages Progress": "Прогресс по языкам",
    "No languages selected yet": "Языки пока не выбраны",
    "Select Languages": "Выбрать языки",
    "About": "Обо мне",
    "Links": "Ссылки",
    "Website": "Веб-сайт",

    # Settings
    "Save Settings": "Сохранить настройки",
    "Cancel": "Отмена",
    "Danger Zone": "Опасная зона",
    "Change Password": "Изменить пароль",
    "Verify Email": "Подтвердить email",
    "Delete Account": "Удалить аккаунт",
    "This action is irreversible!": "Это действие необратимо!",
    "Deleting your account will permanently remove all your data including:": "Удаление аккаунта безвозвратно удалит все ваши данные, включая:",
    "Learning progress and statistics": "Прогресс и статистику обучения",
    "Completed lessons and exercises": "Завершенные уроки и упражнения",
    "Practice history and code submissions": "Историю практики и отправки кода",
    "AI chat history": "Историю чатов с ИИ",
    "Personal settings and preferences": "Личные настройки и предпочтения",
    "Type your username to confirm:": "Введите ваше имя пользователя для подтверждения:",
    "Are you absolutely sure? This cannot be undone.": "Вы абсолютно уверены? Это нельзя отменить.",
    "Account deletion not yet implemented": "Удаление аккаунта еще не реализовано",

    # Languages
    "All Languages": "Все языки",
    "No languages available yet": "Языки пока недоступны",

    # Language detail
    "Enrolled": "Записано",
    "day streak": "дней серии",
    "Continue Learning": "Продолжить обучение",
    "Continue Course": "Продолжить курс",
    "Add to Learning": "Добавить в обучение",
    "Available Courses": "Доступные курсы",
    "Featured": "Рекомендуемое",
    "topics": "тем",
    "lessons": "уроков",
    "No courses available yet": "Курсов пока нет",
    "Courses for this language are coming soon!": "Курсы для этого языка скоро будут доступны!",

    # Program detail
    "Home": "Главная",
    "Languages": "Языки",
    "About This Course": "О данном курсе",
    "Prerequisites": "Предварительные требования",
    "Curriculum": "Учебный план",
    "subtopics": "подтемы",
    "min": "мин",
    "and": "и",
    "more": "еще",
    "No topics published yet": "Тем пока не опубликовано",
    "Total Lessons": "Всего уроков",
    "Enroll Free": "Записаться бесплатно",
    "hours": "часов",
    "students": "студентов",

    # About
    "About RTK": "О RTK",
    "Rust Token Killer - Learn 6 Programming Languages in One Platform": "RTK - Изучение 6 языков программирования на одной платформе",
    "Our Mission": "Наша миссия",
    "RTK was created to make learning programming languages accessible, engaging, and effective. We believe that anyone can learn to code with the right guidance, practice, and tools.": "RTK был создан, чтобы сделать изучение языков программирования доступным, увлекательным и эффективным. Мы верим, что каждый может научиться кодировать с правильным руководством, практикой и инструментами.",
    "Key Features": "Ключевые возможности",
    "6 languages, 12+ courses, 150+ lessons with clear prerequisites and progression paths.": "6 языков, 12+ курсов, 150+ уроков с четкими предварительными требованиями и путями прогрессии.",
    "Interactive Practice": "Интерактивная практика",
    "Real code execution in browser with automated testing, hints, and explanations.": "Выполнение реального кода в браузере с автоматизированным тестированием, подсказками и объяснениями.",
    "Multi-provider AI (OpenAI, Anthropic) for explanations, code review, and personalized help.": "Мультипровайдерный ИИ (OpenAI, Anthropic) для объяснений, ревью кода и персонализированной помощи.",
    "SM-2 algorithm for optimal review scheduling and long-term retention.": "Алгоритм SM-2 для оптимального планирования повторений и долговременного запоминания.",
    "Detailed stats, streaks, heatmaps, achievements, and exportable data.": "Подробная статистика, серии, тепловые карты, достижения и экспортируемые данные.",
    "Privacy First": "Конфиденциальность превыше всего",
    "Your data belongs to you. No tracking, no ads, export anytime.": "Ваши данные принадлежат вам. Нет отслеживания, нет рекламы, экспортируйте в любое время.",
    "Tech Stack": "Технологический стек",
    "Backend": "Бэкенд",
    "Frontend": "Фронтенд",
    "AI & Tools": "ИИ и инструменты",
    "Credits": "Авторы",
    "Built with passion for developers, by developers. Special thanks to the open-source community.": "Создано с энтузиазмом для разработчиков, разработчиками. Особая благодарность сообществу открытого кода.",

    # Contact
    "Contact Us": "Связаться с нами",
    "Have questions? We'd love to hear from you!": "Есть вопросы? Мы будем рады услышать вас!",
    "Name": "Имя",
    "Email": "Электронная почта",
    "Subject": "Тема",
    "Select a topic": "Выбрать тему",
    "General Inquiry": "Общий вопрос",
    "Bug Report": "Сообщение об ошибке",
    "Feature Request": "Запрос функции",
    "Partnership": "Партнерство",
    "Other": "Другое",
    "Message": "Сообщение",
    "Tell us more...": "Расскажите подробнее...",
    "Send Message": "Отправить сообщение",
    "Other Ways to Reach Us": "Другие способы связи",
    "GitHub": "GitHub",
    "Discord": "Discord",
    "Frequently Asked Questions": "Часто задаваемые вопросы",
    "Is RTK really free?": "RTK действительно бесплатен?",
    "Yes! RTK is completely free to use. No credit card required, no hidden fees. We may offer optional premium features in the future, but the core learning experience will always be free.": "Да! RTK полностью бесплатен. Кредитная карта не требуется, нет скрытых комиссий. В будущем могут появиться дополнительные премиум-функции, но базовый опыт обучения всегда останется бесплатным.",
    "Which languages are supported?": "Какие языки поддерживаются?",
    "Currently: Python, JavaScript, Java, C++, Go, and Rust. More languages are planned for future releases.": "В настоящее время: Python, JavaScript, Java, C++, Go и Rust. Больше языков запланировано к будущим релизам.",
    "Do I need to install anything?": "Нужно ли что-то устанавливать?",
    "No! Everything runs in your browser. Our code editor uses Monaco (VS Code's editor) and code execution happens on our servers via Piston API.": "Нет! Все работает в вашем браузере. Редактор кода использует Monaco (редактор VS Code), выполнение кода — на наших серверах через Piston API.",
    "How does the AI assistant work?": "Как работает AI-помощник?",
    "RTK integrates with multiple AI providers (OpenAI, Anthropic). You can use it for code explanations, debugging help, hints, and learning guidance. API keys can be configured in settings.": "RTK интегрируется с несколькими провайдерами ИИ (OpenAI, Anthropic). Используйте его для объяснений кода, помощи с отладкой, подсказок и руководства по обучению. Ключи API настраиваются в настройках.",
    "Can I export my data?": "Могу ли я экспортировать мои данные?",
    "Yes! You can export your progress, settings, and learning data anytime from the Progress section. We believe your data belongs to you.": "Да! Экспортируйте прогресс, настройки и данные об обучении в любое время из раздела Прогресс. Мы считаем, что ваши данные принадлежат вам.",

    # Model field names / verbose_name
    "name": "имя",
    "slug": "слаг",
    "description": "описание",
    "icon": "иконка",
    "color": "цвет",
    "logo": "логотип",
    "version": "версия",
    "programs count": "количество программ",
    "topics count": "количество тем",
    "lessons count": "количество уроков",
    "programming language": "язык программирования",
    "programming languages": "языки программирования",
    "language": "язык",
    "prerequisite programs": "предварительные программы",
    "Programs that must be completed before this one": "Программы, которые нужно пройти перед этой",
    "target level": "целевой уровень",
    "Beginner": "Начинающий",
    "Intermediate": "Средний",
    "Advanced": "Продвинутый",
    "All Levels": "Все уровни",
    "estimated hours": "оценочные часы",
    "course program": "учебная программа",
    "course programs": "учебные программы",
    "program": "программа",
    "topic": "тема",
    "topics": "темы",
    "subtopic": "подтема",
    "subtopics": "подтемы",
    "lesson": "урок",
    "lessons": "уроки",
    "learning objectives": "цели обучения",
    "List of learning objectives for this topic": "Список целей обучения для этой темы",
    "prerequisite topics": "предварительные темы",
    "difficulty": "сложность",
    "Easy": "Легко",
    "Medium": "Средне",
    "Hard": "Сложно",
    "Expert": "Эксперт",
    "estimated minutes": "оценочные минуты",
    "base topic": "базовая тема",
    "short description": "короткое описание",
    "content": "содержимое",
    "Structured lesson content (blocks: heading, text, code, list, table, image, etc.)": "Структурированное содержимое урока (блоки: заголовок, текст, код, список, таблица, изображение и т.д.)",
    "created by": "создано",
    "updated by": "обновлено",
    "change log": "журнал изменений",
    "lesson attachment": "вложение урока",
    "lesson attachments": "вложения уроков",
    "file": "файл",
    "file size (bytes)": "размер файла (байт)",
    "MIME type": "MIME-тип",
    "Image": "Изображение",
    "Document": "Документ",
    "Code File": "Файл кода",
    "Archive": "Архив",
    "Other": "Другое",
    "type": "тип",
    "lesson version": "версия урока",
    "lesson versions": "версии уроков",
    "user": "пользователь",
    "users": "пользователи",
    "username": "имя пользователя",
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.": "Обязательно. 150 символов или меньше. Только буквы, цифры и @/./+/-/_.",
    "A user with that username already exists.": "Пользователь с таким именем пользователя уже существует.",
    "email address": "электронная почта",
    "first name": "имя",
    "last name": "фамилия",
    "preferred language": "предпочитаемый язык",
    "Python": "Python",
    "C++": "C++",
    "C#": "C#",
    "JavaScript": "JavaScript",
    "Rust": "Rust",
    "CSS": "CSS",
    "C": "C",
    "current level": "текущий уровень",
    "Beginner": "Начинающий",
    "Intermediate": "Средний",
    "Advanced": "Продвинутый",
    "onboarding completed": "онбординг завершен",
    "onboarding step": "шаг онбординга",
    "interface language": "язык интерфейса",
    "theme": "тема",
    "Dark": "Тёмная",
    "Light": "Светлая",
    "System": "Системная",
    "email notifications": "уведомления по email",
    "Telegram ID": "ID Telegram",
    "Telegram username": "Имя пользователя Telegram",
    "Telegram first name": "Имя Telegram",
    "Telegram last name": "Фамилия Telegram",
    "last activity": "последняя активность",
    "user profile": "профиль пользователя",
    "user profiles": "профили пользователей",
    "bio": "биография",
    "avatar": "аватар",
    "daily goal (minutes)": "дневная цель (минуты)",
    "preferred difficulty": "предпочитаемая сложность",
    "notify new content": "уведомлять о новом контенте",
    "notify reminders": "уведомлять о напоминаниях",
    "notify achievements": "уведомлять о достижениях",
    "public profile": "открытый профиль",
    "show progress": "показывать прогресс",
    "user settings": "настройки пользователя",
    "editor theme": "тема редактора",
    "editor font size": "размер шрифта редактора",
    "editor tab size": "размер табуляции редактора",
    "editor word wrap": "перенос слов в редакторе",
    "auto run code": "автоматический запуск кода",
    "show line numbers": "показывать номера строк",
    "auto advance to next lesson": "автоматический переход к следующему уроку",
    "show hints by default": "показывать подсказки по умолчанию",
    "spaced repetition enabled": "интервальное повторение включено",
    "preferred AI provider": "предпочитаемый провайдер ИИ",
    "OpenAI": "OpenAI",
    "Anthropic": "Anthropic",
    "Auto": "Авто",
    "preferred AI model": "предпочитаемая модель ИИ",

    # Common model fields
    "created at": "создано",
    "updated at": "обновлено",
    "status": "статус",
    "published": "опубликовано",
    "draft": "черновик",
    "hidden": "скрыто",
    "archived": "архивировано",
    "order": "порядок",
    "published at": "опубликовано в",

    # Practice
    "Practice Task": "Задача практики",
    "Practice Tasks": "Задачи практики",
    "task type": "тип задачи",
    "All Practice Tasks": "Все задачи практики",
    "All Tasks": "Все задачи",
    "Practice Session": "Сессия практики",
    "Practice Sessions": "Сессии практики",
    "AI feedback": "Отклик ИИ",
    "hints used": "использовано подсказок",
    "attempts": "попыток",
    "time spent": "время затрачено",
    "xp earned": "XP заработано",
    "submitted code": "отправленный код",
    "test results": "результаты тестов",

    # Progress
    "User Progress": "Прогресс пользователя",
    "Lesson Progress": "Прогресс урока",
    "Topic Progress": "Прогресс темы",
    "Error History": "История ошибок",
    "Test Result": "Результат теста",
    "error type": "тип ошибки",
    "count": "количество",
    "interval days": "интервал дней",
    "ease factor": "коэффициент легкости",
    "next review": "следующее повторение",
    "is resolved": "разрешено",
    "test type": "тип теста",
    "score": "оценка",
    "questions total": "всего вопросов",
    "questions correct": "верных ответов",
    "passed": "пройдено",

    # AI
    "AI Chat": "Чат с ИИ",
    "AI Code Review": "Ревью кода ИИ",
    "AI Usage Statistics": "Статистика использования ИИ",
    "AI chat session": "сессия чата с ИИ",
    "AI chat sessions": "сессии чата с ИИ",
    "AI message": "сообщение ИИ",
    "AI messages": "сообщения ИИ",
    "AI prompt template": "шаблон запроса ИИ",
    "AI prompt templates": "шаблоны запросов ИИ",
    "AI provider": "провайдер ИИ",
    "AI providers": "провайдеры ИИ",
    "AI usage stats": "статистика использования ИИ",
    "API key": "ключ API",
    "AI integration coming soon. Your question: ": "Интеграция с ИИ скоро будет доступна. Ваш вопрос: ",
    "Ask Assistant": "Спросить помощника",
    "Ask a Question": "Задать вопрос",
    "Assistant": "Помощник",
    "Explain": "Объяснить",
    "Code Review": "Ревью кода",
    "Generate Exercise": "Сгенерировать упражнение",

    # Status / labels
    "Published": "Опубликовано",
    "Draft": "Черновик",
    "Hidden": "Скрыто",
    "Archived": "Архивировано",
    "Active": "Активно",
    "Inactive": "Неактивно",

    # Form labels and validation
    "A user with that email already exists.": "Пользователь с таким email уже существует.",
    "Account created successfully! Welcome to RTK!": "Аккаунт успешно создан! Добро пожаловать в RTK!",
    "150 chars max. Letters, digits and @/./+/-/_ only.": "Максимум 150 символов. Только буквы, цифры и @/./+/-/_.",
    "At least 8 characters.": "Не менее 8 символов.",

    # Misc
    "About": "Обо мне",
    "Links": "Ссылки",
    "Website": "Веб-сайт",
}

# .po file header
PO_HEADER = '''# Russian translations for RTK project
msgid ""
msgstr ""
"Project-Id-Version: RTK 1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: \\n"
"PO-Revision-Date: \\n"
"Last-Translator: \\n"
"Language-Team: Russian <\\n>"
"Language: ru\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>20) ? 1 : 2);\\n"
'''

# Build .po content
po_content = PO_HEADER + "\n"

for english, russian in TRANSLATIONS.items():
    escaped_english = english.replace('\\', '\\\\').replace('"', '\\"')
    escaped_russian = russian.replace('\\', '\\\\').replace('"', '\\"')
    po_content += f'msgid "{escaped_english}"\n'
    po_content += f'msgstr "{escaped_russian}"\n\n'

# Write .po file
po_file = LOCALE_DIR / "django.po"
po_file.write_text(po_content, encoding="utf-8")
print(f"Written {po_file} with {len(TRANSLATIONS)} translations")


def unescape_po_string(s):
    """Convert .po escape sequences to actual characters (\\n, \\", \\\\, \\t, \\r)."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == 'n':
                result.append('\n')
            elif nxt == 't':
                result.append('\t')
            elif nxt == 'r':
                result.append('\r')
            elif nxt == '"':
                result.append('"')
            elif nxt == '\\':
                result.append('\\')
            else:
                result.append(s[i])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def compile_mo(po_path, mo_path):
    """Compile a .po file to .mo format using pure Python."""
    messages = []
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    current_msgid = None
    current_msgstr = None
    collecting_msgid = False
    collecting_msgstr = False

    for line in content.split('\n'):
        stripped = line.rstrip('\r\n')
        if stripped.startswith('msgid '):
            if current_msgid is not None:
                messages.append((current_msgid, current_msgstr or ""))
            val = stripped[6:]
            if val.startswith('"') and val.endswith('"'):
                current_msgid = unescape_po_string(val[1:-1])
            else:
                current_msgid = unescape_po_string(val)
            collecting_msgid = True
            collecting_msgstr = False
        elif stripped.startswith('msgstr '):
            val = stripped[7:]
            if val.startswith('"') and val.endswith('"'):
                current_msgstr = unescape_po_string(val[1:-1])
            else:
                current_msgstr = unescape_po_string(val)
            collecting_msgstr = True
            collecting_msgid = False
        elif stripped.startswith('"') and collecting_msgid:
            val = stripped[1:-1] if stripped.endswith('"') else stripped[1:]
            current_msgid += unescape_po_string(val)
        elif stripped.startswith('"') and collecting_msgstr:
            val = stripped[1:-1] if stripped.endswith('"') else stripped[1:]
            current_msgstr += unescape_po_string(val)

    if current_msgid is not None:
        messages.append((current_msgid, current_msgstr or ""))

    messages = [(m, s) for m, s in messages if m is not None]
    messages.sort(key=lambda x: (x[0] != "", x[0]))  # header (empty msgid) first

    mo_data = bytearray()
    mo_data.extend(struct.pack('<I', 0x950412de))  # magic (Python gettext LE_MAGIC)
    mo_data.extend(struct.pack('<I', 0))  # version
    mo_data.extend(struct.pack('<I', len(messages)))  # num messages

    msgid_table_offset = 28
    msgstr_table_offset = msgid_table_offset + len(messages) * 8

    mo_data.extend(struct.pack('<I', msgid_table_offset))
    mo_data.extend(struct.pack('<I', msgstr_table_offset))
    mo_data.extend(struct.pack('<I', 0))  # hash table size
    mo_data.extend(struct.pack('<I', 0))  # hash table offset

    current_str_offset = msgstr_table_offset + len(messages) * 8

    msgid_table = bytearray()
    msgstr_table = bytearray()
    strings_data = bytearray()

    for msgid, msgstr in messages:
        msgid_bytes = msgid.encode('utf-8')
        msgstr_bytes = msgstr.encode('utf-8')

        msgid_table.extend(struct.pack('<I', len(msgid_bytes)))
        msgid_table.extend(struct.pack('<I', current_str_offset))
        strings_data.extend(msgid_bytes)
        current_str_offset += len(msgid_bytes)

        msgstr_table.extend(struct.pack('<I', len(msgstr_bytes)))
        msgstr_table.extend(struct.pack('<I', current_str_offset))
        strings_data.extend(msgstr_bytes)
        current_str_offset += len(msgstr_bytes)

    mo_data.extend(msgid_table)
    mo_data.extend(msgstr_table)
    mo_data.extend(strings_data)
    mo_data.extend(b'\x00')  # trailing byte: Python gettext requires tend < buflen

    mo_path.write_bytes(mo_data)
    print(f"Written {mo_path} with {len(messages)} messages")


mo_file = LOCALE_DIR / "django.mo"
compile_mo(po_file, mo_file)
