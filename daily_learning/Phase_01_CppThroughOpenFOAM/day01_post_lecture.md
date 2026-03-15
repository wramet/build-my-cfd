# Day 01 — Post-Lecture Notes: Templates & Generic Programming

**Date:** 2026-03-15
**Day:** 01 of 84
**Topic:** Building `Field<T>` with Modern C++

---

## Part 1: Pattern Identification

### What I understood

Without templates, every CFD data type (`double`, `int`, `Vector3`) needs its own class
(`ScalarField`, `VectorField`, `TensorField`, ...) even though the logic is identical.
Templates solve this by parameterizing code by type — one `Field<T>` replaces N separate classes.

We use `std::vector<T>` as backing storage instead of raw pointers. This gives us automatic
memory allocation and deallocation (RAII), so no manual `new`/`delete`.

### What I missed

**Template instantiation:** The compiler does not share one piece of code for all types.
When you write `Field<double>` and `Field<Vector3>`, the compiler generates **two separate
classes** at compile time — each fully specialized. This is called **template instantiation**.

```cpp
Field<double>  pressure(1000);   // compiler generates Field_double class
Field<Vector3> velocity(1000);   // compiler generates Field_Vector3 class
```

Consequence: zero runtime overhead (no vtable, no type check) but potential **code bloat**
if you instantiate many types.

**Template argument deduction:** When calling template functions you rarely need to write
the type explicitly — the compiler deduces it from the argument:

```cpp
Field<double> pressure(100);
double total = sum(pressure);       // compiler deduces Type = double
// same as: double total = sum<double>(pressure);
```

**`noexcept` on non-throwing functions:** Methods like `size()` and `empty()` are marked
`noexcept` as a performance hint — the compiler can optimize call sites that know no
exception will be thrown.

```cpp
std::size_t size() const noexcept { return data_.size(); }
bool empty()       const noexcept { return data_.empty(); }
```

---

## Part 2: OpenFOAM Source — Historical Comparison

### What I understood

OpenFOAM's `Field<Type>` inherits from both `List<Type>` (raw `new/delete` storage) and
`tmp<Field<Type>>::refCount` (intrusive reference counting). These were correct solutions
for C++98 — they solved real memory management and ownership problems before C++11 move
semantics existed.

### What I missed

**`pTraits<Type>::zero` vs `T{}`:** OpenFOAM uses `pTraits<Type>::zero` as a type-safe
zero value because `Type()` was not reliable in C++98. Modern C++ uses **value
initialization** `T{}` which is guaranteed to zero-initialize for all arithmetic types and
call the default constructor for class types.

```cpp
// OpenFOAM (C++98)
Type result = pTraits<Type>::zero;

// Modern C++20
T result = T{};   // equivalent, cleaner, no pTraits needed
```

**`tmp<Field<Type>>`:** OpenFOAM's `tmp<>` wrapper was a pre-C++11 workaround to avoid
copying large fields when returning from functions. In C++11+, **move semantics** handle
this automatically — the compiler moves (not copies) the return value with zero extra cost.

**`typedef` vs `using`:** The `using` alias can be templated, which `typedef` cannot:

```cpp
// typedef cannot do this:
// template<typename T> typedef Field<T> FieldOf;  // ILLEGAL

// using can:
template<typename T> using FieldOf = Field<T>;     // OK
```

This is why all modern code prefers `using`.

---

## Part 3: C++ Mechanics Explained

### What I understood

C++20 Concepts let us write explicit requirements for what `T` must support. This moves
errors from runtime to compile time and produces clear error messages instead of 40-line
template noise.

For the `Field<T>` case, we don't use base class + virtual because:
- These classes store data and perform uniform math operations — the logic is identical
  for every type.
- Virtual dispatch adds overhead (~2 ns per call) which is significant when iterating
  over millions of cells per time step.

### My question from Part 3 — answered

> "Is the reason we don't use base class because these classes only store data and
> compute statistics?"

**Partially correct.** The complete rule is:

| Use **templates** when... | Use **virtual dispatch** when... |
|---|---|
| Algorithm is identical, only the type changes | Behavior changes depending on the subtype |
| You need zero-overhead tight loops | Swapping implementations at runtime is needed |
| Compile-time type safety matters | You need a heterogeneous collection (`vector<Base*>`) |

`Field<T>` uses templates because `sum()`, `operator+`, `average()` — the logic is
100% identical whether `T` is `double` or `Vector3`. Only the **type** changes, not
the **behavior**. This is exactly the template use case.

### What I missed

**Two-phase compilation:** C++ compiles templates in two phases:
- **Phase 1** (template definition): syntax is checked, non-dependent names resolved.
- **Phase 2** (template instantiation): `T` is substituted, all type-dependent names
  resolved. Errors caught here appear only when you first use `Field<SomeType>`.

Concepts move Phase 2 errors to Phase 1 — you get the error at the template definition
site, not at the call site.

**The `FieldElement` concept in full:**

```cpp
template<typename T>
concept FieldElement = requires(T a, T b, double s) {
    { T{} };                                        // zero-initialization
    { a + b } -> std::same_as<T>;                  // addition returns T
    { a += b };                                     // in-place accumulation
    { s * a } -> std::same_as<T>;                  // scalar-left multiply
    { a < b } -> std::convertible_to<bool>;        // ordering for max/min
};
```

Each `{ expr } -> ReturnType` line is a **requirement** — the concept fails at compile
time if any expression is invalid or returns the wrong type.

---

## Part 4: Implementation Exercise

### What I understood

- **`+` vs `+=`:** `operator+` creates a new `Field` (returns by value); `operator+=`
  modifies the existing object in-place and returns `*this`.
- **Constructor overloads:** Multiple constructors let the class be built from a size,
  a size + fill value, or an initializer list.
- **`const` vs non-`const` operator[]:** Both are needed — one for reading from a
  `const Field`, one for writing to a non-`const` Field.

### What I missed

**`friend operator*(double, Field<T>)` — commutative scalar multiply:**

The scalar multiply is a `friend` free function, not a member. This is intentional:

```cpp
// If it were a member:
field * 2.0;   // OK: field.operator*(2.0)
2.0 * field;   // ERROR: 2.0 has no operator*(Field)

// As a friend free function:
friend Field operator*(double s, const Field& f);
2.0 * field;   // OK: operator*(2.0, field)
field * 2.0;   // still needs a separate overload or explicit conversion
```

This is the standard way to achieve **commutative** operators when the left operand is
not of the class type.

**`std::reduce` and `std::ranges::transform` instead of raw loops:**

```cpp
// Old (raw loop):
T sum_val = T{};
for (int i = 0; i < size_; ++i) sum_val += data_[i];

// Modern (std::reduce):
T sum_val = std::reduce(data_.begin(), data_.end(), T{});
```

`std::reduce` can be parallelized with `std::execution::par` — the raw loop cannot.
`std::ranges::transform` works on ranges and composes with other range operations.

**`average()` as a non-member free function:**

```cpp
template<FieldElement T>
T average(const Field<T>& f) {
    if (f.empty()) throw std::runtime_error("average() on empty Field");
    return (1.0 / static_cast<double>(f.size())) * f.sum();
}
```

Three details here:
1. **Non-member by design** — `average()` is not a method of `Field`. It is a generic
   algorithm that works on any type satisfying `FieldElement`. This keeps `Field` minimal.
2. **`static_cast<double>(f.size())`** — `size()` returns `std::size_t` (unsigned).
   Dividing `1.0 / std::size_t` can produce incorrect results in edge cases.
   The cast to `double` ensures floating-point division.
3. **Uses `friend operator*(double, Field<T>)`** — the scalar multiply must exist for
   this to compile, which is why `friend operator*` is needed in the class.

**Range support — `begin()` / `end()`:**

```cpp
auto begin()       { return data_.begin(); }
auto end()         { return data_.end(); }
auto begin() const { return data_.cbegin(); }
auto end()   const { return data_.cend(); }
```

Exposing these four methods turns `Field<T>` into a range. This enables:
- Range-based `for (const auto& v : field)`
- All `std::ranges::` algorithms (`max_element`, `transform`, `sort`, ...)
- Future composition with `std::views`

**`std::ostream& operator<<` — truncated display:**

The `<<` operator only prints the first 5 elements and appends `...` if there are more.
This is a deliberate design choice — printing a million-element field to stdout is never
useful.

---

## Summary of Missed Points

| # | Topic | Why it matters |
|---|-------|----------------|
| 1 | Template instantiation generates separate classes per type | Explains zero overhead + code bloat trade-off |
| 2 | Template argument deduction | Explains why you rarely write `sum<double>(f)` |
| 3 | `noexcept` on non-throwing methods | Performance optimization hint for the compiler |
| 4 | `pTraits<Type>::zero` vs `T{}` | Links OpenFOAM pattern to modern equivalent |
| 5 | `tmp<>` wrapper → move semantics | Explains why OpenFOAM needs `tmp<>` and we don't |
| 6 | Two-phase template compilation | Explains when template errors fire |
| 7 | Full `FieldElement` concept syntax | Each requirement line is a checked expression |
| 8 | `friend operator*(double, Field<T>)` — commutativity | Why `2.0 * field` requires a free function |
| 9 | `std::reduce` is parallelizable | Performance reason to prefer it over raw loops |
| 10 | `average()` as non-member + `static_cast<double>` | Non-member design + safe size_t division |
| 11 | `begin()`/`end()` enabling range support | Unlocks all `std::ranges::` algorithms |

---

## Key Patterns to Remember

```
Raw new/delete    → std::vector<T>          (RAII, automatic memory)
typedef           → using                   (template-compatible aliases)
for(int i=0;...)  → std::reduce / transform (composable, parallelizable)
unconstrained T   → FieldElement T          (concept, clear errors)
member operator*  → friend free operator*   (enables a * b when a is not Field)
```

---

**Next:** Day 02 — C++20 Concepts in depth. Write your own Concepts, understand `requires`
clauses, and see why Concepts replace OpenFOAM's heavy SFINAE patterns.
