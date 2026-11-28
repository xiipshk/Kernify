@echo off
chcp 65001 >nul
setlocal EnableExtensions DisableDelayedExpansion
title Kernify - установка
cd /d "%~dp0"

echo ============================================
echo   Kernify - установка для Windows
echo ============================================
echo.

REM ============================================
REM 1. Поиск подходящего Python (3.9 - 3.13)
REM ============================================
echo [1/8] Поиск Python...
set "PY_CMD="
for %%V in (3.12 3.11 3.10 3.13) do (
    if not defined PY_CMD (
        py -%%V -c "import sys" >nul 2>&1
        if not errorlevel 1 set "PY_CMD=py -%%V"
    )
)
if not defined PY_CMD (
    python -c "import sys" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD goto :no_python

for /f "delims=" %%V in ('%PY_CMD% -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"') do set "PY_VER=%%V"
%PY_CMD% -c "import sys; sys.exit(0 if (3, 9) <= sys.version_info < (3, 14) else 1)"
if errorlevel 1 goto :bad_python
echo       Найден Python %PY_VER%  [%PY_CMD%]

REM ============================================
REM 2. Виртуальное окружение
REM ============================================
echo.
echo [2/8] Виртуальное окружение...
if exist "venv\Scripts\python.exe" goto :venv_existing
if exist ".venv\Scripts\python.exe" goto :venv_existing_dot
if exist "venv" goto :venv_from_mac

%PY_CMD% -m venv venv
if errorlevel 1 goto :venv_failed
set "VENV_PY=venv\Scripts\python.exe"
echo       Создано окружение venv
goto :venv_ready

:venv_from_mac
echo       В папке venv находится окружение от macOS/Linux.
echo       Создаю отдельное окружение .venv для Windows...
%PY_CMD% -m venv .venv
if errorlevel 1 goto :venv_failed
set "VENV_PY=.venv\Scripts\python.exe"
echo       Создано окружение .venv
goto :venv_ready

:venv_existing
set "VENV_PY=venv\Scripts\python.exe"
echo       Использую существующее окружение venv
goto :venv_ready

:venv_existing_dot
set "VENV_PY=.venv\Scripts\python.exe"
echo       Использую существующее окружение .venv
goto :venv_ready

:venv_ready
if not exist "%VENV_PY%" goto :venv_failed

REM ============================================
REM 3. Обновление pip
REM ============================================
echo.
echo [3/8] Обновление pip...
"%VENV_PY%" -m pip install --upgrade pip wheel setuptools
if errorlevel 1 echo       ПРЕДУПРЕЖДЕНИЕ: не удалось обновить pip, продолжаю...

REM ============================================
REM 4. Зависимости
REM ============================================
echo.
echo [4/8] Установка зависимостей...
echo       Ставлю пакеты, необходимые для работы сайта...
"%VENV_PY%" -m pip install "Django==4.2.16" "djangorestframework==3.15.2" "django-environ>=0.11.0" "Pillow>=10.4.0" "httpx>=0.27.2" "django-ratelimit>=4.1.0" "django-json-widget>=2.2.0"
if errorlevel 1 goto :deps_failed

"%VENV_PY%" -c "import django, environ, rest_framework, PIL, httpx" >nul 2>&1
if errorlevel 1 goto :deps_failed

echo.
echo       Устанавливаю остальные пакеты из requirements.txt...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 echo       ПРЕДУПРЕЖДЕНИЕ: часть необязательных пакетов не установилась. На работу сайта это не влияет.
echo       Зависимости готовы.

REM ============================================
REM 5. Файл .env
REM ============================================
echo.
echo [5/8] Настройка .env...
if exist ".env" goto :env_ready
if not exist ".env.example" goto :env_missing

copy /y ".env.example" ".env" >nul
"%VENV_PY%" -c "from pathlib import Path; import re; from django.core.management.utils import get_random_secret_key; p = Path('.env'); t = p.read_text(encoding='utf-8'); t = re.sub(r'(?m)^SECRET_KEY=.*$', lambda m: 'SECRET_KEY=' + get_random_secret_key().replace('#', ''), t); p.write_text(t, encoding='utf-8')"
if errorlevel 1 goto :env_missing
echo       Создан .env со случайным SECRET_KEY
goto :env_ready

:env_missing
echo       ПРЕДУПРЕЖДЕНИЕ: .env.example не найден, создаю минимальный .env
> ".env" echo SECRET_KEY=django-insecure-change-me-in-production
>> ".env" echo DEBUG=True
>> ".env" echo ALLOWED_HOSTS=localhost,127.0.0.1
>> ".env" echo DATABASE_URL=sqlite:///db.sqlite3

:env_ready

REM ============================================
REM 6. Миграции базы данных
REM ============================================
echo.
echo [6/8] Применение миграций базы данных...
"%VENV_PY%" manage.py migrate --noinput
if errorlevel 1 goto :failed

REM ============================================
REM 7. Статические файлы
REM ============================================
echo.
echo [7/8] Сборка статических файлов...
"%VENV_PY%" manage.py collectstatic --noinput --verbosity 0
if errorlevel 1 goto :failed
echo       Статика собрана

REM ============================================
REM 8. Администратор и раннер кода
REM ============================================
echo.
echo [8/8] Дополнительная настройка...
call :maybe_superuser
call :setup_runner

echo.
echo ============================================
echo   Установка завершена!
echo ============================================
echo.
echo   Запуск сайта:  start.bat
echo   Сайт:          http://127.0.0.1:8000/
echo   Админка:       http://127.0.0.1:8000/admin/
echo.
echo   Порт можно изменить:  start.bat 8001
echo.
pause
exit /b 0

REM ============================================
REM Подпрограммы
REM ============================================

:maybe_superuser
"%VENV_PY%" -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup(); from accounts.models import User; raise SystemExit(0 if User.objects.filter(is_superuser=True).exists() else 1)" >nul 2>&1
if not errorlevel 1 exit /b 0
echo.
echo       Администратор ещё не создан.
choice /c YN /n /m "Создать администратора сайта сейчас? [Y/N] "
if errorlevel 2 exit /b 0
echo.
"%VENV_PY%" manage.py createsuperuser
exit /b 0

:setup_runner
where docker >nul 2>&1
if errorlevel 1 goto :runner_no_docker
docker info >nul 2>&1
if errorlevel 1 goto :runner_not_running

docker image inspect kernify-runner >nul 2>&1
if not errorlevel 1 goto :runner_have_image
echo.
echo       Собираю образ для выполнения кода. Первый раз это занимает несколько минут...
docker build -t kernify-runner -f native-runner/Dockerfile native-runner
if errorlevel 1 goto :runner_build_failed

:runner_have_image
docker ps --format "{{.Names}}" | findstr /x "kernify-runner" >nul 2>&1
if not errorlevel 1 goto :runner_already
docker rm -f kernify-runner >nul 2>&1
docker run -d --name kernify-runner --restart unless-stopped -p 127.0.0.1:2000:2000 kernify-runner >nul 2>&1
if errorlevel 1 goto :runner_start_failed
echo       Раннер кода запущен: 127.0.0.1:2000
exit /b 0

:runner_already
echo       Раннер кода уже запущен.
exit /b 0

:runner_no_docker
echo.
echo       Docker не найден. Выполнение кода в задачах будет недоступно.
where winget >nul 2>&1
if errorlevel 1 goto :runner_docker_manual
choice /c YN /n /m "Установить Docker Desktop сейчас через winget? [Y/N] "
if errorlevel 2 goto :runner_docker_manual
echo.
echo       Устанавливаю Docker Desktop. Это может занять несколько минут...
winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
if errorlevel 1 goto :runner_docker_failed
echo.
echo       Docker Desktop установлен.
echo       Запустите Docker Desktop, при необходимости перезагрузите компьютер,
echo       затем снова запустите install.bat, чтобы настроить раннер кода.
exit /b 0

:runner_docker_manual
echo       Установить Docker Desktop можно вручную:
echo       https://www.docker.com/products/docker-desktop/
echo       После установки запустите Docker Desktop и снова запустите install.bat.
exit /b 0

:runner_docker_failed
echo       ПРЕДУПРЕЖДЕНИЕ: не удалось установить Docker Desktop автоматически.
echo       Установите его вручную: https://www.docker.com/products/docker-desktop/
exit /b 0

:runner_not_running
echo.
echo       Docker установлен, но не запущен. Выполнение кода будет недоступно.
echo       Запустите Docker Desktop и при необходимости снова запустите install.bat.
exit /b 0

:runner_build_failed
echo       ПРЕДУПРЕЖДЕНИЕ: не удалось собрать образ раннера.
echo       Выполнение кода в задачах будет недоступно.
exit /b 0

:runner_start_failed
echo       ПРЕДУПРЕЖДЕНИЕ: не удалось запустить контейнер раннера.
echo       Выполнение кода в задачах будет недоступно.
exit /b 0

REM ============================================
REM Ошибки
REM ============================================

:no_python
echo.
echo   Python не найден.
where winget >nul 2>&1
if errorlevel 1 goto :python_manual
choice /c YN /n /m "Установить Python 3.12 автоматически через winget? [Y/N] "
if errorlevel 2 goto :python_manual
echo.
echo   Устанавливаю Python 3.12...
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo   Если установка завершилась, закройте это окно и запустите install.bat снова.
pause
exit /b 1

:python_manual
echo.
echo   Установите Python 3.12 вручную:
echo   https://www.python.org/downloads/windows/
echo   При установке отметьте "Add python.exe to PATH".
pause
exit /b 1

:bad_python
echo.
echo   Неподходящая версия Python: %PY_VER%
echo   Нужен Python от 3.9 до 3.13, рекомендуется 3.12.
echo   Скачать: https://www.python.org/downloads/windows/
where winget >nul 2>&1
if errorlevel 1 goto :bad_python_end
choice /c YN /n /m "Установить Python 3.12 автоматически через winget? [Y/N] "
if errorlevel 2 goto :bad_python_end
echo.
echo   Устанавливаю Python 3.12...
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo   После установки закройте это окно и запустите install.bat снова.
:bad_python_end
pause
exit /b 1

:venv_failed
echo.
echo   ОШИБКА: не удалось создать виртуальное окружение.
echo   Установите Python 3.12 и запустите install.bat снова.
pause
exit /b 1

:deps_failed
echo.
echo   ОШИБКА: не удалось установить зависимости.
echo   Проверьте подключение к интернету и версию Python, рекомендуется 3.12.
pause
exit /b 1

:failed
echo.
echo   ОШИБКА при выполнении команды. Смотрите сообщения выше.
pause
exit /b 1
