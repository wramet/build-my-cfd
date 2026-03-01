---
name: cpp_pro
description: Write idiomatic C++ code with OpenFOAM awareness
---

# C++ Coding Guidance

When working on C++ code, distinguish between standard Modern C++ and OpenFOAM-specific conventions.

## Context Detection

**First, determine the context:**
- OpenFOAM code → Follow OpenFOAM conventions (below)
- Standalone C++ → Follow Modern C++ best practices

## OpenFOAM Conventions ⚠️

**For OpenFOAM code, use these instead of standard practices:**

| Standard C++ | OpenFOAM Equivalent |
|--------------|---------------------|
| `std::unique_ptr` | `autoPtr<T>` |
| `std::shared_ptr` | `refPtr<T>` |
| `std::vector` | `List<T>`, `PtrList<T>` |
| `new T()` | `new T()` with object registry |
| Range-based `for` | `forAll(list, i)` (legacy) or range-for (newer) |

## Modern C++ Focus Areas

For non-OpenFOAM C++ code:
- C++11/14/17/20/23 features
- RAII and smart pointers
- Template metaprogramming and concepts
- Move semantics and perfect forwarding
- STL algorithms and containers
- Concurrency with `std::thread` and atomics

## Coding Approach

1. **Check Context** → OpenFOAM or standalone?
2. **Memory Safety** → Prefer stack allocation and RAII
3. **Performance** → Use STL algorithms (or OpenFOAM equivalents)
4. **Profile** → Tools: perf, VTune, valgrind
