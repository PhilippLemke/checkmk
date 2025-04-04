# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# TODO(sp) We should really use autotools here...
ifneq ($(shell which g++-14 2>/dev/null),)
        CXX := g++-14 -std=c++20
else ifneq ($(shell which clang++-19 2>/dev/null),)
        CXX := clang++-19 -std=c++20
else ifneq ($(shell which g++-13 2>/dev/null),)
        CXX := g++-13 -std=c++20
else ifneq ($(shell which clang++-18 2>/dev/null),)
        CXX := clang++-18 -std=c++20
else ifneq ($(shell which clang++-17 2>/dev/null),)
        CXX := clang++-17 -std=c++20
else ifneq ($(shell which clang++-16 2>/dev/null),)
        CXX := clang++-16 -std=c++20
else ifneq ($(shell which g++-12 2>/dev/null),)
        CXX := g++-12 -std=c++20
else ifneq ($(shell which clang++-15 2>/dev/null),)
        CXX := clang++-15 -std=c++20
else ifneq ($(shell which clang++-14 2>/dev/null),)
        CXX := clang++-14 -std=c++20
else ifneq ($(shell which clang++-13 2>/dev/null),)
        CXX := clang++-13 -std=c++20
else ifneq ($(shell which g++-11 2>/dev/null),)
        CXX := g++-11 -std=c++20
else ifneq ($(shell which clang++-12 2>/dev/null),)
        CXX := clang++-12 -std=c++20
else ifneq ($(shell which g++-10 2>/dev/null),)
        CXX := g++-10 -std=c++20
else ifneq ($(shell which g++ 2>/dev/null),)
        CXX := g++ -std=c++20
else
        CXX := clang++ -std=c++20
endif

CXXFLAGS    := -g -O3 -Wall -Wextra
LDFLAGS     := -static-libstdc++

.PHONY: all clean

all: $(EXECUTABLES)

clean:
	$(RM) $(EXECUTABLES)
