# 84-Session C++ & Software Engineering Roadmap --- Learning from OpenFOAM

## Overview

This roadmap teaches **intermediate-to-advanced C++** and **real-world software engineering** by studying OpenFOAM as a production-grade case study. Over 84 sessions across 5 phases, you will reverse-engineer design patterns, data structures, architecture decisions, and performance techniques from one of the largest open-source C++ codebases in scientific computing --- then apply everything by building your own mini CFD solver from scratch.

---

## Summary Table

| Phase | Sessions | Topic | Milestone |
|-------|----------|-------|-----------|
| 1 | 01--14 | C++ Through OpenFOAM | Type-safe `Field<T>` with expression templates |
| 2 | 15--28 | Data Structures & Memory | LDU matrix with Gauss-Seidel solver |
| 3 | 29--42 | Software Architecture Patterns | Mini RTS-style factory for linear solvers |
| 4 | 43--56 | Performance Optimization | Optimized `Field<T>` with benchmarks |
| 5 | 57--84 | Focused CFD Component | 1D advection-diffusion solver with SIMPLE |

---

## Learning Objectives

1. Intermediate-to-advanced C++ coding patterns
2. Real-world software architecture and design patterns
3. Performance optimization: data structures, algorithms, profiling
4. OpenFOAM as a case study of production C++ engineering

---

# Phase 1: C++ Through OpenFOAM's Eyes (Days 01--14)

**Focus:** Templates, CRTP, policy-based design, smart pointers, expression templates, RAII, move semantics.

**Source Targets:**
- `src/OpenFOAM/primitives/`
- `src/OpenFOAM/fields/Fields/`
- `src/OpenFOAM/memory/`
- `src/finiteVolume/interpolation/surfaceInterpolation/`

---

### Day 01: Templates & Generic Programming --- Study `Field<Type>`

- Read `src/OpenFOAM/fields/Fields/Field/Field.H` and identify template parameters
- Understand why OpenFOAM uses `Field<scalar>`, `Field<vector>`, `Field<tensor>` instead of separate classes
- Compare with `std::vector<T>` --- what extra responsibilities does `Field<T>` carry?
- Write a minimal `Field<T>` template with `size()`, `operator[]`, and a constructor

**Deliverable:** A working `Field<T>` template that compiles for `scalar` and `vector` types.

---

### Day 02: Template Specialization --- How OpenFOAM Handles Scalar vs Vector

- Study how `Field<scalar>` gains arithmetic operators that `Field<tensor>` does not
- Examine partial specialization and explicit specialization patterns in OpenFOAM
- Understand `SFINAE` at a high level --- how the compiler selects overloads
- Write specializations: `Field<scalar>::max()` vs `Field<vector>::mag()`

**Deliverable:** Template specializations that provide type-appropriate operations.

---

### Day 03: Class Templates Deep Dive --- `GeometricField<Type, PatchField, GeoMesh>`

- Read `GeometricField.H` and map out its three template parameters
- Understand why `PatchField` and `GeoMesh` are template parameters (not runtime choices)
- Trace how `volScalarField` is a typedef for a specific `GeometricField` instantiation
- Diagram the relationship: `GeometricField` -> `DimensionedField` -> `Field`

**Deliverable:** A written class diagram showing the `GeometricField` template hierarchy and its typedefs.

---

### Day 04: CRTP Pattern --- `surfaceInterpolationScheme` Hierarchy

- Read `surfaceInterpolationScheme.H` and identify the Curiously Recurring Template Pattern
- Understand how CRTP enables static polymorphism (no vtable overhead)
- Compare CRTP with virtual dispatch --- when does OpenFOAM use each?
- Implement a toy CRTP hierarchy: `Base<Derived>` with `interpolate()`

**Deliverable:** A CRTP-based interpolation scheme hierarchy with two concrete schemes (e.g., `linear`, `upwind`).

---

### Day 05: Policy-Based Design --- How Schemes Select Behavior at Compile Time

- Study how `limitedSurfaceInterpolationScheme` uses a `Limiter` policy
- Read `vanLeer.H` and `SuperBee.H` to see how limiter policies differ
- Understand the compile-time strategy pattern: policy classes injected as template parameters
- Implement a `LimitedField<T, LimiterPolicy>` with two policies

**Deliverable:** A policy-based design example with interchangeable limiter strategies.

---

### Day 06: Smart Pointers --- `autoPtr<>`, `tmp<>`, `refCount`

- Read `autoPtr.H` and compare with `std::unique_ptr` --- what does OpenFOAM add?
- Read `tmp.H` and understand its dual role: owning pointer or const reference
- Study `refCount` and how `tmp<>` manages reference-counted temporaries
- Write a mini `tmp<Field<T>>` that handles both owned and borrowed fields

**Deliverable:** A working `tmp<T>` implementation with move semantics and reference counting.

---

### Day 07: RAII and Resource Management --- `IOobject` Lifecycle

- Read `IOobject.H` and understand how it ties object lifetime to the file system
- Study how constructors register objects and destructors clean up
- Trace the lifecycle: construction -> registration -> read -> write -> destruction
- Identify RAII patterns in `regIOobject` and `objectRegistry`

**Deliverable:** A written analysis of the `IOobject` RAII lifecycle with a sequence diagram.

---

### Day 08: Move Semantics & Perfect Forwarding --- `tmp<>` Move Constructor

- Read the move constructor and move assignment operator in `tmp.H`
- Understand why move semantics matter for large field operations (avoid megabyte copies)
- Study perfect forwarding with `std::forward` and universal references
- Benchmark: copy vs move for a 1-million-element `Field<scalar>`

**Deliverable:** Benchmark results showing the performance impact of move semantics on field operations.

---

### Day 09: Expression Templates --- Field Arithmetic Without Temporaries

- Understand the problem: `a + b + c` creates two temporary `Field` objects
- Study how expression templates defer evaluation until assignment
- Read OpenFOAM's approach (or lack thereof) and compare with Eigen/Blitz++
- Implement a minimal expression template for `Field<scalar>` addition

**Deliverable:** An expression template system that evaluates `a + b + c` in a single loop with no temporaries.

---

### Day 10: Operator Overloading --- `Field<T>` Operator Design

- Read `FieldFunctions.H` and `FieldFunctionsM.H` (macro-generated operators)
- Understand why OpenFOAM uses macros to generate `operator+`, `operator*`, etc.
- Study return-type deduction for mixed-type operations (scalar * vector)
- Add `operator+`, `operator-`, `operator*` to your `Field<T>` using expression templates

**Deliverable:** A `Field<T>` with complete arithmetic operators backed by expression templates.

---

### Day 11: Iterators & Range-Based Patterns --- The `forAll` Macro

- Read the `forAll` macro definition and understand what it expands to
- Compare `forAll(field, i)` with C++11 range-based for loops
- Study `forAllIter` and `forAllConstIter` for container traversal
- Discuss: why does OpenFOAM use macros instead of modern C++ ranges?

**Deliverable:** A comparison document: `forAll` macro vs range-based for vs `std::for_each`, with performance notes.

---

### Day 12: Type Traits & SFINAE --- OpenFOAM's `typeInfo` System

- Read `typeInfo.H`, `className.H`, and the `TypeName` macro
- Understand how `typeName` provides runtime type identification without full RTTI
- Study SFINAE (Substitution Failure Is Not An Error) in template overload selection
- Implement a simplified `typeInfo` system with `typeName()` for your classes

**Deliverable:** A type identification system for your `Field<T>` and scheme classes.

---

### Days 13--14: Mini-Project --- Build a Type-Safe `Field<T>` with Expression Templates

- Combine all Phase 1 concepts into a single cohesive library
- Requirements: `Field<T>` with expression templates, move semantics, `tmp<>` wrapper, `typeInfo`
- Add unit tests: arithmetic correctness, no temporary allocations, move vs copy
- Write a benchmark: 1M-element field arithmetic chain

**Deliverable:** A complete `Field<T>` library with expression templates, smart pointer management, and benchmarks. This is the foundation for all subsequent phases.

---

## Phase 1 Milestone

> **M1** --- Day 14: Type-safe `Field<T>` library complete, benchmarked, and tested.

---

# Phase 2: Data Structures & Memory (Days 15--28)

**Focus:** LDU sparse matrix, cache-friendly storage, `HashTable`, memory pools, compact topology storage.

**Source Targets:**
- `src/OpenFOAM/matrices/lduMatrix/`
- `src/OpenFOAM/containers/`
- `src/OpenFOAM/meshes/polyMesh/`
- `src/OpenFOAM/fields/Fields/`

---

### Day 15: LDU Matrix Format --- Why Not CSR for CFD?

- Read `lduMatrix.H` and understand the Lower-Diagonal-Upper storage format
- Compare LDU with CSR/CSC: memory layout, access patterns, fill-in behavior
- Understand why LDU suits FVM: symmetric sparsity pattern, face-based addressing
- Sketch the LDU layout for a simple 5-cell mesh

**Deliverable:** A written comparison of LDU vs CSR with diagrams showing memory layout for a sample mesh.

---

### Day 16: LDU Addressing --- Owner/Neighbour Arrays

- Read `lduAddressing.H` and understand `owner()` and `neighbour()` arrays
- Trace how a mesh face maps to a matrix off-diagonal entry
- Understand the constraint: `owner[face] < neighbour[face]` and why it matters
- Implement `lduAddressing` for a structured 1D mesh (N cells, N-1 internal faces)

**Deliverable:** A working `lduAddressing` class for a 1D mesh with owner/neighbour arrays.

---

### Day 17: Matrix-Vector Multiply --- Cache-Friendly Implementation

- Read `lduMatrix::Amul()` and trace the three-pass multiply (lower, diagonal, upper)
- Understand why separate passes over lower/upper are cache-friendly
- Benchmark: LDU multiply vs naive CSR multiply on a 100K-cell mesh
- Profile cache misses using `cachegrind` or equivalent

**Deliverable:** An LDU matrix-vector multiply with cache-miss analysis and benchmark results.

---

### Day 18: Sparse Matrix Assembly --- How `fvMatrix` Populates LDU

- Read `fvMatrix.H` and trace how `fvm::laplacian` assembles matrix coefficients
- Understand the face-loop pattern: for each face, add to `owner` row and `neighbour` row
- Study how boundary conditions modify the diagonal and source
- Implement assembly for the 1D Laplacian: `d2T/dx2 = 0` with Dirichlet BCs

**Deliverable:** A 1D Laplacian matrix assembled in LDU format, solved, and verified against the analytical solution.

---

### Day 19: Cache Access Patterns --- Why Owner/Neighbour Ordering Matters

- Study how face ordering affects memory access during matrix-vector multiply
- Understand bandwidth reduction: Cuthill-McKee and reverse Cuthill-McKee reordering
- Measure the effect of random vs ordered face numbering on multiply performance
- Experiment with `renumberMesh` in OpenFOAM

**Deliverable:** A benchmark showing the performance impact of face ordering on matrix-vector multiply.

---

### Day 20: OpenFOAM `List<T>` --- Internals vs `std::vector`

- Read `List.H` and `UList.H` --- understand the non-owning `UList` base class
- Compare memory management: `List` always allocates, `UList` can view existing memory
- Study `setSize()`, `resize()`, and how they differ from `std::vector::resize()`
- Implement a simplified `List<T>` / `UList<T>` pair

**Deliverable:** A `List<T>` with a non-owning `UList<T>` base class, with tests for view semantics.

---

### Day 21: `DynamicList` & `CompactListList` --- Variable-Size Containers

- Read `DynamicList.H` --- OpenFOAM's equivalent of a growable vector with capacity
- Read `CompactListList.H` --- a flat array with offset indexing (like CSR row pointers)
- Understand when to use each: `DynamicList` for building, `CompactListList` for access
- Implement `CompactListList` and use it to store variable-length adjacency lists

**Deliverable:** A `CompactListList` implementation storing cell-to-face connectivity.

---

### Day 22: `HashTable<T>` --- Open Addressing in OpenFOAM

- Read `HashTable.H` and identify the collision resolution strategy
- Study the hash function selection and bucket sizing (power of two)
- Compare with `std::unordered_map`: open addressing vs chaining
- Benchmark insertion and lookup for 100K entries

**Deliverable:** A simplified `HashTable<T>` with open addressing and performance comparison against `std::unordered_map`.

---

### Day 23: `HashSet` & `wordHashSet` --- Practical Usage Patterns

- Read `HashSet.H` and understand it as `HashTable<nil>`
- Study `wordHashSet` usage in OpenFOAM: tracking field names, patch names
- Examine set operations: intersection, union, difference
- Use `wordHashSet` to implement a field registry that tracks registered names

**Deliverable:** A field registry using `HashSet` that prevents duplicate registrations.

---

### Day 24: Memory Pools --- `UList` and `SubList` Zero-Copy Views

- Read `SubList.H` and understand how it provides a view into a contiguous `List`
- Study `SubField.H` and its use for patch-level field access without copying
- Understand the zero-copy philosophy: views share memory with the parent
- Implement `SubList` with bounds checking in debug mode

**Deliverable:** A `SubList<T>` view class with debug-mode bounds checking and a benchmark showing zero-copy performance.

---

### Day 25: Compact Storage --- `labelList`, `faceList` for Mesh Topology

- Read how `polyMesh` stores topology: `points_`, `faces_`, `owner_`, `neighbour_`
- Understand `faceList` as `List<face>` where `face` is `List<label>` (variable-size)
- Study the trade-off: flexibility of `faceList` vs compactness of `CompactListList`
- Calculate memory usage for a 1M-cell hex mesh under both storage schemes

**Deliverable:** A memory analysis comparing `faceList` vs `CompactListList` for mesh topology storage.

---

### Day 26: `Field<T>` Memory --- Alignment, Padding, SIMD Readiness

- Examine `Field<scalar>` memory layout: is it 16-byte or 32-byte aligned?
- Study how alignment affects SIMD (SSE needs 16-byte, AVX needs 32-byte)
- Read `aligned_alloc` usage (or its absence) in OpenFOAM
- Modify your `Field<T>` to use aligned allocation and measure the effect

**Deliverable:** An aligned `Field<T>` with benchmarks showing SIMD-friendly vs unaligned performance.

---

### Days 27--28: Mini-Project --- LDU Matrix with Gauss-Seidel Solver, Benchmark vs Dense

- Build a complete LDU matrix class with addressing, assembly, and multiply
- Implement Gauss-Seidel and Jacobi iterative solvers
- Assemble and solve the 1D heat equation on a 10K-cell mesh
- Benchmark: LDU Gauss-Seidel vs dense Gaussian elimination (memory and time)

**Deliverable:** A working LDU matrix library with iterative solvers. Benchmark report comparing sparse vs dense performance.

---

## Phase 2 Milestone

> **M2** --- Day 28: LDU matrix library with iterative solvers, benchmarked against dense storage.

---

# Phase 3: Software Architecture Patterns (Days 29--42)

**Focus:** RTS factory pattern, dictionary system, plugin architecture, build system, I/O framework, boundary condition design.

**Source Targets:**
- `src/OpenFOAM/db/runTimeSelection/`
- `src/OpenFOAM/db/dictionary/`
- `src/OpenFOAM/db/IOobject/`
- `src/OpenFOAM/db/Time/`
- `wmake/`

---

### Day 29: RunTimeTypeSelection (RTS) Overview --- Factory Pattern in C++

- Read `runTimeSelectionTables.H` and understand the macro-based factory pattern
- Trace how `New()` creates objects by string name at runtime
- Compare RTS with a textbook factory pattern and with `std::map<string, creator>`
- Diagram the RTS mechanism: registration, lookup, construction

**Deliverable:** A written analysis of the RTS pattern with a flowchart showing object creation from string name.

---

### Day 30: RTS Internals --- `declareRunTimeSelectionTable` Macros

- Expand the macros manually: `declareRunTimeSelectionTable`, `defineRunTimeSelectionTable`
- Understand the static `HashTable` of constructor function pointers
- Study the `add...ToTable` helper class that registers at static initialization time
- Identify the risks: static initialization order fiasco, debugging difficulty

**Deliverable:** A line-by-line macro expansion showing exactly what the RTS macros generate.

---

### Day 31: Adding a New RTS Class --- Write a Custom Scheme

- Follow the steps to add a new `surfaceInterpolationScheme` to OpenFOAM
- Create the `.H` and `.C` files with proper macros
- Compile and verify that `New("myScheme", ...)` returns your class
- Document the exact steps: what to write, what macros to invoke, what to link

**Deliverable:** A working custom interpolation scheme registered via RTS, with step-by-step instructions.

---

### Day 32: Dictionary System --- `IOdictionary`, Token, `primitiveEntry`

- Read `dictionary.H`, `entry.H`, `primitiveEntry.H`
- Understand the token stream: how text is parsed into typed values
- Study the tree structure: `dictionary` contains `entry` objects (key-value or sub-dictionary)
- Implement a simplified dictionary that stores `string -> variant(int, double, string)`

**Deliverable:** A mini dictionary class that parses key-value pairs from text.

---

### Day 33: Dictionary Parsing --- How OpenFOAM Reads `controlDict`

- Trace the parsing path: file -> `ISstream` -> tokenizer -> `dictionary::read()`
- Understand token types: `word`, `scalar`, `label`, `string`, punctuation
- Study how nested `{}` creates sub-dictionaries
- Extend your mini dictionary to handle nested dictionaries and typed lookups

**Deliverable:** A dictionary parser that reads nested configuration files with typed value retrieval.

---

### Day 34: Plugin Architecture --- How `fvSchemes` Loads Interpolation Schemes

- Read `fvSchemes.H` and trace how it reads scheme names from the dictionary
- Understand the full chain: dictionary -> string name -> RTS lookup -> scheme object
- Study how this enables adding new schemes without modifying core code
- Diagram the plugin architecture: user config -> dictionary -> factory -> object

**Deliverable:** A flowchart of the plugin loading chain from configuration file to instantiated scheme object.

---

### Day 35: `IOobject` & `objectRegistry` --- Automatic I/O

- Read `IOobject.H` and understand `readOpt` and `writeOpt` enumerations
- Study `objectRegistry.H` and how it manages a collection of `regIOobject` entries
- Trace what happens when `objectRegistry` destructs: automatic writing of modified objects
- Implement a mini `objectRegistry` that stores named objects and writes them on destruction

**Deliverable:** A mini object registry with automatic write-on-destruct behavior.

---

### Day 36: Time Class Architecture --- Time Stepping and Object Management

- Read `Time.H` and understand its dual role: time control and top-level `objectRegistry`
- Study `Time::operator++()` and how it advances the time step
- Understand output control: `writeInterval`, `writeControl`, `purgeWrite`
- Diagram the `Time` class responsibilities and its inheritance chain

**Deliverable:** A class diagram of `Time` showing its roles as time controller, object registry, and I/O manager.

---

### Day 37: Boundary Condition Framework --- Strategy Pattern with `PatchField`

- Read `fvPatchField.H` and its virtual interface: `evaluate()`, `updateCoeffs()`
- Study how `fixedValueFvPatchField` and `zeroGradientFvPatchField` implement the interface
- Understand how BC coefficients (`valueInternalCoeffs`, `valueBoundaryCoeffs`) feed into `fvMatrix`
- Implement a mini BC framework: `PatchField` base with `fixedValue` and `zeroGradient`

**Deliverable:** A boundary condition framework with strategy-pattern dispatch and matrix coefficient injection.

---

### Day 38: Build System --- wmake Internals, `Make/files`, `Make/options`

- Read `wmake` scripts and understand the build process
- Study `Make/files` (source listing) and `Make/options` (include/link paths)
- Understand `lnInclude` directories and why OpenFOAM flattens headers
- Compare `wmake` with CMake: pros and cons for a large C++ project

**Deliverable:** A comparison document: `wmake` vs CMake, with a working `Make/files` and `Make/options` for your library.

---

### Day 39: Dependency Management --- `lnInclude`, Library Linking

- Trace how `wmake` generates `lnInclude` symlinks
- Understand library dependency chains: `libOpenFOAM.so` -> `libfiniteVolume.so`
- Study `LD_LIBRARY_PATH` and how OpenFOAM finds shared libraries at runtime
- Set up a multi-library build: your `Field<T>` library linked by your solver

**Deliverable:** A multi-library build configuration where a solver links against your `Field<T>` library.

---

### Day 40: Error Handling --- `FatalError`, `WarningIn`, `InfoProxy`

- Read `error.H` and understand `FatalErrorIn`, `FatalIOErrorIn`
- Study the error stream hierarchy: `messageStream`, `error`, `IOerror`
- Understand how OpenFOAM formats error messages with file/line info
- Add structured error handling to your libraries: fatal errors, warnings, info messages

**Deliverable:** An error handling system for your libraries with formatted messages and abort-on-fatal behavior.

---

### Days 41--42: Mini-Project --- Mini RTS-Style Factory for Linear Solvers

- Build a complete RTS-style factory system from scratch (no macros)
- Register at least three solver types: `Jacobi`, `GaussSeidel`, `PCG`
- Read solver selection from a dictionary file
- Solve the 1D heat equation using dictionary-selected solver

**Deliverable:** A working RTS factory with dictionary-driven solver selection. Demonstrate adding a new solver without modifying existing code.

---

## Phase 3 Milestone

> **M3** --- Day 42: Mini RTS factory with dictionary-driven configuration, demonstrated with linear solvers.

---

# Phase 4: Performance Optimization (Days 43--56)

**Focus:** Profiling, SIMD, OpenMP, cache optimization, memory allocation, algorithm complexity, I/O performance.

**Source Targets:**
- `src/OpenFOAM/fields/Fields/Field/`
- `src/OpenFOAM/matrices/lduMatrix/solvers/`
- `src/OpenFOAM/meshes/polyMesh/`
- `src/Pstream/`

---

### Day 43: Profiling Basics --- `perf`, `gprof`, `callgrind` on OpenFOAM

- Set up profiling tools: `perf record`/`perf report`, `gprof`, `valgrind --tool=callgrind`
- Profile a simple OpenFOAM solver (e.g., `laplacianFoam`) on a test case
- Identify the top 5 hottest functions and their call counts
- Document the profiling workflow: compile flags, run command, analysis

**Deliverable:** A profiling report for `laplacianFoam` identifying hot functions.

---

### Day 44: Flame Graphs --- Visualizing Hot Paths in a CFD Solver

- Generate flame graphs from `perf` data using Brendan Gregg's tools
- Interpret the flame graph: width = time, depth = call stack
- Compare flame graphs for different mesh sizes (1K, 10K, 100K cells)
- Identify the scaling bottleneck: solver, assembly, or I/O

**Deliverable:** Flame graphs for three mesh sizes with analysis of scaling behavior.

---

### Day 45: Cache Analysis --- `cachegrind`, Understanding L1/L2/L3 Misses

- Run `valgrind --tool=cachegrind` on your LDU matrix-vector multiply
- Interpret the output: instruction cache vs data cache, L1 vs LL misses
- Compare cache performance for sequential vs random access patterns
- Calculate theoretical cache miss rate for LDU multiply and compare with measured

**Deliverable:** A cache analysis report with theoretical vs measured miss rates.

---

### Day 46: SIMD Fundamentals --- SSE/AVX and Field Arithmetic

- Understand SIMD lanes: SSE (128-bit, 2 doubles), AVX (256-bit, 4 doubles), AVX-512 (8 doubles)
- Write an explicit SIMD kernel for `Field<scalar>` addition using intrinsics
- Compare performance: scalar loop vs SSE vs AVX
- Identify alignment requirements for each instruction set

**Deliverable:** A SIMD-accelerated field addition with benchmark results for each instruction set width.

---

### Day 47: Auto-Vectorization --- Compiler Flags, Checking Assembly Output

- Compile your `Field<T>` operations with `-O2 -ftree-vectorize -fopt-info-vec`
- Read the compiler optimization report: which loops were vectorized?
- Examine assembly output (`-S`) to verify SIMD instructions were generated
- Identify and fix vectorization blockers: aliasing, alignment, complex control flow

**Deliverable:** A document showing which loops auto-vectorize and which do not, with fixes for the blockers.

---

### Day 48: OpenMP Basics --- Parallel Loops in Field Operations

- Add `#pragma omp parallel for` to `Field<T>` arithmetic
- Measure speedup with 1, 2, 4, 8 threads on a 10M-element field
- Understand thread overhead: when is the field too small for OpenMP to help?
- Identify the crossover point: serial vs parallel

**Deliverable:** Speedup curves for OpenMP-parallelized field operations with crossover analysis.

---

### Day 49: OpenMP Advanced --- Reduction, Scheduling, False Sharing

- Implement parallel reduction: `Field<scalar>::sum()`, `Field<scalar>::max()`
- Compare scheduling strategies: static, dynamic, guided
- Demonstrate false sharing with a counter array and fix it with padding
- Apply to matrix-vector multiply: parallelize the face loop

**Deliverable:** Parallel reductions and a false-sharing demonstration with fix.

---

### Day 50: Memory Allocation --- `malloc` Alternatives, Pool Allocators

- Profile allocation overhead in a solver loop: how many `malloc`/`free` calls per iteration?
- Implement a simple pool allocator for fixed-size `Field<scalar>` temporaries
- Compare `malloc`, `jemalloc`, `tcmalloc`, and pool allocator performance
- Measure the effect on solver iteration time

**Deliverable:** A pool allocator for field temporaries with benchmark results.

---

### Day 51: Avoiding Temporaries --- Expression Templates Revisited for Performance

- Revisit the expression template system from Phase 1 with performance focus
- Measure: how many temporaries does `a + b * c - d` create with vs without expression templates?
- Profile memory allocation count in a typical solver right-hand-side assembly
- Optimize a real solver expression to eliminate all intermediate allocations

**Deliverable:** Before/after profiling showing temporary elimination in a solver expression.

---

### Day 52: Algorithm Complexity --- Mesh Traversal, Face Sorting, Renumbering

- Analyze the complexity of common mesh operations: face lookup, cell neighbor traversal
- Study bandwidth-reducing reorderings: Cuthill-McKee, Sloan
- Implement reverse Cuthill-McKee for your 1D/2D mesh
- Measure the effect on solver convergence rate and matrix-vector multiply time

**Deliverable:** A mesh renumbering implementation with convergence and performance comparison.

---

### Day 53: I/O Performance --- Parallel I/O, Buffering Strategies

- Profile I/O time in an OpenFOAM simulation: what fraction of total time is I/O?
- Study buffered vs unbuffered writes for field output
- Implement binary field output and compare with ASCII (size and speed)
- Examine OpenFOAM's `collated` file format for parallel I/O

**Deliverable:** An I/O benchmark comparing ASCII, binary, buffered, and unbuffered strategies.

---

### Day 54: MPI Fundamentals --- `Pstream`, Domain Decomposition Basics

- Read `Pstream.H` and understand OpenFOAM's MPI abstraction layer
- Study `UPstream`, `IPstream`, `OPstream` for point-to-point communication
- Understand domain decomposition: `decomposePar`, processor boundaries
- Diagram the communication pattern for a halo exchange on a decomposed mesh

**Deliverable:** A written analysis of OpenFOAM's MPI layer with a communication diagram for halo exchange.

---

### Days 55--56: Mini-Project --- Optimize Your `Field<T>` Class, Measure with Benchmarks

- Apply all Phase 4 techniques to your `Field<T>` library from Phase 1
- Add: aligned allocation, expression templates, OpenMP parallel loops, optional SIMD
- Create a comprehensive benchmark suite: allocation, arithmetic, reduction, mixed expressions
- Produce a performance report: baseline vs optimized, with flame graphs

**Deliverable:** An optimized `Field<T>` library with a comprehensive benchmark report showing measurable improvements.

---

## Phase 4 Milestone

> **M4** --- Day 56: Optimized `Field<T>` library with performance report demonstrating measurable improvements over baseline.

---

# Phase 5: Focused CFD Component (Days 57--84)

**Focus:** Apply all learned patterns to build a well-engineered 1D advection-diffusion solver with SIMPLE algorithm.

**Source Targets:**
- `src/finiteVolume/fvMatrices/`
- `src/finiteVolume/finiteVolume/fvm/`
- `src/finiteVolume/finiteVolume/fvc/`
- `applications/solvers/`

---

### Days 57--58: Project Setup --- Architecture and Class Hierarchy

- Design the overall class hierarchy: `Mesh`, `Field`, `Matrix`, `Solver`, `Operator`, `BoundaryCondition`
- Define interfaces using lessons from Phase 3: RTS for solvers and schemes, dictionary for configuration
- Set up the build system: `Make/files`, `Make/options` (or CMake)
- Create the project directory structure and stub files

**Deliverable:** A project skeleton with class hierarchy diagram, build system, and compilable stubs.

---

### Days 59--60: Project Setup --- Build System and Testing Framework

- Configure the build for your mini solver: library + application
- Set up a testing framework (Catch2, Google Test, or simple asserts)
- Write the first test: `Field<scalar>` arithmetic correctness
- Establish a CI-like workflow: build, test, benchmark

**Deliverable:** A working build + test pipeline that compiles and runs unit tests.

---

### Days 61--62: 1D Mesh --- Points, Faces, Cells with Proper Data Structures

- Implement a 1D mesh class using `CompactListList` or equivalent for topology
- Store: points (1D coordinates), faces (cell boundaries), cells (face pairs)
- Compute geometric quantities: cell volumes (lengths), face areas (1.0), cell centers, face centers
- Implement owner/neighbour addressing for internal faces

**Deliverable:** A 1D mesh class with geometry computation and owner/neighbour addressing, tested for a 100-cell uniform mesh.

---

### Days 63--64: 1D Mesh --- Boundary Patches and Non-Uniform Spacing

- Add boundary patch support: inlet (left face), outlet (right face)
- Implement graded (non-uniform) cell spacing for boundary-layer resolution
- Add mesh quality metrics: aspect ratio, expansion ratio
- Write mesh-to-VTK output for visualization in ParaView

**Deliverable:** A 1D mesh with boundary patches, graded spacing, and VTK output.

---

### Days 65--66: Field & Matrix --- `volScalarField` Equivalent with LDU Storage

- Implement a `ScalarField` class on the 1D mesh with internal and boundary values
- Implement the LDU matrix class with 1D mesh addressing
- Implement boundary coefficient injection: `valueInternalCoeffs`, `valueBoundaryCoeffs`
- Test: create a field, assemble a matrix, verify dimensions

**Deliverable:** A mesh-aware `ScalarField` and `LDUMatrix` with boundary condition support.

---

### Days 67--68: Field & Matrix --- Matrix Assembly and Solver Integration

- Implement `fvMatrix<scalar>` that combines LDU matrix with source vector and boundary contributions
- Implement the `solve()` interface using your Gauss-Seidel and PCG solvers from Phase 2
- Add under-relaxation support
- Test: assemble and solve the Laplacian equation `d2T/dx2 = 0` with Dirichlet BCs

**Deliverable:** A working `fvMatrix` that assembles and solves the 1D Laplacian, verified against analytical solution.

---

### Days 69--70: FVM Operators --- `ddt` and `div` Using RTS Selection

- Implement `fvm::ddt` with Euler implicit scheme (matrix contribution + source from old time)
- Implement `fvm::div` with upwind scheme (face flux, owner/neighbour contributions)
- Register both operators with your RTS factory for dictionary selection
- Test `fvm::ddt`: verify time-stepping with a decaying field

**Deliverable:** Working `fvm::ddt` and `fvm::div` operators, RTS-registered, with verification tests.

---

### Days 71--72: FVM Operators --- `laplacian` and Explicit Operators

- Implement `fvm::laplacian` with face-interpolated diffusivity
- Implement explicit operators: `fvc::grad`, `fvc::div`
- Add face interpolation (linear, upwind) using your scheme hierarchy
- Test: solve the steady diffusion equation and compare with analytical solution

**Deliverable:** Complete FVM operator set (ddt, div, laplacian, grad) with verification.

---

### Days 73--74: Linear Solvers --- PCG and Gauss-Seidel with Benchmarking

- Integrate your Phase 2 solvers with the `fvMatrix` framework
- Implement diagonal preconditioning for PCG
- Add convergence monitoring: residual history, iteration count
- Benchmark: PCG vs Gauss-Seidel for the Laplacian on 1K, 10K, 100K cells

**Deliverable:** Integrated linear solvers with convergence monitoring and scaling benchmarks.

---

### Days 75--76: SIMPLE Algorithm --- Pressure-Velocity Coupling

- Implement the SIMPLE loop for 1D incompressible flow:
  1. Momentum predictor: solve for `U*`
  2. Pressure equation: solve for `p'` using H/A formulation
  3. Velocity correction: `U = U* - (1/A) * grad(p')`
- Implement Rhie-Chow interpolation for face velocity
- Add under-relaxation for pressure and velocity

**Deliverable:** A working SIMPLE algorithm for 1D channel flow, verified against the Poiseuille flow analytical solution.

---

### Days 77--78: SIMPLE Algorithm --- Convergence and Scalar Transport

- Add SIMPLE convergence checking: residual drop, iteration limits
- Implement scalar transport: solve `ddt(T) + div(phi, T) = laplacian(DT, T)` within the SIMPLE loop
- Test: heated 1D channel with inlet temperature and wall flux
- Verify temperature profile against analytical Graetz-like solution

**Deliverable:** SIMPLE with scalar transport, verified for heated channel flow.

---

### Days 79--80: Source Term Extension --- Adding a Volumetric Source

- Design a source term framework using RTS: `fvSource` base class with concrete implementations
- Implement `fixedValueSource` (constant), `fieldProportionalSource` (proportional to field value)
- Add source terms to both momentum and scalar transport equations
- Test: channel flow with a volumetric heat source, compare with analytical solution

**Deliverable:** An RTS-based source term framework integrated with the solver.

---

### Days 81--82: Testing and Documentation

- Write comprehensive tests for all components: mesh, field, matrix, operators, solver
- Profile the complete solver: identify bottlenecks with flame graphs
- Apply Phase 4 optimizations where they matter most
- Write a user guide: how to set up a case, configure the dictionary, run, and post-process

**Deliverable:** A tested and documented solver with profiling report.

---

### Days 83--84: Final Benchmark --- Compare with OpenFOAM, Document, Reflect

- Set up an equivalent case in OpenFOAM (`laplacianFoam` or `simpleFoam` on a 1D mesh)
- Compare results: field values, residual convergence, iteration counts
- Compare code design: your RTS vs OpenFOAM RTS, your `fvMatrix` vs OpenFOAM's
- Write a final project report: what you built, what you learned, what you would do differently

**Deliverable:** A final benchmark report comparing your solver with OpenFOAM, and a reflective project summary.

---

## Phase 5 Milestone

> **M5** --- Day 84: Complete 1D advection-diffusion solver with SIMPLE algorithm, benchmarked against OpenFOAM.

---

# Milestone Summary

| Milestone | Day | Deliverable | Key Verification |
|-----------|-----|-------------|------------------|
| M1 | 14 | Type-safe `Field<T>` with expression templates | Unit tests pass, no temporary allocations in chained expressions |
| M2 | 28 | LDU matrix with iterative solvers | Solves 1D heat equation, matches analytical solution |
| M3 | 42 | Mini RTS factory with dictionary config | New solver added without modifying existing code |
| M4 | 56 | Optimized `Field<T>` with benchmarks | Measurable speedup over Phase 1 baseline |
| M5 | 84 | 1D solver with SIMPLE, compared to OpenFOAM | Results match OpenFOAM within discretization error |

---

# Appendix: OpenFOAM Source Reading Guide

| Phase | Key Source Files | What to Look For |
|-------|-----------------|------------------|
| 1 | `Field.H`, `GeometricField.H`, `tmp.H`, `autoPtr.H` | Template patterns, smart pointer design |
| 2 | `lduMatrix.H`, `lduAddressing.H`, `List.H`, `HashTable.H` | Storage layout, access patterns |
| 3 | `runTimeSelectionTables.H`, `dictionary.H`, `IOobject.H`, `Time.H` | Factory pattern, I/O design |
| 4 | `Field.C` (arithmetic), `lduMatrix` solvers, `Pstream.H` | Hot loops, parallelization |
| 5 | `fvMatrix.H`, `fvm*.C`, `fvc*.C`, `simpleFoam.C` | FVM discretization, algorithm structure |

---

*Last Updated: 2026-03-01*
*Curriculum: C++ and Software Engineering Through OpenFOAM*
*Total Sessions: 84 across 5 phases*
