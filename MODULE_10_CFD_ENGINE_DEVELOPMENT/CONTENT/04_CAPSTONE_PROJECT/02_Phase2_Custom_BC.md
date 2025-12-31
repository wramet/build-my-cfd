# Phase 2: Custom Boundary Condition

Creating a Convective Heat Transfer Boundary Condition

---

## Learning Objectives

By the end of this phase, you will be able to:

- Understand and navigate the OpenFOAM boundary condition class hierarchy
- Implement a custom BC using the `mixedFvPatchField` base class
- Compile boundary conditions into shared libraries and link them to solvers
- Apply mathematical derivation to translate physical BCs into OpenFOAM implementation
- Debug common BC compilation and runtime errors

---

## What is a Convective Boundary Condition?

A convective boundary condition models heat transfer between a surface and surrounding fluid using **Newton's Law of Cooling**:

$$q'' = h(T - T_\infty)$$

At the boundary, heat flux from convection equals conductive flux:

$$-k \frac{\partial T}{\partial n} = h(T - T_\infty)$$

Where:
- $h$ = convective heat transfer coefficient [W/m²K]
- $T$ = surface temperature [K]
- $T_\infty$ = ambient temperature [K]  
- $k$ = thermal conductivity [W/mK]

**Why implement this?** OpenFOAM provides `externalWallHeatFlux` but implementing your own teaches the fundamental BC architecture used throughout OpenFOAM.

---

## Why Use mixedFvPatchField?

OpenFOAM's `mixedFvPatch` implements the generalized Robin boundary condition:

$$T_b = f \cdot T_{ref} + (1-f) \cdot T_c + \frac{g}{\delta}$$

This single form can represent:
- **Dirichlet** (fixedValue): set $f=1$, $T_b = T_{ref}$
- **Neumann** (fixedGradient): set $f=0$, $T_b = T_c + g/\delta$
- **Robin** (convective): set $0<f<1$, weighted combination

Our convective BC maps naturally to this form by deriving the proper value fraction.

---

## How to Implement: Mathematical Derivation

### From Physics to Code

**Step 1: Balance heat flux at boundary**

$$h(T_b - T_\infty) = -k \frac{T_b - T_c}{\delta}$$

**Step 2: Solve for boundary temperature $T_b$**

Expand terms:
$$h T_b - h T_\infty = -\frac{k}{\delta} T_b + \frac{k}{\delta} T_c$$

Collect $T_b$ terms:
$$T_b\left(h + \frac{k}{\delta}\right) = h T_\infty + \frac{k}{\delta} T_c$$

Solve:
$$T_b = \frac{h T_\infty + \frac{k}{\delta} T_c}{h + \frac{k}{\delta}}$$

**Step 3: Match to OpenFOAM mixed form**

$$T_b = \frac{h}{h + k/\delta} T_\infty + \frac{k/\delta}{h + k/\delta} T_c + 0$$

Therefore:
- **valueFraction** = $\frac{h}{h + k/\delta}$
- **refValue** = $T_\infty$
- **refGrad** = 0

<details>
<summary><strong>📖 Extended Derivation (Discretization Details)</strong></summary>

#### Finite Difference Approximation

Consider a boundary cell with center $P$ and boundary face $f$:

```
    |------- δ -------| ← distance from cell center to face
    Cell P            Face f (boundary)
    ●━━━━━━━━━━━━━━━━━○
    T_c                T_b
```

Using first-order finite difference:

$$\frac{\partial T}{\partial n} \approx \frac{T_b - T_c}{\delta}$$

#### Limiting Behavior Check

**Case 1: Very high h (h → ∞)**
- valueFraction → 1
- $T_b = T_\infty$ (Dirichlet/fixedValue)
- Physical: infinite convection → surface equals ambient

**Case 2: Very low h (h → 0)**
- valueFraction → 0  
- $T_b = T_c$ (zeroGradient/insulated)
- Physical: no convection → no heat flux

**Case 3: Typical values**
- h = 100, k = 1, δ = 0.01
- δCoeffs = 100
- valueFraction = 100 / (100 + 1×100) = 0.5
- $T_b = 0.5 T_\infty + 0.5 T_c$

</details>

---

## Implementation: Step-by-Step

### Step 1: Create BC Directory Structure

```bash
mkdir -p $FOAM_RUN/myConvectiveBC/Make
cd $FOAM_RUN/myConvectiveBC
```

**Required files:**
```
myConvectiveBC/
├── Make/
│   ├── files
│   └── options
├── myConvectiveFvPatchScalarField.H
└── myConvectiveFvPatchScalarField.C
```

---

### Step 2: Write Header File (.H)

<details>
<summary><strong>myConvectiveFvPatchScalarField.H</strong></summary>

```cpp
#ifndef myConvectiveFvPatchScalarField_H
#define myConvectiveFvPatchScalarField_H

#include "mixedFvPatchFields.H"

namespace Foam
{

class myConvectiveFvPatchScalarField
:
    public mixedFvPatchScalarField
{
    // Private Data

        //- Heat transfer coefficient [W/m²K]
        scalar h_;

        //- Ambient temperature [K]
        scalar Tinf_;

        //- Thermal conductivity [W/mK]
        scalar kappa_;


public:

    //- Runtime type information
    TypeName("myConvective");


    // Constructors

        //- Construct from patch and internal field
        myConvectiveFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&
        );

        //- Construct from patch, internal field and dictionary
        myConvectiveFvPatchScalarField
        (
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const dictionary&
        );

        //- Construct by mapping given onto a new patch
        myConvectiveFvPatchScalarField
        (
            const myConvectiveFvPatchScalarField&,
            const fvPatch&,
            const DimensionedField<scalar, volMesh>&,
            const fvPatchFieldMapper&
        );

        //- Construct as copy
        myConvectiveFvPatchScalarField
        (
            const myConvectiveFvPatchScalarField&
        );

        //- Construct and return a clone
        virtual tmp<fvPatchScalarField> clone() const
        {
            return tmp<fvPatchScalarField>
            (
                new myConvectiveFvPatchScalarField(*this)
            );
        }

        //- Construct as copy setting internal field reference
        myConvectiveFvPatchScalarField
        (
            const myConvectiveFvPatchScalarField&,
            const DimensionedField<scalar, volMesh>&
        );

        //- Construct and return a clone setting internal field reference
        virtual tmp<fvPatchScalarField> clone
        (
            const DimensionedField<scalar, volMesh>& iF
        ) const
        {
            return tmp<fvPatchScalarField>
            (
                new myConvectiveFvPatchScalarField(*this, iF)
            );
        }


    // Member functions

        //- Update the coefficients associated with the patch field
        virtual void updateCoeffs();

        //- Write
        virtual void write(Ostream&) const;
};


} // End namespace Foam

#endif
```

</details>

---

### Step 3: Write Implementation File (.C)

<details>
<summary><strong>myConvectiveFvPatchScalarField.C</strong></summary>

```cpp
#include "myConvectiveFvPatchScalarField.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"
#include "surfaceFields.H"

namespace Foam
{

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

myConvectiveFvPatchScalarField::myConvectiveFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF
)
:
    mixedFvPatchScalarField(p, iF),
    h_(0),
    Tinf_(0),
    kappa_(0)
{
    refValue() = 0;
    refGrad() = 0;
    valueFraction() = 0;
}


myConvectiveFvPatchScalarField::myConvectiveFvPatchScalarField
(
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const dictionary& dict
)
:
    mixedFvPatchScalarField(p, iF),
    h_(dict.get<scalar>("h")),
    Tinf_(dict.get<scalar>("Tinf")),
    kappa_(dict.get<scalar>("kappa"))
{
    refValue() = Tinf_;
    refGrad() = 0;
    valueFraction() = 0;

    if (dict.found("value"))
    {
        fvPatchScalarField::operator=
        (
            scalarField("value", dict, p.size())
        );
    }
    else
    {
        fvPatchScalarField::operator=(Tinf_);
    }
}


myConvectiveFvPatchScalarField::myConvectiveFvPatchScalarField
(
    const myConvectiveFvPatchScalarField& ptf,
    const fvPatch& p,
    const DimensionedField<scalar, volMesh>& iF,
    const fvPatchFieldMapper& mapper
)
:
    mixedFvPatchScalarField(ptf, p, iF, mapper),
    h_(ptf.h_),
    Tinf_(ptf.Tinf_),
    kappa_(ptf.kappa_)
{}


myConvectiveFvPatchScalarField::myConvectiveFvPatchScalarField
(
    const myConvectiveFvPatchScalarField& ptf
)
:
    mixedFvPatchScalarField(ptf),
    h_(ptf.h_),
    Tinf_(ptf.Tinf_),
    kappa_(ptf.kappa_)
{}


myConvectiveFvPatchScalarField::myConvectiveFvPatchScalarField
(
    const myConvectiveFvPatchScalarField& ptf,
    const DimensionedField<scalar, volMesh>& iF
)
:
    mixedFvPatchScalarField(ptf, iF),
    h_(ptf.h_),
    Tinf_(ptf.Tinf_),
    kappa_(ptf.kappa_)
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void myConvectiveFvPatchScalarField::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    // Get distance from cell center to face (OpenFOAM stores 1/δ)
    const scalarField& delta = patch().deltaCoeffs();

    // Mixed BC: T_face = valueFraction * refValue + (1-valueFraction) * T_cell
    // Derived from: -k dT/dn = h(T - Tinf)
    // Result: valueFraction = h / (h + k * deltaCoeffs)
    
    valueFraction() = h_ / (h_ + kappa_ * delta);
    refValue() = Tinf_;
    refGrad() = 0;

    mixedFvPatchScalarField::updateCoeffs();
}


void myConvectiveFvPatchScalarField::write(Ostream& os) const
{
    fvPatchScalarField::write(os);
    os.writeEntry("h", h_);
    os.writeEntry("Tinf", Tinf_);
    os.writeEntry("kappa", kappa_);
    writeEntry("value", os);
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePatchTypeField
(
    fvPatchScalarField,
    myConvectiveFvPatchScalarField
);

} // End namespace Foam
```

</details>

**🔍 Implementation Checkpoint:** Verify `updateCoeffs()` implements the derived formula correctly before proceeding.

---

### Step 4: Create Build Files

#### Make/files

```
myConvectiveFvPatchScalarField.C

LIB = $(FOAM_USER_LIBBIN)/libmyConvectiveBC
```

#### Make/options

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

LIB_LIBS = \
    -lfiniteVolume
```

---

### Step 5: Compile the BC

```bash
cd $FOAM_RUN/myConvectiveBC
wmake libso
```

**Expected output:**
```
Making dependency list for source file myConvectiveFvPatchScalarField.C
...
ls $FOAM_USER_LIBBIN/libmyConvectiveBC.so
```

**Checkpoint:** Verify library exists at `$FOAM_USER_LIBBIN/libmyConvectiveBC.so`

<details>
<summary><strong>🔧 Troubleshooting: Compilation Errors</strong></summary>

**Error: "undefined reference to vtable"**
```bash
# Symptoms:
# .so: undefined reference to 'vtable for Foam::myConvectiveFvPatchScalarField'

# Solution: Ensure ALL virtual functions are implemented
virtual void updateCoeffs();        // Required
virtual void write(Ostream&) const;  // Required
virtual tmp<fvPatchScalarField> clone() const;  // Required
```

**Error: "fatal error: mixedFvPatchFields.H: No such file"**
```bash
# Solution: Check Make/options includes finiteVolume
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
```

**Error: Template instantiation errors**
```bash
# Solution: Verify makePatchTypeField macro at end of .C file
makePatchTypeField
(
    fvPatchScalarField,
    myConvectiveFvPatchScalarField
);
```

</details>

---

### Step 6: Update Solver Makefiles

Edit `myHeatFoam/Make/options`:

```makefile
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(FOAM_USER_LIBBIN)/../myConvectiveBC

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -L$(FOAM_USER_LIBBIN) -lmyConvectiveBC
```

Recompile solver:
```bash
cd $FOAM_RUN/myHeatFoam
wmake
```

---

### Step 7: Create Test Case

**Directory structure:**
```
test_convective/
├── 0/
│   └── T
├── constant/
│   └── polyMesh/
└── system/
    ├── controlDict
    ├── fvSchemes
    └── fvSolution
```

**0/T file:**
```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 500;

boundaryField
{
    left
    {
        type            fixedValue;
        value           uniform 500;
    }
    right
    {
        type            myConvective;          // Custom BC
        h               100;                   // [W/m²K]
        Tinf            300;                   // [K]
        kappa           1;                     // [W/mK]
        value           uniform 300;
    }
    frontAndBack
    {
        type            empty;
    }
}
```

---

## Validation and Testing

### Run Test Case

```bash
cd test_convective
blockMesh
myHeatFoam
```

**Expected output checkpoint:**
```
Time = 1
diffusion epsilon = 0.01
...
```

### Check Surface Temperature

```bash
postProcess -func "patchAverage(name=right, T)"
cat postProcessing/patchAverage/0/right_T.dat
```

**Expected behavior:**
- Initial T = 500 K (hot left boundary)
- Right surface cools toward 300 K ambient
- Steady state depends on h/k ratio

<details>
<summary><strong>🔍 Detailed Validation: Energy Balance Check</strong></summary>

**At steady state:**
- Conductive flux = Convective flux
- $-k \frac{dT}{dx} = h(T_{surface} - T_{\infty})$

**Check with postProcess:**
```bash
# Get temperature gradient at right patch
postProcess -func "grad(T)"

# Sample near right boundary
sample -surface -sampleDict system/sampleDict
```

**Analytical solution for 1D:**
$$T(x) = T_{\infty} + (T_L - T_{\infty})\frac{1 + Bi(x/L)}{1 + Bi}$$

Where $Bi = hL/k$ (Biot number)

</details>

<details>
<summary><strong>🔧 Runtime Debugging Checklist</strong></summary>

**Problem 1: "Unknown boundary patch type myConvective"**
```
--> FOAM FATAL IO ERROR:
Unknown boundary patch type myConvective
Valid patch types: (fixedValue fixedGradient ...)
```
**Solution:**
1. Check TypeName in .H: `TypeName("myConvective");`
2. Check type in 0/T: `type myConvective;`
3. Verify makePatchTypeField macro in .C
4. Ensure library compiled successfully

**Problem 2: "cannot open shared object file"**
```
myHeatFoam: error while loading shared libraries:
libmyConvectiveBC.so: cannot open shared object file
```
**Solution:**
```bash
# Check library exists
ls $FOAM_USER_LIBBIN/libmyConvectiveBC.so

# Check Make/options in solver has:
EXE_LIBS = -L$(FOAM_USER_LIBBIN) -lmyConvectiveBC

# Rebuild solver
cd $FOAM_RUN/myHeatFoam && wmake
```

**Problem 3: Temperature oscillation**
```
Time = 1, right patch T = 450 K
Time = 2, right patch T = 320 K
Time = 3, right patch T = 430 K
```
**Solution:**
```bash
# Reduce time step for stability
deltaT  0.001;  # Was 0.01

# Add solver relaxation
system/fvSolution:
solvers
{
    T
    {
        solver          PCG;
        tolerance       1e-06;
        relTol          0.01;
    }
}
```

**Problem 4: Incorrect heat flux**
```bash
# Add debug output to updateCoeffs():
if (Pstream::master() && this->size() > 0)
{
    Info<< "myConvective BC:" << nl
        << "  h = " << h_ << nl
        << "  kappa = " << kappa_ << nl
        << "  delta[0] = " << delta[0] << nl
        << "  valueFraction[0] = " << (h_ / (h_ + kappa_ * delta[0])) << endl;
}
```

**Check:**
- valueFraction should be between 0 and 1
- For h=100, k=1, δ=0.01: valueFraction = 0.5

</details>

---

## Practical Debugging Worksheet

Use this checklist when BC fails:

| Symptom | Check | Command |
|---------|-------|---------|
| Compilation error | All virtual functions implemented? | `grep "virtual" *.H` |
| Linking error | Library path correct? | `ls $FOAM_USER_LIBBIN/lib*.so` |
| Runtime error | TypeName matches dictionary? | `grep TypeName *.H` |
| Wrong values | updateCoeffs() formula correct? | Add debug Info<< |
| Instability | Time step too large? | Reduce deltaT |

---

## Extensions

### Exercise 1: Time-Varying Ambient Temperature

```cpp
// In .H, add:
autoPtr<Function1<scalar>> TinfFunction_;

// In constructor dict:
TinfFunction_ = Function1<scalar>::New("Tinf", dict);

// In updateCoeffs():
scalar TinfNow = TinfFunction_->value(this->db().time().timeOutputValue());
refValue() = TinfNow;
```

### Exercise 2: Spatially-Varying h

Read h from a `volScalarField`:
```cpp
// In updateCoeffs():
const volScalarField& hField = 
    db().lookupObject<volScalarField>("hField");
```

### Exercise 3: Add Radiation Term

$$q'' = h(T - T_\infty) + \epsilon \sigma (T^4 - T_{\infty}^4)$$

Requires nonlinear iteration (linearize $T^4$ ≈ $4T_{ref}^3(T - T_{ref})$).

---

## Key Takeaways

- **mixedFvPatchField** is the universal BC base class for Robin-type conditions
- Derive **valueFraction**, **refValue**, and **refGrad** from first principles
- BC class hierarchy: `fvPatchField` → `mixedFvPatchField` → custom BC
- **Runtime selection**: `TypeName` + `makePatchTypeField` macro enable dictionary loading
- Always test limiting behavior (h→0, h→∞) to verify implementation
- Debug BCs by printing `updateCoeffs()` values on first iteration

---

## Deliverables Checklist

- [ ] Compiled `libmyConvectiveBC.so` at `$FOAM_USER_LIBBIN`
- [ ] Modified `myHeatFoam` Make/options linking the library
- [ ] Test case `0/T` using `type myConvective`
- [ ] Validation showing surface temperature approaching expected steady state
- [ ] Debug worksheet with observed values

---

## Next Phase

Proceed to [Phase 3: Add Turbulence Model](03_Phase3_Turbulence_Model.md) to implement a k-epsilon turbulence model from scratch.