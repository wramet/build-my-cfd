# Section 12: Dimensional Analysis (การวิเคราะห์มิติ)

## Overview (ภาพรวม)

Dimensional analysis is a fundamental aspect of computational fluid dynamics (CFD) engineering, ensuring physical consistency and unit correctness throughout simulations. ⭐ In OpenFOAM, dimensional analysis is enforced at compile-time through sophisticated template mechanisms, preventing dimensionally inconsistent operations from even being compiled.

### Learning Objectives (เป้าหมายการเรียนรู้)

- Understand the DimensionSet class and unit checking system ⭐
- Master dimensioned types (dimensionedScalar, dimensionedVector, etc.) ⭐
- Learn compile-time dimensional consistency enforcement ⭐
- Calculate dimensionless numbers for R410A flow analysis ⭐
- Implement unit conversion in OpenFOAM applications ⭐

---

## DimensionSet Class and Unit Checking (คลาส DimensionSet และการตรวจสอบหน่วย)

The `dimensionSet` class is the foundation of dimensional analysis in OpenFOAM, representing the dimensions of physical quantities in a 7-dimensional SI system.

### ⭐ Core Architecture (สถาปัตยกรรมหลัก)

```cpp
// File: openfoam_temp/src/OpenFOAM/dimensionSet/dimensionSet.H:133-148
class dimensionSet
{
public:
    // Member constants
    enum
    {
        nDimensions = 7    // Number of dimensions in SI is 7
    };

    enum dimensionType
    {
        MASS,               // kilogram   kg
        LENGTH,             // metre      m
        TIME,               // second     s
        TEMPERATURE,        // Kelvin     K
        MOLES,              // kilomole   kmol
        CURRENT,            // Ampere     A
        LUMINOUS_INTENSITY  // Candela    Cd
    };
};
```

### ⭐ Dimension Representation (การแทนมิติทางกายภาพ)

Each physical quantity is represented as an array of exponents:

```cpp
// File: openfoam_temp/src/OpenFOAM/dimensionSet/dimensionSet.H:165
private:
    // Array of dimension exponents
    scalar exponents_[nDimensions];
```

For example:
- Velocity: `[0, 1, -1, 0, 0, 0, 0]` → LT⁻¹
- Pressure: `[1, -1, -2, 0, 0, 0, 0]` → ML⁻¹T⁻²
- Temperature: `[0, 0, 0, 1, 0, 0, 0]` → Θ

### ⭐ Built-in Dimension Constants (ค่าคงที่มิติที่มีให้ใช้งาน)

```cpp
// File: openfoam_temp/src/OpenFOAM/dimensionSet/dimensionSets.C:51-91
const Foam::dimensionSet Foam::dimless(0, 0, 0, 0, 0, 0, 0);

const Foam::dimensionSet Foam::dimMass(1, 0, 0, 0, 0, 0, 0);
const Foam::dimensionSet Foam::dimLength(0, 1, 0, 0, 0, 0, 0);
const Foam::dimensionSet Foam::dimTime(0, 0, 1, 0, 0, 0, 0);
const Foam::dimensionSet Foam::dimTemperature(0, 0, 0, 1, 0, 0, 0);

const Foam::dimensionSet Foam::dimVelocity(dimLength/dimTime);
const Foam::dimensionSet Foam::dimPressure(dimForce/dimArea);
const Foam::dimensionSet Foam::dimDynamicViscosity(dimDensity*dimKinematicViscosity);
```

### Example: Creating Custom Dimensions (ตัวอย่าง: สร้างมิติที่กำหนดเอง)

```cpp
#include "dimensionSet.H"

// Create custom dimension for heat transfer coefficient
dimensionSet dimHeatTransfer(1, 0, -3, -1, 0, 0, 0);  // MT⁻³Θ⁻¹

// Or derive from existing dimensions
dimensionSet dimThermalDiffusivity(dimThermalConductivity/dimDensity/dimSpecificHeatCapacity);
```

---

## Dimensioned Types (ชนิดข้อมูลมีมิติ)

OpenFOAM provides templated `dimensioned` classes that associate dimensions with values, ensuring dimensional consistency during compilation.

### � dimensionedScalar (สเกลาร์มีมิติ)

```cpp
typedef dimensioned<scalar> dimensionedScalar;

// Basic constructors
dimensionedScalar p("pressure", dimPressure, 101325.0);  // 101325 Pa
dimensionedScalar T("temperature", dimTemperature, 298.0);  // 298 K

// Operations preserve dimensions
dimensionedScalar newP = p + dimensionedScalar("dp", dimPressure, 1000.0);
dimensionedScalar rho = p / (dimGasConstant * T);  // dimensionally consistent
```

### � dimensionedVector (เวกเตอร์มีมิติ)

```cpp
typedef dimensioned<vector> dimensionedVector;

// Velocity field
dimensionedVector U("velocity", dimVelocity, vector(1.0, 0.0, 0.0));  // 1 m/s

// Operations
dimensionedVector momentum = dimensionedScalar("mass", dimMass, 1.0) * U;
```

### � dimensionedTensor (เทนเซอร์มีมิติ)

```cpp
typedef dimensioned<tensor> dimensionedTensor;

// Stress tensor
dimensionedTensor sigma("stress", dimPressure, tensor(0, 0, 0, 0, 0, 0, 0, 0, 0));
```

### � Matrix Operations with Dimensional Consistency (การดำเนินการเมทริกซ์ที่สอดคล้องกันด้วยมิติ)

```cpp
// File: openfoam_temp/src/OpenFOAM/dimensionedTypes/dimensionedType/dimensionedType.H:272-283
dimensioned<Type> cmptMultiply
(
    const dimensioned<Type>&,
    const dimensioned<Type>&
);

dimensioned<Type> cmptDivide
(
    const dimensioned<Type>&,
    const dimensioned<Type>&
);
```

```cpp
// Component-wise operations preserve dimensions
dimensionedVector scaledU = cmptMultiply(U, dimensionedScalar("scale", dimless, 2.0));
```

---

## Compile-Time Unit Consistency (ความสอดคล้องของหน่วยแบบคอมไพล์เวลา)

OpenFOAM's template system enforces dimensional consistency at compile-time, preventing dimensionally invalid operations.

### ⭐ Template-Based Enforcement (การบังคับการใช้หน่วยแบบเทมเพลต)

```cpp
// File: openfoam_temp/src/OpenFOAM/dimensionedTypes/dimensionedType/dimensionedType.H:298-304
template<class Type>
dimensioned<Type> operator+
(
    const dimensioned<Type>&,
    const dimensioned<Type>&
);

template<class Type>
dimensioned<Type> operator-
(
    const dimensioned<Type>&,
    const dimensioned<Type>&
);
```

### ⭐ Example of Compile-Time Error (ตัวอย่างข้อผิดพลาดขณะคอมไพล์)

```cpp
// This will NOT compile - dimensionally inconsistent
dimensionedScalar p("pressure", dimPressure, 101325.0);
dimensionedScalar T("temperature", dimTemperature, 298.0);
dimensionedScalar velocity("velocity", dimVelocity, 1.0);

// ERROR: Cannot add pressure and temperature
// dimensionedScalar invalid = p + T;

// ERROR: Cannot divide pressure by velocity (dimensions don't match)
// dimensionedScalar invalid2 = p / velocity;
```

### ⭐ Valid Operations (การดำเนินการที่ถูกต้อง)

```cpp
// Valid operations
dimensionedScalar pressureGradient = p / dimensionedScalar("L", dimLength, 1.0);
dimensionedScalar dynamicPressure = 0.5 * dimDensity * sqr(velocity);
```

### ⭐ Compile-Time Dimension Checking (การตรวจสอบมิติขณะคอมไพล์)

```cpp
// Function template ensures dimensional consistency
template<class Type>
dimensioned<Type> calculateKineticEnergy
(
    const dimensioned<Type>& velocity,
    const dimensionedScalar& density
)
{
    // This ensures the velocity has velocity dimensions
    static_assert
    (
        dimensionSet::nDimensions == 7,
        "Velocity must have 7 dimensions"
    );

    return 0.5 * density * sqr(velocity);
}
```

---

## Dimensionless Numbers for R410A Flow (ตัวเลขไร้มิติสำหรับการไหลของ R410A)

For R410A evaporator simulation, key dimensionless numbers characterize the flow and heat transfer phenomena.

### Reynolds Number (จำนวนไรน็อลด์)

```cpp
dimensionedScalar Re = dimDensity * velocity * diameter / dimDynamicViscosity;
```

For R410A in tubes:
- Typical range: 10,000 - 100,000 for turbulent flow
- Critical value for transition: ~2300

### Prandtl Number (จำนวนพรันด์ทล์)

```cpp
dimensionedScalar Pr = dimDynamicViscosity * dimSpecificHeatCapacity / dimThermalConductivity;
```

For R410A:
- Liquid phase: Pr ≈ 4-6 at evaporator conditions
- Vapor phase: Pr ≈ 0.7-1.0

### Nusselt Number (จำนวนนัสเซลต์)

```cpp
dimensionedScalar Nu = dimHeatTransfer * diameter / dimThermalConductivity;
```

For R410A flow condensation:
- Dittus-Boelter equation: Nu = 0.023 × Re^0.8 × Pr^0.4
- Shah correlation for condensation: Nu = 0.023 × Re^0.8 × Pr^0.4

### Bond Number (จำนวนบอนด์)

```cpp
dimensionedScalar Bo = (dimDensity - dimVapor) * gravity * surfaceTension / pow(density, 2);
```

For R410A:
- Characterizes gravity vs. surface tension forces
- Important for flow regime prediction

### Implementation Example (ตัวอย่างการใช้งาน)

```cpp
// Calculate dimensionless numbers for R410A
dimensionedScalar Re =
    rho * U * dimensionedScalar("D", dimLength, 0.01) / mu;

dimensionedScalar Pr =
    mu * dimensionedScalar("Cp", dimSpecificHeatCapacity, 1600.0) / k;

dimensionedScalar Nu_ref = 0.023 * pow(Re, 0.8) * pow(Pr, 0.4);

// Check if flow is turbulent
if (Re.value() > 2300)
{
    Info << "Turbulent flow detected. Re = " << Re << endl;
}
```

---

## Unit Conversion in OpenFOAM (การแปลงหน่วยใน OpenFOAM)

The `unitConversion` class enables automatic unit conversion between different unit systems.

### ⭐ Unit Conversion Architecture (สถาปัตยกรรมการแปลงหน่วย)

```cpp
// File: openfoam_temp/src/OpenFOAM/unitConversion/unitConversion.H:68-111
class unitConversion
{
private:
    // The dimensions
    dimensionSet dimensions_;

    // Array of dimensionless unit exponents
    scalar exponents_[nDimlessUnits];

    // The conversion multiplier
    scalar multiplier_;
};
```

### ⭐ Common Unit Conversions (การแปลงหน่วยทั่วไป)

```cpp
// Temperature: Celsius to Kelvin
unitConversion tempConversion(dimTemperature, 0, 0, 1.0);  // °C to K
dimensionedScalar T_C = dimensionedScalar("T", tempConversion, 25.0);  // 25°C
dimensionedScalar T_K = T_C.value();  // 298.15 K

// Pressure: bar to Pascal
unitConversion pressureConversion(dimPressure, 0, 0, 1e5);  // bar to Pa
dimensionedScalar p_bar = dimensionedScalar("p", pressureConversion, 1.0);  // 1 bar
dimensionedScalar p_Pa = p_bar.value();  // 100000 Pa
```

### ⭐ Using Unit Conversion Templates (ใช้เทมเพลตการแปลงหน่วย)

```cpp
// File: openfoam_temp/src/OpenFOAM/unitConversion/unitConversion.H:165-178
template<class T>
T toStandard(const T&) const;

template<class T>
T toUser(const T&) const;
```

```cpp
// Convert field values to user units
dimensionedScalar T_standard(300.0, dimTemperature);
unitConversion tempOffset(dimTemperature, 0, 0, -273.15);
dimensionedScalar T_user = tempOffset.toUser(T_standard);

Info << "Temperature in user units: " << T_user << endl;
```

### ⭐ Dictionary-Based Unit Configuration (การตั้งค่าหน่วยจาก Dictionary)

```cpp
// In system/controlDict
units
{
    length    "m";
    time      "s";
    mass      "kg";
    temperature "K";
    pressure  "Pa";
    velocity  "m/s";
}

// Read units from dictionary
dimensionedScalar readPressure
(
    "p",
    dict.lookup("pressure"),  // unit specification
    dict                       // dictionary
);
```

---

## R410A Property Dimensional Analysis (การวิเคราะห์มิติคุณสมบัติของ R410A)

### ⭐ R410A Property Units (หน่วยของคุณสมบัติ R410A)

| Property | Dimension | Typical Value |
|---------|-----------|---------------|
| Pressure | [1, -1, -2, 0, 0, 0, 0] | 2000-4000 Pa |
| Temperature | [0, 0, 0, 1, 0, 0, 0] | 258-313 K |
| Density (liquid) | [1, -3, 0, 0, 0, 0, 0] | 1000-1200 kg/m³ |
| Density (vapor) | [1, -3, 0, 0, 0, 0, 0] | 10-50 kg/m³ |
| Dynamic Viscosity | [1, -1, -1, 0, 0, 0, 0] | 1e-5 - 2e-4 Pa·s |
| Specific Heat | [0, 2, -2, -1, 0, 0, 0] | 1000-2000 J/kg·K |
| Thermal Conductivity | [1, 1, -3, -1, 0, 0, 0] | 0.01-0.1 W/m·K |

### ⭐ Example: R410A Property Calculations (ตัวอย่าง: การคำนวณคุณสมบัติ R410A)

```cpp
#include "dimensionedScalar.H"

// R410A properties at evaporator conditions
dimensionedScalar p_evap("p", dimPressure, 2000000.0);  // 20 bar
dimensionedScalar T_evap("T", dimTemperature, 283.0);   // 10°C

// Property correlations
dimensionedScalar rho_liquid = dimensionedScalar("rho_l", dimDensity, 1100.0);
dimensionedScalar rho_vapor = p_evap / (dimensionedScalar("R", dimGasConstant, 0.11) * T_evap);

dimensionedScalar mu_liquid = dimensionedScalar("mu_l", dimDynamicViscosity, 1.5e-4);
dimensionedScalar mu_vapor = dimensionedScalar("mu_v", dimDynamicViscosity, 1.2e-5);

dimensionedScalar k_liquid = dimensionedScalar("k_l", dimThermalConductivity, 0.08);
dimensionedScalar k_vapor = dimensionedScalar("k_v", dimThermalConductivity, 0.01);

dimensionedScalar Cp_liquid = dimensionedScalar("Cp_l", dimSpecificHeatCapacity, 1800.0);
dimensionedScalar Cp_vapor = dimensionedScalar("Cp_v", dimSpecificHeatCapacity, 1200.0);

// Dimensionless numbers
dimensionedScalar Pr_liquid = mu_liquid * Cp_liquid / k_liquid;
dimensionedScalar Pr_vapor = mu_vapor * Cp_vapor / k_vapor;

// Quality calculation
dimensionedScalar x = dimensionedScalar("quality", dimless, 0.5);
```

### ⭐ Property Consistency Checks (การตรวจสอบความสอดคล้องของคุณสมบัติ)

```cpp
// Ensure pressure-temperature consistency
dimensionedScalar p_sat = saturationPressure(T_evap);
if (mag(p_evap - p_sat) > 0.1 * p_evap)
{
    Warning << "Pressure not consistent with saturation pressure!" << endl;
}

// Check density consistency
dimensionedScalar rho_total = 1.0 / (x/rho_vapor + (1-x)/rho_liquid);
```

### ⭐ Two-Flow Rate Calculations (การคำนวณอัตราการไหลสองเฟส)

```cpp
// Mass flow rates
dimensionedScalar mdot_total = dimensionedScalar("mdot", dimMassFlux, 0.1);
dimensionedScalar mdot_liquid = mdot_total * (1 - x);
dimensionedScalar mdot_vapor = mdot_total * x;

// Volumetric flow rates
dimensionedScalar Qdot_liquid = mdot_liquid / rho_liquid;
dimensionedScalar Qdot_vapor = mdot_vapor / rho_vapor;

// Superficial velocities
dimensionedScalar G = dimensionedScalar("G", dimMassFlux, 400.0);  // Mass flux
dimensionedScalar U_sl = G * (1 - x) / rho_liquid;  // Liquid superficial velocity
dimensionedScalar U_sv = G * x / rho_vapor;         // Vapor superficial velocity

dimensionedScalar U_mixture = U_sl + U_sv;
```

---

## Summary (สรุป)

### Key Points (จุดสำคัญ)

1. ⭐ Dimensional analysis is enforced at compile-time in OpenFOAM
2. ⭐ The `dimensionSet` class represents 7-dimensional SI units
3. ⭐ `dimensioned` types ensure dimensional consistency during operations
4. ⭐ Dimensionless numbers characterize R410A flow physics
5. ⭐ Unit conversion enables flexible input/output handling

### Best Practices (แนวที่ดีที่สุด)

1. Always use dimensioned types for physical quantities
2. Verify dimensional consistency in complex expressions
3. Use built-in dimension constants when available
4. Document custom dimensions clearly
5. Check unit conversion accuracy for boundary conditions

### Future Topics (หัวข้อในอนาคต)

- User-defined dimension systems
- Custom dimension checking functions
- Extended dimensional analysis for complex physics
- Integration with thermodynamic property libraries

---

*References:*
- OpenFOAM src/OpenFOAM/dimensionSet/
- OpenFOAM src/OpenFOAM/dimensionedTypes/
- OpenFOAM src/OpenFOAM/unitConversion/
- OpenFOAM global/constants/dimensionedConstants.H