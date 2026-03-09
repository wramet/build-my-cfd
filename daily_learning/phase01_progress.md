# Phase 1 Progress — Modern C++ Foundation (Days 01–14)

**Goal:** Build a complete, tested `Field<T>` library
**Milestone:** move = O(1), expression templates = 0 allocations, ≥10 tests passing

---

## Day 01 — Templates & Generic Programming

**Core concept:** Class templates eliminate type duplication — one `Field<T>` replaces N separate classes.

```
Part 1: Pattern Identification
  ✅ 1.1  The Problem — Type Duplication
  ✅ 1.2  Templates — The Solution
  ✅ 1.3  Our Design vs OpenFOAM's Design
  [ ] 1.4  Template Instantiation — What the Compiler Does

Part 2: OpenFOAM Source — Historical Comparison
  [ ] 2.1  OpenFOAM's Field<Type> (C++98 style)
  [ ] 2.2  OpenFOAM's Arithmetic — Macro loops
  [ ] 2.3  Type Aliases — typedef vs using

Part 3: C++ Mechanics Explained
  [ ] 3.1  Two-Phase Compilation Model
  [ ] 3.2  C++20 Concepts — Explicit Requirements
  [ ] 3.3  Template Argument Deduction
  [ ] 3.4  Why Not virtual + Inheritance?

Part 4: Implementation Exercise
  [ ] 4.1  Build Field<T> from scratch (compile & run)

Part 5: Exercises
  [ ] 5.1  Instantiation count
  [ ] 5.2  magnitude()
  [ ] 5.3  normalize()
```

---

## Day 02 — C++20 Concepts & Constraints

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4 — Deliverable
```

---

## Day 03 — Mesh-to-Field Relationship

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 04 — CRTP — Static Polymorphism

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 05 — Policy-Based Design

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 06 — Smart Pointers

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4 — Deliverable
```

---

## Day 07 — Move Semantics

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 08 — Perfect Forwarding

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4 — Deliverable
```

---

## Day 09 — Expression Templates Part 1

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 10 — C++20 Modules

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 11 — C++20 Ranges

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4 — Deliverable
```

---

## Day 12 — Type Traits & SFINAE

```
[ ] Part 1
[ ] Part 2
[ ] Part 3
[ ] Part 4
[ ] Part 5 — Deliverable
```

---

## Day 13 — Mini-Project Part 1

```
[ ] Part 1 — Project Overview
[ ] Part 2 — File Structure
[ ] Part 3 — Core Implementation
[ ] Part 4 — Tests
[ ] Part 5 — Benchmark
[ ] Part 6 — Deliverable
```

---

## Day 14 — Mini-Project Part 2

```
[ ] Part 1 — Project Overview
[ ] Part 2 — File Structure
[ ] Part 3 — Core Implementation
[ ] Part 4 — Tests
[ ] Part 5 — Benchmark
[ ] Part 6 — Deliverable
```

---

## Phase 1 Milestone Checklist

- [ ] Day 13–14 deliverable compiles: `cmake -S . -B build && cmake --build build`
- [ ] `ctest` passes ≥ 10 tests
- [ ] Benchmark shows: copy = O(n), move = O(1)
- [ ] Benchmark shows: expression templates = 0 allocations
