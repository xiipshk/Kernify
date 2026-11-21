# -*- coding: utf-8 -*-
"""Заполняет пустые bash-блоки в фикстурах уроков осмысленными командами.

Запуск: python fill_empty_bash_blocks.py
После этого нужно переимпортировать уроки в БД.
"""

import json
import os

BASE = 'fixtures/lessons'

# (файл, индекс блока) -> содержимое
FILL = {
    # ---------------- Python ----------------
    'python/11.json': {
        21: """python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\\Scripts\\activate       # Windows

pip install --upgrade pip
deactivate""",
        25: """pip install requests
pip install "requests>=2.31,<3"
pip list
pip show requests
pip uninstall requests""",
        54: """pip install ruff
ruff check .          # линтинг
ruff format .         # форматирование
ruff check --fix .    # автоисправление""",
        58: """python -m build
python -m twine upload dist/*""",
    },
    'python/22.json': {
        13: """python -m cProfile -o profile.out script.py
python -c "import pstats; pstats.Stats('profile.out').sort_stats('cumtime').print_stats(20)"

# Визуализация:
pip install snakeviz
snakeviz profile.out""",
        52: """pip install py-spy
py-spy top --pid 12345
py-spy record -o profile.svg --pid 12345 --duration 30""",
        54: """# Непрерывный сбор профилей (Pyroscope, Datadog, Grafana Cloud)
pyroscope exec -application-name myapp -- python app.py""",
    },
    'python/24.json': {
        60: """# py-spy умеет показывать нативные (C) кадры
py-spy record --native -o native-profile.svg -- python app.py

# perf на Linux — символы C-расширения
perf record -g python app.py
perf report""",
    },
    'python/30.json': {
        5: """python -m build
python -m twine upload dist/*""",
        14: """pip install isort
isort src/
isort --check-only --diff src/   # проверка без изменений

# или через ruff:
ruff check --select I --fix .""",
    },
    'python/31.json': {
        11: """pip install python-dotenv
export DATABASE_URL="postgresql://user:pass@localhost/db"
python -c "import os; print(os.environ['DATABASE_URL'])"
# .env — только для локальной разработки, добавьте его в .gitignore""",
    },
    'python/32.json': {
        26: """pip install alembic
alembic init migrations
alembic revision --autogenerate -m "add users table"
alembic upgrade head
alembic downgrade -1""",
    },
    'python/33.json': {
        8: """python -m pydoc -b       # локальная документация stdlib в браузере
python -c "import this"   # Zen of Python""",
        15: """git clone https://github.com/python/cpython.git
cd cpython
./configure --with-pydebug
make -j$(nproc)
./python -c "import sys; print(sys.version)\"""",
        42: """git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

python -m build
python -m twine upload dist/*""",
    },

    # ---------------- C++ ----------------
    'cpp/18.json': {
        19: """g++ -std=c++20 -c src/main.cpp -o main.o
g++ -std=c++20 -c src/math.cpp -o math.o
g++ main.o math.o -o app
./app""",
    },
    'cpp/19.json': {
        10: """g++ -fsanitize=address,undefined -g -O1 main.cpp -o app
./app""",
        25: """clang-tidy main.cpp -- -std=c++20 -I include
clang-tidy -checks='-*,bugprone-*,modernize-*' src/*.cpp -- -std=c++20""",
        27: """cppcheck --enable=all --std=c++20 -I include src/""",
    },
    'cpp/21.json': {
        17: """perf record -g ./app
perf report
perf stat ./app""",
        21: """# Instruments из состава Xcode
xcrun xctrace record --template 'Time Profiler' --launch ./app""",
        23: """# Windows Performance Recorder / Analyzer
wpr -start CPU -filemode
# ... запустить приложение ...
wpr -stop cpu.etl
wpa cpu.etl""",
        26: """g++ -std=c++20 -O2 bench.cpp -lbenchmark -lpthread -o bench
./bench --benchmark_format=console""",
    },
    'cpp/22.json': {
        20: """pip install pre-commit
pre-commit install
pre-commit run --all-files""",
    },
    'cpp/23.json': {
        66: """# UBSan
clang++ -fsanitize=undefined -fno-sanitize-recover=all -g main.cpp -o app

# Valgrind (memcheck)
valgrind --tool=memcheck --leak-check=full ./app""",
    },
    'cpp/29.json': {
        44: """nm -C libmylib.a | head
objdump -t libmylib.so | c++filt
readelf -Ws libmylib.so | c++filt""",
    },
    'cpp/30.json': {
        10: """# Локальный просмотр ассемблера (аналог Compiler Explorer)
g++ -std=c++20 -O2 -S main.cpp -o main.s
clang++ -std=c++20 -O2 -S -masm=intel main.cpp -o main.s
cat main.s""",
        33: """perf record -g -F 999 ./app
perf report --stdio
perf annotate""",
        35: """vtune -collect hotspots -result-dir results ./app
vtune -report summary -result-dir results""",
        51: """g++ -std=c++20 -O2 -fprofile-generate -o app main.cpp
./app                 # собираем профиль на реальных данных
g++ -std=c++20 -O2 -fprofile-use -o app main.cpp""",
        53: """cl /O2 /GL main.cpp /Fe:app.exe /link /LTCG /GENPROFILE
app.exe
cl /O2 /GL main.cpp /Fe:app.exe /link /LTCG /USEPROFILE""",
        55: """clang++ -O2 -fno-reorder-blocks-and-partition -Wl,--emit-relocs main.cpp -o app
perf record -e cycles:u -j any,u -o perf.data -- ./app
llvm-bolt app -o app.bolt -data perf.data -reorder-blocks=ext-tsp -reorder-functions=hfsort""",
    },
    'cpp/31.json': {
        15: """g++ -fsanitize=address -fno-omit-frame-pointer -g -O1 main.cpp -o app
ASAN_OPTIONS=detect_leaks=1 ./app""",
        23: """g++ -fsanitize=address -g -O1 main.cpp -o app
ASAN_OPTIONS=detect_leaks=1 ./app""",
        25: """# HWASan (ARM64 / Android)
clang++ --target=aarch64-linux-android -fsanitize=hwaddress -g main.cpp -o app

# KASAN — только для ядра Linux (CONFIG_KASAN=y)""",
        29: """clang++ -fsanitize=fuzzer,address -g fuzz_target.cpp -o fuzz
./fuzz -max_len=1024 -runs=100000""",
        31: """afl-clang-fast++ -g fuzz_target.cpp -o app
afl-fuzz -i seeds/ -o output/ -- ./app @@""",
        38: """# Минимальный запуск с корпусом и словарём
./fuzz corpus/ -dict=tokens.dict -max_total_time=600 -jobs=4 -workers=4""",
        41: """scan-build --use-analyzer=$(which clang++) cmake --build build
# или напрямую:
scan-build g++ -std=c++20 main.cpp -o app""",
        43: """clang-tidy -checks='-*,bugprone-*,cert-*,clang-analyzer-*' src/*.cpp -- -std=c++20""",
        52: """g++ -std=c++20 -O2 -D_FORTIFY_SOURCE=3 \\
  -fstack-protector-strong -fstack-clash-protection \\
  -fcf-protection=full -fPIE -pie -Wl,-z,relro,-z,now \\
  main.cpp -o app""",
        68: """# Генерация SBOM через Syft
syft dir:. -o spdx-json > sbom.spdx.json

# или CycloneDX
cyclonedx-cpp --input build/compile_commands.json --output sbom.json""",
        70: """# Проверка уязвимостей по SBOM
grype sbom:sbom.spdx.json
# или
osv-scanner --lockfile=conan.lock""",
        72: """# Фиксируем окружение и проверяем воспроизводимость сборки
SOURCE_DATE_EPOCH=1700000000 g++ -std=c++20 -O2 main.cpp -o app
sha256sum app""",
    },
    'cpp/32.json': {
        38: """g++ -std=c++20 main.cpp $(pkg-config --cflags --libs fmt) -o app
pkg-config --modversion fmt""",
    },
    'cpp/33.json': {
        32: """doxygen Doxyfile
# результат — docs/html/index.html""",
    },

    # ---------------- JavaScript ----------------
    'javascript/15.json': {
        36: """npm install --save-dev esbuild
npx esbuild src/index.ts --bundle --minify --outfile=dist/bundle.js
npx esbuild src/index.ts --bundle --watch --outfile=dist/bundle.js""",
    },
    'javascript/18.json': {
        42: """npm install dotenv
node -r dotenv/config app.js
# в продакшене секреты берутся из окружения / secret manager""",
    },
    'javascript/19.json': {
        8: """npx eslint .
npx eslint . --fix
npx eslint src/ --max-warnings=0""",
        60: """npx madge --circular src/
npx depcruise src/
npx knip""",
    },
    'javascript/20.json': {
        30: """npm audit
npm audit fix
npm audit --production""",
        53: """npm install --save-dev webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/stats.json
# или для Vite:
npx vite-bundle-visualizer""",
    },
    'javascript/27.json': {
        58: """node --inspect app.js
# DevTools → Memory → Take heap snapshot
node --heap-prof app.js""",
    },
    'javascript/28.json': {
        8: """node --prof app.js
node --prof-process isolate-*.log > profile.txt
node --cpu-prof app.js""",
    },
    'javascript/29.json': {
        48: """npm audit
npm ci --ignore-scripts
npm audit signatures""",
        52: """npm audit signatures
npm view lodash dist.integrity
npm ci""",
        74: """npm audit --json > audit.json
npm audit fix
npm outdated""",
    },
    'javascript/30.json': {
        23: """npx vite-bundle-visualizer
npx webpack-bundle-analyzer stats.json
npx source-map-explorer dist/assets/*.js""",
        53: """npm install --save-dev turbo
npx turbo run build test lint
# или Nx
npx nx graph""",
        64: """npx vite build --mode production
npx source-map-explorer dist/assets/*.js""",
    },
    'javascript/31.json': {
        29: """npm install --save-dev openapi-typescript
npx openapi-typescript ./openapi.yaml -o ./src/api-types.ts""",
    },

    # ---------------- Rust ----------------
    'rust/01.json': {
        8: """winget install Rustlang.Rustup
rustup-init.exe
rustup default stable-msvc""",
        45: """rustc -O main.rs
rustc -g main.rs
rustc --edition 2021 main.rs -o app
rustc --emit=asm main.rs""",
        50: """cargo new hello_rust
cd hello_rust
cargo run""",
    },
    'rust/09.json': {
        78: """mkdir my_workspace && cd my_workspace
cargo new --lib core
cargo new --bin app
# добавьте members = ["core", "app"] в Cargo.toml
cargo build --workspace""",
    },
    'rust/18.json': {
        61: """cargo test
cargo test -- --nocapture
cargo test add_tests
cargo test --release""",
    },
    'rust/22.json': {
        24: """cargo run -- --urls urls.txt --depth 2 --concurrency 10
cargo test""",
    },
    'rust/31.json': {
        25: """rustup target add aarch64-unknown-linux-gnu
rustup target add x86_64-pc-windows-gnu
rustup target list --installed""",
        49: """cargo login
cargo publish --dry-run
cargo publish""",
        51: """cargo yank --version 1.0.1
cargo yank --version 1.0.1 --undo""",
        60: """cargo login --registry=my-registry
# токен сохраняется в ~/.cargo/credentials.toml
cargo publish --registry=my-registry""",
        65: """cargo install cargo-edit cargo-watch cargo-nextest cargo-audit
cargo add serde --features derive
cargo watch -x run""",
        72: """cargo run -p xtask -- generate
cargo xtask generate   # алиас в .cargo/config.toml""",
        88: """cargo update
cargo update -p serde
cargo update --dry-run
cargo tree -d""",
    },
    'rust/32.json': {
        23: """heaptrack ./target/release/app
heaptrack_gui heaptrack.app.*.gz""",
    },

    # ---------------- CSS ----------------
    'css/31.json': {
        12: """sass styles/main.scss styles/main.css
sass --watch styles/main.scss:styles/main.css
sass --style=compressed styles/main.scss styles/main.min.css""",
        40: """npx postcss src/styles.css -o dist/styles.css
npx postcss src/styles.css -o dist/styles.css --watch""",
        94: """npx stylelint "**/*.css"
npx stylelint "**/*.css" --fix""",
    },

    # ---------------- C# ----------------
    'csharp/01.json': {
        26: """dotnet build
dotnet build -c Release
dotnet publish -c Release -o ./publish
dotnet publish -c Release -r linux-x64 --self-contained true""",
    },
    'csharp/11.json': {
        9: """dotnet add package System.Text.Json   # для .NET 6/7
dotnet restore""",
    },
    'csharp/18.json': {
        13: """dotnet build
ildasm MyApp.dll /out=MyApp.il
# или кросс-платформенно:
dotnet tool install -g ilspycmd
ilspycmd MyApp.dll""",
        49: """sn -k key.snk
csc /keyfile:key.snk Program.cs
sn -v MyApp.dll""",
        54: """dotnet tool install -g dotnet-counters
dotnet-counters monitor -p 12345
dotnet-trace collect -p 12345 --duration 00:00:30
dotnet-dump collect -p 12345""",
    },
    'csharp/19.json': {
        43: """dotnet test --collect:"XPlat Code Coverage"
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator -reports:coverage.cobertura.xml -targetdir:coveragereport -reporttypes:Html""",
        52: """dotnet-dump collect -p 12345 -o dump.dmp
dotnet-dump analyze dump.dmp
# внутри: clrstack, dumpheap -stat, gcroot <addr>""",
    },
    'csharp/20.json': {
        40: """dotnet tool install --global dotnet-ef
dotnet ef migrations add InitialCreate
dotnet ef database update
dotnet ef migrations list""",
    },
    'csharp/24.json': {
        6: """dotnet build
dotnet tool install -g ilspycmd
ilspycmd bin/Debug/net8.0/MyApp.dll""",
    },
    'csharp/28.json': {
        13: """dotnet tool install -g dotnet-trace
dotnet-trace collect -p 12345 --profile cpu-sampling
dotnet-trace convert trace.nettrace --format speedscope""",
        15: """PerfView.exe collect /onlyProviders=*Microsoft-Windows-DotNETRuntime
PerfView.exe trace.etl""",
        28: """dotnet publish -c Release -p:PublishReadyToRun=true
DOTNET_TieredPGO=1 dotnet run -c Release""",
    },
    'csharp/33.json': {
        42: """dotnet-trace collect -p $(pgrep MyApp) --profile cpu-sampling
dotnet-counters monitor -p $(pgrep MyApp) --counters System.Runtime""",
    },
}


def main():
    filled = 0
    errors = []
    for rel, blocks_map in FILL.items():
        path = os.path.join(BASE, rel)
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        blocks = data['content_blocks']
        for idx, content in blocks_map.items():
            if idx >= len(blocks):
                errors.append(f'{rel}: индекс {idx} вне диапазона ({len(blocks)})')
                continue
            block = blocks[idx]
            if block.get('type') != 'code':
                errors.append(f'{rel}#{idx}: тип {block.get("type")!r}, ожидался code')
                continue
            if str(block.get('language', '')).lower() not in ('bash', 'shell', 'sh'):
                errors.append(f'{rel}#{idx}: язык {block.get("language")!r}, ожидался bash')
                continue
            if str(block.get('content', '') or '').strip():
                errors.append(f'{rel}#{idx}: блок уже заполнен, пропущен')
                continue
            block['content'] = content.strip('\n')
            filled += 1
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')

    print(f'Заполнено блоков: {filled}')
    if errors:
        print('Проблемы:')
        for e in errors:
            print('  -', e)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
