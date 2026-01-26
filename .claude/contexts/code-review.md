# Code Review Mode

You are in **Code Review Mode** for OpenFOAM C++ code.

## Mode Priority

1. **OpenFOAM Patterns:** Follow conventions
2. **Memory Safety:** Proper use of tmp<>, autoPtr<>
3. **Style:** 4-space indent, camelCase naming

## Active Agents

| Agent | Model | Backend | Purpose |
|-------|-------|---------|---------|
| **engineer** | deepseek-chat | DeepSeek | Code analysis |
| **architect** | glm-4.7 | Z.ai | Design review |

## OpenFOAM Coding Standards

### Indentation and Naming
```cpp
// ✅ Good
Info << "Processing field: " << fieldName << nl;
volScalarField T(mesh, dimensionedScalar(dimSet, 1));

// ❌ Bad
std::cout<<"Processing field: "<<fieldName;
```

### Memory Management
```cpp
// ✅ Good
tmp<volScalarField> tT(new volScalarField(mesh, dimSet, 1));
// tT automatically deleted

// ❌ Bad
volScalarField* T = new volScalarField(mesh, dimSet, 1);
delete T;  // Easy to forget
```

### Field Access
```cpp
// ✅ Good
U.boundaryFieldRef().updateCoeffs();

// ❌ Bad
U.boundaryField()[patchI].correctBoundaryConditions();
```

## Common Issues to Catch

1. **Memory leaks** - Missing delete or smart pointer misuse
2. **Const correctness** - Missing const on methods that should be const
3. **Reference vs copy** - Unnecessary copies of large fields
4. **Boundary conditions** - Forgetting to update BCs after solve
5. **Dimension inconsistency** - Wrong dimensions for physics

## Review Checklist

- [ ] Uses OpenFOAM naming conventions
- [ ] Proper memory management (tmp<>, autoPtr<>)
- [ ] Const correctness
- [ ] Efficient field access (ref where possible)
- [ ] BCs updated after modifications
- [ ] Dimensions consistent with physics
- [ ] Includes proper header includes
- [ ] No hardcoded dimensions (use dimensionSet)

## Example Review

**Input:**
```cpp
void solve()
{
    U = solve(U Eqn);
}
```

**Review:**
```
❌ Issues:
1. Return type missing
2. Reference not captured efficiently
3. No BC update

✅ Better:
tmp<fvVectorMatrix> UEqn(fvm::div(phi, U) + turbulence->divDevReff(U), U);
solve(UEqn == -fvc::grad(p));
U.correctBoundaryConditions();
```

## Commands

### Quick Review
```bash
/delegate engineer "Review this code for OpenFOAM best practices"
```

### Deep Analysis
```bash
/delegate architect "Analyze the class structure of this solver"
```

### Fix Issues
```bash
/delegate engineer "Refactor this code to follow OpenFOAM patterns"
```
