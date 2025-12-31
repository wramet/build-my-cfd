# Performance Considerations

Performance Considerations in Object-Oriented OpenFOAM Programming

---

## Overview

> **Virtual functions have small overhead, but can significantly impact tight loops. Understanding when and how to use them is critical for performance-critical CFD code.**

Performance optimization in OpenFOAM requires understanding the trade-offs between **runtime flexibility** (virtual functions) and **compile-time efficiency** (templates). This module provides measurable benchmarks, profiling techniques, and decision frameworks for choosing the right approach.

---

## Learning Objectives

By the end of this module, you will be able to:

- **Measure** the actual performance cost of virtual function calls in OpenFOAM
- **Identify** performance-critical code paths where virtual overhead matters
- **Apply** mitigation strategies: batching, template dispatch, and hybrid approaches
- **Profile** OpenFOAM code using specific tools to detect virtual call bottlenecks
- **Decide** when to use virtual functions versus templates based on measurable criteria

---

## 1. Understanding the Costs: The What, Why, and How

### 1.1 What: Virtual Function Call Overhead

**Definition:** A virtual function call requires:
1. V-table lookup (indirect addressing)
2. Potential instruction cache miss
3. Branch prediction challenges

**Benchmark Results (x86-64 architecture):**

| Operation Type | Cycles | Relative Cost | When It Matters |
|----------------|--------|---------------|-----------------|
| Direct call | ~1-2 cycles | 1x | Never |
| Virtual call (cached) | ~10-20 cycles | 10-20x | Inner loops |
| Virtual call (cache miss) | ~100+ cycles | 100+x | Tight loops |
| Virtual call per cell | ~10-20 cycles × N cells | Millions | ALWAYS |

**Real OpenFOAM Impact:**

```cpp
// Example: 1M cells, 1000 timesteps
// Direct: 1M × 1000 × 1 cycle = 1B cycles (~0.3 seconds @ 3GHz)
// Virtual: 1M × 1000 × 15 cycles = 15B cycles (~5 seconds @ 3GHz)
// Overhead: 4.7 seconds PER MODEL CALL
```

### 1.2 Why: The Performance Impact

**Key Insight:** Virtual function overhead is **not** about the single call cost—it's about **amplification through iteration**.

```cpp
// Seemingly innocent code
forAll(mesh.cells(), cellI)
{
    scalar value = turbulence->muEff()[cellI];  // Virtual call
    // Do computation...
}
// Problem: For 1M cells = 1M virtual calls per timestep!
```

### 1.3 How: Measuring Your Specific Case

**Benchmark Template:**

```cpp
// Test performance in YOUR specific case
#include <chrono>

class VirtualModel
{
public:
    virtual scalar compute(scalar x) const { return x * x; }
};

class DirectModel
{
public:
    scalar compute(scalar x) const { return x * x; }
};

void benchmarkVirtualVsDirect()
{
    const label nIter = 10000000;
    scalarField x(nIter, 1.0);
    scalarField result(nIter);
    
    // Virtual call benchmark
    auto* virtualModel = new VirtualModel();
    auto start = std::chrono::high_resolution_clock::now();
    forAll(x, i)
    {
        result[i] = virtualModel->compute(x[i]);
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto virtualTime = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    // Direct call benchmark
    DirectModel directModel;
    start = std::chrono::high_resolution_clock::now();
    forAll(x, i)
    {
        result[i] = directModel.compute(x[i]);
    }
    end = std::chrono::high_resolution_clock::now();
    auto directTime = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    Info<< "Virtual: " << virtualTime.count() << " ms" << nl
        << "Direct: " << directTime.count() << " ms" << nl
        << "Overhead: " << (virtualTime.count() - directTime.count()) << " ms" << endl;
}
```

---

## 2. When Virtual Overhead Matters: Decision Framework

### 2.1 The Call Frequency Spectrum

```
HIGH FREQUENCY (Virtual BAD)    LOW FREQUENCY (Virtual OK)
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Per-cell operations              Per-timestep setup    │
│  Per-face operations              Per-iteration config  │
│  Inner loop calculations          Solver selection      │
│  Boundary condition evaluation    Model creation        │
│  Field equation evaluation        I/O operations        │
│                                                           │
│  TEMPLATE preferred               VIRTUAL acceptable    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Decision Tree: Virtual vs Template

```
START: Need runtime selection?
│
├─ NO → Use TEMPLATES (compile-time)
│  └─ Example: Field operations, math kernels
│
└─ YES → Call frequency?
   │
   ├─ HIGH (>1000 calls/step) → Consider HYBRID approach
   │  │
   │  └─ Can you batch operations?
   │     ├─ YES → Virtual per batch, template per element
   │     └─ NO → Accept overhead OR redesign
   │
   └─ LOW (<1000 calls/step) → Use VIRTUAL
      └─ Example: turbulence->correct(), mesh.update()
```

### 2.3 Real OpenFOAM Examples

**Acceptable Virtual Usage:**

```cpp
// 1. Once per timestep (OK)
turbulence->correct();
mesh.readUpdate();
runTime.write();

// 2. Model selection (OK)
autoPtr<compressible::turbulenceModel> turbulence
(
    compressible::turbulenceModel::New(rho, U, phi, thermo)
);

// 3. Per-boundary (usually OK)
forAll(mesh.boundary(), patchI)
{
    fvPatchVectorField& pf = U.boundaryFieldRef()[patchI];
    pf.updateCoeffs();  // Virtual per patch (typically <100 patches)
}
```

**Problematic Virtual Usage:**

```cpp
// 1. Per-cell virtual call (BAD)
forAll(mesh.cells(), cellI)
{
    scalar k = turbulence->k()[cellI];  // Virtual per cell!
}

// BETTER: Access field directly
const volScalarField& k = turbulence->k();  // One virtual call
forAll(mesh.cells(), cellI)
{
    scalar kCell = k[cellI];  // Direct access
}

// 2. Per-face virtual call (BAD)
forAll(mesh.faces(), faceI)
{
    vector flux = model->calculateFlux(faceI);  // Virtual per face!
}

// BETTER: Batch process
surfaceVectorField fluxes = model->calculateFluxes();  // One virtual call
```

---

## 3. Mitigation Strategies: Theory to Practice

### 3.1 Strategy 1: Batch Processing

**Theory:** Replace N virtual calls with 1 virtual call + N direct operations.

**Simple Example:**

```cpp
// BAD: Per-cell virtual calls
class Model
{
public:
    virtual scalar compute(label cellI) const;
};

forAll(cells, cellI)
{
    result[cellI] = model->compute(cellI);  // 1M virtual calls
}

// GOOD: Batched processing
class Model
{
public:
    virtual void computeField(scalarField& result) const;  // 1 virtual call
};

model->computeField(result);  // 1 virtual call + 1M direct ops
```

**OpenFOAM Real Example:**

```cpp
// BEFORE: Per-cell virtual
class MyTransportModel
{
public:
    virtual scalar diffusivity(label cellI) const = 0;
};

void solveTransport()
{
    forAll(mesh.cells(), cellI)
    {
        scalar D = transportModel->diffusivity(cellI);  // Virtual per cell
        DEqn[cellI] = fvm::laplacian(D, T);
    }
}

// AFTER: Batched
class MyTransportModel
{
public:
    virtual const volScalarField& diffusivity() const = 0;  // Return field reference
};

void solveTransport()
{
    const volScalarField& D = transportModel->diffusivity();  // One virtual call
    DEqn = fvm::laplacian(D, T);  // Direct field operation
}
```

### 3.2 Strategy 2: Template-Based Dispatch

**Theory:** Move dispatch to compile-time, eliminating runtime v-table lookup.

**Simple Example:**

```cpp
// Runtime dispatch (virtual)
void solveVirtual(BaseModel& model)
{
    for (int i = 0; i < N; ++i)
        result[i] = model.compute(i);  // Virtual call in loop
}

// Compile-time dispatch (template)
template<class Model>
void solveTemplate(Model& model)
{
    for (int i = 0; i < N; ++i)
        result[i] = model.compute(i);  // Direct call (inlined)
}
```

**OpenFOAM Real Example:**

```cpp
// Template function for specific turbulence model
template<class TurbModel>
void solveTurbulenceEquation(TurbModel& turb)
{
    // Direct calls - compiler can optimize
    volScalarField& k = turb.k();
    volScalarField& epsilon = turb.epsilon();
    volScalarField::Internal nut = turb.nut()();
    
    // Solver code with direct field access
    tmp<fvScalarMatrix> kEqn
    (
        fvm::ddt(k)
      + fvm::div(phi, k)
      - fvm::laplacian(nut, k)
      + ...  // Direct operations, no virtual calls
    );
}

// Usage: compile-time selection
solveTurbulenceEquation(kEpsilon);  // kEpsilon type known at compile time
```

### 3.3 Strategy 3: Hybrid Approach (Virtual + Template)

**Theory:** Use virtual for high-level selection, templates for inner loops.

**OpenFOAM Pattern:**

```cpp
// Virtual interface for high-level selection
class TurbulenceModel
{
public:
    // Virtual: Called once per timestep
    virtual void correct() = 0;
    
    // Virtual: Return field reference (called once)
    virtual const volScalarField& k() const = 0;
    
    // Template: Inner loop operations (no virtual)
    template<class Type>
    tmp<GeometricField<Type, fvPatchField, volMesh>> 
    div(const GeometricField<Type, fvsPatchField, surfaceMesh>& phi) const
    {
        // Direct field operations
        return fvc::div(phi);
    }
};

// Implementation
class kEpsilon : public TurbulenceModel
{
public:
    virtual void correct() override
    {
        // One virtual call, then direct operations
        // ... (model-specific equations)
    }
    
    virtual const volScalarField& k() const override
    {
        return k_;  // Return reference (cheap)
    }
    
private:
    volScalarField k_;
    volScalarField epsilon_;
};
```

---

## 4. Profiling OpenFOAM Code: Tools and Techniques

### 4.1 Tool 1: perf (Linux)

**Installation:**
```bash
sudo apt-get install linux-tools-common linux-tools-generic
```

**Basic Usage:**
```bash
# Record profile
perf record -g --call-graph dwarf -F 99 simpleFoam

# Analyze results
perf report

# Look for specific function
perf report | grep -A 10 "virtual"
```

**Interpreting Results:**
```
Samples: 12K of event 'cycles'
  5.2%  simpleFoam  solverFoam       [.] turbulenceModel::correct()
  3.8%  simpleFoam  libturbulenceModel.so  [.] kEpsilon::correct()
  2.1%  simpleFoam  solverFoam       [.] fvMatrix::solve()
  
# If you see many virtual function calls in top 10, investigate!
```

### 4.2 Tool 2: Valgrind/Callgrind

**Usage:**
```bash
# Profile with callgrind
valgrind --tool=callgrind --callgrind-out-file=callgrind.out \
    simpleFoam -parallel

# Analyze with kcachegrind
kcachegrind callgrind.out

# Look for high-cost virtual calls
```

**Key Metrics:**
- **Ir**: Instruction reads (total work)
- **I1mr**: L1 instruction cache misses (virtual call penalty)
- **Dr**: Data reads

### 4.3 Tool 3: OpenFOAM Built-in Profiling

**Add to Code:**
```cpp
#include "cpuTime.H"

// Profile specific code section
cpuTime timer;

// Code to profile
forAll(mesh.cells(), cellI)
{
    scalar k = turbulence->k()[cellI];  // Potential virtual call
}

Info<< "Per-cell loop time: " << timer.cpuTimeIncrement() << " s" << endl;

// Compare with batched version
cpuTime timer2;
const volScalarField& kField = turbulence->k();
forAll(mesh.cells(), cellI)
{
    scalar kCell = kField[cellI];
}
Info<< "Batched loop time: " << timer2.cpuTimeIncrement() << " s" << endl;
```

### 4.4 Tool 4: Compiler Optimization Reports

**Enable optimization reporting:**
```bash
wmake -k YOUR_SOLVER
# Add to Make/options: CXXFLAGS += -Rpass=inline -Rpass-missed=inline
```

**Check for inlining:**
```
remark: function 'turbulenceModel::k()' not inlined into 'solveTransport'
  → Virtual function preventing inlining (expected)
  
remark: function 'kEpsilon::computeKField' inlined into loop
  → Good! Template-based dispatch working
```

### 4.5 Profiling Checklist

```
□ Profile with realistic case (production mesh size)
□ Compare virtual vs non-virtual versions
□ Check both single-core and parallel performance
□ Verify optimization flags (-O3 -march=native)
□ Look for hotspots with perf/callgrind
□ Measure actual wall-clock time (not just cycles)
```

---

## 5. Practical Exercise: Optimize This Code

### Problem: Slow Transport Solver

```cpp
// CURRENT CODE (SLOW)
class MyTransportModel
{
public:
    virtual scalar getDiffusivity(label cellI) const = 0;
    virtual scalar getReactionRate(label cellI) const = 0;
};

void solveTransport(MyTransportModel& model)
{
    volScalarField& T = T_;
    volScalarField& C = C_;
    
    forAll(mesh.cells(), cellI)
    {
        scalar D = model.getDiffusivity(cellI);      // Virtual #1
        scalar R = model.getReactionRate(cellI);     // Virtual #2
        
        TEqn[cellI] = fvm::laplacian(D, T) + R * C[cellI];  // BAD: Can't do this
    }
    
    TEqn.solve();
}
```

### Task: Apply Performance Optimizations

**Step 1: Identify the Issues**
- [ ] Virtual call frequency too high
- [ ] Cannot build fvMatrix cell-by-cell
- [ ] Missing field-level operations

**Step 2: Redesign the Interface**

```cpp
// BETTER DESIGN
class MyTransportModel
{
public:
    // Return field references (single virtual call)
    virtual const volScalarField& diffusivity() const = 0;
    virtual const volScalarField& reactionRate() const = 0;
    
    // Or compute entire field at once
    virtual void computeTransportCoeffs(
        volScalarField& D,
        volScalarField& R
    ) const = 0;
};
```

**Step 3: Rewrite the Solver**

```cpp
// YOUR CODE HERE
void solveTransport(MyTransportModel& model)
{
    // TODO: Implement optimized version
    // Hint: Use field operations, not cell-by-cell
}
```

**Step 4: Benchmark**

```cpp
// Test your solution
void benchmark()
{
    cpuTime timer;
    
    // Original: ~1000 ms (1M cells)
    // Your target: <50 ms
    
    solveTransport(transportModel);
    
    Info<< "Solver time: " << timer.cpuTimeIncrement() << " s" << endl;
}
```

**Expected Result:**
- Original: 1M cells × 2 virtual calls = 2M virtual calls (~1000 ms)
- Optimized: 2 virtual calls + 2M direct ops (~10-50 ms)
- **Speedup: 20-100x**

---

## 6. Key Takeaways Summary

### Performance Hierarchy

```
FASTEST → Templates (compile-time) → Field operations → Direct calls
SLOWER → Virtual (batched) → One virtual per field
SLOWEST → Virtual per cell → Avoid in inner loops!
```

### Decision Matrix

| Scenario | Recommended Approach | Rationale |
|----------|---------------------|-----------|
| Model selection | Virtual | One-time cost, flexibility needed |
| Field operations | Template | Called millions of times |
| Per-cell calculation | Direct (batched) | Avoid virtual in loops |
| Per-timestep setup | Virtual | Low frequency |
| Boundary conditions | Virtual (acceptable) | Medium-low frequency |

### Best Practices

1. **Profile first, optimize second** - Measure actual performance
2. **Batch field operations** - One virtual per field, not per cell
3. **Use templates for hot paths** - Compile-time dispatch
4. **Return field references** - Cheap virtual, cheap copy
5. **Test with realistic data** - Small cases hide problems

### Common Pitfalls

- ❌ Premature optimization without profiling
- ❌ Virtual calls in per-cell loops
- ❌ Ignoring cache effects
- ❌ Over-templating (code bloat)
- ❌ Forgetting to test in parallel

---

## Concept Check

<details>
<summary><b>1. How much slower are virtual functions compared to direct calls?</b></summary>

**Answer:** Approximately **10-20x slower per call** for cached virtual calls, and **100x+ slower** with cache misses. However, the real impact comes from amplification through iteration. For 1M cells, one virtual call per cell adds billions of cycles over a simulation.
</details>

<details>
<summary><b>2. When does virtual function overhead actually matter?</b></summary>

**Answer:** Virtual overhead matters in **tight inner loops** called millions of times (per-cell, per-face operations). It's typically acceptable for high-level operations called once per timestep (model selection, setup, I/O).
</details>

<summary><b>3. What are the three main mitigation strategies?</b></summary>

**Answer:** 
1. **Batch processing** - One virtual call per field instead of per cell
2. **Template-based dispatch** - Compile-time selection for performance-critical code
3. **Hybrid approach** - Virtual for selection, templates for implementation
</details>

<details>
<summary><b>4. How do you profile OpenFOAM code for virtual call overhead?</b></summary>

**Answer:** Use `perf record/report` on Linux, `valgrind/callgrind` for detailed call graphs, OpenFOAM's built-in `cpuTime` for targeted measurements, and compiler optimization reports to check inlining. Always profile with realistic mesh sizes.
</details>

<details>
<summary><b>5. Should you avoid virtual functions entirely in OpenFOAM?</b></summary>

**Answer:** **No!** Virtual functions are essential for runtime selection (turbulence models, boundary conditions). Use them appropriately: virtual for high-level selection, templates for performance-critical inner loops. The key is knowing **where** to use each approach.
</details>

---

## Related Documentation

- **Overview:** [00_Overview.md](00_Overview.md) - Fundamental concepts
- **Virtual Functions:** [02_Abstract_Interfaces.md](02_Abstract_Interfaces.md) - Interface design
- **Inheritance:** [03_Inheritance_Hierarchies.md](03_Inheritance_Hierarchies.md) - Hierarchy organization
- **Run-Time Selection:** [04_Run_Time_Selection_System.md](04_Run_Time_Selection_System.md) - OpenFOAM's RTS
- **Design Patterns:** [05_Design_Patterns_in_Physics.md](05_Design_Patterns_in_Physics.md) - Applied patterns
- **Common Errors:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md) - Debugging techniques

---

**Next:** Apply these concepts in [05_Design_Patterns_in_Physics.md](05_Design_Patterns_in_Physics.md) to see real-world examples of performance-aware design patterns in OpenFOAM physics models.