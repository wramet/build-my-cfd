---
name: cpp-pro
author: sickn33 (Ported & Adapted)
description: Write idiomatic C++ code (Modern vs OpenFOAM aware).
---

# C++ Pro

## Use this skill when
- Working on C++ tasks or workflows
- Needing guidance on Modern C++ features (C++11/14/17/20)
- Refactoring legacy C++ code
- Optimizing for performance

## ⚠️ Important: OpenFOAM Context
**If working on OpenFOAM code, ignore standard "Modern C++" advice in favor of OpenFOAM conventions:**
- **Smart Pointers**: Use `autoPtr` and `tmp` instead of `std::unique_ptr` or `std::shared_ptr`.
- **Memory**: Use OpenFOAM's memory management and object registry.
- **Containers**: Prefer `List`, `PtrList`, `GeometricField` over `std::vector` for field data.
- **Loops**: Use `forAll(list, i)` macros where appropriate in legacy code, but prefer range-based loops `for(const auto& x : list)` in newer OpenFOAM versions.

## Focus Areas (Standard C++)
- Modern C++ (C++11/14/17/20/23) features
- RAII and smart pointers
- Template metaprogramming and concepts
- Move semantics and perfect forwarding
- STL algorithms and containers
- Concurrency with std::thread and atomics

## Approach
1. **Check Context**: Is this OpenFOAM code or standalone C++?
2. **Memory Safety**: Prefer stack allocation and RAII.
3. **Performance**: Leverage STL algorithms (or OpenFOAM equivalents).
4. **Profile**: Use tools like perf and VTune.
