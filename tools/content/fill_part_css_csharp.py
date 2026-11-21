# -*- coding: utf-8 -*-
"""Пустые code-блоки: CSS, C#."""

from fill_common import apply_fill

FILL = {
    'css/31.json': {
        114: r"""
name: Visual Regression

on: [push, pull_request]

jobs:
  backstop:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - run: npx http-server dist -p 8080 &
      - run: npm run backstop:test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: backstop-report
          path: backstop_data
""",
    },
    'csharp/19.json': {
        38: r"""
root = true

[*]
charset = utf-8
end_of_line = crlf
insert_final_newline = true
indent_style = space
indent_size = 4
trim_trailing_whitespace = true

[*.{cs,csx}]
dotnet_sort_system_directives_first = true
dotnet_style_qualification_for_field = false:suggestion
csharp_new_line_before_open_brace = all
csharp_prefer_braces = true:suggestion
dotnet_diagnostic.IDE0005.severity = error
dotnet_diagnostic.CA1062.severity = warning

[*.{json,yml,yaml,csproj,props}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
""",
        57: r"""
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
      - name: Restore
        run: dotnet restore
      - name: Build
        run: dotnet build --no-restore -c Release
      - name: Test
        run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage"
      - name: Coverage report
        uses: danielpalme/ReportGenerator-GitHub-Action@5
        with:
          reports: "**/TestResults/**/coverage.cobertura.xml"
          targetdir: coverage-report
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage-report
""",
    },
    'csharp/22.json': {
        48: r"""
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY *.sln .
COPY src/MyApp.Domain/*.csproj src/MyApp.Domain/
COPY src/MyApp.Application/*.csproj src/MyApp.Application/
COPY src/MyApp.Infrastructure/*.csproj src/MyApp.Infrastructure/
COPY src/MyApp.Api/*.csproj src/MyApp.Api/
RUN dotnet restore src/MyApp.Api/MyApp.Api.csproj

COPY . .
RUN dotnet publish src/MyApp.Api/MyApp.Api.csproj \
    -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
COPY --from=build /app/publish .
USER $APP_UID
ENTRYPOINT ["dotnet", "MyApp.Api.dll"]
""",
    },
    'csharp/33.json': {
        17: r"""
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:

env:
  DOTNET_VERSION: "8.0.x"
  DOTNET_NOLOGO: "true"
  DOTNET_CLI_TELEMETRY_OPTOUT: "true"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release --logger "trx;LogFileName=results.trx"
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: "**/*.trx"

  publish:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ env.DOTNET_VERSION }}
      - run: dotnet publish src/Api/Api.csproj -c Release -o publish
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
""",
        21: r"""
# ADR-0001: Adopt Clean Architecture

- **Status:** Accepted
- **Date:** 2026-01-15
- **Deciders:** Architecture team
- **Related:** ADR-0002 (CQRS), ADR-0005 (Observability)
""",
        28: r"""
---

# Postmortem: заказы зависли в статусе "Pending"

- **Incident ID:** INC-2026-014
- **Severity:** SEV-2
- **Duration:** 47 минут
- **Affected service:** myproject-worker
- **Author:** on-call engineer
""",
        37: r"""
Action Items
------------
[ ] Add circuit breaker for payment gateway        @backend-team   due 2026-02-01
[ ] Implement idempotency keys for order creation  @backend-team   due 2026-02-10
[ ] Add distributed lock around order processing    @platform       due 2026-02-15
[ ] Alert on queue depth > 10 000                   @sre            due 2026-01-31

Lessons Learned
---------------
- Retry без идемпотентности превращает сбой платёжного шлюза в дубли заказов.
- Отсутствие алерта на глубину очереди увеличило время обнаружения до 25 минут.
""",
        40: r"""
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "nuget"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    groups:
      microsoft:
        patterns: ["Microsoft.*", "System.*"]
      testing:
        patterns: ["xunit*", "NSubstitute*", "FluentAssertions*"]
    ignore:
      - dependency-name: "Microsoft.EntityFrameworkCore*"
        update-types: ["version-update:semver-major"]

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
