# Test Framework Coding - Overview

ภาพรวมกรอบการทดสอบ (Test Framework)

---

## Learning Objectives

After completing this module, you will be able to:

- **Identify** the three levels of testing in OpenFOAM (Unit, Integration, System) and understand when to apply each
- **Design** test directory structures for both unit tests and system tests
- **Implement** automated test scripts using the Allrun pattern with validation
- **Choose** appropriate testing tools and approaches for different validation scenarios

---

## 1. What is Test Framework?

> **Test Framework** = Framework สำหรับ testing OpenFOAM code

### WHAT (Definition)
A test framework provides systematic methods to verify that your OpenFOAM code works correctly at different levels:

- **Unit Tests**: Validate individual functions and methods
- **Integration Tests**: Verify components work together properly  
- **System Tests**: Confirm complete solver runs produce expected results

### WHY (Benefits)
- **Early bug detection**: Catch issues during development before they propagate
- **Confidence in changes**: Refactor or modify code with assurance tests will catch regressions
- **Documentation**: Tests serve as executable examples of how code should be used
- **Debugging efficiency**: Isolated tests pinpoint problem areas quickly
- **Quality assurance**: Ensure physics and numerics remain correct over time

### HOW (Implementation)
OpenFOAM testing combines:
- Custom test executables for unit testing
- Tutorial-style cases for integration and system testing
- Shell scripts (Allrun/Allclean) for automation
- Reference solutions for validation comparison

---

## 2. Testing Levels Pyramid

```
        ▲ System Tests (10%)
       /  \    - Complete solver runs
      /----\   - Full case validation
     /------\
    / Integration \  Integration Tests (20%)
   /----------------\ - Component interaction
  /   Unit Tests (70%)  \ - Function tests
/------------------------\ - Class tests
```

### Testing Level Comparison

| Level | Scope | What It Tests | Tool | When to Use |
|:---|:---|:---|:---|:---|
| **Unit** | Single function/class | Individual algorithms, boundary conditions, mathematical operations | Custom test executables | During development of new classes/functions |
| **Integration** | Multiple components | Component interaction, mesh-model coupling, solver-model integration | Test cases with mesh + models | After combining multiple components |
| **System** | Complete solver/case | End-to-end workflow, convergence, physical correctness | Allrun/Allclean scripts | Before releasing solver or case |

### Progressive Testing Strategy

The pyramid structure reflects testing frequency and importance:

1. **Unit tests (70%)**: Fast, isolated, run frequently during development
2. **Integration tests (20%)**: Moderate speed, verify component interactions
3. **System tests (10%)**: Slower but comprehensive, validate complete workflows

This approach ensures bugs are caught early at the level where they're cheapest to fix.

---

## 3. Test Directory Structure

### Unit Test Structure

**Purpose**: Test individual functions or classes in isolation

```
tests/unit/
├── Test_vector.C          # Test source code - contains test cases
├── Make/
│   ├── files              # Source files list (e.g., Test_vector.C)
│   └── options            # Compiler flags and dependencies
└── Test_vector            # Compiled executable
```

**Component Explanations**:

- **Test_vector.C**: Contains test code using OpenFOAM's testing macros (e.g., `assert`, `EXPECT`)
- **Make/files**: Lists source files to compile (similar to solver compilation)
- **Make/options**: Specifies compilation flags, EXE_INC (include paths), and LIB_LIBS (libraries to link)
- **Test_vector executable**: Compiled binary that runs when executing tests

**When to use**: Testing mathematical functions, boundary condition implementations, utility classes

### System Test Structure

**Purpose**: Validate complete solver runs with realistic cases

```
tutorials/test_case/
├── Allrun                 # Main test script - runs solver and validates results
├── Allclean               # Cleanup script - removes generated files
├── system/                # OpenFOAM settings (controlDict, fvSchemes, etc.)
├── constant/              # Mesh (polyMesh) and physical properties
├── 0/                     # Initial and boundary conditions
└── expected/              # Reference/benchmark results for comparison
```

**Component Explanations**:

- **Allrun**: Orchestrates the test workflow (mesh generation → solver execution → validation)
- **Allclean**: Removes generated files to enable clean test re-runs
- **system/**: OpenFOAM configuration dictionaries controlling numerics and solver settings
- **constant/**: Mesh and time-independent physical properties
- **0/**: Initial field values and boundary condition definitions
- **expected/**: Known good solutions (experimental data, analytical solutions, or verified numerical results)

**When to use**: Validating new solvers, verifying case setup, regression testing

---

## 4. Allrun Pattern Implementation

### WHAT (Definition)
The Allrun pattern is a standardized shell script template that automates test execution and validation.

### WHY (Benefits)
- **Reproducibility**: Same test runs identically every time
- **Automation**: Enables continuous integration and batch testing
- **Clear reporting**: Immediate pass/fail feedback
- **Easy debugging**: Scripted steps are traceable and debuggable

### HOW (Implementation)

```bash
#!/bin/bash
# Change to test directory (handles script execution from any location)
cd ${0%/*} || exit 1

# Load OpenFOAM helper functions (runApplication, etc.)
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# === Test Execution Phase ===
runApplication blockMesh      # Generate mesh
runApplication simpleFoam     # Run solver

# === Validation Phase ===
# Compare results with expected/benchmark data
if diff -q expected/p postProcessing/p > /dev/null; then
    echo "PASSED"
else
    echo "FAILED"
    exit 1
fi
```

**Key Components**:

1. **Directory navigation** (`cd ${0%/*}`): Ensures script runs from test directory location
2. **RunFunctions loading**: Provides `runApplication` helper that handles:
   - Logging output to log files
   - Error checking and exit on failure
   - Parallel execution support
3. **Test execution**: Sequential commands to run mesh generation and solver
4. **Validation**: Diff comparison against reference results
5. **Exit codes**: Returns 0 (pass) or 1 (fail) for CI/CD integration

**Advanced Validation Options**:

```bash
# Numerical tolerance check (for floating-point results)
if [[ $(awk 'BEGIN {print ($1 < 0.001)}' <<<"$error") -eq 1 ]]; then
    echo "PASSED"
fi

# Multi-file validation
for file in expected/*.csv; do
    diff -q "$file" "postProcessing/$(basename $file)" || exit 1
done
```

---

## 5. Module Contents

| File | Topic | Skill Level | Lines | Focus |
|:---|:---|:---:|:---:|:---|
| **01_Unit_Testing** | Function tests | ⭐⭐ | ~160 | Writing test cases for individual functions |
| **02_Validation** | Physics checks | ⭐⭐⭐ | ~160 | Comparing with analytical/experimental data |
| **03_Automation** | Scripts | ⭐⭐⭐⭐ | ~164 | CI/CD integration and batch testing |

**Recommended Learning Path**:
1. Start with **Unit Testing** (01) → Learn test-writing fundamentals
2. Progress to **Validation** (02) → Understand physics verification methods
3. Advance to **Automation** (03) → Build complete testing infrastructure

---

## 6. Quick Reference

| Test Type | Use Case | Tool | Execution Time | Run Frequency |
|:---|:---|:---|:---|:---|
| **Unit** | Single function/class validation | Custom executable | Seconds | Every code change |
| **Integration** | Component interaction | Test with mesh | Minutes | After component updates |
| **System** | Full case validation | Allrun script | Minutes-hours | Before commits/releases |
| **Validation** | Physics verification | Compare with experiment | Hours-days | For new physics models |

---

## Key Takeaways

✅ **Testing pyramid**: 70% unit tests, 20% integration tests, 10% system tests provides optimal efficiency

✅ **Test structure**: Unit tests use executables with Make/ system; system tests use tutorial-style directories with Allrun scripts

✅ **Allrun pattern**: Standardized script template enables automated, reproducible testing with validation

✅ **expected/ directory**: Critical for regression testing - stores reference solutions for comparison

✅ **Progressive approach**: Start with unit tests during development, add integration tests when combining components, use system tests for final validation

---

## Concept Check

<details>
<summary><b>1. What is the difference between unit and system tests?</b></summary>

- **Unit Tests**: Test individual functions or classes in isolation (e.g., a turbulence model function, a boundary condition calculation)
  - Fast execution (seconds)
  - No mesh or case setup required
  - Written as C++ test executables
  
- **System Tests**: Test complete solver runs with full cases
  - Longer execution (minutes to hours)
  - Include mesh, boundary conditions, solver
  - Written as Allrun scripts with case directories
</details>

<details>
<summary><b>2. What does the Allrun script do?</b></summary>

**Allrun** orchestrates the complete test workflow:

1. **Setup**: Changes to test directory
2. **Execution**: Runs mesh generation (blockMesh) and solver (simpleFoam)
3. **Validation**: Compares results against expected/ reference data
4. **Reporting**: Returns PASSED/FAILED status with appropriate exit codes

This enables automated testing in CI/CD pipelines.
</details>

<details>
<summary><b>3. What is the purpose of the expected/ directory?</b></summary>

The **expected/** directory stores reference/benchmark results:

- **Analytical solutions**: Exact mathematical results (e.g., manufactured solutions)
- **Experimental data**: Physical measurements from literature or experiments
- **Verified numerical results**: Previously validated solver outputs

During testing, current solver outputs are compared against these expected results to detect:
- Code regressions (bugs introduced by changes)
- Convergence issues (solver not reaching correct solution)
- Physics errors (incorrect boundary conditions, models)

</details>

<details>
<summary><b>4. When should you write unit tests vs integration tests?</b></summary>

**Write unit tests when**:
- Developing new functions or classes
- Implementing mathematical algorithms
- Creating boundary conditions or source terms
- Need rapid feedback during development

**Write integration tests when**:
- Combining multiple components (e.g., mesh + solver + turbulence model)
- Testing data flow between modules
- Verifying API compatibility between classes
- Need to validate component interactions beyond individual unit tests

</details>

---

## Related Documents

**Test Framework** (this module):
- **Unit Testing:** [01_Unit_Testing.md](01_Unit_Testing.md) - Writing test cases for individual functions and classes
- **Validation:** [02_Validation_Coding.md](02_Validation_Coding.md) - Physics verification methods and comparison techniques
- **Automation:** [03_Automation_Scripts.md](03_Automation_Scripts.md) - CI/CD integration and batch testing infrastructure

**Related Concepts**:
- **Verification Fundamentals** ([MODULE_08](../)) - Method of Manufactured Solutions, Richardson Extrapolation
- **Python Automation** ([MODULE_07/06](../../07_UTILITIES_AUTOMATION/CONTENT/06_EXPERT_UTILITIES)) - Scripting techniques for test automation
- **OpenFOAM Programming** ([MODULE_05](../../05_OPENFOAM_PROGRAMMING)) - Creating testable code architecture