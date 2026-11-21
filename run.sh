#!/bin/bash
# ============================================
# Kernify - Запуск локального сервера (macOS)
# Запуск: ./run.sh  (или bash run.sh)
# Можно сделать двойной клик в Finder если переименовать в run.command
# ============================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/Users/xiip.shk/работа/Kernify"
PORT="${1:-8000}"  # Можно передать порт: ./run.sh 8001

cd "$PROJECT_DIR"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Kernify - Запуск сервера разработки${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Виртуальное окружение не найдено!${NC}"
    echo -e "Сначала запустите: ${YELLOW}./install.sh${NC}"
    exit 1
fi

# Активация окружения
source venv/bin/activate

# Проверка .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env не найден, создаю из примера...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" .env
        echo -e "${GREEN}✅ .env создан${NC}"
    else
        echo -e "${RED}❌ .env.example не найден${NC}"
        exit 1
    fi
fi

# Проверка миграций (быстрая)
echo -e "${YELLOW}🔍 Проверка миграций...${NC}"
python manage.py migrate --check > /dev/null 2>&1 || {
    echo -e "${YELLOW}⚠️  Есть неприменённые миграции, применяю...${NC}"
    python manage.py migrate
}

echo -e "${GREEN}✅ Готово к запуску${NC}"
echo ""
echo -e "${BLUE}🌐 Сервер будет доступен по адресу:${NC}"
echo -e "   ${GREEN}http://127.0.0.1:$PORT/${NC}"
echo -e "   ${GREEN}http://localhost:$PORT/${NC}"
echo ""
echo -e "${BLUE}📋 Админка:${NC}"
echo -e "   ${GREEN}http://127.0.0.1:$PORT/admin/${NC}"
echo ""
echo -e "${YELLOW}Для остановки нажмите ${BLUE}Ctrl+C${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# ============================================
# Раннер кода (Docker + контейнер kernify-runner)
# ============================================
export PATH="$HOME/homebrew/bin:$PATH"

start_runner() {
    echo -e "${BLUE}🐳 Подготовка раннера кода...${NC}"

    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker не найден — запуск кода будет недоступен.${NC}"
        return 0
    fi

    # Docker-машина (Colima): запускаем, если не работает
    if ! docker info >/dev/null 2>&1; then
        if command -v colima >/dev/null 2>&1; then
            echo -e "${YELLOW}▶️  Запускаю Docker-машину (Colima)...${NC}"
            colima start >/dev/null 2>&1 || {
                echo -e "${YELLOW}⚠️  Не удалось запустить Colima — запуск кода недоступен.${NC}"
                return 0
            }
        else
            echo -e "${YELLOW}⚠️  Colima не найден — запуск кода недоступен.${NC}"
            return 0
        fi
    fi

    # Образ раннера: собираем при первом запуске
    if ! docker image inspect kernify-runner >/dev/null 2>&1; then
        echo -e "${YELLOW}🔨 Первый запуск: собираю образ раннера (займёт несколько минут)...${NC}"
        docker build -t kernify-runner -f native-runner/Dockerfile native-runner >/dev/null 2>&1 || {
            echo -e "${YELLOW}⚠️  Не удалось собрать образ раннера — запуск кода недоступен.${NC}"
            return 0
        }
    fi

    # Контейнер: запускаем, если ещё не работает
    if docker ps --format '{{.Names}}' | grep -q '^kernify-runner$'; then
        echo -e "${GREEN}✅ Раннер кода уже запущен (127.0.0.1:2000)${NC}"
    else
        docker rm -f kernify-runner >/dev/null 2>&1 || true
        if docker run -d --name kernify-runner --restart unless-stopped \
            -p 127.0.0.1:2000:2000 kernify-runner >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Раннер кода запущен (127.0.0.1:2000)${NC}"
        else
            echo -e "${YELLOW}⚠️  Не удалось запустить контейнер раннера — запуск кода недоступен.${NC}"
        fi
    fi
    echo ""
}

start_runner

# Ежедневный вызов — гарантируем, что задача на сегодня выбрана (идемпотентно).
python manage.py set_daily_challenge --days 7 >/dev/null 2>&1 || true

# Запуск сервера
python manage.py runserver "0.0.0.0:$PORT"