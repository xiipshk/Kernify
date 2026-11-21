# -*- coding: utf-8 -*-
"""Пустые code-блоки: Rust (TOML / конфигурации)."""

from fill_common import apply_fill

FILL = {
    'rust/08.json': {
        31: r"""
[dependencies]
thiserror = "2.0"
""",
        33: r"""
[dependencies]
anyhow = "1.0"
""",
    },
    'rust/09.json': {
        42: r"""
[workspace]
members = ["core", "app", "shared"]
resolver = "2"

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
""",
        76: r"""
[features]
default = ["json"]
json = ["dep:serde_json"]
""",
    },
    'rust/18.json': {
        34: r"""
[dev-dependencies]
proptest = "1.5"
""",
        43: r"""
[dev-dependencies]
mockall = "0.13"
""",
        52: r"""
# Отключить тесты для библиотеки пакета
[lib]
test = false
doctest = false

# Отключить тесты для конкретного бинарника
[[bin]]
name = "tool"
path = "src/main.rs"
test = false
""",
    },
    'rust/19.json': {
        23: r"""
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
chrono = { version = "0.4", features = ["serde"] }
""",
    },
    'rust/22.json': {
        6: r"""
# config.toml
max_depth = 3
max_concurrent = 50
timeout_secs = 10
user_agent = "crawler/0.1 (+https://example.com/bot)"

[storage]
output_dir = "data/pages"
format = "json"

[filter]
allowed_domains = ["example.com", "docs.example.com"]
""",
    },
    'rust/30.json': {
        20: r"""
[build-dependencies]
bindgen = "0.70"

[dependencies]
libc = "0.2"
""",
        33: r"""
[package]
name = "embedded-demo"
version = "0.1.0"
edition = "2021"

[dependencies]
cortex-m = "0.7"
cortex-m-rt = "0.7"
panic-halt = "1.0"

[profile.release]
panic = "abort"
lto = true
opt-level = "s"
""",
    },
    'rust/31.json': {
        3: r"""
[workspace]
members = ["crates/core", "crates/cli"]
resolver = "2"
""",
        5: r"""
# Вариант 1: виртуальный манифест (без [package])
[workspace]
members = ["core", "cli"]

# Вариант 2: пакет, который одновременно является корнем workspace
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"

[workspace]
members = ["core"]
""",
        7: r"""
[workspace]
members = ["core", "cli"]
resolver = "2"

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
""",
        16: r"""
[features]
default = ["std"]
std = []

# Фичи должны только добавлять возможности (additive)
ui = ["dep:ratatui"]
metrics = ["dep:prometheus"]
full = ["ui", "metrics"]

# ❌ Плохо: фича, которая отключает поведение по умолчанию,
# ломает feature unification при сборке нескольких крейтов.
""",
        27: r"""
# .cargo/config.toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
runner = "qemu-aarch64 -L /usr/aarch64-linux-gnu"

[target.x86_64-pc-windows-gnu]
linker = "x86_64-w64-mingw32-gcc"

[build]
target-dir = "target"
""",
        31: r"""
# .cargo/config.toml
[target.x86_64-unknown-linux-musl]
linker = "zig cc -target x86_64-linux-musl"

[target.aarch64-unknown-linux-musl]
linker = "zig cc -target aarch64-linux-musl"

[target.x86_64-pc-windows-gnu]
linker = "zig cc -target x86_64-windows-gnu"
""",
        36: r"""
[profile.dev]
opt-level = 0
debug = true

[profile.release]
opt-level = 3
debug = false
lto = "thin"
codegen-units = 16
""",
        45: r"""
[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"
description = "Короткое описание крейта"
license = "MIT OR Apache-2.0"
repository = "https://github.com/user/my-crate"
readme = "README.md"
keywords = ["cli", "parser"]
categories = ["command-line-utilities"]
exclude = ["tests/fixtures/*", ".github/*"]
""",
        47: r"""
# [package].version следует SemVer: MAJOR.MINOR.PATCH
# 1.4.2 -> 1.4.3  Патч: исправление, обратная совместимость
# 1.4.2 -> 1.5.0  Минор: новая функциональность, обратная совместимость
# 1.4.2 -> 2.0.0  Мажор: ломающие изменения

[dependencies]
serde = "^1.0"     # >=1.0.0, <2.0.0
log = "=0.4.22"    # точная версия
tokio = ">=1.30, <2"
""",
        56: r"""
[registries.my-registry]
index = "sparse+https://registry.example.com/index/"

[registries.crates-io]
replace-with = "my-registry"
""",
        58: r"""
[dependencies]
internal-logger = { version = "0.3", registry = "my-registry" }
internal-macros = { git = "https://git.example.com/libs/macros", tag = "v1.2.0" }
""",
        67: r"""
# deny.toml
[advisories]
db-path = "~/.cargo/advisory-db"
vulnerability = "deny"
unmaintained = "warn"
yanked = "deny"

[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause"]
confidence-threshold = 0.8

[bans]
multiple-versions = "warn"
deny = [{ name = "openssl" }]
""",
        69: r"""
# Makefile.toml (cargo-make)
[tasks.build]
command = "cargo"
args = ["build", "--workspace"]

[tasks.test]
command = "cargo"
args = ["nextest", "run", "--workspace"]

[tasks.ci]
dependencies = ["format", "lint", "test"]
""",
        79: r"""
[build-dependencies]
cc = "1.1"

# В build.rs
# cc::Build::new().file("src/native.c").compile("native");
""",
        82: r"""
[patch.crates-io]
serde = { git = "https://github.com/serde-rs/serde", branch = "master" }
my-crate = { path = "../my-crate" }

[target.'cfg(target_os = "linux")'.patch.crates-io]
libc = { git = "https://github.com/rust-lang/libc" }
""",
        86: r"""
[workspace.package]
version = "1.2.3"
edition = "2021"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
serde = "1"

# crates/core/Cargo.toml
[package]
name = "core"
version.workspace = true
edition.workspace = true
license.workspace = true

[dependencies]
serde.workspace = true
""",
        91: r"""
# Корневой Cargo.toml
[workspace]
members = ["core", "app"]
resolver = "2"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }

# core/Cargo.toml
[package]
name = "core"
version = "0.1.0"
edition = "2021"

[features]
default = ["json"]
json = ["dep:serde_json"]

[dependencies]
serde.workspace = true
serde_json = { version = "1", optional = true }
""",
        93: r"""
# .cargo/config.toml для embedded-таргета
[target.thumbv7em-none-eabihf]
rustflags = ["-C", "link-arg=-Tlink.x"]

[build]
target = "thumbv7em-none-eabihf"

[unstable]
build-std = ["core", "alloc"]
""",
    },
    'rust/32.json': {
        4: r"""
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "my_bench"
harness = false
""",
        20: r"""
[dependencies]
mimalloc = { version = "0.1", default-features = false }

# Альтернативы:
# tikv-jemallocator = "0.5"
# snmalloc-rs = "0.3"
""",
        41: r"""
[dev-dependencies]
loom = "0.7"

[target.'cfg(loom)'.dev-dependencies]
loom = "0.7"
""",
        62: r"""
[dev-dependencies]
proptest = "1.5"
""",
        64: r"""
[dev-dependencies]
quickcheck = "1.0"
quickcheck_macros = "1.0"
""",
    },
    'rust/33.json': {
        9: r"""
[workspace]
resolver = "2"
members = ["core", "cli", "server", "xtask"]

[workspace.package]
version = "0.1.0"
edition = "2021"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
anyhow = "1"
thiserror = "2"
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
""",
        51: r"""
[package]
name = "my-project-core"
version = "0.1.0"
edition = "2021"
description = "Ядро проекта: библиотека с бизнес-логикой"
license = "MIT OR Apache-2.0"
repository = "https://github.com/example/my-project"
readme = "README.md"
keywords = ["library", "core"]
categories = ["development-tools"]

[package.metadata.docs.rs]
all-features = true
rustdoc-args = ["--cfg", "docsrs"]
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
