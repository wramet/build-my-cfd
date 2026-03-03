# Curriculum Revision Progress — Modern C++ & CFD Architecture

> **Last Updated:** 2026-03-03
> **Current Position:** Phase 5 Complete (Days 57-84), All Phases Complete
> **Approach:** Build a Modern C++17/20 CFD framework from scratch — no proprietary macros, no legacy patterns

---

## Phase Overview

| Phase | Days | Topic | Status | Files Done |
|-------|------|-------|--------|------------|
| 1 | 01–14 | Modern C++ Foundation | ✅ Complete | 14 / 14 |
| 2 | 15–28 | Data Structures & Memory | ✅ Complete | 14 / 14 |
| 3 | 29–42 | Architecture & Build Systems | ✅ Complete | 14 / 14 |
| 4 | 43–56 | Performance Optimization | ✅ Complete | 14 / 14 |
| 5 | 57–84 | VOF-Ready CFD Component | ✅ Complete | 28 / 28 |
| **Total** | **01–84** | | | **84 / 84** |

---

## Phase 1: Modern C++ Foundation (Days 01–14) ✅ COMPLETE

All 14 files verified correct by QC agent (2026-03-01).

- [x] 01.md — Templates & Generic Programming — `Field<T>`
- [x] 02.md — C++20 Concepts & Constraints
- [x] 03.md — Expression Templates & Lazy Evaluation
- [x] 04.md — CRTP — Static Polymorphism
- [x] 05.md — Policy-Based Design
- [x] 06.md — Smart Pointers — `std::unique_ptr` vs Legacy
- [x] 07.md — Move Semantics — Zero-Copy Field Operations
- [x] 08.md — Move Semantics & Perfect Forwarding
- [x] 09.md — Expression Templates — Field Arithmetic
- [x] 10.md — C++20 Modules — Replacing Header Files
- [x] 11.md — `std::format` — Modern String Formatting
- [x] 12.md — Type Traits & SFINAE
- [x] 13.md — Mini-Project Part 1 — `Field<T>` with Expression Templates
- [x] 14.md — Mini-Project Part 2 — Testing & Benchmarking

---

## Phase 2: Data Structures & Memory (Days 15–28) ✅ COMPLETE

**Action key:** R=Revise | X=Replace | ✅=Done

| File | Action | New Topic | Status |
|------|--------|-----------|--------|
| 15.md | R | LDU Matrix Format — Why FV Needs Sparse Storage | ✅ |
| 16.md | R | LDU Addressing — `owner` and `neighbour` Arrays | ✅ |
| 17.md | R | Cache-Friendly Matrix-Vector Multiply — LDU SpMV | ✅ |
| 18.md | R | Sparse Matrix Assembly — The Face-Loop Pattern | ✅ |
| 19.md | X | Cache Access Patterns — Sequential vs Random | ✅ |
| 20.md | X | Zero-Copy Views with `std::span` | ✅ |
| 21.md | X | Flat Arrays & Offsets — Compact Cell-to-Face Adjacency | ✅ |
| 22.md | X | Modern Hashing — `std::unordered_map` for Boundary Lookups | ✅ |
| 23.md | X | Polymorphic Memory Resources (PMR) — C++17 `<memory_resource>` | ✅ |
| 24.md | X | Mesh Topology Storage — Memory Footprint Analysis | ✅ |
| 25.md | R | Memory Alignment — Preparing for SIMD | ✅ |
| 26.md | R | Matrix Boundary Conditions — LDU Source and Diagonal | ✅ |
| 27.md | X | Mini-Project Day 27 — LDU Matrix Library Integration | ✅ |
| 28.md | X | Mini-Project Day 28 — Gauss-Seidel Solver | ✅ |

---

## Phase 3: Architecture & Build Systems (Days 29–42) ✅ COMPLETE

All 14 files have been created, replacing OpenFOAM internals with Modern CMake/Factory.

| File | New Topic | Status |
|------|-----------|--------|
| 29.md | Modern CMake — Replacing `wmake` | ✅ |
| 30.md | Modern CMake Part 2 — Shared Libraries and Linking | ✅ |
| 31.md | The Modern Factory Pattern — `std::function` Registry | ✅ |
| 32.md | Plugin Self-Registration — Static Initializers | ✅ |
| 33.md | Configuration I/O — JSON with `nlohmann/json` | ✅ |
| 34.md | Dynamic Configuration — Factory + JSON Integration | ✅ |
| 35.md | The Object Registry — Central Field Database | ✅ |
| 36.md | Time & State Control — Solver Loop Architecture | ✅ |
| 37.md | Boundary Condition Interface — Virtual + Factory | ✅ |
| 38.md | Modern Error Handling — Exceptions and `<system_error>` | ✅ |
| 39.md | Dependency Management — CMake `FetchContent` | ✅ |
| 40.md | Logging — `spdlog` for High-Performance Logging | ✅ |
| 41.md | Mini-Project Day 41 — CMake-Driven Factory Build | ✅ |
| 42.md | Mini-Project Day 42 — Integration Test | ✅ |

---

## Phase 4: Performance Optimization (Days 43–56) ✅ COMPLETE

Days 43–46 revised (added deliverables). Days 47–56 created from scratch.

| File | Action | New Topic | Status |
|------|--------|-----------|--------|
| 43.md | R | Profiling Workflows — Setup and Methodology | ✅ |
| 44.md | R | Flame Graphs — Visualizing Call Stacks | ✅ |
| 45.md | R | Auto-Vectorization — Getting SIMD for Free | ✅ |
| 46.md | R | SIMD Intrinsics — Manual AVX2 | ✅ |
| 47.md | **NEW** | OpenMP Basics — Parallelizing Face Loops | ✅ |
| 48.md | **NEW** | C++17 Parallel Algorithms — `std::execution::par_unseq` | ✅ |
| 49.md | **NEW** | False Sharing & Parallel Reductions | ✅ |
| 50.md | **NEW** | Allocation Profiling — Valgrind Massif | ✅ |
| 51.md | **NEW** | Eliminating Temporaries — Zero-Allocation Inner Loop | ✅ |
| 52.md | **NEW** | Mesh Bandwidth Optimization — Reverse Cuthill-McKee | ✅ |
| 53.md | **NEW** | Parallel I/O Concepts — ASCII vs Binary Field Output | ✅ |
| 54.md | **NEW** | MPI Fundamentals — Domain Decomposition Concepts | ✅ |
| 55.md | **NEW** | Mini-Project Day 55 — Integrated Optimization | ✅ |
| 56.md | **NEW** | Mini-Project Day 56 — Benchmark Report | ✅ |

---

## Phase 5: VOF-Ready CFD Component (Days 57–84) ✅ COMPLETE

**All 28 files have been created from scratch.**

| Files | New Topic | Status |
|-------|-----------|--------|
| 57–58.md | Project Architecture — CMake Structure | ✅ |
| 59–60.md | 1D Mesh Implementation | ✅ |
| 61–62.md | Geometric Fields on 1D Mesh | ✅ |
| 63–64.md | Equation Assembly — `fvMatrix` | ✅ |
| 65–66.md | Temporal Operators — `fvm::ddt` | ✅ |
| 67–68.md | Spatial Operators — `fvm::div` and `fvm::laplacian` | ✅ |
| 69–70.md | Linear Solver Integration — PCG and Residual Monitoring | ✅ |
| 71–72.md | The SIMPLE Loop — Pressure-Velocity Coupling | ✅ |
| 73–74.md | Rhie-Chow Interpolation | ✅ |
| 75–76.md | Scalar Transport & Flux Limiters | ✅ |
| 77–78.md | Boundedness Testing — VOF `alpha` in [0, 1] | ✅ |
| 79–80.md | Factory-Driven Source Terms | ✅ |
| 81–82.md | VTK Output — Visualizing in ParaView | ✅ |
| 83–84.md | Final Benchmark and Retrospective | ✅ |

---

## Content Standard (Quick Reference)

Every file must satisfy its **Tier** requirements — see [`.claude/rules/tiered-complexity.md`](.claude/rules/tiered-complexity.md) for full spec.

| Tier | When | Min Lines | Min Code Blocks | Parts |
|------|------|-----------|----------------|-------|
| T1 — Concept Intro | Single new C++ feature | 350 | 3 | 4 |
| T2 — Applied Pattern | Concept applied to CFD, with benchmark | 550 | 4 | 5 |
| T3 — Architecture Day | Multi-concept system design | 750 | 5 | 5 |
| T4 — Mini-Project | Complete implementation with tests | 900 | 6 | 6 |

**All tiers require:**
- [ ] All code blocks balanced + have language tags
- [ ] Ends with `## Deliverable` section
- [ ] No skipped header levels
- [ ] No `// TODO` or `// ... rest` placeholders in code

---

## Commit Strategy

| Milestone | Commit |
|-----------|--------|
| PLAN.md created | `docs: Add PLAN.md curriculum progress tracker` |
| Phase 2 complete | `content: Complete Phase 2 Data Structures & Memory (Days 15-28)` |
| Phase 3 complete | `content: Complete Phase 3 Architecture & Build Systems (Days 29-42)` |
| Phase 4 complete | `content: Complete Phase 4 Performance Optimization (Days 43-56)` |
| Phase 5 complete | `content: Complete Phase 5 VOF-Ready CFD Component (Days 57-84)` |
