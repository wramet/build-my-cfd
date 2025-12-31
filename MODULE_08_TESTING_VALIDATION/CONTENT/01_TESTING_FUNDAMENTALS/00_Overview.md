# Testing Fundamentals - Overview

ภาพรวมพื้นฐานการทดสอบ (Testing Fundamentals)

---

## Learning Objectives

After studying this overview, you will be able to:

| Objective | Action Verb |
|:---|:---:|
| Define and distinguish verification from validation | **Distinguish** |
| Identify the four levels of testing hierarchy | **Identify** |
| Select appropriate testing strategies for OpenFOAM development | **Select** |
| Apply testing workflows to catch bugs early in development | **Apply** |
| Design a comprehensive testing plan for CFD simulations | **Design** |

---

## Prerequisites

**Required Knowledge:**
- Basic understanding of OpenFOAM case structure (`0/`, `constant/`, `system/`)
- Familiarity with C++ programming fundamentals
- Elementary knowledge of partial differential equations (PDEs)

**Helpful Background:**
- Experience running basic OpenFOAM solvers (`simpleFoam`, `interFoam`)
- Exposure to software development practices
- Understanding of numerical methods (discretization, convergence)

---

## The 3W Framework: Testing in OpenFOAM

### What: Formal Definition and Mathematical Context

**Testing** encompasses two distinct but complementary activities:

**Verification** (Mathematical Correctness):
- **Definition:** The process of determining whether a model implementation accurately represents the developer's conceptual description and the solution to the model
- **Mathematical Context:** Solves the equations correctly → Checks numerical accuracy and code correctness
- **Formal Statement:** "Are we solving the equations **right**?"
- **Scope:** Discretization schemes (`system/fvSchemes`), linear solvers (`system/fvSolution`), algorithmic implementation

**Validation** (Physical Realism):
- **Definition:** The process of determining the degree to which a model is an accurate representation of the real world
- **Mathematical Context:** Solves the right equations → Checks physics accuracy against experimental data
- **Formal Statement:** "Are we solving the **right** equations?"
- **Scope:** Physical models (`0/` fields), boundary conditions (`constant/polyMesh`), turbulence models, experimental benchmarking

> **Key Insight:** Verification confirms the mathematics is implemented correctly; validation confirms the mathematics represents reality accurately.

### Why: Consequences of Inadequate Testing

**Without Verification:**
- **Failed Simulations:** Code silently produces incorrect results due to discretization errors, solver tolerances, or boundary condition implementation bugs
- **Wasted Compute Resources:** Running 1000-core simulations for days only to discover results are numerically wrong
- **False Confidence:** Plots look "reasonable" but contain non-physical artifacts from implementation errors
- **Example:** A turbulence model bug producing 15% error in wall shear stress—undetectable without systematic verification

**Without Validation:**
- **Physics Mismatch:** Correctly solved equations that don't represent actual flow physics (e.g., using k-ε in laminar regime)
- **Experimental Discrepancy:** Results diverge from wind tunnel measurements by orders of magnitude
- **Design Failures:** Engineering decisions based on non-predictive simulations lead to product failures
- **Example:** RANS simulation correctly solving equations but missing separation bubble due to inadequate turbulence modeling

**Economic Impact:**
- Typical CFD project: 70% computation, 20% pre-processing, **10% testing** (should be 30%)
- Cost of finding bug: Unit test stage = $100; System test = $1,000; Post-validation = $10,000+

### How: Specific OpenFOAM Workflow

**Step 1: Unit Testing (Function-Level)**
```bash
# Test individual OpenFOAM classes
cd $FOAM_SRC/OpenFOAM/meshes/polyMesh
wmakeTest
./testPolyMesh
```
- **Scope:** Single functions (e.g., `vector::operator^()`, `fvMesh::cellCentres()`)
- **Time:** Seconds per test
- **Tools:** OpenFOAM test framework, Google Test (see Module 03)

**Step 2: Integration Testing (Component-Level)**
```bash
# Test component interactions
cd test/integration
./testFvMeshWithFields
```
- **Scope:** Multiple classes working together (e.g., `fvMesh` + `volScalarField` + `boundaryConditions`)
- **Time:** Minutes per test
- **Tools:** Custom test suites, fixture setups

**Step 3: System Testing (Case-Level)**
```bash
# Run complete solver on known solution
cd tutorials/incompressible/simpleFoam/pitzDaily
blockMesh
simpleFoam
# Compare against reference solution
foamDictionary system/controlDict -entry endTime -set 1000
```
- **Scope:** Full solver runs on tutorial/benchmark cases
- **Time:** Hours per test
- **Tools:** Tutorial cases, regression test scripts

**Step 4: Validation (Physics-Level)**
```bash
# Compare with experimental data
cd validation/ahmedBody
runSimulation
postProcess/compareWithExperiment.py
```
- **Scope:** Compare simulation results with wind tunnel/PIV measurements
- **Time:** Days to weeks
- **Tools:** Benchmark databases (e.g., ERCOFTAC, NACA), experimental datasets

**Continuous Integration Integration:**
```yaml
# .github/workflows/test.yml (automated on every commit)
name: OpenFOAM Tests
on: [push]
jobs:
  verification:
    - runs unit tests
    - runs grid convergence study
  validation:
    - runs benchmark cases
    - compares with reference data
```

---

## When to Use This Method: Decision Guide

| Scenario | Recommended Testing | Example |
|:---|:---|:---|
| **Developing new turbulence model** | Verification (MMS) + Validation (benchmark) | k-omega SST variant → Test on flat plate (verification) + airfoil (validation) |
| **Debugging solver crash** | Unit Tests → Integration Tests | Isolate failing function → Test mesh/field interaction |
| **Validating new boundary condition** | System Test + Validation | Custom inlet profile → Test on pipe flow (system) + compare with experiment |
| **Optimizing solver performance** | Profiling + Regression Testing | Faster linear solver → Profile speedup + ensure results unchanged |
| **Production simulation** | Full V&V suite | Industrial case → Unit + integration + system + validation before trusting results |
| **Code refactoring** | Regression Tests only | Restructure code → Run full test suite to ensure no behavior change |

**Testing Pyramid Strategy:**
- **60% Unit Tests:** Fast, isolated function testing (catch bugs early)
- **20% Integration Tests:** Component interaction validation
- **15% System Tests:** End-to-end solver validation
- **5% Validation:** Physics comparison with experiments

---

## Testing Levels (ปิรามิดการทดสอบ)

```
         ▲ Validation (5%)
        /  \    - Compare with experiment
       /----\   - Benchmark cases
      /------\
     / System Tests (15%)\ - Full solver runs
    /---------------------\
   / Integration Tests (20%)\ - Component interaction
  /----------------------------\
/     Unit Tests (60%)         \ - Function tests
--------------------------------
```

| Level | Scope | OpenFOAM Example | Time | Bug Detection Cost |
|:---|:---|:---|:---:|:---:|
| **Unit** | Single function | Test `vector::operator^()` | Seconds | $1 |
| **Integration** | Components | Test `fvMesh` + `volScalarField` | Minutes | $10 |
| **System** | Full Case | Run `simpleFoam` on tutorial | Hours | $100 |
| **Validation** | Physics | Compare with wind tunnel data | Days | $1,000+ |

> **Thai Memory Aid (จำง่ายๆ):** Verification = Math Check (แก้สมการถูกไหม?) | Validation = Physics Check (ใช้สมการถูกไหม?)

---

## Module Structure

| Folder | Topic | Content | Key Deliverables |
|:---|:---|:---|:---|
| **02_VERIFICATION** | Code correctness | MMS, Grid Convergence, GCI | Formal error estimates, grid convergence studies |
| **03_TEST_FRAMEWORK** | Coding tests | Unit Tests, Integration, Automation | Reusable test infrastructure, CI/CD pipeline |
| **04_VALIDATION** | Physics accuracy | Benchmarks, Experimental comparison | Validation reports, uncertainty quantification |
| **05_QA_AUTOMATION** | CI/profiling | Regression Testing, Performance Profiling | Automated testing workflows, performance dashboards |

**Learning Path:**
1. **Start Here:** Understand testing fundamentals (current document)
2. **Then:** Learn verification methods (MMS, grid convergence) in Module 02
3. **Next:** Build test framework in Module 03
4. **Apply:** Validate against experiments in Module 04
5. **Automate:** Set up CI/CD and profiling in Module 05

---

## Cross-References

**Within Testing Module:**
- **Verification Fundamentals:** [../02_VERIFICATION_FUNDAMENTALS/00_Overview.md](../02_VERIFICATION_FUNDAMENTALS/00_Overview.md) → MMS, GCI, grid convergence
- **Test Framework:** [../03_TEST_FRAMEWORK_CODING/00_Overview.md](../03_TEST_FRAMEWORK_CODING/00_Overview.md) → Unit tests, mocking, CI/CD
- **Validation:** [../04_VALIDATION_BENCHMARKS/00_Overview.md](../04_VALIDATION_BENCHMARKS/00_Overview.md) → Benchmark databases, experimental comparison
- **QA Automation:** [../05_QA_AUTOMATION_PROFILING/00_Overview.md](../05_QA_AUTOMATION_PROFILING/00_Overview.md) → Regression testing, profiling tools

**Related Modules:**
- **OpenFOAM Programming:** [../../../MODULE_05_OPENFOAM_PROGRAMMING/00_Overview.md](../../../MODULE_05_OPENFOAM_PROGRAMMING/00_Overview.md) → Understanding code structure for testing
- **CFD Fundamentals:** [../../../MODULE_01_CFD_FUNDAMENTALS/00_Overview.md](../../../MODULE_01_CFD_FUNDAMENTALS/00_Overview.md) → Governing equations for verification

---

## Concept Check

<details>
<summary><b>1. What is the difference between verification and validation?</b></summary>

- **Verification:** Code does math right (แก้สมการถูกไหม?) → Checks numerical accuracy, discretization, solver implementation
- **Validation:** Results match reality (ใช้สมการถูกไหม?) → Checks physics accuracy against experiments
- **Key:** Verification = solve equations right; Validation = solve right equations
</details>

<details>
<summary><b>2. What is a unit test in OpenFOAM context?</b></summary>

**Test single function/class** in isolation (e.g., `vector::operator^()`, `fvMesh::cellCentres()`)

- **Scope:** Individual functions/methods
- **Speed:** Seconds
- **Example:** Test cross product calculation returns correct vector magnitude
</details>

<details>
<summary><b>3. Why automate testing?</b></summary>

**Consistent, reproducible** testing on every change

- **Catch bugs early:** Unit tests find issues before integration
- **Prevent regressions:** Automated tests catch breaking changes immediately
- **Enable confident refactoring:** Test suite ensures code behavior unchanged
- **CI/CD integration:** Tests run automatically on every commit/PR
</details>

<details>
<summary><b>4. When should you use verification vs validation?</b></summary>

**Use Verification when:**
- Implementing new numerical scheme
- Debugging solver convergence issues
- Comparing solver versions
- Estimating numerical errors (GCI)

**Use Validation when:**
- Selecting turbulence model for application
- Comparing with experimental measurements
- Establishing simulation credibility for design decisions
- Publishing results requiring physics verification

**Both needed:** Complete V&V requires verification (math correct) + validation (physics correct)
</details>

---

## Key Takeaways

✓ **Testing = Verification + Validation:** Verification confirms numerical correctness; validation confirms physical realism (Roache's dual criteria)

✓ **Test Pyramid Strategy:** 60% unit tests (fast, catch bugs early) → 20% integration → 15% system → 5% validation (expensive but essential)

✓ **Economic Case:** Bug found at unit test stage = $100; same bug found post-validation = $10,000+ (100× cost increase)

✓ **OpenFOAM Workflow:** Unit tests (seconds) → Integration tests (minutes) → System tests (hours) → Validation (days) → CI/CD automation

✓ **Complete V&V Required:** For production simulations, always perform both verification (grid convergence, MMS) AND validation (benchmark comparison) before trusting results