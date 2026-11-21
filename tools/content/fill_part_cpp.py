# -*- coding: utf-8 -*-
"""Пустые code-блоки: C++."""

from fill_common import apply_fill

FILL = {
    'cpp/18.json': {
        10: r"""
cmake_minimum_required(VERSION 3.20)
project(myapp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(myapp src/main.cpp)
""",
        12: r"""
add_library(mylib STATIC src/math.cpp src/string_utils.cpp)
target_include_directories(mylib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE mylib)

target_compile_features(mylib PUBLIC cxx_std_20)
""",
        14: r"""
include(FetchContent)

FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG 10.2.1
)
FetchContent_MakeAvailable(fmt)

target_link_libraries(mylib PRIVATE fmt::fmt)
""",
        17: r"""
cmake_minimum_required(VERSION 3.28)
project(modules_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_SCAN_FOR_MODULES ON)

add_executable(demo src/main.cpp)
target_sources(demo PRIVATE
    FILE_SET CXX_MODULES FILES src/math.cppm
)
""",
    },
    'cpp/19.json': {
        19: r"""
cmake_minimum_required(VERSION 3.20)
project(tests LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
add_compile_options(-g -O0 -Wall -Wextra)

add_executable(tests tests/test_main.cpp)
target_include_directories(tests PRIVATE include third_party/doctest)
""",
        31: r"""
find_package(PVS_Studio REQUIRED)

pvs_studio_add_target(
    TARGET myapp
    ANALYZE
    OUTPUT PVS-Studio.log
    FORMAT tasklist
    MODE GA:1,2
)
""",
        33: r"""
name: C++ CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Configure
        run: cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
      - name: Build
        run: cmake --build build -j
      - name: Test
        run: ctest --test-dir build --output-on-failure
""",
    },
    'cpp/22.json': {
        9: r"""
cmake_minimum_required(VERSION 3.20)
project(taskmanager LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_subdirectory(src)
add_subdirectory(tests)
""",
        18: r"""
name: CI

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v4
        with:
          path: build
          key: ${{ runner.os }}-cmake-${{ hashFiles('**/CMakeLists.txt') }}
      - run: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
      - run: cmake --build build -j
      - run: ctest --test-dir build --output-on-failure
""",
    },
    'cpp/29.json': {
        4: r"""
cmake_minimum_required(VERSION 3.24)
project(bigproject LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

add_subdirectory(libs)
add_subdirectory(apps)
add_subdirectory(tests)
""",
        6: r"""
add_library(mylib
    src/foo.cpp
    src/bar.cpp
)
add_library(mylib::mylib ALIAS mylib)

target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)
""",
        8: r"""
add_library(headerlib INTERFACE)
add_library(headerlib::headerlib ALIAS headerlib)

target_include_directories(headerlib INTERFACE include)
target_compile_features(headerlib INTERFACE cxx_std_20)
""",
        27: r"""
cmake_minimum_required(VERSION 3.28)
project(module_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_SCAN_FOR_MODULES ON)

add_library(demo)
target_sources(demo
    PUBLIC
        FILE_SET CXX_MODULES FILES
            src/math.cppm
            src/math_impl.cpp
)
""",
        33: r"""
# toolchains/aarch64-linux-gnu.cmake
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_C_COMPILER aarch64-linux-gnu-gcc)
set(CMAKE_CXX_COMPILER aarch64-linux-gnu-g++)

set(CMAKE_FIND_ROOT_PATH /usr/aarch64-linux-gnu)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
""",
        39: r"""
# Канадский крест: build (A) -> host (B) -> target (C)
cmake -S . -B build-b \
  -DCMAKE_TOOLCHAIN_FILE=toolchains/aarch64.cmake \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache

cmake --build build-b -j
""",
        49: r"""
include(CPack)

set(CPACK_PACKAGE_NAME "mylib")
set(CPACK_PACKAGE_VERSION "1.0.0")
set(CPACK_PACKAGE_CONTACT "dev@example.com")
set(CPACK_GENERATOR "TGZ;DEB;RPM")

# сборка пакетов:
# cmake --build build --target package
""",
        51: r"""
# conanfile.py
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

class MyLibRecipe(ConanFile):
    name = "mylib"
    version = "1.0.0"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def layout(self):
        cmake_layout(self)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
""",
    },
    'cpp/30.json': {
        46: r"""
set_target_properties(myapp PROPERTIES
    UNITY_BUILD ON
    UNITY_BUILD_BATCH_SIZE 8
)
""",
        48: r"""
target_precompile_headers(myapp PRIVATE
    <vector>
    <string>
    <unordered_map>
    <memory>
)
""",
    },
    'cpp/31.json': {
        49: r"""
name: CodeQL

on:
  push:
    branches: [main]
  schedule:
    - cron: "0 3 * * 1"

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: cpp
      - run: cmake -S . -B build && cmake --build build
      - uses: github/codeql-action/analyze@v3
""",
    },
    'cpp/32.json': {
        8: r"""
add_library(core src/core/*.cpp)
add_library(auth src/auth/*.cpp)
add_library(api src/api/*.cpp)

target_link_libraries(auth PUBLIC core)
target_link_libraries(api PUBLIC core auth)
""",
        36: r"""
include(CMakePackageConfigHelpers)

install(TARGETS mylib EXPORT mylibTargets)
install(EXPORT mylibTargets
    FILE mylibTargets.cmake
    NAMESPACE mylib::
    DESTINATION lib/cmake/mylib
)

configure_package_config_file(
    cmake/mylibConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/mylibConfig.cmake
    INSTALL_DESTINATION lib/cmake/mylib
)
""",
    },
    'cpp/33.json': {
        28: r"""
name: Benchmarks

on:
  pull_request:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
      - run: cmake --build build --target bench
      - run: ./build/bench --benchmark_format=json > bench.json
      - uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: googlecpp
          output-file-path: bench.json
""",
        36: r"""
# FastLog

Быстрая потокобезопасная библиотека логирования для C++20.

## Установка

```bash
cmake -S . -B build
cmake --build build
```

## Быстрый старт

```cpp
#include <fastlog/logger.hpp>

int main() {
    auto logger = fastlog::Logger::create("app");
    logger->info("Hello, {}", "world");
}
```

## Лицензия

MIT
""",
        47: r"""
MIT License

Copyright (c) 2026 FastLog contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
""",
        50: r"""
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        compiler: [gcc, clang]
    steps:
      - uses: actions/checkout@v4
      - run: cmake -S . -B build -DCMAKE_CXX_COMPILER=${{ matrix.compiler }}
      - run: cmake --build build -j
      - run: ctest --test-dir build --output-on-failure
""",
        53: r"""
# ports/fastlog/portfile.cmake
vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO example/fastlog
    REF v1.0.0
    SHA512 0000000000000000000000000000000000000000000000000000000000000000
    HEAD_REF main
)

vcpkg_cmake_configure(SOURCE_PATH "${SOURCE_PATH}")
vcpkg_cmake_install()
vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/fastlog)
""",
        55: r"""
# conanfile.py
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake

class FastLogConan(ConanFile):
    name = "fastlog"
    version = "1.0.0"
    settings = "os", "compiler", "build_type", "arch"

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
""",
    },
}

if __name__ == '__main__':
    apply_fill(FILL)
