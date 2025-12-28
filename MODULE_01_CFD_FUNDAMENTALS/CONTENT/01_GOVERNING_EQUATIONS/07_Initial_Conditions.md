# Initial Conditions

Initial Conditions (ICs) คือ **สถานะเริ่มต้นของ field ทั้งหมดที่เวลา $t=0$** กำหนดใน directory `0/` ค่าเริ่มต้นที่เหมาะสมช่วยให้ simulation ลู่เข้าได้เร็วขึ้นและมีเสถียรภาพ

---

## โครงสร้างไฟล์ Initial Condition

ทุกไฟล์ใน `0/` มีโครงสร้างเดียวกัน:

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;    // หรือ volScalarField
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // หน่วย: m/s
internalField   uniform (0 0 0);   // ค่าเริ่มต้น (Initial Condition)

boundaryField
{
    inlet   { type fixedValue; value uniform (10 0 0); }
    outlet  { type zeroGradient; }
    walls   { type noSlip; }
}
```

| ส่วน | ความหมาย |
|------|----------|
| `dimensions` | หน่วยของ field: [mass length time temp moles current] |
| `internalField` | **Initial Condition** — ค่าเริ่มต้นทั้งโดเมน |
| `boundaryField` | Boundary Conditions — ค่าที่ขอบเขต |

---

## ประเภทของ Initial Field

### 1. Uniform (ค่าเดียวทั้งโดเมน)

```cpp
internalField   uniform (0 0 0);       // Vector
internalField   uniform 0;             // Scalar
```

### 2. Non-uniform (#codeStream)

สำหรับ field ที่มีรูปแบบซับซ้อน:

```cpp
// Parabolic velocity profile
internalField   #codeStream
{
    code
    #{
        const vectorField& C = mesh().C();
        vectorField& U = *this;
        scalar R = 0.05;              // Pipe radius
        scalar Umax = 2.0;            // Max velocity
        
        forAll(C, i)
        {
            scalar r = sqrt(sqr(C[i].y()) + sqr(C[i].z()));
            scalar u = Umax * (1.0 - sqr(r/R));
            U[i] = vector(u, 0, 0);
        }
    #};
};
```

### 3. From Previous Solution (mapFields)

```bash
# Copy solution from coarse mesh to fine mesh
mapFields ../coarseMesh -sourceTime latestTime
```

---

## Velocity Field (`0/U`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // m/s
internalField   uniform (0 0 0);   // เริ่มจากนิ่ง
```

**แนวทาง:**
- Steady-state: เริ่มจาก $(0, 0, 0)$ หรือค่าประมาณ
- Transient: ใช้ค่าที่ตรงกับสภาพจริงที่ $t=0$

---

## Pressure Field (`0/p`)

### Incompressible Flow

```cpp
dimensions      [0 2 -2 0 0 0 0];  // m²/s² (kinematic pressure)
internalField   uniform 0;         // Gauge pressure = 0
```

### Compressible Flow

```cpp
dimensions      [1 -1 -2 0 0 0 0]; // Pa (absolute pressure)
internalField   uniform 101325;    // Atmospheric pressure
```

| ประเภท | Dimensions | ค่าทั่วไป |
|--------|------------|----------|
| Incompressible | `[0 2 -2 0 0 0 0]` | 0 (gauge) |
| Compressible | `[1 -1 -2 0 0 0 0]` | 101325 (absolute) |

---

## Temperature Field (`0/T`)

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}

dimensions      [0 0 0 1 0 0 0];   // K
internalField   uniform 300;       // 300 K
```

---

## Turbulence Fields

### Turbulent Kinetic Energy (`0/k`)

$$k = \frac{3}{2}(I \cdot U)^2$$

```cpp
dimensions      [0 2 -2 0 0 0 0];  // m²/s²
internalField   uniform 0.375;     // k = 1.5 * (0.05 * 10)^2
```

### Dissipation Rate (`0/epsilon`)

$$\epsilon = C_\mu^{0.75} \cdot k^{1.5} / l$$

```cpp
dimensions      [0 2 -3 0 0 0 0];  // m²/s³
internalField   uniform 14.855;
```

### Specific Dissipation (`0/omega`)

$$\omega = k^{0.5} / (C_\mu^{0.25} \cdot l)$$

```cpp
dimensions      [0 0 -1 0 0 0 0];  // 1/s
internalField   uniform 440;
```

> ⚠️ **ข้อควรระวัง:** ห้ามกำหนด k, epsilon, omega เป็น 0 — จะทำให้เกิด division by zero

---

## Phase Fraction (`0/alpha.water`)

สำหรับ multiphase (VOF):

```cpp
dimensions      [0 0 0 0 0 0 0];   // Dimensionless (0-1)
internalField   uniform 0;         // Initially no water

// หรือใช้ setFields สร้าง interface
```

| ค่า α | ความหมาย |
|-------|----------|
| 0 | ไม่มี phase นี้ (เช่น อากาศ) |
| 1 | เต็มด้วย phase นี้ (เช่น น้ำ) |
| 0 < α < 1 | Interface |

---

## กลยุทธ์การเริ่มต้น

### Steady-State Simulation

| กลยุทธ์ | ข้อดี | ข้อเสีย |
|---------|-------|---------|
| Zero fields | ง่าย | อาจลู่เข้าช้า |
| Potential flow | ลู่เข้าเร็ว | ต้องคำนวณก่อน |
| Previous solution | เร็วที่สุด | ต้องมี solution เดิม |

### Transient Simulation

- ค่าเริ่มต้น **สำคัญมาก** — เป็นสภาพจริงที่ $t=0$
- ต้องสอดคล้องกับ physics (เช่น $\nabla \cdot \mathbf{u} = 0$)

---

## เครื่องมือที่เกี่ยวข้อง

| เครื่องมือ | หน้าที่ |
|-----------|--------|
| `setFields` | กำหนดค่าเริ่มต้นตาม region (เช่น cylinder ของน้ำ) |
| `mapFields` | Copy solution จาก mesh หนึ่งไปอีก mesh |
| `potentialFoam` | สร้าง potential flow เป็นค่าเริ่มต้น |
| `checkMesh` | ตรวจสอบ mesh ก่อนรัน |

---

## ปัญหาที่พบบ่อย

| ปัญหา | สาเหตุ | วิธีแก้ |
|-------|--------|--------|
| Division by zero | k, epsilon = 0 | ใส่ค่าบวกเล็กๆ |
| Dimension mismatch | หน่วยไม่ถูกต้อง | ตรวจสอบ `dimensions` |
| Non-physical start | IC ขัดกับ physics | ตรวจสอบ $\nabla \cdot \mathbf{u} = 0$ |
| Slow convergence | IC ห่างจาก solution | ใช้ potential flow หรือ mapFields |

---

## Concept Check

<details>
<summary><b>1. ถ้าใส่ k = 0 และ epsilon = 0 จะเกิดอะไรขึ้น?</b></summary>

Solver จะ crash เนื่องจาก eddy viscosity $\nu_t = C_\mu k^2/\epsilon$ มีการหารด้วย epsilon ควรใส่ค่าบวกเล็กๆ เสมอ
</details>

<details>
<summary><b>2. internalField กับ boundaryField ต่างกันอย่างไร?</b></summary>

`internalField` คือค่าเริ่มต้นที่ $t=0$ ภายในโดเมน ส่วน `boundaryField` คือ boundary conditions ที่บังคับตลอดการคำนวณ
</details>

<details>
<summary><b>3. เมื่อไหร่ควรใช้ mapFields?</b></summary>

เมื่อต้องการ:
- Copy solution จาก coarse mesh ไป fine mesh (mesh refinement study)
- ใช้ steady-state solution เป็น IC สำหรับ transient
- Restart simulation จาก checkpoint
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [06_Boundary_Conditions.md](06_Boundary_Conditions.md) — เงื่อนไขขอบเขต
- **บทถัดไป:** [08_Key_Points_to_Remember.md](08_Key_Points_to_Remember.md) — สรุปประเด็นสำคัญ
- **ดูเพิ่มเติม:** [04_Dimensionless_Numbers.md](04_Dimensionless_Numbers.md) — การคำนวณ k, epsilon จาก I และ Re