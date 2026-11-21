#!/bin/bash
# ============================================
# Kernify - Скрипт установки для macOS
# Запуск: ./install.sh  (или bash install.sh)
# ============================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/xiip.shk/работа/Kernify"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Kernify - Установка окружения (macOS)${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

cd "$PROJECT_DIR"

# 1. Проверка Python
echo -e "${YELLOW}[1/7] Проверка Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден. Установите через: brew install python${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION найден${NC}"

# 2. Проверка/создание виртуального окружения
echo -e "${YELLOW}[2/7] Настройка виртуального окружения...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Виртуальное окружение создано${NC}"
else
    echo -e "${GREEN}✅ Виртуальное окружение уже существует${NC}"
fi

# 3. Активация и обновление pip
echo -e "${YELLOW}[3/7] Активация окружения и обновление pip...${NC}"
source venv/bin/activate
pip install --upgrade pip wheel setuptools > /dev/null 2>&1
echo -e "${GREEN}✅ pip обновлён${NC}"

# 4. Установка зависимостей
echo -e "${YELLOW}[4/7] Установка Python-зависимостей...${NC}"
# Основные зависимости (Django и др. не в requirements.txt — ставим явно)
# django-environ>=0.11.0 — исправляет SyntaxError на Python 3.9+ (environ без django- ставит сломанный пакет)
pip install django "django-environ>=0.11.0" djangorestframework pillow python-dotenv django-ratelimit pytest-django > /dev/null 2>&1
# Зависимости из requirements.txt (тесты, линтеры)
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
fi
echo -e "${GREEN}✅ Зависимости установлены${NC}"

# 5. Настройка .env
echo -e "${YELLOW}[5/7] Настройка .env файла...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        # Генерируем случайный SECRET_KEY
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        # Подставляем в .env (macOS sed требует '' для -i)
        sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        echo -e "${GREEN}✅ .env создан из примера, SECRET_KEY сгенерирован${NC}"
    else
        echo -e "${RED}❌ .env.example не найден${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env уже существует${NC}"
fi

# 6. Миграции БД
echo -e "${YELLOW}[6/7] Применение миграций базы данных...${NC}"
python manage.py migrate
echo -e "${GREEN}✅ Миграции применены${NC}"

# 7. Сборка статики
echo -e "${YELLOW}[7/7] Сборка статических файлов...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Статика собрана${NC}"

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${GREEN}🎉 Установка завершена успешно!${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Следующие шаги:"
echo -e "  1. Создайте суперюзера для админки:"
echo -e "     ${YELLOW}source venv/bin/activate && python manage.py createsuperuser${NC}"
echo -e "  2. Запустите сервер:"
echo -e "     ${YELLOW}./run.sh${NC}  (или ${YELLOW}source venv/bin/activate && python manage.py runserver${NC})"
echo -e "  3. Откройте в браузере: ${BLUE}http://127.0.0.1:8000/${NC}"
echo -e "  4. Админка: ${BLUE}http://127.0.0.1:8000/admin/${NC}"
echo ""