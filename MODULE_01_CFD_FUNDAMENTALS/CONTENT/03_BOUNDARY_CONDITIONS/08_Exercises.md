# แบบฝึกหัด Boundary Conditions

> **Learning Objectives**
>
> หลังจากฝึกหัดทั้งหมดนี้ คุณจะสามารถ:
> - **เขียน BC files ใน directory `0/`** สำหรับสถานการณ์จริง (velocity, pressure, thermal)
> - **คำนวณ turbulence inlet values** (k, ε, ω) จากพารามิเตอร์ flow
> - **แก้ไข BC errors** ที่พบบ่อย (backflow, over-specification, wrong types)
> - **เลือก BC type ที่เหมาะสม** จากสถานการณ์ที่กำหนด
> - **ตรวจสอบ solution correctness** ด้วย verification checklist
>
> **Prerequisites:** ควรอ่าน 01-06 ก่อน เพื่อเข้าใจ BC types และ formulation

---

## ภาพรวมแบบฝึกหัด (WHAT)

แบบฝึกหัดเชิงปฏิบัติสำหรับการตั้งค่า BC ใน OpenFOAM เน้นฝึก:
1. **Basic BC Setup** — แบบฝึกหัด 1-2: พื้นฐาน velocity/pressure/thermal
2. **Turbulence BCs** — แบบฝึกหัด 3: คำนวณและตั้งค่า k-ε model
3. **Advanced Scenarios** — แบบฝึกหัด 4-5: backflow, convection
4. **Debugging Skills** — แบบฝึกหัด 6: หาและแก้ error
5. **Time-Varying BCs** — แบบฝึกหัด 7: BC ขึ้นกับเวลา

---

## Exercise Summary Table

| # | แบบฝึกหัด | ระดับ | เวลา | แนวคิดที่ทดสอบ | BC Types ที่ใช้ |
|---|------------|--------|-------|-----------------|------------------|
| 1 | Pipe Flow | ⭐ Basic | 10 นาที | Inlet/outlet pairing | fixedValue, zeroGradient, noSlip |
| 2 | Heat Transfer | ⭐ Basic | 10 นาที | Thermal BCs | fixedValue, zeroGradient (adiabatic) |
| 3 | Turbulent Flow | ⭐⭐ Intermediate | 20 นาที | Turbulence calculations | Wall functions, calculated |
| 4 | Backflow Problem | ⭐⭐ Intermediate | 15 นาที | Outlet stability | inletOutlet, pressureInletOutletVelocity |
| 5 | Convective Wall | ⭐⭐ Intermediate | 15 นาที | Robin BC, heat transfer | externalWallHeatFlux, mixed |
| 6 | Debug Errors | ⭐⭐⭐ Advanced | 20 นาที | Error diagnosis | Multiple corrections |
| 7 | Time-Varying Inlet | ⭐⭐⭐ Advanced | 25 นาที | Transient BCs | uniformFixedValue, codedFixedValue |

---

## แบบฝึกหัด 1: Pipe Flow — Basic Velocity/Pressure

**⭐ ระดับ Basic — ประมาณ 10 นาที**

### Learning Goal
ฝึกตั้งค่า BC พื้นฐานสำหรับ incompressible flow แบบง่าย

### โจทย์

ตั้งค่า BC สำหรับการไหลในท่อกลม:
- **Inlet:** Velocity = 1 m/s ในทิศทาง x
- **Outlet:** Atmospheric pressure (reference = 0)
- **Wall:** No-slip

### คำแนะนำ

1. พิจารณา continuity equation — ถ้า inlet กำหนด velocity (Dirichlet) outlet ควรกำหนด pressure (Dirichlet)
2. U ที่ wall ใช้ `noSlip` หรือ `fixedValue (0 0 0)` ก็ได้
3. p ที่ inlet/outlet ใช้ `zeroGradient` เมื่อ U เป็น Dirichlet

### Solution Verification Checklist
- [ ] Inlet U: `fixedValue (1 0 0)` ✓
- [ ] Outlet U: `zeroGradient` ✓
- [ ] Wall U: `noSlip` หรือ `fixedValue (0 0 0)` ✓
- [ ] Inlet p: `zeroGradient` ✓
- [ ] Outlet p: `fixedValue 0` ✓
- [ ] Wall p: `zeroGradient` ✓
- [ ] Dimensions ถูกต้อง: U `[0 1 -1 0 0 0 0]`, p `[0 2 -2 0 0 0 0]` ✓

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// 0/U
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (1 0 0);
    }
    outlet
    {
        type    zeroGradient;
    }
    wall
    {
        type    noSlip;
    }
}

// 0/p
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type    zeroGradient;
    }
    outlet
    {
        type    fixedValue;
        value   uniform 0;
    }
    wall
    {
        type    zeroGradient;
    }
}
```
</details>

---

## แบบฝึกหัด 2: Heat Transfer — Thermal BCs

**⭐ ระดับ Basic — ประมาณ 10 นาที**

### Learning Goal
ฝึกตั้งค่า BC สำหรับ heat convection — Dirichlet (fixed T) และ adiabatic (zero gradient)

### โจทย์

ตั้งค่า BC สำหรับ heat transfer ใน channel:
- **Inlet:** T = 300 K
- **Outlet:** Zero gradient (fully developed)
- **Top wall:** Fixed T = 400 K (heated)
- **Bottom wall:** Adiabatic (insulated)

### คำแนะนำ

1. Adiabatic = ไม่มี heat flux = `zeroGradient` สำหรับ T
2. Outlet thermal BC มักใช้ `zeroGradient` เมื่อ flow ออกนอก domain
3. `fixedValue` สำหรับ T ที่ wall คือ Dirichlet BC (prescribed temperature)

### Solution Verification Checklist
- [ ] Inlet T: `fixedValue 300` ✓
- [ ] Outlet T: `zeroGradient` ✓
- [ ] Top wall T: `fixedValue 400` ✓
- [ ] Bottom wall T: `zeroGradient` (adiabatic) ✓
- [ ] Dimensions ถูกต้อง: T `[0 0 0 1 0 0 0]` ✓

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// 0/T
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}
dimensions      [0 0 0 1 0 0 0];
internalField   uniform 300;

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform 300;
    }
    outlet
    {
        type    zeroGradient;
    }
    topWall
    {
        type    fixedValue;
        value   uniform 400;
    }
    bottomWall
    {
        type    zeroGradient;
    }
}
```
</details>

---

## แบบฝึกหัด 3: Turbulent Flow — k-ε Calculations

**⭐⭐ ระดับ Intermediate — ประมาณ 20 นาที**

### Learning Goal
คำนวณและตั้งค่า turbulence BCs สำหรับ k-ε model พร้อมใช้ wall functions

### โจทย์

กำหนด turbulence BC สำหรับ k-ε model:
- **Inlet:** Turbulence intensity I = 5%, length scale l = 0.01 m
- **Outlet:** Zero gradient
- **Wall:** Wall functions (kqRWallFunction, epsilonWallFunction, nutkWallFunction)

**สูตรที่ต้องใช้:**
- $k = \frac{3}{2}(UI)^2$ — turbulent kinetic energy
- $\varepsilon = C_\mu^{3/4} \frac{k^{3/2}}{l}$ — dissipation rate
- $C_\mu = 0.09$ — model constant

### คำนวณ k และ ε สำหรับ U = 10 m/s

**Step-by-step:**

```
Given:
I = 0.05 (5%)
U = 10 m/s
l = 0.01 m
Cμ = 0.09

Step 1: Calculate k
k = 1.5 × (U × I)²
  = 1.5 × (10 × 0.05)²
  = 1.5 × (0.5)²
  = 1.5 × 0.25
  = 0.375 m²/s²

Step 2: Calculate ε
ε = Cμ^0.75 × k^1.5 / l
  = 0.09^0.75 × 0.375^1.5 / 0.01
  = 0.164 × 0.229 / 0.01
  = 3.76 m²/s³
```

### Solution Verification Checklist
- [ ] k inlet: `fixedValue 0.375` ✓
- [ ] ε inlet: `fixedValue 3.76` ✓
- [ ] k outlet: `zeroGradient` ✓
- [ ] ε outlet: `zeroGradient` ✓
- [ ] k wall: `kqRWallFunction` ✓
- [ ] ε wall: `epsilonWallFunction` ✓
- [ ] nut wall: `nutkWallFunction` ✓
- [ ] nut inlet/outlet: `calculated` (field คำนวณจาก k, ε) ✓

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// 0/k
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      k;
}
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0.375;

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform 0.375;
    }
    outlet
    {
        type    zeroGradient;
    }
    wall
    {
        type    kqRWallFunction;
        value   uniform 0.375;
    }
}

// 0/epsilon
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      epsilon;
}
dimensions      [0 2 -3 0 0 0 0];
internalField   uniform 3.76;

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform 3.76;
    }
    outlet
    {
        type    zeroGradient;
    }
    wall
    {
        type    epsilonWallFunction;
        value   uniform 3.76;
    }
}

// 0/nut
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      nut;
}
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type    calculated;
        value   uniform 0;
    }
    outlet
    {
        type    calculated;
        value   uniform 0;
    }
    wall
    {
        type    nutkWallFunction;
        value   uniform 0;
        Cmu     0.09;     // Model constant (default: 0.09)
        kappa   0.41;     // von Karman constant
        E       9.8;      // Log-law constant
    }
}
```

> **⚠️ หมายเหตุ:** `value` ใน wall function BCs เป็นเพียง initial guess — solver จะคำนวณค่าจริงจาก wall function formula ตาม y+ ที่ได้จาก mesh
</details>

---

## แบบฝึกหัด 4: Backflow Problem — Outlet Stability

**⭐⭐ ระดับ Intermediate — ประมาณ 15 นาที**

### Learning Goal
จัดการปัญหา backflow ที่ outlet ซึ่งทำให้ simulation diverge

### โจทย์

Simulation diverges เพราะมี backflow (recirculation) ที่ outlet

**BC ปัจจุบัน (ใช้ไม่ได้):**
```cpp
outlet
{
    type    zeroGradient;
}
```

### คำแนะนำ

1. **Root cause:** `zeroGradient` ไม่มีการกำหนดค่า velocity เมื่อ flow ไหลย้อนกลับ → solver ใช้ค่าจาก internalField ซึ่งอาจผิด
2. **Solution 1:** `inletOutlet` — ใช้ `inletValue` เมื่อมี backflow
3. **Solution 2:** `pressureInletOutletVelocity` — คล้ายกันแต่กำหนดด้วย pressure gradient
4. **Permanent fix:** ขยาย outlet domain ให้ไกลจาก recirculation zone

### Solution Verification Checklist
- [ ] ใช้ `inletOutlet` หรือ `pressureInletOutletVelocity` ✓
- [ ] `inletValue` = (0 0 0) สำหรับ backflow ✓
- [ ] `value` = ค่า initial guess (flow direction) ✓
- [ ] ตรวจสอบว่า outlet อยู่ไกลจาก recirculation zone (ถ้าเป็นไปได้) ✓

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// Option 1: inletOutlet
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);    // ค่าที่ใช้เมื่อมี backflow
    value       uniform (10 0 0);   // Initial guess (normal flow)
}

// Option 2: pressureInletOutletVelocity
outlet
{
    type    pressureInletOutletVelocity;
    value   uniform (10 0 0);       // Initial guess
}
```

**Best Practice:**
- ถ้ามี backflow เป็นประจำ → ขยาย domain ให้ outlet อยู่ไกลจาก zone ที่มี recirculation
- ถ้าเป็น transient backflow (ชั่วคราว) → `inletOutlet` เพียงพอ
</details>

---

## แบบฝึกหัด 5: Convective Wall — Robin BC

**⭐⭐ ระดับ Intermediate — ประมาณ 15 นาที**

### Learning Goal
ตั้งค่า convective heat transfer BC (Robin type) — ใช้ heat transfer coefficient h

### โจทย์

ตั้งค่า convective heat transfer ที่ wall:
- **Heat transfer coefficient:** h = 25 W/(m²·K)
- **Ambient temperature:** T∞ = 293 K
- **Interior:** T = 350 K

### คำแนะนำ

1. **Robin BC:** q = h(T∞ - Tw) หรือ $\frac{\partial T}{\partial n} = \frac{h}{k}(T_{\infty} - T_w)$
2. **Option 1:** `externalWallHeatFlux` — BC เฉพาะสำหรับ heat transfer (แนะนำ)
3. **Option 2:** `mixed` — Robin BC แบบ manual: $\alpha = \frac{1}{1 + Bi}$ โดย $Bi = \frac{hL}{k}$

### Solution Verification Checklist
- [ ] ใช้ `externalWallHeatFlux` mode `coefficient` (แนะนำ) ✓
- [ ] หรือใช้ `mixed` พร้อม `valueFraction` ที่เหมาะสม ✓
- [ ] h = 25, Ta = 293 ✓
- [ ] Dimensions: T `[0 0 0 1 0 0 0]` ✓

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// Option 1: externalWallHeatFlux (แนะนำ)
convWall
{
    type    externalWallHeatFlux;
    mode    coefficient;             // ใช้ heat transfer coefficient
    h       uniform 25;              // W/(m²·K)
    Ta      uniform 293;             // Ambient temperature (K)
}

// Option 2: mixed (manual Robin BC)
convWall
{
    type            mixed;
    refValue        uniform 293;     // T∞ (reference value)
    refGradient     uniform 0;       // Gradient สำหรับ Dirichlet limit
    valueFraction   uniform 0.5;     // 0 = pure Neumann, 1 = pure Dirichlet
                                    // ปรับตาม Biot number: Bi = hL/k
                                    // α = 1/(1 + Bi)
}
```

**Guideline for `valueFraction`:**
- ถ้า Bi >> 1 (convection dominant) → `valueFraction` → 1
- ถ้า Bi << 1 (conduction dominant) → `valueFraction` → 0
- ถ้า Bi ≈ 1 → `valueFraction` ≈ 0.5
</details>

---

## แบบฝึกหัด 6: Debug Errors — Error Diagnosis

**⭐⭐⭐ ระดับ Advanced — ประมาณ 20 นาที**

### Learning Goal
พัฒนาความสามารถในการหาและแก้ไข BC errors ที่พบบ่อย

### โจทย์

หา errors ทั้งหมดใน BC files ด้านล่าง และแก้ไข:

```cpp
// 0/U (มี errors)
FoamFile { ... }
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform 10;           // ❌ Error 1
    }
    outlet
    {
        type    fixedValue;           // ❌ Error 2
        value   uniform 0;
    }
    wall
    {
        type    zeroGradient;         // ❌ Error 3
    }
}

// 0/p (มี errors)
FoamFile { ... }
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type    fixedValue;           // ❌ Error 4
        value   uniform 100;
    }
    outlet
    {
        type    zeroGradient;         // ❌ Error 5
    }
    wall
    {
        type    zeroGradient;
    }
}
```

### คำแนะนำในการหา errors

1. **Check BC consistency:** U และ p ต้องไม่ over-specify boundary
2. **Check field types:** U เป็น `volVectorField` → value ต้องเป็น vector `(x y z)`
3. **Check physical correctness:** Wall U = `noSlip`, Outlet U = `zeroGradient`
4. **Check reference pressure:** Outlet p ควรเป็น `fixedValue` (reference)

### Solution Verification Checklist
- [ ] Error 1: U inlet value → vector `uniform (10 0 0)` ✓
- [ ] Error 2: U outlet → `zeroGradient` ✓
- [ ] Error 3: U wall → `noSlip` ✓
- [ ] Error 4: p inlet → `zeroGradient` ✓
- [ ] Error 5: p outlet → `fixedValue 0` ✓
- [ ] BC pairing ถูกต้อง: inlet (U: Dirichlet, p: Neumann) ✓
- [ ] BC pairing ถูกต้อง: outlet (U: Neumann, p: Dirichlet) ✓

<details>
<summary><b>คำตอบ</b></summary>

**Errors ทั้งหมด:**

| # | Error | Why Wrong | Fix |
|---|-------|-----------|-----|
| 1 | `inlet U value uniform 10` | U เป็น `volVectorField` ต้องเป็น vector | `uniform (10 0 0)` |
| 2 | `outlet U fixedValue 0` | Outlet U ควรเป็น `zeroGradient` (Neumann) | `type zeroGradient;` |
| 3 | `wall U zeroGradient` | Wall U ควรเป็น `noSlip` (Dirichlet = 0) | `type noSlip;` |
| 4 | `inlet p fixedValue` | เมื่อ U inlet เป็น Dirichlet, p ต้องเป็น Neumann | `type zeroGradient;` |
| 5 | `outlet p zeroGradient` | Outlet p ควรเป็น `fixedValue` (reference pressure) | `type fixedValue; value uniform 0;` |

**Fixed Files:**

```cpp
// 0/U
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);

boundaryField
{
    inlet
    {
        type    fixedValue;
        value   uniform (10 0 0);     // ✅ Fixed: vector format
    }
    outlet
    {
        type    zeroGradient;          // ✅ Fixed: Neumann BC
    }
    wall
    {
        type    noSlip;                // ✅ Fixed: no-slip condition
    }
}

// 0/p
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;

boundaryField
{
    inlet
    {
        type    zeroGradient;          // ✅ Fixed: Neumann BC
    }
    outlet
    {
        type    fixedValue;            // ✅ Fixed: reference pressure
        value   uniform 0;
    }
    wall
    {
        type    zeroGradient;          // ✅ OK: pressure gradient normal to wall
    }
}
```
</details>

---

## แบบฝึกหัด 7: Time-Varying Inlet — Transient BCs

**⭐⭐⭐ ระดับ Advanced — ประมาณ 25 นาที**

### Learning Goal
ตั้งค่า BC ที่ขึ้นกับเวลา — ใช้ `uniformFixedValue` หรือ `codedFixedValue`

### โจทย์

Inlet velocity ramp จาก 0 ถึง 10 m/s ใน 2 วินาทีแรก แล้วคงที่ที่ 10 m/s

### คำแนะนำ

1. **Option 1:** `uniformFixedValue` + `table` — ง่ายแต่ไม่ยืดหยุ่น
2. **Option 2:** `codedFixedValue` — เขียน C++ code สำหรับ logic ที่ซับซ้อน
3. **Ramp function:** U(t) = Umax × (t / t_ramp) สำหรับ t < t_ramp

### Solution Verification Checklist
- [ ] ใช้ `uniformFixedValue` หรือ `codedFixedValue` ✓
- [ ] Table หรือ code ให้ U = 0 ที่ t = 0 ✓
- [ ] U ramp ถึง Umax = 10 ที่ t = 2 ✓
- [ ] U คงที่ = 10 สำหรับ t > 2 ✓

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// Option 1: uniformFixedValue with table
inlet
{
    type            uniformFixedValue;
    uniformValue    table
    (
        (0      (0 0 0))      // t = 0, U = 0
        (2      (10 0 0))     // t = 2, U = 10 (linear interpolation)
        (100    (10 0 0))     // t = 100, U = 10 (constant)
    );
}

// Option 2: codedFixedValue (flexible)
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);
    name    rampInlet;               // Function name
    
    code
    #{
        // Get current time
        scalar t = this->db().time().value();
        
        // Ramp parameters
        scalar Umax = 10.0;           // Maximum velocity (m/s)
        scalar rampTime = 2.0;        // Ramp duration (s)
        
        // Calculate velocity
        scalar U = (t < rampTime) ? Umax * t / rampTime : Umax;
        
        // Apply to field
        vectorField& field = *this;
        field = vector(U, 0, 0);
    #};
}

// Option 3: codedFixedValue with smooth ramp (tanh function)
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);
    name    smoothRampInlet;
    
    code
    #{
        scalar t = this->db().time().value();
        scalar Umax = 10.0;
        scalar rampTime = 2.0;
        scalar tau = rampTime / 5.0;  // Time constant
        
        // Smooth ramp using tanh
        scalar U = Umax * tanh(t / tau);
        
        vectorField& field = *this;
        field = vector(U, 0, 0);
    #};
}
```

**Comparison:**
- `uniformFixedValue + table`: ง่าย, ใช้ได้เมื่อรู้ล่วงหน้า
- `codedFixedValue`: ยืดหยุ่น, ใช้ได้กับ logic ซับซ้อน, แต่ต้อง compile
</details>

---

## Concept Check — Self-Assessment

<details>
<summary><b>1. ทำไม inlet U ใช้ fixedValue แต่ p ใช้ zeroGradient?</b></summary>

**Answer:** เพื่อหลีกเลี่ยง over-specification — ถ้ากำหนดทั้ง U และ p เป็น Dirichlet (fixedValue) ที่ boundary เดียวกัน จะขัดแย้งกับ continuity equation → solver จะ diverge หรือให้ผลลัพธ์ผิด

**Rule of thumb:** สำหรับ incompressible flow:
- **Inlet:** U = fixedValue, p = zeroGradient
- **Outlet:** U = zeroGradient, p = fixedValue (reference)
</details>

<details>
<summary><b>2. calculated type ใช้เมื่อไหร่?</b></summary>

**Answer:** เมื่อ field นั้นคำนวณจาก field อื่น โดย solver — ไม่ต้องกำหนดค่า explicit ที่ boundary

**Examples:**
- `nut` (turbulent viscosity) คำนวณจาก k และ ε ใน turbulence model
- `alpha` ใน multiphase flow คำนวณจาก VOF method
- ใช้ `calculated` พร้อม `value uniform 0` เป็น initial guess
</details>

<details>
<summary><b>3. Wall function ใช้ BC type อะไรสำหรับ velocity?</b></summary>

**Answer:** Velocity ที่ wall ใช้ `noSlip` หรือ `fixedValue (0 0 0)` — wall function ใช้สำหรับ **turbulence fields** (k, ε, ω, nut) ไม่ใช่ velocity

**Why:** Wall function คือสมการที่คำนวณ k, ε, ω, nut จาก velocity profile ใน near-wall region — velocity เองยังเป็น no-slip อยู่
</details>

<details>
<summary><b>4. เลือก inletOutlet หรือ pressureInletOutletVelocity เมื่อไหร่?</b></summary>

**Answer:**
- **inletOutlet:** ใช้เมื่อต้องการกำหนด `inletValue` (velocity ที่จะใช้เมื่อมี backflow) explicitly
- **pressureInletOutletVelocity:** ใช้เมื่อต้องการให้ velocity ที่ backflow คำนวณจาก pressure gradient

**General rule:** ลอง `pressureInletOutletVelocity` ก่อน — ถ้าไม่ได้ผล ให้ใช้ `inletOutlet` และปรับ `inletValue`
</details>

---

## Key Takeaways

✅ **BC Pairing สำคัญมาก:** ใช้ Dirichlet + Neumann คู่กัน (U กับ p)
- Inlet: U = Dirichlet, p = Neumann
- Outlet: U = Neumann, p = Dirichlet

✅ **Turbulence Calculations:** จำสูตร $k = 1.5(UI)^2$ และ $\varepsilon = C_\mu^{0.75} k^{1.5} / l$

✅ **Wall Functions:** ใช้สำหรับ k, ε, nut — velocity ยังเป็น noSlip

✅ **Backflow Handling:** ใช้ `inletOutlet` หรือ `pressureInletOutletVelocity` — หรือขยาย domain

✅ **Robin BC:** ใช้ `externalWallHeatFlux` สำหรับ convection — ใช้ `mixed` เมื่อต้องการ manual control

✅ **Debug BCs:** เช็ค (1) field types (vector vs scalar), (2) BC pairing, (3) physical correctness

---

## เอกสารที่เกี่ยวข้อง

- **บทถัดไป:** [กลับสู่หน้าแรก](00_Overview.md) — ภาพรวม Boundary Conditions
- **บทก่อนหน้า:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — การแก้ปัญหา BC
- **เรียนรู้เพิ่มเติม:** [05_Common_Boundary_Conditions_in_OpenFOAM.md](05_Common_Boundary_Conditions_in_OpenFOAM.md) — BC types ที่ใช้บ่อย
- **ทฤษฎีพื้นฐาน:** [02_Fundamental_Classification.md](02_Fundamental_Classification.md) — Dirichlet/Neumann/Robin