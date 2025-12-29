# Phase 2: Custom Boundary Condition

สร้าง Convective Heat Transfer BC

---

## Objective

> **สร้าง `myConvectiveFvPatchScalarField`** สำหรับ convective heat transfer

$$q'' = h(T - T_\infty)$$

ที่ boundary: $-k \frac{\partial T}{\partial n} = h(T - T_\infty)$

---

## เป้าหมายการเรียนรู้

- เข้าใจ BC class hierarchy
- Implement `mixedFvPatchField`
- Compile boundary condition เป็น library

---

## Mathematical Background

### From Physics to OpenFOAM Implementation

#### Newton's Law of Cooling

At the boundary, heat flux from convection equals heat flux by conduction:

$$q''_{convection} = q''_{conduction}$$

$$h(T_s - T_\infty) = -k \frac{\partial T}{\partial n}$$

Where:
- $h$ = heat transfer coefficient [W/m²K]
- $T_s$ = surface (boundary) temperature [K]
- $T_\infty$ = ambient temperature [K]
- $k$ = thermal conductivity [W/mK]
- $\frac{\partial T}{\partial n}$ = temperature gradient normal to wall

#### Discretization at Boundary Face

Consider a boundary cell with center $P$ and boundary face $f$:

```
    |------- δ -------| ← distance from cell center to face
    Cell P            Face f (boundary)
    ●━━━━━━━━━━━━━━━━━○
    T_c                T_b
```

Using finite difference approximation:

$$\frac{\partial T}{\partial n} \approx \frac{T_b - T_c}{\delta}$$

Substitute into Newton's law:

$$h(T_b - T_\infty) = -k \frac{T_b - T_c}{\delta}$$

#### Solve for Boundary Temperature $T_b$

Expand:
$$h T_b - h T_\infty = -\frac{k}{\delta} T_b + \frac{k}{\delta} T_c$$

Collect $T_b$ terms:
$$h T_b + \frac{k}{\delta} T_b = h T_\infty + \frac{k}{\delta} T_c$$

Factor:
$$T_b \left(h + \frac{k}{\delta}\right) = h T_\infty + \frac{k}{\delta} T_c$$

Solve:
$$T_b = \frac{h T_\infty + \frac{k}{\delta} T_c}{h + \frac{k}{\delta}}$$

#### Rewrite in OpenFOAM Mixed Form

OpenFOAM's `mixedFvPatch` uses:

$$T_b = \text{valueFraction} \times \text{refValue} + (1 - \text{valueFraction}) \times T_c + \frac{\text{refGrad}}{\delta}$$

Match with our equation:

$$T_b = \frac{h}{h + \frac{k}{\delta}} T_\infty + \frac{\frac{k}{\delta}}{h + \frac{k}{\delta}} T_c + 0$$

Therefore:
- **valueFraction** = $\frac{h}{h + k \cdot \delta}$
- **refValue** = $T_\infty$
- **refGrad** = 0

Where $\delta$ in OpenFOAM is accessed via `patch().deltaCoeffs()` (returns $1/\delta$).

#### In Code

This is exactly what's in `updateCoeffs()`:

```cpp
void myConvectiveFvPatchScalarField::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    // Get δ coefficient (OpenFOAM stores 1/δ)
    const scalarField& delta = patch().deltaCoeffs();

    // valueFraction = h / (h + k/δ)
    // But deltaCoeffs returns 1/δ, so:
    // valueFraction = h / (h + k * deltaCoeffs)
    valueFraction() = h_ / (h_ + kappa_ * delta);

    refValue() = Tinf_;      // Ambient temperature
    refGrad() = 0;           // No explicit gradient term

    mixedFvPatchScalarField::updateCoeffs();
}
```

---

### Quick Derivation Check

**Limit cases:**

1. **Very high h (h → ∞):** `valueFraction → 1`
   - $T_b = T_\infty$ (Dirichlet/fixedValue)
   - Makes sense: infinite convection → surface equals ambient

2. **Very low h (h → 0):** `valueFraction → 0`
   - $T_b = T_c$ (zeroGradient/insulated)
   - Makes sense: no convection → no heat flux

3. **Typical values:** h = 100, k = 1, δ = 0.01
   - δCoeffs = 100
   - valueFraction = 100 / (100 + 1×100) = 0.5
   - $T_b = 0.5 T_\infty + 0.5 T_c$
   - Equal weighting between ambient and cell

---

Robin (mixed) BC:

$$T_b = \frac{h T_\infty + k\frac{T_c}{\delta}}{h + \frac{k}{\delta}}$$

Where:
- $T_b$ = boundary temperature
- $T_c$ = cell center temperature
- $\delta$ = distance from cell center to boundary
- $h$ = heat transfer coefficient
- $k$ = thermal conductivity
- $T_\infty$ = ambient temperature

---

## Step 1: Create BC Files

### Directory Structure

```
myConvectiveBC/
├── Make/
│   ├── files
│   └── options
├── myConvectiveFvPatchScalarField.H
└── myConvectiveFvPatchScalarField.C
```

---

### myConvectiveFvPatchScalarField.H

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

---

### myConvectiveFvPatchScalarField.C

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

    // Get distance from cell center to face
    const scalarField& delta = patch().deltaCoeffs();

    // Mixed BC coefficients
    // T_face = valueFraction * refValue + (1-valueFraction) * T_cell
    //        + refGrad / delta

    // From: -k dT/dn = h(T - Tinf)
    // We derive: valueFraction = h / (h + k/delta)

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

---

## Step 2: Make Files

### Make/files

```
myConvectiveFvPatchScalarField.C

LIB = $(FOAM_USER_LIBBIN)/libmyConvectiveBC
```

### Make/options

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude

LIB_LIBS = \
    -lfiniteVolume
```

---

## Step 3: Compile

```bash
cd myConvectiveBC
wmake libso

# Output:
# Making dependency list for source file myConvectiveFvPatchScalarField.C
# ...
# libmyConvectiveBC.so
```

---

## Step 4: Update Solver

### Make/options (myHeatFoam)

```
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(FOAM_USER_LIBBIN)/../myConvectiveBC    // Add this

EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -L$(FOAM_USER_LIBBIN) -lmyConvectiveBC     // Add this
```

---

## Step 5: Create Test Case

### 0/T with Convective BC

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
        value           uniform 500;           // Hot surface
    }
    right
    {
        type            myConvective;          // Our custom BC!
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

## Step 6: Validate

### Expected Behavior

At steady state:
- Heat flux at right = $h(T_{surface} - T_{inf})$
- Should match internal conduction

### Validation

```bash
# Run
myHeatFoam

# Check surface temperature
postProcess -func "patchAverage(name=right, T)"
```

Compare with expected $T_{surface}$ from energy balance.

---

## การ Debug ปัญหาที่พบบ่อย

### ปัญหา 1: "undefined reference to vtable"

**อาการ:**
```bash
# .so: undefined reference to 'vtable for Foam::myConvectiveFvPatchScalarField'
collect2: error: ld returned 1 exit status
```

**วินิจฉัย:** ไม่ได้ implement virtual functions ครบ

**วิธีแก้:**
```cpp
// Make sure ALL virtual functions from mixedFvPatchScalarField are implemented:

// In .H file:
virtual void updateCoeffs();        // Must implement
virtual void write(Ostream&) const;  // Must implement

// Check you didn't forget:
virtual tmp<fvPatchScalarField> clone() const;  // Constructor clone
virtual tmp<fvPatchScalarField> clone(const DimensionedField<scalar, volMesh>&) const;
```

**Common mistake:** Forgetting to implement `write()` method

---

### ปัญหา 2: Library Not Found

**อาการ:**
```bash
myHeatFoam: error while loading shared libraries:
libmyConvectiveBC.so: cannot open shared object file
```

**วินิจฉัย:** Library path ไม่อยู่ใน `LD_LIBRARY_PATH`

**วิธีแก้:**
```bash
# Check library exists
ls $FOAM_USER_LIBBIN/libmyConvectiveBC.so

# Add to Make/options in solver:
EXE_LIBS = \
    ... \
    -L$(FOAM_USER_LIBBIN) -lmyConvectiveBC

# Or add to ~/.bashrc:
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$FOAM_USER_LIBBIN
```

---

### ปัญหา 3: BC Not Loading

**อาการ:**
```
--> FOAM FATAL IO ERROR:
Unknown boundary patch type myConvective
Valid patch types:
10
(
fixedValue
fixedGradient
...
)
```

**วินิจฉัย:** BC ไม่ได้ลงทะเบียนกับ RTS

**วิธีแก้:**
```cpp
// Check end of .C file:

makePatchTypeField
(
    fvPatchScalarField,
    myConvectiveFvPatchScalarField
);

// This macro expands to:
// - Creates factory function
// - Registers with run-time selection table

// Make sure TypeName matches:
// In .H:
TypeName("myConvective");  // Case sensitive!

// In 0/T:
type            myConvective;  // Must match exactly!
```

---

### ปัญหา 4: Wrong Heat Flux

**อาการ:**
Boundary temperature ไม่ตรงกับค่าที่คาดหวัง

**วินิจฉัย:** คำนวณผิดพลาดใน `updateCoeffs()`

**การ Debug:**
```cpp
// Add to updateCoeffs():
void myConvectiveFvPatchScalarField::updateCoeffs()
{
    if (updated())
    {
        return;
    }

    const scalarField& delta = patch().deltaCoeffs();

    // DEBUG: Print first face values
    if (Pstream::master())
    {
        Info<< "myConvective BC:" << nl
            << "  h = " << h_ << nl
            << "  kappa = " << kappa_ << nl
            << "  Tinf = " << Tinf_ << nl
            << "  delta[0] = " << delta[0] << nl
            << "  valueFraction[0] = " << (h_ / (h_ + kappa_ * delta[0])) << nl;
    }

    valueFraction() = h_ / (h_ + kappa_ * delta);
    refValue() = Tinf_;
    refGrad() = 0;

    mixedFvPatchScalarField::updateCoeffs();
}
```

**Check output:**
```
myConvective BC:
  h = 100
  kappa = 1
  Tinf = 300
  delta[0] = 100
  valueFraction[0] = 0.5
```

Verify: `valueFraction = 100 / (100 + 1×100) = 0.5` ✓

---

### ปัญหา 5: Temperature Oscillation

**อาการ:**
```
Time = 1
right patch T = 450 K

Time = 2
right patch T = 320 K

Time = 3
right patch T = 430 K
```

**วินิจฉัย:** Convection แรงเกินไปทำให้ instability

**วิธีแก้:**
```bash
# Under-relax the BC (not directly supported in mixedFvPatch)

# Workaround: Reduce time step
vim system/controlDict

deltaT  0.001;  # Was 0.01

# Or add relaxation to solver
vim system/fvSolution

solvers
{
    T
    {
        solver          PCG;
        tolerance       1e-06;
        relTol          0.01;  # Add this
    }
}
```

---

## ทดสอบ BC ของคุณ

### Minimal Test Case

```bash
# Create minimal case
mkdir test_convective
cd test_convective

# Copy from phase 1
cp -r ../../1D_diffusion/* .

# Modify 0/T
vim 0/T

# Change right BC:
right
{
    type            myConvective;
    h               100;
    Tinf            300;
    kappa           1;
    value           uniform 300;
}

# Run
blockMesh
myHeatFoam

# Check result
postProcess -func "patchAverage(name=right, T)"
cat postProcessing/patchAverage/0/right_T.dat
```

### ผลลัพธ์ที่คาดหวัง

```
# Patch right T
500
450
425
410
400
395
390
...
```

Temperature should approach steady state based on convection strength.

---

## Exercises

1. **Add Time-varying Tinf:** Make ambient temperature a function of time
2. **Field-based h:** Read h from a `volScalarField` instead of constant
3. **Radiation Term:** Add $q'' = \epsilon \sigma (T^4 - T_{inf}^4)$

---

## Deliverables

- [ ] Compiled `libmyConvectiveBC.so`
- [ ] Updated solver linking to library
- [ ] Test case with convective BC
- [ ] Validation of heat balance

---

## ถัดไป

เมื่อ Phase 2 เสร็จแล้ว ไปต่อที่ [Phase 3: Add Turbulence](03_Phase3_Turbulence_Model.md)
