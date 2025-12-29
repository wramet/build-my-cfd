# Modern C++ for CFD

C++17/20 Features ที่ช่วย CFD Development

---

## Overview

> **C++ evolves — เรียนรู้ features ใหม่ที่ช่วยเขียน CFD code ดีขึ้น**

OpenFOAM uses C++11/14. Modern C++ offers:
- Safer memory management
- Cleaner syntax
- Better performance tools

---

## C++17 Features

### 1. std::optional

```cpp
// Old way: pointer + null check
scalar* findPressure(label cellI)
{
    if (cellI < mesh.nCells())
        return &p[cellI];
    return nullptr;  // Error case
}

// Usage: must check for null
scalar* pPtr = findPressure(100);
if (pPtr != nullptr)
    scalar val = *pPtr;
```

```cpp
// C++17 way: explicit optional
std::optional<scalar> findPressure(label cellI)
{
    if (cellI < mesh.nCells())
        return p[cellI];
    return std::nullopt;  // Clearly "no value"
}

// Usage: intent is clear
if (auto val = findPressure(100))
    Info << *val << endl;
```

---

### 2. Structured Bindings

```cpp
// Old way
std::pair<scalar, vector> result = getFlux(facei);
scalar magnitude = result.first;
vector direction = result.second;

// C++17 way
auto [magnitude, direction] = getFlux(facei);
```

CFD Example:
```cpp
// Decompose face data
for (const auto& [owner, neighbour, area] : faceData)
{
    flux[owner] += phi * area;
    flux[neighbour] -= phi * area;
}
```

---

### 3. if constexpr (Compile-time Branching)

```cpp
// Old: SFINAE or runtime check
template<typename T>
void operate(T& field)
{
    if (std::is_same<T, scalar>::value)
        // Scalar-specific code
    else
        // Vector/tensor code
}

// C++17: compile-time decision
template<typename T>
void operate(T& field)
{
    if constexpr (std::is_same_v<T, scalar>)
    {
        // Only compiled for scalar
        field = sqr(field);
    }
    else
    {
        // Only compiled for non-scalar
        field = mag(field);
    }
}
```

---

### 4. Parallel Algorithms

```cpp
#include <execution>
#include <algorithm>

std::vector<double> field(1000000);

// Old: sequential
std::transform(field.begin(), field.end(), field.begin(),
               [](double x) { return x * x; });

// C++17: parallel
std::transform(std::execution::par, 
               field.begin(), field.end(), field.begin(),
               [](double x) { return x * x; });

// C++17: parallel and vectorized
std::transform(std::execution::par_unseq, 
               field.begin(), field.end(), field.begin(),
               [](double x) { return x * x; });
```

---

## C++20 Features

### 1. Concepts (Constrained Templates)

```cpp
// Old: template accepts anything, error messages are cryptic
template<typename T>
T dot(const T& a, const T& b);  // What is T supposed to be?

// C++20: define requirements
template<typename T>
concept VectorLike = requires(T v) {
    { v.x() } -> std::convertible_to<scalar>;
    { v.y() } -> std::convertible_to<scalar>;
    { v.z() } -> std::convertible_to<scalar>;
    { v.size() } -> std::same_as<label>;
};

template<VectorLike V>
scalar dot(const V& a, const V& b)
{
    return a.x()*b.x() + a.y()*b.y() + a.z()*b.z();
}

// Error messages now say "V does not satisfy VectorLike"
```

---

### 2. Ranges

```cpp
#include <ranges>

// Old way: explicit loop
std::vector<double> result;
for (const auto& cell : mesh.cells())
{
    if (cell.volume() > 1e-6)
    {
        result.push_back(cell.volume() * cell.volume());
    }
}

// C++20: pipelines
auto result = mesh.cells()
    | std::views::filter([](auto& c) { return c.volume() > 1e-6; })
    | std::views::transform([](auto& c) { return sqr(c.volume()); })
    | std::ranges::to<std::vector>();
```

---

### 3. Coroutines

```cpp
// Async I/O for large field writes
generator<volScalarField> streamFields(const fvMesh& mesh)
{
    for (const auto& fieldName : fieldNames)
    {
        // Load field on demand
        volScalarField field(IOobject(fieldName, ...), mesh);
        co_yield field;  // Return and suspend
    }
}

// Usage
for (const auto& field : streamFields(mesh))
{
    process(field);
    // Previous field can be freed immediately
}
```

---

### 4. std::span (Non-owning View)

```cpp
// Old: pointer + size
void process(scalar* data, label size)
{
    for (label i = 0; i < size; ++i)
        data[i] *= 2;
}

// C++20: span = view into contiguous data
void process(std::span<scalar> data)
{
    for (auto& x : data)
        x *= 2;
}

// Works with vectors, arrays, C-arrays
std::vector<scalar> vec(100);
process(vec);  // Implicit conversion

scalar arr[100];
process(arr);  // Works too!
```

---

## Why OpenFOAM Doesn't Use These Yet

| Reason | Explanation |
|:---|:---|
| **HPC Cluster compilers** | Many clusters have old GCC (4.8!) |
| **Stability** | New features = new bugs |
| **Testing** | Massive test suite needs update |
| **Backward compatibility** | Users have old code |

---

## Adopting Modern C++ Gradually

### In Your Own Code

```cpp
// Use modern features in your solvers/libraries
// OpenFOAM doesn't restrict what YOU use

#include <optional>
#include <span>

std::optional<vector> findNormal(label faceI)
{
    if (mesh.isInternalFace(faceI))
        return mesh.Sf()[faceI] / mesh.magSf()[faceI];
    return std::nullopt;
}
```

---

## Feature Summary

| Feature | Version | Use Case |
|:---|:---:|:---|
| `std::optional` | C++17 | Nullable returns |
| Structured bindings | C++17 | Multiple returns |
| `if constexpr` | C++17 | Compile-time dispatch |
| Parallel algorithms | C++17 | Easy parallelism |
| Concepts | C++20 | Template constraints |
| Ranges | C++20 | Pipelines |
| Coroutines | C++20 | Async, generators |
| `std::span` | C++20 | Non-owning views |

---

## Concept Check

<details>
<summary><b>1. Concepts vs SFINAE: เมื่อไหร่ใช้อะไร?</b></summary>

**SFINAE:** (Substitution Failure Is Not An Error)
- Old technique for template constraints
- Cryptic error messages
- Hard to read and maintain

**Concepts (C++20):**
- Clear, readable constraints
- Good error messages
- Self-documenting

**Use Concepts if:** Compiler supports C++20
**Use SFINAE if:** Need older compiler support
</details>

<details>
<summary><b>2. ทำไม parallel algorithms ดี?</b></summary>

**Old way:**
```cpp
#pragma omp parallel for
for (int i = 0; i < n; ++i) ...
```
- Requires OpenMP
- Manual parallelization

**std::execution::par:**
```cpp
std::transform(std::execution::par, ...);
```
- Standard C++
- Compiler/library handles details
- Portable

**Trade-off:** May be slower than hand-tuned OpenMP
</details>

---

## Exercise

1. **Modernize Code:** เปลี่ยน function ให้ใช้ `std::optional`
2. **Use Concepts:** สร้าง concept สำหรับ "Field-like" types
3. **Parallel Algorithm:** เปลี่ยน loop เป็น `std::transform` + `par`

---

## เอกสารที่เกี่ยวข้อง

- **ก่อนหน้า:** [GPU Computing](02_GPU_Computing.md)
- **กลับหน้าแรก:** [MODULE 10 Navigator](../../00_Navigator.md)

---

## 🎉 Congratulations!

คุณผ่าน MODULE 10: CFD Engine Development แล้ว!

**สิ่งที่คุณได้เรียนรู้:**
- ผ่าโค้ด OpenFOAM ได้
- Design Patterns ที่ใช้จริง
- Performance Engineering
- สร้าง Solver ตั้งแต่ศูนย์
- ทางเลือกนอก OpenFOAM

**ก้าวต่อไป:** เขียน CFD Engine ของคุณเอง! 🚀
