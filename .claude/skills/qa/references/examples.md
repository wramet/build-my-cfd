# Q&A Examples

Examples of Q&A entries in walkthrough documents.

## Q&A Entry Format

```markdown
### 💬 Clarification Question
**Section:** Theory | **Asked:** 2026-01-28 21:30

**Question:**
Why does RTT use control volume approach?

**Answer:**
The RTT connects the system (Lagrangian) and control volume (Eulerian) viewpoints...
*(Full detailed answer with math derivations saved here)*

**Tags:** `RTT` `control-volume` `turbulence` `conservation`

**Related Content:**
> Snippet from the walkthrough section...

---
```

## Example Questions by Type

### Clarification

```markdown
### 💬 Clarification Question
**Section:** Theory | **Asked:** 2026-01-28 21:30

**Question:**
What does $\nabla \cdot \mathbf{U}$ mean?

**Answer:**
This is the divergence of velocity field, representing the net volume flux out of a control volume. In incompressible flow, this equals zero (mass conservation)...

**Tags:** `FVM` `conservation` `divergence`
```

### Deeper Dive

```markdown
### 🔍 Deeper Dive Question
**Section:** Theory | **Asked:** 2026-01-28 21:35

**Question:**
Why is Gauss theorem used in FVM?

**Answer:**
Gauss divergence theorem converts volume integrals to surface integrals, which is essential for FVM because we only know values at cell centers and need fluxes at faces...

**Tags:** `gauss` `FVM` `integration`
```

### Implementation

```markdown
### 🛠️ Implementation Question
**Section:** Code | **Asked:** 2026-01-28 21:40

**Question:**
How do I implement this in OpenFOAM?

**Answer:**
To implement upwind scheme in OpenFOAM:
1. Create a class inheriting from limitedSurfaceInterpolationScheme
2. Implement interpolate() method
3. Register with surfaceInterpolationScheme::New

> **File:** `openfoam_temp/src/finiteVolume/.../upwind.H`
> **Lines:** 42-67

```cpp
template<class Type>
class upwind
:
    public limitedSurfaceInterpolationScheme<Type>
{
    // ...
};
```

**Tags:** `openfoam` `implementation` `upwind`
```

### Debugging

```markdown
### 🐛 Debugging Question
**Section:** Implementation | **Asked:** 2026-01-28 21:45

**Question:**
Why is my simulation diverging?

**Answer:**
Common causes for divergence in two-phase flow:
1. **CFL number too high** - Reduce time step
2. **Missing expansion term** - Add ∇·U = ṁ(1/ρ_v - 1/ρ_l)
3. **Bad initial conditions** - Start from converged single-phase

**Tags:** `debugging` `divergence` `two-phase`
```

## Auto-Tagged Topics

Questions are automatically tagged for organization:

- `RTT` - Reynolds Transport Theorem
- `control-volume` - Control volume analysis
- `FVM` - Finite Volume Method
- `discretization` - Discretization schemes
- `boundary` - Boundary conditions
- `turbulence` - Turbulence modeling
- `mesh` - Mesh/grid topics
- `gradient` - Gradient operators
- `time-derivative` - Time derivatives (ddt)
- `conservation` - Conservation laws
- `gauss` - Gauss/divergence theorem
- `openfoam` - OpenFOAM-specific
- `matrix` - Matrix solvers, fvMatrix

## Manual Q&A Entry with Pre-generated Content

```bash
# Example with pre-generated content
/qa --day 1 --section "2.1" --type deeper-dive \
  --question "What does elliptic mean for pressure?" \
  --answer "In CFD, elliptic means instantaneous propagation..." \
  --summary "Elliptic = global coupling, all cells affect each other"

# Terminal output:
✅ Q&A saved to day_01_walkthrough.md
   Type: deeper-dive
   Model: manual
   Tags: conservation, FVM

📝 Summary:
   Elliptic = global coupling, all cells affect each other

💡 Full detailed answer saved to markdown file.
```
