@echo off
chcp 65001 >nul
setlocal EnableExtensions DisableDelayedExpansion
title Kernify - запуск сайта
cd /d "%~dp0"

set "PORT=%~1"
if not defined PORT set "PORT=8000"

echo ============================================
echo   Kernify - запуск сайта
echo ============================================
echo.

REM ============================================
REM Поиск виртуального окружения
REM ============================================
set "VENV_PY="
if exist "venv\Scripts\python.exe" set "VENV_PY=venv\Scripts\python.exe"
if not defined VENV_PY if exist ".venv\Scripts\python.exe" set "VENV_PY=.venv\Scripts\python.exe"
if not defined VENV_PY goto :no_venv

"%VENV_PY%" -c "import django" >nul 2>&1
if errorlevel 1 goto :no_deps

REM ============================================
REM Проверка .env
REM ============================================
if exist ".env" goto :env_ready
echo .env не найден, создаю из .env.example...
if not exist ".env.example" goto :env_ready
copy /y ".env.example" ".env" >nul
"%VENV_PY%" -c "from pathlib import Path; import re; from django.core.management.utils import get_random_secret_key; p = Path('.env'); t = p.read_text(encoding='utf-8'); t = re.sub(r'(?m)^SECRET_KEY=.*$', lambda m: 'SECRET_KEY=' + get_random_secret_key().replace('#', ''), t); p.write_text(t, encoding='utf-8')"

:env_ready
REM ============================================
REM Миграции и ежедневная задача
REM ============================================
echo Проверяю миграции...
"%VENV_PY%" manage.py migrate --noinput
if errorlevel 1 goto :failed

"%VENV_PY%" manage.py set_daily_challenge --days 7 >nul 2>&1

call :start_runner

REM ============================================
REM Запуск сервера
REM ============================================
echo.
echo   Сайт:    http://127.0.0.1:%PORT%/
echo   Админка: http://127.0.0.1:%PORT%/admin/
echo.
echo   Для остановки нажмите Ctrl+C.
echo ============================================
echo.

start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 4; Start-Process 'http://127.0.0.1:%PORT%/'"

"%VENV_PY%" manage.py runserver 127.0.0.1:%PORT%
goto :eof

REM ============================================
REM Подпрограммы
REM ============================================

:start_runner
where docker >nul 2>&1
if errorlevel 1 goto :runner_no_docker
docker info >nul 2>&1
if errorlevel 1 goto :runner_not_running

docker image inspect kernify-runner >nul 2>&1
if errorlevel 1 goto :runner_no_image

docker ps --format "{{.Names}}" | findstr /x "kernify-runner" >nul 2>&1
if not errorlevel 1 goto :runner_already

docker start kernify-runner >nul 2>&1
if errorlevel 1 docker run -d --name kernify-runner --restart unless-stopped -p 127.0.0.1:2000:2000 kernify-runner >nul 2>&1
if errorlevel 1 goto :runner_start_failed
echo Раннер кода запущен: 127.0.0.1:2000
exit /b 0

:runner_already
echo Раннер кода уже запущен.
exit /b 0

:runner_no_docker
echo Docker не найден - выполнение кода в задачах будет недоступно.
echo Запустите install.bat, чтобы установить Docker Desktop.
exit /b 0

:runner_not_running
echo Docker не запущен - выполнение кода в задачах будет недоступно.
echo Для выполнения кода запустите Docker Desktop.
exit /b 0

:runner_no_image
echo Раннер кода не настроен. Запустите install.bat при работающем Docker Desktop.
exit /b 0

:runner_start_failed
echo Не удалось запустить раннер кода - выполнение кода будет недоступно.
exit /b 0

REM ============================================
REM Ошибки
REM ============================================

:no_venv
echo.
echo   Виртуальное окружение не найдено.
echo   Сначала запустите install.bat.
echo.
pause
exit /b 1

:no_deps
echo.
echo   Зависимости не установлены.
echo   Запустите install.bat.
echo.
pause
exit /b 1

:failed
echo.
echo   Не удалось запустить сайт. Смотрите сообщения выше.
pause
exit /b 1
