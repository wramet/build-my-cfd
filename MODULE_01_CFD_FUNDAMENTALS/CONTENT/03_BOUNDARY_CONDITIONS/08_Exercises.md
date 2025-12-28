# แบบฝึกหัด Boundary Conditions

แบบฝึกหัดเชิงปฏิบัติสำหรับการตั้งค่า BC ใน OpenFOAM

---

## แบบฝึกหัด 1: Pipe Flow

### โจทย์

ตั้งค่า BC สำหรับการไหลในท่อกลม:
- Inlet: Velocity 1 m/s
- Outlet: Atmospheric pressure
- Wall: No-slip

### เขียน 0/U และ 0/p

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// 0/U
FoamFile { ... }
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
FoamFile { ... }
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

## แบบฝึกหัด 2: Heat Transfer

### โจทย์

ตั้งค่า BC สำหรับ heat transfer ใน channel:
- Inlet: T = 300 K
- Outlet: Zero gradient
- Top wall: Fixed T = 400 K
- Bottom wall: Adiabatic

### เขียน 0/T

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// 0/T
FoamFile { ... }
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

## แบบฝึกหัด 3: Turbulent Flow

### โจทย์

กำหนด turbulence BC สำหรับ k-ε model:
- Inlet: I = 5%, l = 0.01 m
- Outlet: Zero gradient
- Wall: Wall functions

**สูตร:**
- $k = \frac{3}{2}(UI)^2$
- $\varepsilon = C_\mu^{3/4} \frac{k^{3/2}}{l}$
- $C_\mu = 0.09$

### คำนวณ k และ ε สำหรับ U = 10 m/s

<details>
<summary><b>คำตอบ</b></summary>

```
I = 0.05
U = 10 m/s
l = 0.01 m
Cmu = 0.09

k = 1.5 × (10 × 0.05)² = 1.5 × 0.25 = 0.375 m²/s²

ε = 0.09^0.75 × (0.375)^1.5 / 0.01
  = 0.164 × 0.229 / 0.01
  = 3.76 m²/s³
```

```cpp
// 0/k
inlet { type fixedValue; value uniform 0.375; }
outlet { type zeroGradient; }
wall { type kqRWallFunction; value uniform 0.375; }

// 0/epsilon
inlet { type fixedValue; value uniform 3.76; }
outlet { type zeroGradient; }
wall { type epsilonWallFunction; value uniform 3.76; }

// 0/nut
inlet { type calculated; value uniform 0; }
outlet { type calculated; value uniform 0; }
wall { type nutkWallFunction; value uniform 0; }
```
</details>

---

## แบบฝึกหัด 4: Backflow Problem

### โจทย์

Simulation diverges เพราะ backflow ที่ outlet

**ปัจจุบัน:**
```cpp
outlet { type zeroGradient; }
```

### แก้ไข 0/U ให้จัดการ backflow ได้

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// Option 1: inletOutlet
outlet
{
    type        inletOutlet;
    inletValue  uniform (0 0 0);
    value       uniform (10 0 0);
}

// Option 2: pressureInletOutletVelocity
outlet
{
    type    pressureInletOutletVelocity;
    value   uniform (10 0 0);
}
```

**หมายเหตุ:** ถ้ายังไม่ดีขึ้น ให้ขยาย outlet domain ให้ไกลจาก recirculation zone
</details>

---

## แบบฝึกหัด 5: Convective Wall

### โจทย์

ตั้งค่า convective heat transfer:
- h = 25 W/(m²·K)
- T∞ = 293 K

### เขียน BC สำหรับ 0/T

<details>
<summary><b>คำตอบ</b></summary>

```cpp
// Option 1: externalWallHeatFlux
convWall
{
    type    externalWallHeatFlux;
    mode    coefficient;
    h       uniform 25;
    Ta      uniform 293;
}

// Option 2: mixed (manual)
convWall
{
    type            mixed;
    refValue        uniform 293;
    refGradient     uniform 0;
    valueFraction   uniform 0.5;    // ปรับตาม Biot number
}
```
</details>

---

## แบบฝึกหัด 6: Debug Errors

### โจทย์

หา error และแก้ไข:

```cpp
// 0/U
inlet  { type fixedValue; value uniform 10; }
outlet { type fixedValue; value uniform 0; }
wall   { type zeroGradient; }

// 0/p
inlet  { type fixedValue; value uniform 100; }
outlet { type zeroGradient; }
wall   { type zeroGradient; }
```

<details>
<summary><b>คำตอบ</b></summary>

**Errors:**

1. `inlet U value uniform 10` — U ต้องเป็น vector: `uniform (10 0 0)`
2. `outlet U fixedValue 0` — ควรเป็น `zeroGradient`
3. `wall U zeroGradient` — ควรเป็น `noSlip`
4. `inlet p fixedValue` — เมื่อ U เป็น fixedValue, p ควรเป็น `zeroGradient`
5. `outlet p zeroGradient` — ควรเป็น `fixedValue` สำหรับ reference

**แก้ไข:**

```cpp
// 0/U
inlet  { type fixedValue; value uniform (10 0 0); }
outlet { type zeroGradient; }
wall   { type noSlip; }

// 0/p
inlet  { type zeroGradient; }
outlet { type fixedValue; value uniform 0; }
wall   { type zeroGradient; }
```
</details>

---

## แบบฝึกหัด 7: Time-Varying Inlet

### โจทย์

Inlet velocity ramp จาก 0 ถึง 10 m/s ใน 2 วินาทีแรก แล้วคงที่

### เขียน BC

<details>
<summary><b>คำตอบ</b></summary>

```cpp
inlet
{
    type            uniformFixedValue;
    uniformValue    table
    (
        (0      (0 0 0))
        (2      (10 0 0))
        (100    (10 0 0))
    );
}
```

หรือใช้ `codedFixedValue`:

```cpp
inlet
{
    type    codedFixedValue;
    value   uniform (0 0 0);
    name    rampInlet;
    
    code
    #{
        scalar t = this->db().time().value();
        scalar Umax = 10.0;
        scalar rampTime = 2.0;
        
        scalar U = (t < rampTime) ? Umax * t / rampTime : Umax;
        
        vectorField& field = *this;
        field = vector(U, 0, 0);
    #};
}
```
</details>

---

## Concept Check

<details>
<summary><b>1. ทำไม inlet U ใช้ fixedValue แต่ p ใช้ zeroGradient?</b></summary>

เพื่อหลีกเลี่ยง over-specification — ถ้ากำหนดทั้ง U และ p เป็น Dirichlet จะขัดแย้งกับ continuity equation → diverge
</details>

<details>
<summary><b>2. calculated type ใช้เมื่อไหร่?</b></summary>

เมื่อ field นั้นคำนวณจาก field อื่น (เช่น nut คำนวณจาก k และ ε) ไม่ต้องกำหนดค่า explicit
</details>

<details>
<summary><b>3. Wall function ใช้ BC type อะไรสำหรับ velocity?</b></summary>

`noSlip` หรือ `fixedValue (0 0 0)` — wall function ใช้สำหรับ turbulence fields (k, ε, ω, nut) ไม่ใช่ velocity
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [07_Troubleshooting_Boundary_Conditions.md](07_Troubleshooting_Boundary_Conditions.md) — การแก้ปัญหา
- **กลับสู่:** [00_Overview.md](00_Overview.md) — ภาพรวม