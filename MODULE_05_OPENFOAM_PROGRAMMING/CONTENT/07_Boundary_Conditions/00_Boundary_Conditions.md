# MODULE_05 Section 07: Boundary Conditions
# หน่วยที่ 05 ส่วนที่ 07: เงื่อนไขขอบเขต

## 1. Overview / ภาพรวม

### What are Boundary Conditions? / เงื่อนไขขอบเขตคืออะไร?

Boundary conditions (BCs) specify the **behavior of fields** at the boundaries of the computational domain. They represent:
- **Physical constraints**: Inlet velocity, outlet pressure, wall temperature
- **Mathematical requirements**: Well-posed PDE problem
- **Numerical implementation**: How boundary values affect interior solution

เงื่อนไขขอบเขตระบุ **พฤติกรรมของฟิลด์** ที่ขอบเขตของโดเมนการคำนวณ พวกมันแทน:
- **ข้อจำกัดทางฟิสิกส์**: ความเร็วที่ทางเข้า, ความดันที่ทางออก, อุณหภูมิผนัง
- **ความต้องการทางคณิตศาสตร์**: ปัญหา PDE ที่เหมาะสม
- **การนำไปใช้ทางตัวเลข**: ว่าค่าขอบเขตส่งผลต่อค่าภายในอย่างไร

> **Key Insight for R410A Evaporator**: Proper BCs are critical for:
> - **Mass flow inlet** with subcooled liquid R410A
> - **Pressure outlet** with superheated vapor
> - **Wall heat transfer** with evaporation phase change
> - **Adiabatic sections** with no heat transfer

---

## 2. BC Class Hierarchy / ลำดับชั้นคลาส BC

### fvPatchField Base Class / คลาสฐาน fvPatchField

**⭐ Root of All Boundary Conditions**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/fvPatchField/fvPatchField.H`
> **Lines**: 100-150

```mermaid
classDiagram
    class "fvPatchField~Type~" {
        <<abstract>>
        +fvPatch patch
        +DimensionedField field
        +updateCoeffs()*
        +evaluate()*
        +snGrad()*
        +valueInternalCoeffs()*
        +valueBoundaryCoeffs()*
    }

    class "fixedValueFvPatchField" {
        +fixesValue() true
        +Field~Type~ value
    }

    class "fixedGradientFvPatchField" {
        +Field~Type~ gradient
        +evaluate()
    }

    class "zeroGradientFvPatchField" {
        +snGrad() 0
    }

    class "mixedFvPatchField" {
        +scalar refValue
        +scalar refGrad
        +scalar valueFraction
    }

    "fvPatchField~Type~" <|-- "fixedValueFvPatchField"
    "fvPatchField~Type~" <|-- "fixedGradientFvPatchField"
    "fvPatchField~Type~" <|-- "zeroGradientFvPatchField"
    "fvPatchField~Type~" <|-- "mixedFvPatchField"
```

**⭐ Base Class Interface**:

```cpp
// File: src/finiteVolume/fields/fvPatchFields/fvPatchField/fvPatchField.H

template<class Type>
class fvPatchField
:
    public Field<Type>,
    public fvPatchFieldBase
{
protected:
    // Reference to the boundary patch
    const fvPatch& patch_;

    // Reference to the internal field
    const DimensionedField<Type, volMesh>& internalField_;

public:
    // === VIRTUAL FUNCTIONS FOR BC IMPLEMENTATION ===

    // Update coefficients for matrix assembly
    virtual void updateCoeffs() = 0;

    // Evaluate boundary field values
    virtual void evaluate(const Pstream::commsTypes commsType) = 0;

    // Return patch-normal gradient
    virtual tmp<Field<Type>> snGrad() const = 0;

    // Matrix coefficients for value (diagonal and source)
    virtual tmp<Field<Type>> valueInternalCoeffs(const tmp<scalarField>&) const = 0;
    virtual tmp<Field<Type>> valueBoundaryCoeffs(const tmp<scalarField>&) const = 0;

    // Matrix coefficients for gradient
    virtual tmp<Field<Type>> gradientInternalCoeffs() const = 0;
    virtual tmp<Field<Type>> gradientBoundaryCoeffs() const = 0;
};
```

### BC Categories / ประเภทของ BC

| Category | Location | Description | Examples |
|----------|----------|-------------|----------|
| **basic** | `basic/` | Fundamental BCs | fixedValue, fixedGradient, zeroGradient |
| **constraint** | `constraint/` | Mathematical constraints | symmetryPlane, cyclic, processor |
| **derived** | `derived/` | Physics-based BCs | inletOutlet, totalPressure, wallHeatTransfer |

---

## 3. Basic Boundary Conditions / เงื่อนไขขอบเขตพื้นฐาน

### 3.1 Fixed Value / ค่าคงที่

**⭐ Dirichlet Boundary Condition**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/basic/fixedValue/fixedValueFvPatchField.H`
> **Lines**: 27-29

**Mathematical Form**:
$$
\phi|_{\partial \Omega} = \phi_{\text{specified}}
$$

**Usage** (in `0/` field file):

```cpp
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0);  // Constant velocity [m/s]
        // or
        value           nonuniform List<vector>  // Spatially varying
        (
            (10 0 0)
            (9.5 0 0)
            ...
        );
    }

    wall
    {
        type            fixedValue;
        value           uniform 300;  // Wall temperature [K]
    }
}
```

**Implementation Details**:

```cpp
// File: src/finiteVolume/fields/fvPatchFields/basic/fixedValue/fixedValueFvPatchField.C

template<class Type>
tmp<Field<Type>> fixedValueFvPatchField<Type>::valueInternalCoeffs
(
    const tmp<scalarField>& weights
) const
{
    // For fixed value: diagonal coefficient = 1, source = value
    // Matrix: 1 * x_P = value_boundary
    return tmp<Field<Type>>(new Field<Type>(this->size(), pTraits<Type>::one));
}

template<class Type>
tmp<Field<Type>> fixedValueFvPatchField<Type>::valueBoundaryCoeffs
(
    const tmp<scalarField>& weights
) const
{
    // Source term = boundary value
    return *this;
}
```

**⚠️ Key Properties**:
- **Fixes value**: Field cannot be modified by solver
- **Assignability**: `false` (BC ignores assignment operations)
- **Use for**: Inlets, walls with specified temperature/pressure

### 3.2 Fixed Gradient / ค่าเกรเดียนต์คงที่

**⭐ Neumann Boundary Condition**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/basic/fixedGradient/fixedGradientFvPatchField.H`
> **Lines**: 29-33

**Mathematical Form**:
$$
\frac{\partial \phi}{\partial n}\bigg|_{\partial \Omega} = g_{\text{specified}}
$$

**Usage**:

```cpp
boundaryField
{
    outlet
    {
        type            fixedGradient;
        gradient        uniform 0;  // Zero gradient (outflow)
    }

    wall
    {
        type            fixedGradient;
        gradient        uniform 100;  // Heat flux [W/m²]
    }
}
```

**Implementation**:

```cpp
// File: src/finiteVolume/fields/fvPatchFields/basic/fixedGradient/fixedGradientFvPatchField.C

template<class Type>
void fixedGradientFvPatchField<Type>::evaluate
(
    const Pstream::commsTypes commsType
)
{
    // Evaluate patch values from internal field and gradient
    // phi_p = phi_c + gradient / delta
    // where delta = 1 / distance from cell center to face

    Field<Type>::operator=
    (
        this->patchInternalField()  // phi_c
      + gradient_ / this->patch().deltaCoeffs()  // gradient / delta
    );
}

template<class Type>
tmp<Field<Type>> fixedGradientFvPatchField<Type>::snGrad() const
{
    // Return patch-normal gradient
    return gradient_;
}
```

**⚠️ Key Properties**:
- **Fixes gradient**: Normal derivative is fixed
- **Value calculated**: From internal field + gradient
- **Use for**: Outlets, specified heat flux

### 3.3 Zero Gradient / เกรเดียนต์ศูนย์

**⭐ Special Case of Fixed Gradient**

**Mathematical Form**:
$$
\frac{\partial \phi}{\partial n}\bigg|_{\partial \Omega} = 0
$$

**Physical Meaning**:
- Field value at boundary = adjacent cell value
- **No transport** across boundary
- Convective outflow, adiabatic wall

**Usage**:

```cpp
boundaryField
{
    outlet
    {
        type            zeroGradient;  // Outflow condition
    }

    adiabaticWall
    {
        type            zeroGradient;  // Adiabatic (no heat flux)
    }
}
```

**Implementation**:

```cpp
// zeroGradient is a typedef for fixedGradient with gradient = 0
typedef fixedGradientFvPatchField<Type> zeroGradientFvPatchField<Type>;
```

**⚠️ Key Properties**:
- **Outflow**: Fluid leaves domain with no influence from boundary
- **Adiabatic**: No heat transfer across wall
- **Use for**: Outlets, symmetry planes, adiabatic walls

---

## 4. Mixed Boundary Conditions / เงื่อนไขขอบเขตแบบผสม

### 4.1 Mixed (Robin) BC / เงื่อนไขแบบผสม

**⭐ Linear Combination of Value and Gradient**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/basic/mixed/mixedFvPatchField.H`

**Mathematical Form**:
$$
\alpha \phi|_{\partial \Omega} + (1 - \alpha) \frac{\partial \phi}{\partial n}\bigg|_{\partial \Omega} = \text{specified}
$$

**Implementation**:

```cpp
// Mixed BC: valueFraction * refValue + (1 - valueFraction) * (gradient / delta)
// valueFraction = 1: fixedValue
// valueFraction = 0: fixedGradient
// 0 < valueFraction < 1: mixed

boundaryField
{
    wall
    {
        type            mixed;
        refValue        uniform 300;        // Reference value [K]
        refGradient     uniform 0;          // Reference gradient [K/m]
        valueFraction   uniform 0.5;        // 0 = pure gradient, 1 = pure value
    }
}
```

**Physical Applications**:
- **Convective heat transfer**: $h(T - T_{\infty}) = -k \frac{\partial T}{\partial n}$
- **Partial slip walls**: Velocity slip proportional to shear stress

### 4.2 inletOutlet / ทางเข้า-ทางออก

**⭐ Direction-Dependent BC**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/derived/inletOutlet/inletOutletFvPatchField.H`

**Mathematical Form**:
$$
\phi|_{\partial \Omega} = \begin{cases}
\phi_{\text{inlet}} & \text{if } \mathbf{U} \cdot \mathbf{n} < 0 \text{ (inflow)} \\
\frac{\partial \phi}{\partial n} = 0 & \text{if } \mathbf{U} \cdot \mathbf{n} \geq 0 \text{ (outflow)}
\end{cases}
$$

**Usage**:

```cpp
boundaryField
{
    inlet
    {
        type            inletOutlet;
        inletValue      uniform 1;          // Value for inflow
        value           uniform 1;          // Initial value
    }
}
```

**Physical Application**:
- **Backflow prevention**: Prevents reverse flow at outlet
- **Pressure boundary**: Fixed value for inflow, zero gradient for outflow

### 4.3 totalPressure / ความดันทั้งหมด

**⭐ Bernoulli-Based Pressure BC**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/derived/totalPressure/totalPressureFvPatchField.H`

**Mathematical Form**:
$$
p_0 = p + \frac{1}{2} \rho |\mathbf{U}|^2
$$

where $p_0$ is the **total pressure** (stagnation pressure).

**Usage**:

```cpp
boundaryField
{
    inlet
    {
        type            totalPressure;
        p0              uniform 101325;    // Total pressure [Pa]
        gamma           1.4;                // Heat capacity ratio (air)
        // For compressible flow
    }
}
```

**Physical Application**:
- **Compressible flow inlets**: Specified total pressure
- **Aerodynamic simulations**: Stagnation conditions

---

## 5. Constraint Boundary Conditions / เงื่อนไขขอบเขตเชิงข้อจำกัด

### 5.1 Cyclic Boundary / เงื่อนไขเป็นวงจร

**⭐ Periodic Boundary Condition**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/constraint/cyclic/cyclicFvPatchField.H`

**Mathematical Form**:
$$
\phi|_{\partial \Omega_1} = \phi|_{\partial \Omega_2}
$$

where $\partial \Omega_1$ and $\partial \Omega_2$ are coupled cyclic patches.

**Usage** (in `boundary` file in `constant/polyMesh/`):

```cpp
cyclic1
{
    type            cyclic;
    neighbourPatch  cyclic2;  // Name of matching patch
    // Fields automatically match on both patches
}
```

**Physical Application**:
- **Periodic geometries**: Heat exchanger tubes, turbomachinery
- **Infinite domain**: Simulating periodicity

### 5.2 Symmetry Plane / ระนาบสมมาตร

**⭐ Symmetry Boundary Condition**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/constraint/symmetryPlane/symmetryPlaneFvPatchField.H`

**Mathematical Form**:
$$
\mathbf{U} \cdot \mathbf{n} = 0, \quad \frac{\partial \phi}{\partial n} = 0
$$

**Usage**:

```cpp
symmetry
{
    type            symmetryPlane;
}
```

**Physical Application**:
- **Symmetric geometries**: Half-domain simulation
- **Reduces computational cost**

### 5.3 Processor / ตัวประมวลผล

**⭐ Parallel Decomposition Boundary**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/constraint/processor/processorFvPatchField.H`

**Purpose**: Communication between MPI processes in parallel simulations.

**Usage**:

```cpp
// Automatically created by decomposePar
procBoundary0to1
{
    type            processor;
    myProcNo        0;
    neighbProcNo    1;
}
```

**Physical Application**:
- **Domain decomposition**: Divide mesh among processors
- **Parallel computing**: Communication of boundary values

---

## 6. Wall Boundary Conditions / เงื่อนไขขอบเขตผนัง

### 6.1 No-Slip Wall / ผนังไม่ลื่น

**⭐ Standard Velocity BC for Walls**

**Mathematical Form**:
$$
\mathbf{U}|_{\text{wall}} = \mathbf{U}_{\text{wall}}
$$

For stationary wall:
$$
\mathbf{U}|_{\text{wall}} = 0
$$

**Usage**:

```cpp
boundaryField
{
    wall
    {
        type            noSlip;           // Same as fixedValue with value 0
        // or
        type            fixedValue;
        value           uniform (0 0 0);
    }
}
```

### 6.2 Wall Heat Transfer / การถ่ายเทความร้อนผนัง

**⭐ Convective Heat Transfer BC**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/derived/wallHeatTransfer/wallHeatTransferFvPatchField.H`

**Mathematical Form**:
$$
q_w = h (T_{\text{fluid}} - T_{\text{wall}}) = -k \frac{\partial T}{\partial n}
$$

**Usage**:

```cpp
boundaryField
{
    outerWall
    {
        type            externalWallHeatFlux;
        mode            coefficient;       // Heat transfer coefficient mode
        h               uniform 50;        // Heat transfer coefficient [W/(m²·K)]
        Ta              uniform 290;       // Ambient temperature [K]
        // or
        mode            flux;              // Fixed heat flux mode
        q               uniform 1000;      // Heat flux [W/m²]
    }
}
```

**Physical Application**:
- **R410A evaporator**: Refrigerant-side heat transfer
- **Conjugate heat transfer**: Coupled fluid-solid heat transfer

---

## 7. Custom Boundary Conditions / เงื่อนไขขอบเขตที่กำหนดเอง

### Creating a Custom BC / การสร้าง BC ที่กำหนดเอง

**⭐ Example: Time-Varying Velocity Inlet**

```cpp
// === CUSTOM BC: timeVaryingInletVelocity ===
// Location: src/finiteVolume/fields/fvPatchFields/derived/timeVaryingInletVelocity/

#ifndef timeVaryingInletVelocityFvPatchVectorField_H
#define timeVaryingInletVelocityFvPatchVectorField_H

#include "fixedValueFvPatchField.H"
#include "Function1.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

/*---------------------------------------------------------------------------*\
         Class timeVaryingInletVelocityFvPatchVectorField Declaration
\*---------------------------------------------------------------------------*/

class timeVaryingInletVelocityFvPatchVectorField
:
    public fixedValueFvPatchVectorField
{
    // Private Data

        //- Time function
        autoPtr<Function1<vector>> timeFunction_;


public:

    //- Runtime type information
    TypeName("timeVaryingInletVelocity");


    // Constructors

        //- Construct from patch and internal field
        timeVaryingInletVelocityFvPatchVectorField
        (
            const fvPatch&,
            const DimensionedField<vector, volMesh>&
        );

        //- Construct from patch, internal field and dictionary
        timeVaryingInletVelocityFvPatchVectorField
        (
            const fvPatch&,
            const DimensionedField<vector, volMesh>&,
            const dictionary&
        );

        //- Construct by mapping
        timeVaryingInletVelocityFvPatchVectorField
        (
            const timeVaryingInletVelocityFvPatchVectorField&,
            const fvPatch&,
            const DimensionedField<vector, volMesh>&,
            const fieldMapper&
        );

        //- Copy constructor
        timeVaryingInletVelocityFvPatchVectorField
        (
            const timeVaryingInletVelocityFvPatchVectorField&
        );

        //- Construct and return a clone
        virtual tmp<fvPatchVectorField> clone() const
        {
            return tmp<fvPatchVectorField>
            (
                new timeVaryingInletVelocityFvPatchVectorField(*this)
            );
        }


    // Member Functions

        //- Update the coefficients associated with the patch field
        virtual void updateCoeffs();
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
```

**Implementation (.C file)**:

```cpp
#include "timeVaryingInletVelocityFvPatchVectorField.H"
#include "addToRunTimeSelectionTable.H"
#include "fvPatchFieldMapper.H"
#include "volFields.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

// Constructor from patch and internal field
timeVaryingInletVelocityFvPatchVectorField::timeVaryingInletVelocityFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF
)
:
    fixedValueFvPatchVectorField(p, iF),
    timeFunction_(nullptr)
{}


// Constructor from patch, internal field and dictionary
timeVaryingInletVelocityFvPatchVectorField::timeVaryingInletVelocityFvPatchVectorField
(
    const fvPatch& p,
    const DimensionedField<vector, volMesh>& iF,
    const dictionary& dict
)
:
    fixedValueFvPatchVectorField(p, iF, dict, false),  // Don't read value yet
    timeFunction_(Function1<vector>::New("timeFunction", dict))
{
    // Evaluate initial value
    vectorField::operator=(timeFunction_->value(this->db().time().timeOutputValue()));
}


// Update coefficients
void timeVaryingInletVelocityFvPatchVectorField::updateCoeffs()
{
    if (this->updated())
    {
        return;  // Already updated
    }

    // Get current time
    scalar t = this->db().time().timeOutputValue();

    // Evaluate time function
    const vectorField& timeValue = timeFunction_->value(t);

    // Update patch values
    vectorField::operator=(timeValue);

    fixedValueFvPatchVectorField::updateCoeffs();
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePatchTypeField(fvPatchVectorField, timeVaryingInletVelocityFvPatchVectorField);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //
```

**Usage**:

```cpp
boundaryField
{
    inlet
    {
        type            timeVaryingInletVelocity;

        timeFunction    table
        (
            (0    (0 0 10))
            (0.1  (0 0 12))
            (0.2  (0 0 15))
            (0.5  (0 0 10))
        );
    }
}
```

**Compilation**:

```bash
# Add to Make/files
timeVaryingInletVelocityFvPatchVectorField.C

# Add to Make/options
LIB_LIBS = \
    -lfiniteVolume \
    -lmeshTools
```

---

## 8. R410A Evaporator Boundary Conditions / เงื่อนไขขอบเขตเครื่องระเหย R410A

### 8.1 Mass Flow Inlet / ทางเข้าอัตราการไหลของมวล

**⭐ Subcooled Liquid R410A Inlet**

```cpp
// === 0/U ===
boundaryField
{
    inlet
    {
        type            flowRateInletVelocity;
        massFlowRate    0.01;              // Mass flow rate [kg/s]
        rho             rho;               // Use density field
        // For incompressible, use volumetricFlowRate instead
    }
}

// === 0/T ===
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 283;       // Subcooled liquid [K] (~10°C)
    }
}

// === 0/p ===
boundaryField
{
    inlet
    {
        type            zeroGradient;       // Pressure gradient zero at inlet
    }
}

// === 0/alpha ===
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 1;         // Pure liquid (alpha = 1)
    }
}
```

### 8.2 Pressure Outlet / ทางออกความดัน

**⭐ Superheated Vapor R410A Outlet**

```cpp
// === 0/p ===
boundaryField
{
    outlet
    {
        type            fixedValue;
        value           uniform 8e5;       // Saturation pressure at Tsat (~8 bar)
    }
}

// === 0/U ===
boundaryField
{
    outlet
    {
        type            pressureInletOutletVelocity;
        value           uniform (0 0 0);   // Initial guess
    }
}

// === 0/T ===
boundaryField
{
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 298;       // If backflow occurs [K]
        value           uniform 298;
    }
}

// === 0/alpha ===
boundaryField
{
    outlet
    {
        type            inletOutlet;
        inletValue      uniform 0;         // Pure vapor if backflow (alpha = 0)
        value           uniform 0;
    }
}
```

### 8.3 Wall Heat Transfer / การถ่ายเทความร้อนผนัง

**⭐ Evaporating Heat Transfer**

```cpp
// === 0/T ===
boundaryField
{
    tubeWall
    {
        type            externalWallHeatFlux;
        mode            coefficient;
        h               uniform 5000;      // Heat transfer coefficient [W/(m²·K)]
        Ta              uniform 310;       // Hot fluid temperature [K] (~37°C)
        // For R410A evaporator: Ta > Tsat so heat flows INTO refrigerant
    }
}

// === 0/U ===
boundaryField
{
    tubeWall
    {
        type            noSlip;
    }
}

// === 0/alpha ===
boundaryField
{
    tubeWall
    {
        type            zeroGradient;       // No phase change flux at wall
        // (phase change modeled in bulk using volume source)
    }
}
```

**Alternative: Fixed Heat Flux** (simplified):

```cpp
boundaryField
{
    tubeWall
    {
        type            externalWallHeatFlux;
        mode            flux;
        q               uniform 5000;      // Heat flux [W/m²]
    }
}
```

### 8.4 Adiabatic Sections / ส่วนที่ไม่นำความร้อน

**⭐ No Heat Transfer**

```cpp
// === 0/T ===
boundaryField
{
    adiabaticWall
    {
        type            zeroGradient;       // Adiabatic: dT/dn = 0
    }
}

// === 0/U ===
boundaryField
{
    adiabaticWall
    {
        type            noSlip;
    }
}
```

---

## 9. Boundary Condition Mapping / การแม็ปเงื่อนไขขอบเขต

### GroovyBC / OpenFOAM+ Expression-Based BC

**⭐ Mathematical Expressions for BCs**

> **Location**: OpenFOAM+ only (not in OpenFOAM.org)

**Usage**:

```cpp
boundaryField
{
    wall
    {
        type            groovyBC;
        variables       "rho=1.2;V=10;";
        valueExpression "rho*V";            // Expression for value
        gradientExpression "0";             // Expression for gradient
        fractionExpression "1";             // valueFraction (0=gradient, 1=value)
    }
}
```

**Applications**:
- **Time-varying conditions**: Sinusoidal velocity, ramp temperature
- **Spatially-varying conditions**: Parabolic profiles
- **Field-dependent conditions**: Coupled boundary values

### codedFixedValue / Programmatic BC

**⭐ Inline C++ Code for BCs**

> **File**: `openfoam_temp/src/finiteVolume/fields/fvPatchFields/derived/codedFixedValue/`

**Usage**:

```cpp
boundaryField
{
    inlet
    {
        type            codedFixedValue;
        value           uniform (0 0 0);

        code
        #{
            // C++ code to calculate boundary value
            const scalar t = this->db().time().timeOutputValue();
            const scalar x = this->patch().Cf().component(0);  // Face center x-coordinate

            vectorField& Ufield = *this;
            Ufield = vector(0, 0, 10 * Foam::sin(2 * 3.14159 * t));  // Sinusoidal velocity
        #};
    }
}
```

---

## 10. Verification & Best Practices / การตรวจสอบและแนวปฏิบัติที่ดี

### Verification Tests / การทดสอบการตรวจสอบ

**1. Mass Conservation**:

```cpp
// Calculate mass flux imbalance
scalar massIn = sum(pos(phi) & mesh.magSf());
scalar massOut = sum(neg(phi) & mesh.magSf());
scalar massImbalance = massIn + massOut;  // Should be ~0

Info<< "Mass imbalance: " << massImbalance << " kg/s" << endl;
```

**2. BC Consistency**:

```cpp
// Verify pressure-velocity coupling at boundaries
// For fixed pressure outlet: velocity should have zero gradient
// For fixed velocity inlet: pressure should have zero gradient
```

### Best Practices for R410A Evaporator / แนวปฏิบัติที่ดีสำหรับเครื่องระเหย R410A

1. **Inlet BCs**:
   - Use **massFlowRate** for accurate mass flow
   - Specify **subcooled liquid** temperature
   - Set **alpha = 1** (pure liquid)

2. **Outlet BCs**:
   - Use **fixedValue** for pressure
   - Use **pressureInletOutletVelocity** for velocity
   - Allow **backflow** with appropriate alpha value

3. **Wall BCs**:
   - Use **externalWallHeatFlux** for heat transfer
   - Ensure **T_hot_fluid > T_saturation** for evaporation
   - Use **noSlip** for velocity

4. **Stability**:
   - Start with **zeroGradient** for velocity at outlet
   - Ramp **heat flux** gradually to avoid rapid phase change
   - Monitor **Courant number** near interface

---

## 11. Summary / สรุป

### Key Takeaways / จุดสำคัญ

1. **BC Class Hierarchy**:
   - Base class: `fvPatchField<Type>`
   - Derived: `fixedValue`, `fixedGradient`, `zeroGradient`, `mixed`
   - Category: basic, constraint, derived

2. **Mathematical Types**:
   - **Dirichlet** (fixedValue): $\phi|_{\partial \Omega} = \text{const}$
   - **Neumann** (fixedGradient): $\frac{\partial \phi}{\partial n} = \text{const}$
   - **Robin** (mixed): Combination of value and gradient

3. **Basic BCs**:
   - **fixedValue**: Inlets, walls with specified temperature
   - **fixedGradient**: Outlets, heat flux
   - **zeroGradient**: Outflow, adiabatic walls

4. **Advanced BCs**:
   - **cyclic**: Periodic boundaries
   - **symmetryPlane**: Symmetry conditions
   - **inletOutlet**: Direction-dependent (inflow vs. outflow)

5. **R410A Evaporator BCs**:
   - **Inlet**: `massFlowRate` + subcooled liquid temperature
   - **Outlet**: `fixedValue` pressure + `pressureInletOutletVelocity`
   - **Wall**: `externalWallHeatFlux` with heat transfer coefficient

6. **Custom BCs**:
   - Inherit from `fixedValueFvPatchField` or similar
   - Override `updateCoeffs()` to update boundary values
   - Compile with `wmake` in user directory

---

## References / อ้างอิง

1. **OpenFOAM Source Code**:
   - `src/finiteVolume/fields/fvPatchFields/basic/` - Basic BCs
   - `src/finiteVolume/fields/fvPatchFields/constraint/` - Constraint BCs
   - `src/finiteVolume/fields/fvPatchFields/derived/` - Derived BCs

2. **OpenFOAM Documentation**:
   - User Guide: Chapter 5 (Boundary conditions)
   - Programmer's Guide: Chapter 5.4 (Boundary conditions)

3. **Textbooks**:
   - Moukalled, F., Mangani, L., & Darwish, M. (2016). *The Finite Volume Method in Computational Fluid Dynamics* (Chapter 6)

---

*Last Updated: 2026-01-28*
*Next Section: 08_Turbulence_Models*
