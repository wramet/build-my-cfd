# Summary & Exercises

```mermaid
mindmap
  root((Dimensional Analysis))
    dimensionSet
      SI Units (7 Dimensions)
      Exponent Storage
      isDimensionless()
    Arithmetic
      Add/Sub (Match required)
      Mul/Div (Exponent Sum/Diff)
      Pow/Sqrt
    Non-Dimensionalization
      Reference Scales
      Similarity (Re, Fr, Pr)
      Numerical Stability
    Advanced
      Multi-physics Coupling
      Custom Units
      Safety Net Mechanism
```
> **Figure 1:** แผนผังความคิดสรุปองค์ประกอบของการวิเคราะห์มิติ ครอบคลุมทั้งโครงสร้าง dimensionSet กฎพีชคณิตมิติ เทคนิคการทำให้ไร้มิติ และการประยุกต์ใช้ในระบบหลายฟิสิกส์ความปลอดภัยทางฟิสิกส์ไม่ส่งผลกระทบต่อความเร็วในการจำลอง ผ่านการใช้พลังของ C++ Template Metaprogramming ในการตรวจสอบความสอดคล้องทางมิติทั้งหมดที่ขั้นตอนการคอมไพล์โปรแกรมเพียงครั้งเดียว

---

## 12.9. Summary: The Dimensional Safety Net

The OpenFOAM dimensional analysis system represents a foundational advancement in computational fluid dynamics safety and reliability, catching dimensional inconsistencies from the earliest stages of compilation or runtime initialization.

### Core Benefits of the Dimensional System

1. **Automatic Consistency Checking**: Prevents physically meaningless operations such as adding pressure to velocity
2. **Type-Level Physical Safety**: Embeds physical dimensions directly into the C++ type system to verify conservation laws in governing equations
3. **Non-Dimensionalization Support**: Facilitates improved numerical stability and enables similarity analysis
4. **Multi-Physics Integration**: Manages interactions between disparate physical domains (e.g., FSI, MHD) rigorously

> [!INFO] Key Principle
> The dimensional analysis system operates at **both compile-time and runtime** to automatically verify that all mathematical operations are dimensionally consistent, preventing unit conversion errors and physically invalid calculations.

### Fundamental Dimensional Algebra Rules

| Operation | Dimensional Requirement | Example |
|-----------|------------------------|---------|
| Addition/Subtraction | Identical dimensions in all 7 positions | `p + p` |
| Multiplication/Division | Exponents add/subtract algebraically | `velocity * time = length` |
| Power Operations | Exponent multiplied by power value | `length^2 = area` |
| Intrinsic Functions | Arguments must be **dimensionless** | `sin(angle)`, `exp(T/Tref)` |

### Conservation Law Verification

The dimensional system helps verify that conservation laws are correctly implemented by ensuring each term in a conservation equation has identical dimensions.

**Mass Conservation:**
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

**Dimensional Check:**
- $\frac{\partial \rho}{\partial t}$: $[M \, L^{-3} \, T^{-1}]$
- $\nabla \cdot (\rho \mathbf{u})$: $[M \, L^{-3} \, T^{-1}]$

**Momentum Conservation:**
$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

**Dimensional Check:**
- All terms: $[M \, L^{-2} \, T^{-2}]$ (force per volume)

### Multi-Physics Integration Benefits

In complex multi-physics simulations, the dimensional safety net becomes even more valuable as it manages interactions between different physical domains:

```cpp
// Multi-physics coupling with automatic dimensional checking
// Heat transfer affects fluid properties through temperature-dependent viscosity
volScalarField muEff(mu(T));          // Temperature-dependent viscosity
volScalarField alpha(k/(rho*cp));     // Thermal diffusivity

// Buoyancy force with correct dimensions
volVectorField gBuoyancy(rhok * g * T); // [kg/(m²·s²)]
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
โค้ดตัวอย่างนี้แสดงการใช้ระบบ dimensional analysis ใน OpenFOAM เพื่อตรวจสอบความสอดคล้องของหน่วยในระบบ multi-physics แต่ละบรรทัดมีการดำเนินการทางฟิสิกส์ที่ต้องการหน่วยที่ถูกต้อง:

- **บรรทัดที่ 2**: `muEff` คำนวณค่า viscosity ที่ขึ้นกับอุณหภูมิ โดยระบบจะตรวจสอบว่าผลลัพธ์มีหน่วยของ dynamic viscosity [Pa·s] หรือ [M·L⁻¹·T⁻¹] อย่างถูกต้อง
- **บรรทัดที่ 3**: `alpha` คำนวณ thermal diffusivity จากสมการ k/(ρ·cp) โดยระบบจะยืนยันว่าผลลัพธ์มีหน่วย [m²/s] หรือ [L²·T⁻¹] 
- **บรรทัดที่ 6**: `gBuoyancy` คำนวณแรงลอยตัวจากความโน้มถ่วง โดยผลลัพธ์ต้องมีหน่วยของ force per volume [N/m³] หรือ [M·L⁻²·T⁻²] ซึ่งระบบจะตรวจสอบให้โดยอัตโนมัติ

**🔑 Key Concepts:**
- **Compile-time Dimensional Checking**: ระบบตรวจสอบหน่วยขณะคอมไพล์ ป้องกันการดำเนินการที่ไม่สอดคล้องกันทางมิติ
- **Type-Safe Physics Operations**: แต่ละ field มีข้อมูล dimension แนบอยู่ ป้องกันการบวกลบปริมาณที่มีหน่วยต่างกัน
- **Multi-Physics Coupling**: ระบบจัดการการเชื่อมต่อระหว่างฟิสิกส์หลายสาขา (heat transfer, fluid dynamics) อย่างปลอดภัย

**Development Efficiency:**
| Benefit | Description | Impact |
|---------|-------------|--------|
| **Early Error Detection** | Problems caught during compilation | Reduces wasted computation time |
| **Precise Error Identification** | Exact location of dimensional inconsistency | Accelerates problem resolution |
| **Reduced Trial and Error** | Systematic checking instead of guessing unit conversions | Increases code reliability |

**Simulation Reliability:**
- **Physical Correctness**: Results guaranteed to be dimensionally consistent
- **Reproducibility**: Eliminates unit-related sources of variation between simulations
- **Verification Support**: Provides mathematical foundation for code verification procedures

---

## Exercises

### Part 1: Basic Dimensional Analysis

Write the 7-position exponent array (`M L T Theta N I J`) for the following quantities:

1. **Force**: $F = m \cdot a$
2. **Energy**: $E = F \cdot d$
3. **Kinematic Viscosity ($\nu$)**: Units are $m^2/s$
4. **Mass Flow Rate**: Units are $kg/s$

<details>
<summary>💡 Solution - Part 1</summary>

1. **Force**: `[1 1 -2 0 0 0 0]` (Newton: $kg \cdot m/s^2$)
2. **Energy**: `[1 2 -2 0 0 0 0]` (Joule: $kg \cdot m^2/s^2$)
3. **Kinematic Viscosity**: `[0 2 -1 0 0 0 0]` ($m^2/s$)
4. **Mass Flow Rate**: `[1 0 -1 0 0 0 0]` ($kg/s$)

</details>

---

### Part 2: Consistency Verification

A simplified momentum equation is:
$$\frac{\mathbf{U}}{\Delta t} + \mathbf{U} \cdot \nabla \mathbf{U} = -\frac{\nabla p}{\rho}$$

**Question**: Prove whether the units of the leftmost term ($\mathbf{U}/\Delta t$) and the rightmost term ($\nabla p / \rho$) are equal. (Show the exponents)

<details>
<summary>💡 Solution - Part 2</summary>

**Leftmost term analysis ($\mathbf{U}/\Delta t$):**
- $\mathbf{U}$: $[L \, T^{-1}]$ (velocity)
- $\Delta t$: $[T]$ (time)
- **Result**: $[L \, T^{-1}] / [T] = [L \, T^{-2}]$ (Acceleration)

**Rightmost term analysis ($\nabla p / \rho$):**
- $\nabla p$: $[M \, L^{-1} \, T^{-2}] / [L] = [M \, L^{-2} \, T^{-2}]$
- $\rho$: $[M \, L^{-3}]$
- **Result**: $[M \, L^{-2} \, T^{-2}] / [M \, L^{-3}] = [L \, T^{-2}]$ (Acceleration)

**Conclusion**: ✓ Both terms have identical dimensions $[L \, T^{-2}]$

</details>

---

### Part 3: Application Scenario

You are solving flow around a cylinder and find that results from coarse and fine grids give vastly different pressure values:

- If you switch to comparing in terms of the **pressure coefficient ($C_p$)**, which is dimensionless, what trend would you see?
- Write OpenFOAM code to calculate `Cp` from `p`, `p_inf`, `rho`, and `U_inf`

<details>
<summary>💡 Solution - Part 3</summary>

**Trend Observation:**
- You would see that $C_p$ **converges to the same value** even though raw pressures differ (grid independence study)
- Non-dimensional coefficients eliminate scaling differences and reveal the underlying physics

**OpenFOAM Code Implementation:**

```cpp
// Read reference quantities from transport properties dictionary
dimensionedScalar p_inf(
    "p_inf", 
    dimPressure, 
    readScalar(transportProperties.lookup("p_inf"))
);

dimensionedScalar rho(
    "rho", 
    dimDensity, 
    readScalar(transportProperties.lookup("rho"))
);

dimensionedScalar U_inf(
    "U_inf", 
    dimVelocity, 
    readScalar(transportProperties.lookup("U_inf"))
);

// Calculate pressure coefficient using Bernoulli equation
// Cp = (p - p_inf) / (0.5 * rho * U_inf^2)
volScalarField Cp
(
    IOobject("Cp", runTime.timeName(), mesh),
    (p - p_inf) / (0.5 * rho * sqr(U_inf))
);

Cp.write();  // Output field for post-processing
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
โค้ดนี้แสดงการคำนวณ pressure coefficient ($C_p$) ซึ่งเป็นปริมาณไร้มิติที่ใช้ในการวิเคราะห์ผลลัพธ์จากการจำลอง CFD:

- **บรรทัดที่ 2-4**: ประกาศ `p_inf` ซึ่งเป็น reference pressure โดยระบุ `dimPressure` เพื่อให้แน่ใจว่ามีหน่วย [Pa] หรือ [M·L⁻¹·T⁻²] ถูกต้อง
- **บรรทัดที่ 6-8**: ประกาศ `rho` (density) และ `U_inf` (reference velocity) พร้อมระบุหน่วยให้ถูกต้อง
- **บรรทัดที่ 15-18**: คำนวณ $C_p$ จากสมการ $(p - p_\infty) / (0.5 \cdot \rho \cdot U_\infty^2)$ โดยระบบจะตรวจสอบว่าตัวหารและตัวตั้งมีหน่วยเหมือนกัน ทำให้ $C_p$ ไร้มิติโดยอัตโนมัติ

**🔑 Key Concepts:**
- **Non-Dimensionalization**: การแปลงปริมาณมิติให้เป็นไร้มิติช่วยให้เปรียบเทียบผลลัพธ์จาก mesh ต่างกันได้
- **Automatic Dimensional Verification**: ระบบตรวจสอบว่าสมการ $C_p$ ให้ผลลัพธ์ไร้มิติเสมอ
- **Grid Independence Study**: การใช้ค่าไร้มิติช่วยตรวจสอบว่า mesh ละเอียดพอแล้วหรือยัง

**Dimensional Verification:**
- Numerator: $(p - p_\infty)$ → $[M \, L^{-1} \, T^{-2}]$
- Denominator: $0.5 \cdot \rho \cdot U_\infty^2$ → $[M \, L^{-3}] \cdot [L^2 \, T^{-2}] = [M \, L^{-1} \, T^{-2}]$
- **Result**: $C_p$ is dimensionless as required

</details>

---

### Part 4: Advanced Multi-Physics Challenge

For a magnetohydrodynamics (MHD) simulation, you need to verify dimensional consistency for the Lorentz force term:

$$\mathbf{F}_L = \mathbf{J} \times \mathbf{B}$$

Where:
- $\mathbf{J}$ = current density ($A/m^2$)
- $\mathbf{B}$ = magnetic field (Tesla)

**Tasks:**
1. Determine the dimensions of the Lorentz force per unit volume
2. Write OpenFOAM code to declare these fields with proper dimensions
3. Show how the dimensional system prevents mixing electric and magnetic fields incorrectly

<details>
<summary>💡 Solution - Part 4</summary>

**1. Dimensional Analysis:**

| Quantity | Symbol | Dimensions | SI Unit |
|----------|--------|------------|---------|
| Current Density | $\mathbf{J}$ | $[I \, L^{-2}]$ | $A/m^2$ |
| Magnetic Field | $\mathbf{B}$ | $[M \, T^{-2} \, I^{-1}]$ | Tesla |
| Lorentz Force Density | $\mathbf{F}_L$ | $[M \, L^{-2} \, T^{-2}]$ | $N/m^3$ |

**Verification:**
$$[\mathbf{J} \times \mathbf{B}] = [I \, L^{-2}] \cdot [M \, T^{-2} \, I^{-1}] = [M \, L^{-2} \, T^{-2}]$$

**2. OpenFOAM Implementation:**

```cpp
// Define custom electromagnetic dimensions for MHD simulation
// dimensionSet(Mass, Length, Time, Temperature, Moles, Current, LuminousIntensity)
dimensionSet dimCurrentDensity(0, -2, 0, 0, 0, 1, 0);      // [I·L⁻²] = [A/m²]
dimensionSet dimMagneticField(1, 0, -2, 0, 0, -1, 0);      // [M·T⁻²·I⁻¹] = [Tesla]
dimensionSet dimForceDensity(1, -2, -2, 0, 0, 0, 0);       // [M·L⁻²·T⁻²] = [N/m³]

// Declare electromagnetic fields with proper dimensions
volVectorField J
(
    IOobject("J", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimCurrentDensity
);

volVectorField B
(
    IOobject("B", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimMagneticField
);

// Calculate Lorentz force using cross product operator (^)
// The dimensional system automatically verifies that J × B yields force density
volVectorField F_L("F_L", J ^ B);  

// Runtime dimensional verification
if (!F_L.dimensions().matches(dimForceDensity))
{
    FatalErrorIn("calculateLorentzForce")
        << "Lorentz force has incorrect dimensions: " << F_L.dimensions()
        << "Expected: " << dimForceDensity
        << exit(FatalError);
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
โค้ดนี้แสดงการประยุกต์ใช้ระบบ dimensional analysis ในการจำลอง Magnetohydrodynamics (MHD) ซึ่งเป็น multi-physics ที่รวม electromagnetism กับ fluid dynamics:

- **บรรทัดที่ 2-4**: นิยามหน่วย custom สำหรับ current density โดยใช้ `dimensionSet(0, -2, 0, 0, 0, 1, 0)` ซึ่งแทนหน่วย [I·L⁻²] = [A/m²] ตามลำดับ (Mass, Length, Time, Temperature, Moles, Current, LuminousIntensity)
- **บรรทัดที่ 5**: นิยามหน่วย magnetic field [Tesla] ซึ่งมีค่าเท่ากับ [M·T⁻²·I⁻¹]
- **บรรทัดที่ 6**: นิยามหน่วย force density [N/m³] หรือ [M·L⁻²·T⁻²] เพื่อใช้ในการตรวจสอบผลลัพธ์
- **บรรทัดที่ 9-14**: ประกาศ field `J` (current density) และ `B` (magnetic field) โดยระบุ dimension ที่ถูกต้อง ซึ่งป้องกันการกำหนดค่าผิดพลาด
- **บรรทัดที่ 19**: คำนวณ Lorentz force ด้วย cross product operator (`^`) ซึ่งระบบจะตรวจสอบ dimension อัตโนมัติว่าผลลัพธ์มีหน่วยของ force density ถูกต้อง
- **บรรทัดที่ 22-28**: มีการตรวจสอบ dimension เพิ่มเติมขณะ runtime เพื่อความมั่นใจในกรณีที่มีการคำนวณที่ซับซ้อน

**🔑 Key Concepts:**
- **Custom Dimension Sets**: สามารถนิยามหน่วย custom สำหรับฟิสิกส์เฉพาะทาง (electromagnetism) ได้
- **Cross Product Dimensional Rules**: operator `^` (cross product) ทำงานร่วมกับระบบ dimensional เพื่อตรวจสอบหน่วย
- **Multi-Physics Safety**: ระบบป้องกันการผสมผสานปริมาณทางฟิสิกส์ที่ไม่สอดคล้องกัน เช่น การบวก current density กับ magnetic field

**3. Error Prevention:**

The dimensional system prevents these common errors:

```cpp
// ❌ ERROR: Caught by compiler or runtime
// volScalarField invalid = J + B;  
// Cannot add current density to magnetic field (dimensional mismatch)

// ❌ ERROR: Dimension mismatch detected
// volVectorField wrongForce = J * B;  
// Wrong operator - should be cross product for vector multiplication

// ❌ ERROR: Type system prevents mixing incompatible dimensions
// volVectorField badField = J * dimensionedScalar("bad", dimPressure, 1.0);
// Current density cannot multiply with pressure

// ✓ CORRECT: Proper cross product with automatic dimensional validation
volVectorField lorentzForce = J ^ B;  
// Dimensions automatically verified to produce force density
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
ตัวอย่างนี้แสดงประเภทข้อผิดพลาดที่ระบบ dimensional analysis สามารถป้องกันได้ในการจำลอง MHD:

- **บรรทัดที่ 2-3**: พยายามบวก current density (`J`) กับ magnetic field (`B`) ซึ่งมีหน่วยต่างกัน → ระบบจะปฏิเสธเนื่องจาก dimensional mismatch
- **บรรทัดที่ 6-7**: ใช้ multiplication operator (`*`) แทน cross product (`^`) → ผิดทางคณิตศาสตร์และอาจให้หน่วยที่ผิด
- **บรรทัดที่ 10-11**: พยายามคูณ current density กับ pressure ซึ่งไม่มีความสัมพันธ์ทางฟิสิกส์ → ระบบป้องกันการดำเนินการที่ไม่สอดคล้องกัน
- **บรรทัดที่ 15**: การใช้ cross product operator (`^`) อย่างถูกต้อง → ระบบตรวจสอบ dimension และยืนยันผลลัพธ์

**🔑 Key Concepts:**
- **Type-Safe Physics**: แต่ละ field มี "type" ทางฟิสิกส์แนบอยู่ ป้องกันการดำเนินการที่ไม่สมเหตุสมผล
- **Operator Overloading with Dimension Awareness**: operator ทางคณิตศาสตร์ (`+`, `-`, `*`, `^`) ตรวจสอบ dimension อัตโนมัติ
- **Multi-Physics Discipline**: ระบบบังคับให้ผู้ใช้คำนึงถึงความสอดคล้องทางฟิสิกส์เสมอ

</details>

---

### Part 5: Non-Dimensional Solver Implementation

Create a non-dimensional form of the incompressible Navier-Stokes equations for flow around an obstacle.

**Reference quantities:**
- $L_{ref} = 1.0$ m (characteristic length)
- $U_{ref} = 10.0$ m/s (characteristic velocity)
- $\nu = 1.5 \times 10^{-5}$ m²/s (kinematic viscosity)

**Tasks:**
1. Calculate the Reynolds number
2. Write the non-dimensional momentum equation
3. Implement boundary conditions in non-dimensional form

<details>
<summary>💡 Solution - Part 5</summary>

**1. Reynolds Number Calculation:**

$$Re = \frac{U_{ref} \cdot L_{ref}}{\nu} = \frac{10.0 \times 1.0}{1.5 \times 10^{-5}} \approx 666,667$$

**2. Non-Dimensional Momentum Equation:**

$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{Re} \nabla^{*2} \mathbf{u}^*$$

Where:
- $\mathbf{u}^* = \mathbf{u} / U_{ref}$ (dimensionless velocity)
- $p^* = p / (\rho U_{ref}^2)$ (dimensionless pressure)
- $t^* = t \cdot U_{ref} / L_{ref}$ (dimensionless time)
- $\nabla^* = L_{ref} \cdot \nabla$ (dimensionless gradient)

**3. OpenFOAM Implementation:**

```cpp
// createNonDimensionalFields.H
// Define reference quantities for non-dimensionalization
dimensionedScalar LRef("LRef", dimLength, 1.0);    // Reference length [m]
dimensionedScalar URef("URef", dimVelocity, 10.0); // Reference velocity [m/s]
dimensionedScalar nuRef("nuRef", dimKinematicViscosity, 1.5e-5); // Kinematic viscosity [m²/s]

// Calculate Reynolds number (automatically dimensionless)
// Re = (U_ref * L_ref) / ν
dimensionedScalar Re(
    "Re", 
    dimless,  // Explicitly mark as dimensionless
    URef * LRef / nuRef
);

Info << "Reynolds number: " << Re.value() << endl;

// Create non-dimensional velocity field
// u* = u / U_ref (automatically dimensionless due to dimensional division)
volVectorField Ustar
(
    IOobject("Ustar", runTime.timeName(), mesh),
    U / URef  // Dimensional division yields dimensionless field
);

// Create non-dimensional pressure field
// p* = p / (ρ * U_ref²)
volScalarField pstar
(
    IOobject("pstar", runTime.timeName(), mesh),
    p / (rho * sqr(URef))  // sqr(URef) gives [m²/s²]
);
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
โค้ดนี้แสดงการสร้าง field ไร้มิติ (non-dimensional fields) สำหรับการจำลอง CFD โดยใช้ reference quantities:

- **บรรทัดที่ 2-4**: นิยาม reference length `LRef`, reference velocity `URef`, และ kinematic viscosity `nuRef` โดยระบุ dimension ให้ถูกต้องตามหน่วย SI
- **บรรทัดที่ 7-11**: คำนวณ Reynolds number โดยระบบจะตรวจสอบว่า `(URef * LRef) / nuRef` ให้ผลลัพธ์ไร้มิติ หากไม่สอดคล้องจะเกิด error ขณะคอมไพล์
- **บรรทัดที่ 15-19**: สร้าง non-dimensional velocity field `Ustar` โดยหาร velocity ด้วย `URef` ซึ่งระบบจะตรวจสอบว่าผลลัพธ์ไร้มิติ
- **บรรทัดที่ 22-26**: สร้าง non-dimensional pressure field `pstar` โดยใช้ `sqr(URef)` ซึ่งสร้าง [m²/s²] และคูณกับ density เพื่อให้ได้หน่วย pressure ที่เข้ากันได้

**🔑 Key Concepts:**
- **Reference Scales**: การกำหนด reference quantities ช่วยแปลงปัญหามิติให้เป็นไร้มิติ
- **Automatic Dimensionless Creation**: การหารหรือคูณปริมาณที่มีหน่วยเดียวกันสร้างค่าไร้มิติโดยอัตโนมัติ
- **Reynolds Number Parameter**: ค่า Re เป็นพารามิเตอร์เดียวที่ควบคุมฟิสิกส์ของปัญหาไร้มิติ
- **Numerical Advantages**: การแก้สมการไร้มิติช่วยปรับปรุง conditioning ของระบบ linear

**Non-Dimensional Boundary Conditions (`0/Ustar`):**

```cpp
dimensions      [0 0 0 0 0 0 0];  // Explicitly dimensionless

internalField   uniform (1 0 0);  // U/U_ref = 1 at inlet (normalized)

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1 0 0);  // Non-dimensional inlet: u*/U* = 1
    }
    outlet
    {
        type            zeroGradient;  // ∂u*/∂n = 0
    }
    walls
    {
        type            fixedValue;
        value           uniform (0 0 0);  // No-slip condition in non-dimensional form
    }
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
ไฟล์ boundary condition นี้แสดงการใช้ non-dimensional values สำหรับการจำลอง:

- **บรรทัดที่ 1**: ระบุ `dimensions [0 0 0 0 0 0 0]` เพื่อประกาศอย่างชัดเจนว่า field นี้ไร้มิติ ซึ่งช่วยให้ OpenFOAM ตรวจสอบความสอดคล้องได้
- **บรรทัดที่ 3**: `internalField` มีค่า `(1 0 0)` ซึ่งแทนค่า velocity ที่ normalize แล้ว (u/U_ref = 1)
- **บรรทัดที่ 7-10**: Inlet boundary condition กำหนดค่า `(1 0 0)` ซึ่งหมายความว่า normalized velocity ที่ inlet มีค่า 1 ในทิศทาง x
- **บรรทัดที่ 11-14**: Outlet ใช้ `zeroGradient` ซึ่งหมายความว่า gradient ของ velocity ไร้มิติในทิศทางปกติเป็นศูนย์
- **บรรทัดที่ 15-20**: Walls ใช้ `fixedValue (0 0 0)` ซึ่งแทน no-slip condition ในรูปแบบไร้มิติ

**🔑 Key Concepts:**
- **Non-Dimensional BCs**: ค่า boundary conditions ไร้มิติทำให้ผลลัพธ์ scale ได้ง่าย
- **Normalization**: การ normalize ค่า boundary conditions ช่วยลดความซับซ้อนของ setup
- **Physical Similarity**: การใช้ non-dimensional BCs ทำให้สามารถเปรียบเทียบกรณีที่ geometrically similar ได้

**Non-Dimensional Momentum Equation (`UEqn.H`):**

```cpp
// UEqn.H - Non-dimensional form of Navier-Stokes
// The momentum equation is:
// ∂u*/∂t* + (u*·∇*)u* = -∇*p* + (1/Re)∇*²u*
{
    // Build the non-dimensional momentum equation matrix
    fvVectorMatrix UstarEqn
    (
        // Time derivative term: ∂u*/∂t*
        fvm::ddt(Ustar)                      
        
        // Convective term: (u*·∇*)u*
        // phiStar is the non-dimensional flux
      + fvm::div(phiStar, Ustar)             
        
        // Diffusive term: (1/Re)∇*²u*
        // Note: 1/Re is explicitly non-dimensional
      - fvm::laplacian(
            dimensionedScalar("invRe", dimless, 1.0/Re), 
            Ustar
        )  
    );

    // Relax the equation for improved convergence
    UstarEqn.relax();

    // Solve the momentum equation with pressure gradient
    if (pimple.momentumPredictor())
    {
        // -∇*p* term (pressure gradient)
        solve(UstarEqn == -fvc::grad(pstar));
    }
}
```

---

**📂 Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/populationBalanceModel/populationBalanceModel/populationBalanceModel.C`

**📋 Explanation:**
ไฟล์ `UEqn.H` นี้แสดงการ implement non-dimensional momentum equation ใน OpenFOAM:

- **บรรทัดที่ 2**: แสดงสมการไร้มิติที่จะแก้: ∂u*/∂t* + (u*·∇*)u* = -∇*p* + (1/Re)∇*²u*
- **บรรทัดที่ 5**: สร้าง `fvVectorMatrix` สำหรับแก้สมการ momentum ไร้มิติ
- **บรรทัดที่ 8**: `fvm::ddt(Ustar)` แทน time derivative term (∂u*/∂t*) ซึ่งไร้มิติ
- **บรรทัดที่ 11-12**: `fvm::div(phiStar, Ustar)` แทน convective term ((u*·∇*)u*) โดย `phiStar` คือ non-dimensional flux
- **บรรทัดที่ 15-18**: `fvm::laplacian` แทน diffusive term ((1/Re)∇*²u*) โดยระบุค่าสัมประสิทธิ์ `1/Re` ซึ่งไร้มิติชัดเจน
- **บรรทัดที่ 21**: `relax()` ใช้ under-relaxation เพื่อปรับปรุงการลู่เข้าของวิธี iterative
- **บรรทัดที่ 24-27**: แก้สมการ momentum ร่วมกับ pressure gradient term (-∇*p*)

**🔑 Key Concepts:**
- **Non-Dimensional Operators**: `fvm::ddt`, `fvm::div`, `fvm::laplacian` ทำงานกับ field ไร้มิติได้โดยตรง
- **Reynolds Number as Coefficient**: 1/Re เป็นพารามิเตอร์เดียวที่ควบคุม viscous effects
- **SIMPLE/PIMPLE Algorithm**: การแก้ pressure-velocity coupling ยังคงใช้ได้กับสมการไร้มิติ
- **Numerical Stability**: การทำให้ไร้มิติช่วยปรับปรุง conditioning ของระบบ linear

**Advantages of Non-Dimensional Form:**
- **Single Parameter Control**: พารามิเตอร์เดียว (Re) ควบคุมฟิสิกส์ทั้งหมด
- **Scalability**: ผลลัพธ์ scale ได้ง่ายสำหรับปัญหา geometrically similar ใดๆ
- **Improved Numerical Conditioning**: ค่าไร้มิติมังอยู่ในช่วง O(1) ซึ่งดีต่อ solver
- **Direct Experimental Comparison**: สามารถเปรียบเทียบกับข้อมูลทดลองโดยตรง

</details>

---

## Key Takeaways

> [!TIP] Best Practices
> 1. **Always declare dimensions explicitly** when creating fields or constants
> 2. **Use `dimensionSet::matches()`** for runtime dimensional validation
> 3. **Document reference scales** when using non-dimensional formulations
> 4. **Let OpenFOAM handle unit conversions** automatically through the dimensional system
> 5. **Test with known units** to verify solver implementations

> [!WARNING] Common Pitfalls
> - Mixing dimensionless volume fractions ($\alpha$) with dimensional densities ($\rho$)
> - Forgetting that `sin()`, `exp()`, `log()` require dimensionless arguments
> - Losing dimensional information when implementing non-dimensional solvers
> - Incorrect boundary condition dimensions in case files

The dimensional analysis system in OpenFOAM provides a **mathematical foundation for reliable CFD simulations**, ensuring that both numerical accuracy and physical meaning are maintained throughout the computational process.