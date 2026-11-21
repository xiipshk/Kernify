# Нативный arm64 раннер кода для Kernify (лёгкая замена Piston).
# Сборка и запуск:
#   docker build -t kernify-runner -f native-runner/Dockerfile native-runner
#   docker run -d --name kernify-runner --restart unless-stopped \
#       -p 127.0.0.1:2000:2000 kernify-runner
#
# Запускается от непривилегированного пользователя; процесс пользователя
# ограничивается по времени и памяти в server.py.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# C# выполняется через Mono (mcs + mono), он есть в Ubuntu 24.04.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        nodejs \
        g++ \
        rustc \
        mono-mcs \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 runner
WORKDIR /app
COPY server.py /app/server.py

USER runner
EXPOSE 2000
CMD ["python3", "/app/server.py"]
