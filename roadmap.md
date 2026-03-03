# 84-Session Modern C++ & CFD Architecture Roadmap

## Overview

This roadmap teaches **intermediate-to-advanced C++** and **real-world software engineering** by building a modern CFD framework from scratch using C++17/20 and CMake. Over 84 sessions across 5 phases, you will study OpenFOAM's brilliant mathematical abstractions while replacing its proprietary legacy macros and C++98/03 patterns with clean, standard-compliant modern C++.

**Design philosophy:** Every pattern introduced has a direct modern C++ equivalent. The goal is to build code you could take to any project — not just OpenFOAM.

---

## Summary Table

| Phase | Sessions | Topic | Milestone |
|-------|----------|-------|-----------|
| 1 | 01--14 | Modern C++ Foundation | Type-safe `Field<T>` with C++20 Concepts, expression templates & ranges |
| 2 | 15--28 | Data Structures & Memory | LDU matrix using `std::span` and cache-friendly layout |
| 3 | 29--42 | Architecture & Build Systems | Modern Factory pattern & CMake build system |
| 4 | 43--56 | Performance Optimization | OpenMP, C++17 Parallel Execution, and SIMD profiling |
| 5 | 57--84 | VOF-Ready CFD Component | 1D SIMPLE solver with bounded scalar transport |

---

## Learning Objectives

1. Modern C++ (C++17/20) patterns used in real-world scientific computing
2. CFD mathematical abstractions: fields, mesh topology, LDU matrices, SIMPLE algorithm
3. Software architecture: Factory pattern, CMake, plugin systems, dependency management
4. Performance: profiling, SIMD, OpenMP, parallel execution, zero-allocation loops
5. Building a complete, testable CFD framework with Google Test / Catch2

---

# Phase 1: Modern C++ Foundation (Days 01--14)

**Focus:** C++20 Concepts, smart pointers, expression templates, move semantics, and `std::ranges`.

**Build target:** A type-safe `Field<T>` library with expression templates, move semantics, and unit tests.

---

### Day 01: Templates & Generic Programming — `Field<T>` with `std::vector`

- Write a minimal `Field<T>` template backed by `std::vector<T>` (not raw pointers)
- Compare with OpenFOAM's `Field<Type>` which inherits from `List<Type>` — understand why the modern approach uses composition instead
- Use `using` alias syntax instead of `typedef` throughout
- Implement `size()`, `operator[]`, `.sum()`, `.max()` using `std::reduce` from `<numeric>`
- Note: OpenFOAM's `List<Type>` / `UList<Type>` inheritance and `refCount` are C++98 patterns we will not carry forward

**Deliverable:** A `Field<T>` class backed by `std::vector<T>` that compiles for `double` and a simple `Vec3` struct.

---

### Day 02: C++20 Concepts & Constraints

- Learn what a C++20 Concept is: a named set of requirements on template parameters
- Apply `requires std::is_arithmetic_v<T>` to constrain `Field<T>` to numeric types only
- Compare with OpenFOAM's partial specialization approach — Concepts give cleaner compiler errors
- Write a custom Concept: `template<typename T> concept Numeric = std::is_arithmetic_v<T> || requires(T a, T b) { a + b; }`
- Study why this replaces the heavy SFINAE patterns common in older C++ code

**Deliverable:** A constrained `Field<Numeric T>` that gives a clear compile-time error on `Field<std::string>`.

---

### Day 03: The Mesh-to-Field Relationship — Separating Topology from Values

- Design the `GeometricField` concept: mesh topology (cell count, face connectivity) is separate from numerical values
- Build a minimal `Mesh` struct holding `nCells`, `nFaces`, and cell-center coordinates
- Build `GeometricField<T>` that holds a `Mesh` reference and a `Field<T>` of values
- Understand why OpenFOAM's `GeometricField<Type, PatchField, GeoMesh>` three-parameter design exists — then simplify it
- Enforce the invariant: `field.size() == mesh.nCells()` at construction time

**Deliverable:** A `GeometricField<double>` that stores a scalar pressure field on a 1D mesh.

---

### Day 04: CRTP — Static Polymorphism for Interpolation Schemes

- Study the Curiously Recurring Template Pattern (CRTP): `template<class Derived> class Base`
- Implement a static polymorphism hierarchy for `InterpolationScheme<Derived>` — calling `scheme.interpolate()` with zero virtual dispatch overhead
- Compare CRTP against virtual dispatch: benchmark both, understand when each is appropriate
- Write two concrete schemes: `UpwindScheme` and `LinearScheme`, both inheriting via CRTP
- Understand why OpenFOAM uses CRTP in `surfaceInterpolationScheme<Type, Derived>`

**Deliverable:** A compile-time-resolved `InterpolationScheme` hierarchy with benchmarks showing zero overhead vs virtual dispatch.

---

### Day 05: Policy-Based Design — Swapping Flux Limiters at Compile Time

- Learn Policy-Based Design: inject behavior into a class via template policy parameters
- Build `LimitedField<T, LimiterPolicy>` where `LimiterPolicy` provides a `limit(r)` function
- Implement two limiter policies: `VanLeerLimiter` and `SuperBeeLimiter`
- Show that changing the limiter requires changing one template argument, not runtime branching
- Understand the connection to OpenFOAM's `limitedSurfaceInterpolationScheme`

**Deliverable:** A `LimitedField<double, VanLeerLimiter>` and `LimitedField<double, SuperBeeLimiter>` that swap limiters with zero runtime cost.

---

### Day 06: Modern Ownership — `std::unique_ptr` and `std::shared_ptr`

- Study C++ ownership semantics: exclusive (`unique_ptr`) vs shared (`shared_ptr`) ownership
- Understand why OpenFOAM's `autoPtr<T>` was necessary before C++11 — then see that `std::unique_ptr<T>` replaces it completely
- Learn why `tmp<T>` (OpenFOAM's reference-counted temporary) became obsolete once move semantics arrived in C++11
- Practice: wrap a `Field<double>` in `std::unique_ptr` and pass ownership between functions
- Study `make_unique` and `make_shared` — prefer these over `new`

**Deliverable:** A solver factory function that returns `std::unique_ptr<Field<double>>` — no raw `new`/`delete` in sight.

---

### Day 07: Move Semantics — The End of Expensive Copies

- Understand lvalues, rvalues, and rvalue references (`T&&`)
- Implement `Field(Field&&)` and `operator=(Field&&)` — the move constructor and move assignment
- Benchmark: moving a 1-million-element `Field<double>` vs. copying it (expect near-zero cost for move)
- Understand how this replaces OpenFOAM's `tmp<>` mechanism: `tmp<>` existed to avoid copying; move semantics solve the same problem natively
- Write `Field operator+(Field a, const Field& b)` — note how passing `a` by value + move is optimal

**Deliverable:** A `Field<T>` with correct move semantics. Benchmark showing copy = O(n), move = O(1).

---

### Day 08: Perfect Forwarding — Passing Arguments Without Copies

- Learn `std::forward<T>` and forwarding references (`T&&` in template context)
- Write a factory function `make_field(Args&&... args)` that forwards arguments to `Field<T>` constructors without extra copies
- Understand the difference between `std::move` (unconditional cast) and `std::forward` (conditional cast)
- Study how this pattern appears in solver creation routines in CFD frameworks
- Practice: implement a `FieldFactory::create<T>(Args&&...)` function

**Deliverable:** A `FieldFactory::create<T>()` that constructs any field type with perfect forwarding.

---

### Day 09: Expression Templates — The Temporary Allocation Problem (Part 1)

- Understand the problem: `Field c = a + b + c` creates multiple temporary `Field` objects, each requiring heap allocation
- Trace through what the compiler generates for chained `Field` operations without expression templates
- Measure the allocations with Valgrind/AddressSanitizer: count heap allocations per expression
- Understand the lazy evaluation solution: defer computation until assignment
- Study OpenFOAM's expression template approach as a historical case study

**Deliverable:** A benchmark showing the allocation problem — N temporaries for N operations on a `Field<double>`.

---

### Day 10: Expression Templates — Zero-Allocation Engine (Part 2)

- Build a minimal expression template engine using modern C++ auto return type deduction
- Implement `Add<L, R>`, `Mul<L, R>` expression nodes that store references, not computed values
- Wire up `Field::operator+` to return an `Add<Field, Field>` instead of a new `Field`
- Implement `Field::operator=(const Expr& e)` that evaluates the entire expression in one pass
- Verify zero allocations with Valgrind on `Field c = a + b + d + e`

**Deliverable:** An expression template engine for `Field<T>` with verified zero intermediate allocations.

---

### Day 11: C++20 Ranges — Replacing the `forAll` Macro

- Study OpenFOAM's `#define forAll(list, i)` macro — understand why it exists and why macros are problematic (no scope, no type safety, no debugging)
- Learn `std::views` from C++20 `<ranges>`: `std::views::all`, `std::views::iota`, `std::views::filter`, `std::views::transform`
- Rewrite every `forAll` pattern as a range-based for loop or range algorithm
- Write a mesh face loop using `for (auto faceId : std::views::iota(0, mesh.nFaces()))`
- Benchmark: ranges vs raw loops — understand when the compiler generates identical code

**Deliverable:** A mesh processing function using `std::views` exclusively — zero raw index loops, zero macros.

---

### Day 12: Type Traits & RTTI — Runtime and Compile-Time Type Information

- Learn `<type_traits>`: `std::is_same_v`, `std::is_arithmetic_v`, `std::conditional_t`, `std::enable_if_t`
- Study RTTI: `typeid()`, `dynamic_cast` — understand their runtime overhead and when to use them
- Compare with OpenFOAM's custom `typeInfo` system: see how it replicates RTTI functionality manually
- Use `if constexpr` for compile-time branching that the optimizer can eliminate entirely
- Understand when `typeid` is appropriate vs. when virtual dispatch is better

**Deliverable:** A type-dispatching `print_field_info()` function using `typeid` + `if constexpr` — no custom type registry needed.

---

### Days 13--14: Mini-Project — Build the Complete `Field<T>` Library

- **Day 13:** Integrate all Phase 1 concepts into a single, coherent `Field<T>` library:
  - `Field<Numeric T>` with `std::vector` backing and C++20 Concept constraint
  - Move constructor, move assignment, perfect forwarding factory
  - Expression template engine with zero allocations
  - `std::ranges`-based iteration interface
- **Day 14:** Add tests and benchmarks:
  - Write unit tests using Google Test or Catch2 for all operations
  - Benchmark copy vs. move (expect O(n) vs O(1))
  - Benchmark expression templates vs naive (`a + b + c + d`): verify zero intermediate allocations
  - Write a `CMakeLists.txt` to build the library and test executable

**Deliverable:** A complete, tested `Field<T>` library. Test suite: ≥10 tests, all passing. Benchmark report: move = O(1), expression templates = 0 allocations.

---

# Phase 2: Data Structures & Memory (Days 15--28)

**Focus:** LDU sparse matrix, `std::span`, standard containers, cache optimization, and memory alignment.

**Build target:** An LDU matrix library with Gauss-Seidel iterative solver and performance benchmarks.

---

### Day 15: LDU Matrix Format — Why Unstructured FV Meshes Need Sparse Storage

- Study the Lower-Diagonal-Upper (LDU) sparse matrix format
- Understand why dense matrix storage is prohibitive for CFD (memory and compute scale with O(n²))
- Map the LDU structure to a 1D finite volume mesh: how each face contributes one off-diagonal coefficient
- Learn the three arrays: `lower[]`, `diagonal[]`, `upper[]`
- Count nonzeros for a 1D 5-cell mesh and verify the pattern

**Deliverable:** A hand-drawn (or diagram) of the LDU sparsity pattern for a 5-cell 1D mesh, and verified nonzero counts.

---

### Day 16: LDU Addressing — `owner` and `neighbour` Arrays

- Implement `owner[]` and `neighbour[]` integer arrays for a 1D mesh
- Understand what these arrays encode: for each face, which cell is the "owner" and which is the "neighbour"
- Build a `LDUAddressing` struct that holds these arrays and provides `nFaces()`, `nCells()`
- Verify the addressing is consistent: each internal face has exactly one owner and one neighbour
- Connect back to the LDU matrix: face `f` contributes to `lower[f]`, `upper[f]`, and both `diagonal[owner[f]]` and `diagonal[neighbour[f]]`

**Deliverable:** A `LDUAddressing` class for a 10-cell 1D mesh, verified by printing the owner/neighbour pairs.

---

### Day 17: Cache-Friendly Matrix-Vector Multiply — LDU SpMV

- Implement the LDU sparse matrix-vector multiply: `y = A * x`
- Trace through the face-loop implementation: for each face, scatter contributions to owner and neighbour cells
- Profile cache misses using Valgrind's `cachegrind` tool on a large (10,000-cell) 1D mesh
- Understand why the access pattern for `x[owner[f]]` and `x[neighbour[f]]` causes cache thrashing on unstructured meshes
- Compare LDU SpMV performance against a CSR-format implementation

**Deliverable:** An LDU SpMV implementation with cachegrind profiling output. Cache miss report attached.

---

### Day 18: Sparse Matrix Assembly — The Face-Loop Pattern

- Implement the face-loop pattern to assemble coefficients for a 1D Laplacian equation: `∇²φ = 0`
- For each internal face: compute the face diffusivity, add to `lower[f]` and `upper[f]`, subtract from `diagonal[owner[f]]` and `diagonal[neighbour[f]]`
- Handle boundary conditions: Dirichlet (fixed value) modifies `source[]` and `diagonal[]`; Neumann (zero gradient) adds nothing
- Assemble a complete 10-cell 1D Laplacian matrix with Dirichlet BCs at both ends
- Verify by printing the assembled matrix coefficients

**Deliverable:** A fully assembled LDU matrix for the 1D Laplacian `φ_xx = 0` with Dirichlet BCs. Verified against hand calculation.

---

### Day 19: Cache Access Patterns — Sequential vs Random Face Numbering

- Benchmark matrix assembly and SpMV with sequential vs random face numbering on a 1D mesh
- Understand how face renumbering changes the memory access pattern for `owner[]` and `neighbour[]`
- Use `perf stat` to count L1/L2 cache misses for each numbering scheme
- Learn what the Reverse Cuthill-McKee algorithm does conceptually (implementation in Phase 4)
- Quantify the performance difference: sequential should be 2-5× faster on large meshes

**Deliverable:** Benchmark comparing sequential vs random face numbering. Cache miss counts from `perf stat`.

---

### Day 20: Zero-Copy Views with `std::span`

- Study OpenFOAM's `UList<T>`: a non-owning view into memory owned by `List<T>` — avoids O(n) copying
- Learn C++20 `std::span<T>`: does exactly what `UList<T>` does, but is standard, memory-safe, and natively integrates with `<algorithm>`
- Replace all `UList<T>` / `List<T>` concepts with `std::vector<T>` (owning) + `std::span<T>` (non-owning view)
- Write a function that takes `std::span<const double>` and computes the sum — verify it works on subsets of a `std::vector`
- Practice zero-copy slicing: pass boundary face data to a BC function without copying

**Deliverable:** A mesh processing function that passes field subsets as `std::span<const double>` — zero copies verified with address sanitizer.

---

### Day 21: Flat Arrays & Offsets — Compact Cell-to-Face Adjacency

- Study OpenFOAM's `CompactListList<T>`: a jagged array stored as a flat `T[]` + integer offsets
- Replicate this with two `std::vector<int>`: `data[]` for face IDs, `offsets[]` for cell-start positions
- Build `cell_faces(cellId)` that returns a `std::span<int>` into the flat data — zero copies
- Verify the compact layout uses less memory than `std::vector<std::vector<int>>` (one allocation vs. many)
- Benchmark access time: compact layout should show better cache behavior

**Deliverable:** A `CellFaceAdjacency` class storing connectivity as flat arrays. Memory and access-time comparison vs nested `vector<vector>`.

---

### Day 22: Modern Hashing — `std::unordered_map` for Boundary Lookups

- Study how CFD codes map boundary patch names to boundary condition objects
- Benchmark `std::unordered_map<std::string, BC>` against `std::map<std::string, BC>` for lookup performance
- Understand hash map internals: bucket arrays, load factors, rehashing
- Implement a patch registry: `PatchRegistry` that maps patch name to boundary condition type
- Learn when to use `std::unordered_map` (frequent lookup, don't care about order) vs `std::map` (ordered iteration needed)

**Deliverable:** A `PatchRegistry` class using `std::unordered_map`. Benchmark: O(1) patch lookup vs O(log n) for `std::map`.

---

### Day 23: Polymorphic Memory Resources (PMR) — C++17 `<memory_resource>`

- Learn C++17 `std::pmr::polymorphic_allocator` and `std::pmr::monotonic_buffer_resource`
- Understand the use case: temporary matrix objects in the solver loop that are created and destroyed every iteration
- Use a monotonic buffer resource (stack-allocated arena) to rapidly allocate and deallocate temporary matrices
- Measure allocation overhead: `std::pmr::vector<double>` with monotonic buffer vs standard `std::vector<double>`
- Understand how this relates to OpenFOAM's internal memory pool strategies

**Deliverable:** A solver inner loop that uses PMR to allocate temporaries. Allocation overhead benchmark: PMR vs standard allocator.

---

### Day 24: Mesh Topology Storage — Memory Footprint Analysis

- Calculate the memory footprint of storing face connectivity as: (a) `std::vector<std::vector<int>>`, (b) flat compact arrays, (c) CSR-style format
- Implement all three representations for a 100-cell 1D mesh and measure actual memory with `Valgrind/Massif`
- Understand why production CFD codes use compact formats for meshes with millions of cells
- Profile the three representations on read access (iterate all faces of all cells)
- Summarize: which format minimizes memory? Which minimizes access time?

**Deliverable:** Memory footprint report for three mesh topology representations. Access-time benchmark.

---

### Day 25: Memory Alignment — Preparing for SIMD

- Learn memory alignment: why AVX2 SIMD requires 32-byte aligned data
- Use `alignas(32)` to align `Field<T>` arrays for AVX vectorization
- Alternatively, use `std::aligned_alloc` for heap-allocated aligned buffers
- Write a simple `Field<double>` dot product using aligned memory and verify the compiler emits SIMD instructions (check with `-fopt-info-vec` or `objdump`)
- Understand the difference between aligned and unaligned load intrinsics (`_mm256_load_pd` vs `_mm256_loadu_pd`)

**Deliverable:** A `Field<double>` with `alignas(32)` backing. Compiler output showing SIMD instructions generated.

---

### Day 26: Matrix Boundary Conditions — LDU Source and Diagonal Modification

- Implement the assembly of boundary conditions into the LDU matrix
- Dirichlet BC: modify `source[boundaryCell]` and `diagonal[boundaryCell]` — the face coefficient is removed from the off-diagonal and moved to the diagonal (implicit)
- Neumann BC (zero gradient): the face flux is zero — no modification needed
- Robin/mixed BC: understand the linear combination of Dirichlet and Neumann
- Assemble and verify a 1D heat equation with mixed BCs: left wall Dirichlet (T=1), right wall Neumann (dT/dx=0)

**Deliverable:** An LDU matrix assembly supporting Dirichlet and Neumann BCs. Verified solution for the 1D heat equation.

---

### Days 27--28: Mini-Project — LDU Matrix Library with Gauss-Seidel Solver

- **Day 27:** Integrate Phase 2 into a complete LDU matrix library:
  - `LDUAddressing` with `owner[]`, `neighbour[]`
  - `LDUMatrix` with assembly from face loops and BC application
  - `std::span`-based field views for zero-copy access
  - PMR allocator support for temporaries
- **Day 28:** Implement a Gauss-Seidel iterative solver and benchmark:
  - Implement the Gauss-Seidel sweep: iterate over cells, update each using the current residual
  - Monitor convergence: `||r|| < tolerance`
  - Benchmark sparse LDU SpMV vs dense matrix-vector multiply for the same system
  - Add a `CMakeLists.txt` and Google Test unit tests

**Deliverable:** A complete LDU matrix library with Gauss-Seidel solver. Tests: ≥8 tests covering assembly and solver. Benchmark: sparse vs dense.

---

# Phase 3: Architecture & Build Systems (Days 29--42)

**Focus:** Modern CMake, `std::function` Factory pattern, plugin architecture, and standard I/O formats.

**Build target:** A CMake-driven Factory that loads a JSON config and instantiates a solver at runtime.

---

### Day 29: Modern CMake — Replacing `wmake`

- Understand why `wmake` (OpenFOAM's build system) is non-standard and non-portable
- Write a `CMakeLists.txt` using `target_sources` and `target_include_directories`
- Learn the Modern CMake idiom: properties are attached to targets, not set globally
- Build the Phase 1 `Field<T>` library as a CMake target: `add_library(FieldLib STATIC ...)`
- Run `cmake --build` and verify the library compiles

**Deliverable:** A `CMakeLists.txt` that builds the Phase 1 `Field<T>` library. No raw compiler flags, no `wmake`.

---

### Day 30: Modern CMake Part 2 — Shared Libraries and Linking

- Understand `target_link_libraries` with `PUBLIC` vs `PRIVATE` vs `INTERFACE` visibility
- Build the CFD core as a shared library (`.so`/`.dll`): `add_library(CFDCore SHARED ...)`
- Build a separate executable that links against `CFDCore`: `target_link_libraries(solver PRIVATE CFDCore)`
- Understand symbol visibility: `__attribute__((visibility("default")))` and `CMAKE_CXX_VISIBILITY_PRESET`
- Learn `FetchContent` to pull in external dependencies: fetch Google Test from GitHub

**Deliverable:** A `CMakeLists.txt` with a shared `CFDCore` library, a test executable, and Google Test fetched automatically.

---

### Day 31: The Modern Factory Pattern — `std::function` Registry

- Study OpenFOAM's Run-Time Selection (RTS) macros: `declareRunTimeSelectionTable`, `addToRunTimeSelectionTable` — understand what problem they solve
- Recognize that RTS macros are a workaround for C++98 limitations: no lambdas, no `std::function`
- Build a modern Factory using `std::unordered_map<std::string, std::function<std::unique_ptr<Solver>()>>`
- Register solvers: `registry["GaussSeidel"] = []() { return std::make_unique<GaussSeidelSolver>(); }`
- Instantiate by name: `auto solver = registry.at("GaussSeidel")()`

**Deliverable:** A `SolverFactory` with `register()` and `create(name)` methods. No macros.

---

### Day 32: Plugin Self-Registration — Static Initializers

- Learn how static initialization works: objects at file scope are initialized before `main()`
- Use a static initializer to self-register a solver into the Factory without touching the Factory source code
- Implement a `Registrar<T>` helper class whose constructor calls `SolverFactory::register<T>(name)`
- Place `static Registrar<GaussSeidelSolver> reg("GaussSeidel");` in the solver's `.cpp` file
- Understand the SIOF (Static Initialization Order Fiasco) risk and how C++11 "magic statics" solve it

**Deliverable:** A `GaussSeidelSolver` that self-registers using a static initializer. Adding a new solver requires no changes to the Factory core.

---

### Day 33: Configuration I/O — JSON Instead of OpenFOAM Dictionaries

- Study OpenFOAM's custom dictionary format (`FoamFile { ... }`) — understand its capabilities and why it requires a custom parser
- Integrate `nlohmann/json` (via CMake `FetchContent`) as a standard, well-tested alternative
- Write a solver configuration JSON file: `{ "solver": "GaussSeidel", "tolerance": 1e-6, "maxIter": 1000 }`
- Parse the JSON at runtime and extract configuration values with type safety
- Handle parse errors gracefully with `std::runtime_error`

**Deliverable:** A `SolverConfig` class that reads from JSON. Invalid JSON → clear error message.

---

### Day 34: Dynamic Configuration — Factory + JSON Integration

- Combine Day 31 (Factory) and Day 33 (JSON) into a complete configuration-driven solver creation system
- Read the solver name from JSON → look up in Factory registry → instantiate and configure the solver
- Make solver parameters (tolerance, max iterations) configurable from JSON
- Write two JSON configs (one for Gauss-Seidel, one for Jacobi) and verify both instantiate the correct solver
- Add error handling: unknown solver name → `std::runtime_error` with list of registered names

**Deliverable:** A main executable that reads `config.json`, instantiates the requested solver via Factory, and runs it on a 1D Laplacian.

---

### Day 35: The Object Registry — Central Field Database

- Study OpenFOAM's `objectRegistry`: a central store of all active fields, enabling automatic I/O
- Build a `Database` class holding `std::unordered_map<std::string, std::shared_ptr<GeometricField<double>>>`
- Register fields at creation: `db.add("pressure", std::make_shared<GeometricField<double>>(mesh))`
- Look up fields by name: `auto& p = db.get<double>("pressure")`
- Understand why shared ownership (`std::shared_ptr`) is appropriate here: the database and the solver both hold references

**Deliverable:** A `Database` class that stores and retrieves named `GeometricField` objects by type and name.

---

### Day 36: Time & State Control — The Solver Loop Architecture

- Design the `Time` class to control the main solver time loop
- Implement: `Time::loop()` that advances `t += dt`, checks `t < endTime`, and triggers output at `writeInterval`
- Implement a simple CFL condition check: `dt = CFL * minCellSize / maxVelocity`
- Understand how the `Time` class integrates with the `Database` to trigger field writes
- Study how this maps to OpenFOAM's `runTime` object

**Deliverable:** A `Time` class with configurable `dt`, `endTime`, `writeInterval`, and CFL control. Demonstrated in a simple time loop.

---

### Day 37: Boundary Condition Interface — Virtual + Factory Pattern

- Design a `BoundaryCondition` abstract base class with pure virtual `updateCoeffs(LDUMatrix&, Field<double>&)` method
- Implement `FixedValueBC` (Dirichlet) and `ZeroGradientBC` (Neumann) as concrete classes
- Register both BCs in the `SolverFactory` — look up by name from the JSON config
- Apply the Strategy pattern: the solver calls `bc.updateCoeffs(matrix, field)` without knowing which BC type it is
- Test: swap between BCs via JSON without recompiling

**Deliverable:** A `BoundaryCondition` hierarchy registered in the Factory. Solver uses BCs polymorphically from JSON config.

---

### Day 38: Modern Error Handling — Exceptions and `<system_error>`

- Learn when to use exceptions: unexpected, unrecoverable states (not normal control flow)
- Use `std::runtime_error`, `std::invalid_argument`, `std::out_of_range` from `<stdexcept>`
- Use `std::error_code` and `std::system_error` from `<system_error>` for OS-level errors (file I/O, etc.)
- Study the "exception safety" levels: basic, strong, nothrow — understand which your `Field<T>` provides
- Replace all `FatalError << "..." << exit(FatalError)` patterns (OpenFOAM style) with proper C++ exceptions

**Deliverable:** The entire framework throws typed C++ exceptions. No `exit()` calls. All exceptions caught and reported cleanly in `main()`.

---

### Day 39: Dependency Management — CMake `FetchContent`

- Learn CMake `FetchContent` for pulling in external libraries at configure time
- Fetch and integrate: `nlohmann/json`, `spdlog` (logging), and `Catch2` (testing) — all via `FetchContent`
- Understand the difference from `find_package`: `FetchContent` downloads the source, `find_package` uses installed libraries
- Write a `dependencies.cmake` file that centralizes all `FetchContent` declarations
- Verify the build works from a clean directory with no pre-installed libraries

**Deliverable:** A `CMakeLists.txt` with `FetchContent` for all external dependencies. One-command build from clean directory.

---

### Day 40: Logging — `spdlog` for High-Performance Logging

- Integrate `spdlog` (fetched via CMake `FetchContent`) as the framework's logging system
- Use `spdlog::info()`, `spdlog::warn()`, `spdlog::error()` — no raw `printf` or `std::cout` in library code
- Configure log levels from the JSON config: debug mode logs every iteration, production mode logs only convergence
- Use `spdlog`'s async logger for the inner solver loop — logging should not stall computation
- Compare `spdlog` performance against raw `printf`: measure throughput in the solver loop

**Deliverable:** A solver that logs convergence history via `spdlog`. Log level configurable from JSON.

---

### Days 41--42: Mini-Project — CMake-Driven Factory Executable

- **Day 41:** Build the complete CMake-driven Factory:
  - `CMakeLists.txt` with shared `CFDCore` library
  - All dependencies fetched automatically
  - `SolverFactory` with JSON configuration
  - `Database` for field management
  - `BoundaryCondition` hierarchy
- **Day 42:** Integration test:
  - Write a `config.json` that selects `GaussSeidel`, sets `tolerance: 1e-8`, configures BCs
  - Run the executable: reads JSON → instantiates solver → solves 1D Laplacian → logs convergence
  - Add `Catch2` tests covering Factory registration, JSON parsing, BC application
  - Generate a build from a clean directory to verify all `FetchContent` dependencies resolve

**Deliverable:** A self-contained CMake project. One-command build and test. Executable reads JSON, runs solver, passes all tests.

---

# Phase 4: Performance Optimization (Days 43--56)

**Focus:** Profiling, auto-vectorization, OpenMP, C++17 parallel execution, and MPI fundamentals.

**Build target:** An optimized `Field<T>` and LDU solver with a comprehensive benchmark report.

---

### Day 43: Profiling Workflows — Setup and Methodology

- Compile with `-g -O3 -fno-omit-frame-pointer` for profiling with debug symbols and optimization
- Use `perf record` + `perf report` on Linux (or `Instruments` on macOS) to profile the solver loop
- Identify the top 3 hotspots: matrix-vector multiply, field arithmetic, and boundary condition assembly
- Understand the profiling methodology: measure before optimizing, focus on hotspots only
- Generate a baseline performance profile for the Phase 2 LDU solver

**Deliverable:** A profiling report identifying the top 3 hotspots in the LDU solver. Baseline timing for each Phase 2 component.

---

### Day 44: Flame Graphs — Visualizing Call Stacks

- Generate a flame graph for the LDU matrix assembly to visually identify the slowest functions
- Use `perf script` + `flamegraph.pl` (Brendan Gregg's tool) on Linux, or `Instruments` on macOS
- Read the flame graph: wide blocks = more CPU time, tall stacks = deep call chains
- Identify: is the bottleneck in `SpMV`? In field arithmetic? In memory allocation?
- Annotate the flame graph with optimization targets for Days 45-52

**Deliverable:** A flame graph for the LDU solver. Annotated with optimization opportunities.

---

### Day 45: Auto-Vectorization — Getting SIMD for Free

- Compile with `-ftree-vectorize -fopt-info-vec -fopt-info-vec-missed` to see which loops vectorize
- Read the compiler vectorization report: which `Field<T>` loops generate SIMD? Which fail and why?
- Common vectorization blockers: pointer aliasing (fix with `__restrict__`), non-unit stride access, loop-carried dependencies
- Apply `__restrict__` to `Field<T>` operator loops and verify the vectorization report improves
- Measure speedup: auto-vectorized vs scalar baseline (expect 2-4× on float/double)

**Deliverable:** Vectorization report for all `Field<T>` operations. Speedup measurement: auto-vectorized vs scalar.

---

### Day 46: SIMD Intrinsics — Manual AVX2

- Write one key inner loop manually using AVX2 intrinsics (`_mm256_add_pd`, `_mm256_mul_pd`, `_mm256_fmadd_pd`)
- Target: the `Field<T>` dot product or `a = b + alpha * c` (axpy) operation
- Compare performance: manual AVX2 vs compiler auto-vectorized (expect near-identical on modern compilers)
- Understand when manual intrinsics are justified: highly specialized patterns the compiler cannot detect
- Learn aligned vs unaligned loads: `_mm256_load_pd` (requires 32-byte alignment) vs `_mm256_loadu_pd`

**Deliverable:** A manual AVX2 implementation of `Field<T>` axpy. Benchmark: manual SIMD vs auto-vectorized compiler output.

---

### Day 47: OpenMP Basics — Parallelizing Face Loops

- Apply `#pragma omp parallel for` to the LDU matrix-vector multiply face loop
- Identify the data race: multiple threads writing to `y[owner[f]]` and `y[neighbour[f]]` simultaneously
- Fix with `#pragma omp atomic` or by rewriting as a two-pass (gather then scatter) algorithm
- Benchmark on 2, 4, 8 threads: find the minimum mesh size where threading helps (overhead vs speedup threshold)
- Understand the parallel scaling behavior: Amdahl's law for the sequential portions (BC assembly, etc.)

**Deliverable:** A thread-safe OpenMP LDU SpMV. Scaling benchmark: 1 to 8 threads. Threshold mesh size for positive speedup.

---

### Day 48: C++17 Parallel Algorithms — `std::execution::par_unseq`

- Use `std::transform(std::execution::par_unseq, ...)` on `Field<T>` arithmetic operations
- Compare against the OpenMP implementation: syntax differences and performance parity
- Understand when `par_unseq` (unsequenced parallel execution) is safe vs when it can cause data races
- Apply to: `Field<T>::operator+`, `std::inner_product` (dot product) with parallel execution
- Identify the backend: on GCC/Clang with TBB or OpenMP backend, `par_unseq` compiles to thread-pool execution

**Deliverable:** `Field<T>` arithmetic using `std::execution::par_unseq`. Performance comparison: C++17 parallel vs OpenMP.

---

### Day 49: False Sharing & Parallel Reductions

- Implement parallel maximum and minimum functions for CFL condition calculation using OpenMP reduction
- Understand false sharing: two threads write to data in the same 64-byte cache line, causing unnecessary cache invalidation
- Detect false sharing with `perf c2c` or `Intel VTune` cache-to-cache analysis
- Fix: pad thread-local accumulators to 64-byte cache line size (`alignas(64)`)
- Benchmark: false-sharing version vs padded version on a 16-thread machine

**Deliverable:** A parallel CFL calculation with no false sharing. Benchmark showing the performance difference.

---

### Day 50: Allocation Profiling — Valgrind Massif

- Run Valgrind Massif on the full solver loop to track heap allocations over time
- Identify: which allocations happen inside the main time loop? (These are the ones to eliminate)
- Visualize with `ms_print` or `massif-visualizer`: see peak heap usage and allocation call stacks
- Target for elimination: any `Field<T>` temporary allocation inside `for (t = 0; t < endTime; ...)` loop
- Build a list of allocations to eliminate in Days 51-52

**Deliverable:** A Massif heap profile for the solver loop. List of in-loop allocations to eliminate.

---

### Day 51: Eliminating Temporaries — Zero-Allocation Inner Loop

- Apply the expression template engine (Phase 1) to eliminate intermediate `Field<T>` allocations in the solver right-hand-side assembly
- Use PMR (Phase 2, Day 23) with a monotonic buffer for any unavoidable temporaries in the inner loop
- Pre-allocate all working buffers outside the time loop: `residual`, `correction`, `pFace` — reuse via `resize()`-in-place
- Verify with Valgrind Massif: the solver inner loop should show **zero** heap allocations after optimization
- Measure the speedup: allocating vs zero-allocation inner loop (expect 10-30% on memory-bound problems)

**Deliverable:** A solver inner loop with **zero** heap allocations. Massif profile confirming zero in-loop allocations. Speedup measurement.

---

### Day 52: Mesh Bandwidth Optimization — Reverse Cuthill-McKee

- Implement the Reverse Cuthill-McKee (RCM) algorithm to renumber mesh cells for better memory locality
- Understand why RCM helps: cells that are geometrically adjacent should be numerically adjacent, improving cache hit rates for SpMV
- Apply RCM to the 1D mesh from Phase 2 and measure the change in matrix bandwidth
- Benchmark LDU SpMV before and after RCM reordering (expect 10-20% improvement on large meshes)
- Compare with the cachegrind results from Day 19 — see how reordering reduces cache misses

**Deliverable:** An RCM implementation for 1D mesh. SpMV benchmark before/after reordering. Cache miss comparison.

---

### Day 53: Parallel I/O Concepts — ASCII vs Binary Field Output

- Benchmark writing a 1-million-element `Field<double>` to disk: ASCII text vs raw binary (`std::ofstream::binary`)
- Understand why ASCII is standard in OpenFOAM (human-readable) but slow for large fields
- Implement binary output: write the array size header then the raw `double[]` data
- Implement binary input: read the header, `resize()` the `Field<T>`, then read the raw data
- Measure file size and write/read throughput: binary should be 5-10× faster and 3× smaller

**Deliverable:** Binary `Field<T>` serialization. Benchmark: ASCII vs binary throughput and file size.

---

### Day 54: MPI Fundamentals — Domain Decomposition Concepts

- Write a basic MPI program: `MPI_Init`, `MPI_Comm_rank`, `MPI_Comm_size`, `MPI_Finalize`
- Implement `MPI_Send` and `MPI_Recv` to exchange field values between two ranks
- Understand how processor boundaries in domain-decomposed CFD work: they are "coupled" boundary conditions exchanging ghost cell values
- Implement a 1D domain decomposition: split a 100-cell mesh into two 50-cell subdomains with MPI halo exchange
- Understand `MPI_Allreduce` for global reductions (e.g., computing the global maximum residual)

**Deliverable:** A 2-rank MPI program that solves a 1D Laplacian with domain decomposition. Global residual computed via `MPI_Allreduce`.

---

### Days 55--56: Mini-Project — Optimized `Field<T>` Benchmark Report

- **Day 55:** Integrate all Phase 4 optimizations:
  - Auto-vectorized `Field<T>` with `__restrict__`
  - OpenMP-parallel SpMV with no data races
  - Zero-allocation solver inner loop (expression templates + PMR)
  - RCM mesh reordering
- **Day 56:** Generate a comprehensive benchmark report:
  - Baseline (Phase 2 solver) vs fully optimized (Phase 4) throughput
  - Scaling: 1 to 8 OpenMP threads
  - Memory: baseline allocations vs zero-allocation inner loop
  - Vectorization: scalar vs auto-vectorized vs manual SIMD
  - Write a 1-page performance summary: what worked, what the bottleneck is at scale

**Deliverable:** Benchmark report comparing Phase 2 baseline vs Phase 4 optimized. Speedup table across all optimization dimensions.

---

# Phase 5: VOF-Ready CFD Component (Days 57--84)

**Focus:** Building a 1D SIMPLE solver with bounded scalar transport as the prerequisite for multiphase flow.

**Build target:** A complete 1D CFD solver with pressure-velocity coupling, scalar transport, flux limiters, and VTK output.

---

### Days 57--58: Project Architecture — CMake Structure

- Design the CMake project structure for the full 1D CFD solver:
  - `Mesh`: points, faces, cell volumes, face areas, boundary patches
  - `Field`: `Field<T>` with expression templates and move semantics
  - `Matrix`: `LDUMatrix` with Gauss-Seidel solver
  - `Operators`: `fvm::laplacian`, `fvm::div`, `fvm::ddt`
  - `SIMPLE`: momentum predictor, pressure correction, velocity correction
- Write stub `CMakeLists.txt` for each library target
- Define the interfaces: `Operators` depends on `Matrix` and `Field`; `SIMPLE` depends on `Operators`

**Deliverable:** A complete CMake project skeleton. All targets defined, interfaces documented, build succeeds (with empty stubs).

---

### Days 59--60: 1D Mesh Implementation

- Generate 1D mesh: `nCells` cells from `x=0` to `x=L`
- Compute cell volumes: `V[i] = dx` (uniform spacing)
- Compute face areas: `A[f] = 1` (1D, unit cross-section)
- Compute cell-center coordinates: `xC[i] = (i + 0.5) * dx`
- Compute face-center coordinates: `xF[f] = f * dx`
- Add inlet and outlet boundary patches: `BoundaryPatch` with face IDs and patch type

**Deliverable:** A `Mesh1D` class. Print all cell volumes, face areas, and centers for a 5-cell mesh — verified against hand calculation.

---

### Days 61--62: Geometric Fields on the 1D Mesh

- Combine `Mesh1D` and `Field<T>` into `GeometricField<T>` for the 1D mesh
- Store cell-centered values (`volScalarField` equivalent): pressure `p`, velocity `U`
- Store face-centered values (`surfaceScalarField` equivalent): face flux `phi`
- Implement boundary condition querying: `field.boundaryValue(patchId)` returns the BC object for that patch
- Enforce the size invariant: `GeometricField<T>(mesh)` always has `size() == mesh.nCells()`

**Deliverable:** `volScalarField` and `surfaceScalarField` equivalents on the 1D mesh. BCs accessible by patch name.

---

### Days 63--64: Equation Assembly — `fvMatrix`

- Implement the `fvMatrix` equation class that wraps the `LDUMatrix` and source vector
- `fvMatrix` represents a linear system: `A * phi = b`
- Implement under-relaxation: `A_new[i][i] *= 1/alpha; b[i] += (1-alpha)/alpha * A[i][i] * phi_old[i]`
- Implement residual computation: `||A * phi - b|| / ||b||`
- Build: `operator==(fvMatrix, GeometricField<T>)` to assemble and solve an equation system

**Deliverable:** An `fvMatrix` class with assembly, under-relaxation, and residual computation. Tested on a 1D Laplacian.

---

### Days 65--66: Temporal Operators — `fvm::ddt`

- Implement `fvm::ddt(phi)`: Euler implicit time derivative `(phi - phi_old) / dt`
- Returns an `fvMatrix` with `diagonal[i] = V[i] / dt`, `source[i] = V[i] / dt * phi_old[i]`
- Understand why implicit time stepping (treating new-time values implicitly) is unconditionally stable for diffusion
- Test: solve `dphi/dt = 0` (steady state) and verify `phi` converges to the initial value
- Test: solve `dphi/dt = 1` and verify `phi` increases linearly with time

**Deliverable:** `fvm::ddt` operator. Two test cases verifying correct temporal behavior.

---

### Days 67--68: Spatial Operators — `fvm::div` and `fvm::laplacian`

- Implement `fvm::laplacian(D, phi)`: `∇·(D∇φ)` using central differencing across each face
- For each face: `flux = D * (phi[neighbour] - phi[owner]) / distance`
- Implement `fvm::div(phi, U)`: `∇·(φU)` using upwind differencing based on the sign of face flux `phi`
- Upwind: if `phi[face] > 0`, use `owner` cell value; if `phi[face] < 0`, use `neighbour` cell value
- Test: solve 1D steady advection-diffusion with known analytical solution, verify second-order accuracy for laplacian

**Deliverable:** `fvm::laplacian` and `fvm::div` operators. Convergence test: verify laplacian achieves second-order spatial accuracy.

---

### Days 69--70: Linear Solver Integration — PCG and Residual Monitoring

- Integrate the Preconditioned Conjugate Gradient (PCG) solver for symmetric pressure systems
- Integrate Gauss-Seidel for asymmetric velocity systems
- Add residual monitoring: print `[solver] iteration: N, residual: X.XXe-Y` every 100 iterations
- Configure solver selection from JSON: `"pressureSolver": "PCG"`, `"velocitySolver": "GaussSeidel"`
- Add convergence criteria: `residual < tolerance` (typical: 1e-6 for pressure, 1e-4 for velocity)

**Deliverable:** PCG and Gauss-Seidel solvers integrated with residual monitoring. Solver selection from JSON config.

---

### Days 71--72: The SIMPLE Loop — Pressure-Velocity Coupling

- Implement the SIMPLE (Semi-Implicit Method for Pressure-Linked Equations) algorithm for 1D channel flow:
  1. **Momentum predictor:** Solve `A * U* = b_U` using current pressure gradient
  2. **Pressure correction:** Solve `∇·(1/A * ∇p') = ∇·U*`
  3. **Velocity correction:** `U = U* - (1/A) * ∇p'`
  4. **Flux correction:** Update face fluxes `phi` from corrected `U`
- Implement under-relaxation: `alpha_U = 0.7`, `alpha_p = 0.3` (standard SIMPLE values)
- Test: 1D channel flow with `U_inlet = 1`, `p_outlet = 0` — verify `U` converges to 1.0 everywhere (incompressible 1D)

**Deliverable:** A working SIMPLE loop for 1D channel flow. Convergence history showing residuals dropping below tolerance.

---

### Days 73--74: Rhie-Chow Interpolation — Preventing Pressure Checkerboarding

- Understand the checkerboarding problem: collocated pressure-velocity grids allow decoupled pressure oscillations
- Implement Rhie-Chow face-flux interpolation: the face flux uses pressure gradient information to suppress decoupling
- `phi[f] = U_f·n - (1/A_f) * (∇p_f - (1/2)(∇p_owner + ∇p_neighbour))`
- Test: a 1D mesh with an initial checkerboard pressure field — verify Rhie-Chow suppresses the oscillation while pure interpolation does not
- Integrate Rhie-Chow into the SIMPLE flux correction step

**Deliverable:** Rhie-Chow face flux interpolation. Demonstration that checkerboard pressure is suppressed.

---

### Days 75--76: Scalar Transport & Flux Limiters — The Multiphase Prerequisite

- Implement the scalar transport equation for an indicator function `alpha` (Volume of Fluid indicator):
  `∂α/∂t + ∇·(U α) = 0`
- Add flux limiter support to `fvm::div`: instead of pure upwind, use the limiter to reduce numerical diffusion
- Implement SuperBee and vanLeer limiters as limiter policies (connecting back to Phase 1, Day 05)
- The limiter selects the scheme based on the ratio `r = (alpha_D - alpha_U) / (alpha_C - alpha_U)`
- Test: transport a step function in 1D — compare pure upwind (diffusive) vs limited scheme (sharper)

**Deliverable:** `fvm::div` with flux limiter support. Visual comparison: upwind vs SuperBee vs vanLeer on step transport.

---

### Days 77--78: Boundedness Testing — Keeping `alpha` in [0, 1]

- Solve the VOF advection equation:
  `∂α/∂t + ∇·(U α) = 0`
- Use a prescribed velocity field `U = 1` and initial step function `alpha = 1` for x < 0.5, `alpha = 0` elsewhere
- Verify that vanLeer and SuperBee limiters keep `alpha` strictly bounded between **0** and **1** at all times
- Measure: with pure upwind, `alpha` smears over many cells; with limiters, the interface stays sharp
- Quantify: count cells where `alpha < 0` or `alpha > 1` — should be zero with correct limiter implementation

**Deliverable:** Boundedness test for the VOF advection equation. Tabulated results: cells out of bounds for each scheme.

---

### Days 79--80: Factory-Driven Source Terms

- Implement a volumetric source term interface: `SourceTerm::addToMatrix(fvMatrix&, GeometricField<double>&)`
- Register two source terms in the Factory: `GravitySource` and `HeatSource`
- Load source term type and parameters from JSON: `"sourceTerms": [{ "type": "GravitySource", "g": 9.81 }]`
- Test: add a constant body force to the momentum equation and verify the velocity profile shifts accordingly
- Verify: adding zero source term produces identical results to the no-source case

**Deliverable:** A `SourceTerm` Factory. Gravity source term loaded from JSON. Momentum equation test with non-zero body force.

---

### Days 81--82: VTK Output — Visualizing Results in ParaView

- Write a lightweight VTK legacy format exporter for the 1D mesh and fields
- VTK ASCII format for 1D: write `POINTS`, `CELLS`, `CELL_TYPES`, and `CELL_DATA` sections
- Export `p`, `U`, and `alpha` fields to `.vtk` files at each write time
- Open the VTK file in ParaView and verify the velocity and pressure profiles match the analytical solution
- Trigger writes from the `Time` class at `writeInterval` — no extra code in the solver loop

**Deliverable:** A VTK exporter for the 1D solver. ParaView screenshot showing the velocity and `alpha` profiles.

---

### Days 83--84: Final Benchmark and Retrospective

- **Day 83:** Run the complete 1D solver:
  - SIMPLE loop for channel flow: compare against analytical solution `U = 1.0` everywhere
  - Bounded scalar transport: compare against analytical advection of a step function
  - Measure: solver iterations to convergence, wall-clock time, residual history
- **Day 84:** Write a retrospective report:
  - What Modern C++ patterns were most valuable? (Move semantics, Concepts, expression templates, PMR)
  - Where did OpenFOAM's architecture prove superior? Where did the modern approach win?
  - What would Phase 6 add? (3D mesh, parallel domain decomposition, real multiphase PLIC)
  - Architecture diagram of the complete framework: how all 5 phases connect

**Deliverable:** A benchmark comparing the 1D solver against analytical solutions. A written retrospective (≥500 words). A complete architecture diagram.

---

## Quick Reference

### Tools Used Throughout

| Tool | Phase | Purpose |
|------|-------|---------|
| `g++ -std=c++20 -O3` | 1--5 | Compilation standard |
| `CMake ≥ 3.20` | 3--5 | Build system |
| Google Test / Catch2 | 1--5 | Unit testing |
| `nlohmann/json` | 3--5 | Configuration I/O |
| `spdlog` | 3--5 | Logging |
| `perf` + flamegraphs | 4 | CPU profiling |
| `cachegrind` | 2, 4 | Cache profiling |
| `Valgrind Massif` | 4 | Memory profiling |
| `ParaView` | 5 | VTK visualization |
| MPI | 4 | Parallel computing |

### Key C++ Standards Reference

| Feature | Standard | Day First Used |
|---------|----------|----------------|
| `using` aliases | C++11 | 01 |
| Move semantics | C++11 | 07 |
| `std::unique_ptr` | C++11 | 06 |
| `std::function` | C++11 | 31 |
| `std::unordered_map` | C++11 | 22 |
| `std::execution::par_unseq` | C++17 | 48 |
| `std::pmr::*` | C++17 | 23 |
| `if constexpr` | C++17 | 12 |
| C++20 Concepts | C++20 | 02 |
| `std::span` | C++20 | 20 |
| `std::views` / ranges | C++20 | 11 |

---

*Last updated: 2026-03-01*
*Approach: Modern C++17/20 — no proprietary macros, no legacy patterns*
