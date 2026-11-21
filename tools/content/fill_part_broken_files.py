# -*- coding: utf-8 -*-
"""Пустые code-блоки в трёх ранее битых JSON-файлах."""

from fill_common import apply_fill

TQ = '"' * 3

FILL = {
    'python/02.json': {
        5: r"""
# Переменная — имя, которое ссылается на объект в памяти
x = 42
name = "Анна"
price = 199.99
is_active = True

print(x)          # 42
print(name)       # Анна
print(type(x))    # <class 'int'>
""",
        23: rf"""
single = 'одинарные кавычки'
double = "двойные кавычки"
multiline = {TQ}Первая строка
Вторая строка{TQ}

print(single)
print(double)
print(multiline)

text = "Python"
print(text[0])       # P
print(text[-1])      # n
print(text[0:3])     # Pyt
print(len(text))     # 6
print(text.upper())  # PYTHON
""",
        27: r"""
is_ready = True
is_finished = False

print(5 > 3)              # True
print(5 == 3)             # False
print(bool(1), bool(0))   # True False

if is_ready:
    print("Можно начинать")
""",
        31: r"""
number = int("42")
print(number + 8)          # 50

price = float("19.99")
print(price * 2)           # 39.98

age = 20
print("Возраст: " + str(age))

print(int(3.9))            # 3 — дробная часть отбрасывается
print(bool(""))            # False
print(bool("0"))           # True
""",
        35: r"""
name = input("Как вас зовут? ")
print("Привет,", name)

age = int(input("Сколько вам лет? "))
print("Через год вам будет", age + 1)

height = float(input("Ваш рост в метрах: "))
print("Рост в сантиметрах:", height * 100)
""",
    },
    'csharp/32.json': {
        17: r"""
dotnet publish -c Release -r linux-x64 --self-contained false

# Или без указания RID — сборка под текущую платформу
dotnet publish -c Release

# Результат: bin/Release/net8.0/publish/
# Запуск: dotnet MyApp.dll
""",
        21: r"""
dotnet publish -c Release -r linux-x64 --self-contained true
dotnet publish -c Release -r win-x64 --self-contained true
dotnet publish -c Release -r osx-arm64 --self-contained true

# В .csproj:
# <SelfContained>true</SelfContained>
# <RuntimeIdentifier>linux-x64</RuntimeIdentifier>
""",
        35: r"""
dotnet publish -c Release -r linux-x64 \
  -p:PublishSingleFile=true \
  -p:IncludeNativeLibrariesForSelfExtract=true \
  -p:EnableCompressionInSingleFile=true

# Результат: один исполняемый файл MyApp (~60-80 МБ)
""",
        40: r"""
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY *.csproj ./
RUN dotnet restore

COPY . .
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "MyApp.dll"]
""",
        42: r"""
# Native AOT: компиляция в машинный код, .NET Runtime не нужен
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -r linux-x64 -o /app/publish \
    -p:PublishAot=true -p:StripSymbols=true

FROM mcr.microsoft.com/dotnet/runtime-deps:8.0-jammy-chiseled AS runtime
WORKDIR /app
COPY --from=build /app/publish .
USER $APP_UID
ENTRYPOINT ["./MyApp"]
""",
        44: r"""
version: "3.8"
services:
  api:
    build:
      context: .
      target: build
    command: dotnet watch run --project src/Api
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Host=db;Database=myapp;Username=postgres;Password=postgres
    volumes:
      - .:/src
      - ~/.nuget/packages:/root/.nuget/packages
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5
""",
        46: r"""
# Встроенная проверка уязвимых пакетов
dotnet list package --vulnerable --include-transitive

# Машинно-читаемый формат для CI
dotnet list package --vulnerable --format json

# Обновление проблемных пакетов
dotnet list package --outdated
dotnet add package Newtonsoft.Json --version 13.0.3

# Сканирование самого образа
docker scout cves myapp:latest
trivy image myapp:latest
""",
        63: r"""
dotnet publish -c Release -r linux-arm64 --self-contained true
dotnet publish -c Release -r osx-arm64 --self-contained true

# Проверка архитектуры бинарника
file bin/Release/net8.0/linux-arm64/publish/MyApp
uname -m   # arm64 на Apple Silicon

# Запуск x64-образа на Apple Silicon через эмуляцию (медленнее)
docker run --platform linux/amd64 myapp:latest
""",
        65: r"""
# docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest --push .
FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0 AS build
ARG TARGETARCH
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -r linux-$TARGETARCH -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
""",
        70: r"""
dotnet workload install wasm-tools
dotnet publish -c Release -r browser-wasm

# Результат: bin/Release/net8.0/browser-wasm/publish/wwwroot/
# Раздаётся любым статическим хостингом: nginx, GitHub Pages, Azure Static Web Apps
""",
        84: r"""
# NuGetAudit включён по умолчанию в .NET 8+
dotnet restore -p:NuGetAudit=true -p:NuGetAuditMode=all

# Предупреждения NU1902/NU1903 можно сделать ошибками сборки
dotnet build -warnaserror:NU1902,NU1903

# Просмотр уязвимых транзитивных зависимостей
dotnet list package --vulnerable --include-transitive
""",
        89: r"""
name: .NET CI/CD

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build-test-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage"
      - run: dotnet publish src/Api/Api.csproj -c Release -o publish
      - uses: docker/build-push-action@v6
        if: github.ref == 'refs/heads/main'
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
