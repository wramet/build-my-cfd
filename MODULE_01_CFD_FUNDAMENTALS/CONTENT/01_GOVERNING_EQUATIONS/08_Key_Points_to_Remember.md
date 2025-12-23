# ประเด็นสำคัญที่ควรจดจำ

## 1. กฎการอนุรักษ์: รากฐานของ CFD

**ทุกสิ่งใน computational fluid dynamics (CFD)** สร้างขึ้นบนหลักการพื้นฐานของการอนุรักษ์มวล (mass), โมเมนตัม (momentum) และพลังงาน (energy)

กฎการอนุรักษ์เหล่านี้แสดงถึงข้อจำกัดทางกายภาพที่ควบคุมพฤติกรรมของไหล และเป็นแกนหลักทางคณิตศาสตร์ของการจำลอง CFD ทั้งหมด:

- **การอนุรักษ์มวล**: ทำให้มั่นใจว่าของไหลไม่สามารถเกิดขึ้นหรือหายไปเองภายในโดเมนได้
- **การอนุรักษ์โมเมนตัม**: เป็นไปตามกฎข้อที่สองของนิวตันที่นำมาใช้กับตัวกลางต่อเนื่อง
- **การอนุรักษ์พลังงาน**: รักษากฎข้อที่หนึ่งของอุณหพลศาสตร์ตลอดทั้งโดเมนการคำนวณ

ใน OpenFOAM หลักการเหล่านี้ถูกนำมาใช้ผ่านวิธี finite volume method ซึ่งรูปแบบอินทิกรัลของสมการการอนุรักษ์จะถูกนำไปใช้กับแต่ละ control volume

### สมการการขนส่งทั่วไป

สำหรับคุณสมบัติทั่วไป $\phi$ สมการการอนุรักษ์สามารถแสดงได้ดังนี้:
$$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

โดยที่:
- $\rho$ = density
- $\mathbf{u}$ = velocity vector
- $\Gamma$ = diffusion coefficient
- $S_\phi$ = source terms

สมการขนส่งแบบทั่วไปนี้เป็นแม่แบบสำหรับสมการการอนุรักษ์ทั้งหมดใน CFD โดยที่ $\phi$ แทนปริมาณทางกายภาพที่แตกต่างกันขึ้นอยู่กับสมการเฉพาะที่กำลังถูกแก้

### การใช้ Gauss's Divergence Theorem
![[Pasted image 20251223200317.png]]

การนำ finite volume มาใช้ใน OpenFOAM จะทำการ discretize สมการอินทิกรัลเหล่านี้โดยการประยุกต์ใช้ Gauss's divergence theorem:
$$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_S \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

โดยที่:
- $\mathbf{F}$ = flux vector
- $\mathbf{n}$ = outward normal vector ที่ cell faces

การ discretization นี้ทำให้มั่นใจถึงการอนุรักษ์ที่แม่นยำในระดับ discrete ทำให้ finite volume method เหมาะอย่างยิ่งสำหรับการประยุกต์ใช้ CFD ที่คุณสมบัติการอนุรักษ์มีความสำคัญสูงสุด

---

## 2. สมการความต่อเนื่อง: หลักการอนุรักษ์มวล

**สมการความต่อเนื่อง (continuity equation)** แสดงออกทางคณิตศาสตร์ถึงหลักการพื้นฐานที่ว่ามวลไม่สามารถถูกสร้างหรือทำลายได้ภายในระบบของไหล

สมการนี้ระบุว่าอัตราการสะสมมวลภายใน control volume ใดๆ จะต้องเท่ากับ net mass flux ที่ไหลเข้าสู่ปริมาตรนั้น บวกกับ mass sources หรือ sinks ใดๆ

### กรณี Incompressible Flow

สำหรับ incompressible flows ซึ่ง density คงที่ สมการความต่อเนื่องจะลดรูปอย่างมาก:
$$\nabla \cdot \mathbf{u} = 0$$

ข้อจำกัดนี้ทำให้มั่นใจว่าการไหลของไหลยังคงเป็น **solenoidal (divergence-free)** ซึ่งหมายความว่าปริมาตรของ fluid elements ยังคงที่เมื่อเคลื่อนที่ผ่าน flow field

### กรณี Compressible Flow

ในสถานการณ์ compressible flow สมการความต่อเนื่องจะอยู่ในรูปแบบทั่วไปมากขึ้น:
$$\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{u}) = 0$$

สมการนี้คำนึงถึงความแปรผันของ density และมีความสำคัญอย่างยิ่งต่อการจับปรากฏการณ์ต่างๆ เช่น:
- Shock waves
- Acoustic propagation
- High-speed gas dynamics

### Pressure-Velocity Coupling ใน OpenFOAM

ใน OpenFOAM สมการความต่อเนื่องมักจะถูกบังคับใช้ผ่าน pressure-velocity coupling algorithms เฉพาะทาง:

| อัลกอริทึม | ประเภทการจำลอง | ลักษณะการทำงาน |
|-------------|------------------|------------------|
| **SIMPLE** | Steady-state | Semi-implicit พร้อมการวนซ้ำ |
| **PISO** | Transient | Pressure-Implicit with Splitting of Operators |
| **PIMPLE** | Transient ขนาดใหญ่ | ผสมระหว่าง SIMPLE และ PISO |

#### อัลกอริทึม SIMPLE Algorithm

อัลกอริทึม SIMPLE แก้ระบบที่เชื่อมโยงกันผ่านกระบวนการวนซ้ำ:

1. **Momentum Prediction**: แก้สมการ momentum โดยใช้ current pressure field
2. **Pressure Correction**: สร้างสมการ pressure correction จาก continuity
3. **Velocity Correction**: อัปเดต velocity field ตาม pressure correction
4. **Boundary Condition Update**: ใช้ค่าที่แก้ไขแล้วที่ boundaries
5. **Convergence Check**: ตรวจสอบว่า residuals ต่ำกว่าค่า tolerance ที่กำหนด

สำหรับการจำลอง transient อัลกอริทึม PISO จะเพิ่มขั้นตอน corrector เพิ่มเติมเพื่อรักษาความแม่นยำเชิงเวลาในขณะที่มั่นใจถึงการอนุรักษ์มวลในแต่ละ time step

---

## 3. สมการ Navier-Stokes: กฎข้อที่สองของนิวตันสำหรับของไหล

**สมการ Navier-Stokes** แสดงถึงการกำหนดทางคณิตศาสตร์ของกฎข้อที่สองของนิวตันว่าด้วยการเคลื่อนที่ที่นำมาใช้กับ fluid elements

โดยหลักแล้วระบุว่าแรงที่กระทำต่ออนุภาคของไหลเท่ากับมวลของอนุภาคนั้นคูณด้วยความเร่ง สมการเหล่านี้จะรักษาสมดุลระหว่าง:
- **Inertial forces**
- **Pressure forces**
- **Viscous forces**
- **External body forces**

### สมการ Momentum ใน Conservative Form

$$\rho \frac{\partial \mathbf{u}}{\partial t} + \rho (\mathbf{u} \cdot \nabla) \mathbf{u} = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$$

โดยที่:
- $p$ = pressure
- $\mu$ = dynamic viscosity
- $\mathbf{f}$ = body forces (เช่น gravity หรือ electromagnetic forces)

#### การวิเคราะห์เทอมสมการ:

- **ด้านซ้ายมือ**: substantial derivative ของ velocity
  - Temporal acceleration: $\frac{\partial \mathbf{u}}{\partial t}$
  - Convective acceleration: $(\mathbf{u} \cdot \nabla) \mathbf{u}$

- **ด้านขวามือ**: surface forces
  - Pressure gradient forces: $-\nabla p$
  - Viscous forces: $\mu \nabla^2 \mathbf{u}$

![[Pasted image 20251223200332.png]]
### การ Implement ใน OpenFOAM

ใน OpenFOAM เทอมเหล่านี้ถูกนำมาใช้โดยใช้ finite volume discretization พร้อมฟังก์ชันเฉพาะทาง:

```cpp
// OpenFOAM Code Implementation
fvVectorMatrix UEqn
(
    fvm::ddt(rho, U)         // Temporal derivative
  + fvm::div(phi, U)         // Convective term
  - fvm::laplacian(mu, U)    // Diffusion term
 ==
    -fvc::grad(p)            // Pressure gradient
);
```

### รูปแบบไร้มิติและเลขเรย์โนลด์

สมการ Navier-Stokes สามารถทำให้เป็นไร้มิติ (non-dimensionalized) ได้:
$$\frac{\partial \mathbf{u}^*}{\partial t^*} + (\mathbf{u}^* \cdot \nabla^*) \mathbf{u}^* = -\nabla^* p^* + \frac{1}{Re} \nabla^{*2} \mathbf{u}^* + \mathbf{f}^*$$

โดยที่ **Reynolds number** $Re = \frac{\rho UL}{\mu}$ บ่งบอกถึงอัตราส่วนของ inertial forces ต่อ viscous forces

- **ที่ Reynolds numbers สูง**: ผลกระทบของความหนืดจะกลายเป็นสิ่งที่ไม่สำคัญ ยกเว้นใน thin boundary layers ใกล้ผนัง
- **ผลลัพธ์**: นำไปสู่การก่อตัวของ turbulent flow structures ที่ต้องใช้วิธีการ modeling เฉพาะทาง

---

## 4. สมการสถานะ: ความสัมพันธ์ทางอุณหพลศาสตร์

**สมการสถานะ (Equation of State - EOS)** เป็นความสัมพันธ์พื้นฐานในพลศาสตร์ของไหลที่เชื่อมโยงสมบัติทางอุณหพลศาสตร์ เช่น ความดัน ความหนาแน่น และอุณหภูมิ

### กฎแก๊สอุดมคติ (Ideal Gas Law)

สำหรับการไหลแบบอัดตัวได้ กฎแก๊สอุดมคติให้ความสัมพันธ์ระหว่างความดัน ($p$) ความหนาแน่น ($\rho$) และอุณหภูมิ ($T$) ดังนี้:

$$p = \rho R T$$

**โดยที่:**
- $p$ คือ ความดันสัมบูรณ์ [Pa]
- $\rho$ คือ ความหนาแน่นของไหล [kg/m³]
- $R$ คือ ค่าคงที่แก๊สจำเพาะ [J/(kg·K)]
- $T$ คือ อุณหภูมิสัมบูรณ์ [K]

**ข้อสมมติ:**
- ของไหลมีพฤติกรรมเป็นแก๊สอุดมคติ
- ใช้ได้กับแก๊สส่วนใหญ่ที่อุณหภูมิและความดันปกติ
- ปฏิสัมพันธ์ระดับโมเลกุลมีค่าน้อยมาก

### ของไหลที่อัดตัวไม่ได้ (Incompressible Fluid)

สำหรับของเหลว เช่น น้ำ ความหนาแน่นยังคงที่โดยพื้นฐาน:

$$\rho = \text{constant}$$

**เงื่อนไขที่ใช้ได้:**
- การเปลี่ยนแปลงความดันมีค่าน้อยเมื่อเทียบกับ Bulk Modulus
- การเปลี่ยนแปลงอุณหภูมิไม่ส่งผลกระทบต่อความหนาแน่นอย่างมีนัยสำคัญ
- **เลข Mach โดยทั่วไปน้อยกว่า 0.3**

### OpenFOAM Code Implementation

```cpp
// โมเดลทางอุณหพลศาสตร์สำหรับแก๊สอุดมคติ
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;    // สิ่งที่ Implement: p = ρRT
    specie          specie;
    energy          sensibleEnthalpy;
}

// โมเดลทางอุณหพลศาสตร์สำหรับของไหลที่อัดตัวไม่ได้
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState incompressible;  // สิ่งที่ Implement: ρ = constant
    specie          specie;
    energy          sensibleEnthalpy;
}
```

---

## 5. เลขไร้มิติ: พารามิเตอร์ที่ควบคุมระบอบการไหล

เลขไร้มิติเป็นพารามิเตอร์พื้นฐานในพลศาสตร์ของไหลที่บ่งบอกถึงความสำคัญสัมพัทธ์ของปรากฏการณ์ทางฟิสิกส์ที่แข่งขันกัน

### Reynolds Number ($Re$)

Reynolds number อาจกล่าวได้ว่าเป็นพารามิเตอร์ไร้มิติที่สำคัญที่สุดในกลศาสตร์ของไหล:

$$Re = \frac{\rho U L}{\mu} = \frac{\text{Inertial Forces}}{\text{Viscous Forces}}$$

**Flow Regime Classification:**

| ค่า Reynolds Number | ระบอบการไหล | ลักษณะการไหล |
|---------------------|--------------|----------------|
| $Re < 2300$ | Laminar | การไหลเป็นชั้นๆ ไม่มีการปนเปื้อน |
| $2300 < Re < 4000$ | Transitional | การเปลี่ยนผ่านจาก Laminar เป็น Turbulent |
| $Re > 4000$ | Turbulent | การไหลมีการปนเปื้อนและกระเพื่อม |

### Mach Number ($Ma$)

Mach number แสดงถึงอัตราส่วนของความเร็วการไหลต่อความเร็วเสียงเฉพาะที่:

$$Ma = \frac{U}{c} = \frac{\text{Flow Velocity}}{\text{Speed of Sound}}$$

**Mach Number Flow Regimes:**

| ค่า Mach Number | ระบอบการไหล | ผลกระทบของ Compressibility |
|-----------------|---------------|------------------------------|
| $Ma < 0.3$ | Incompressible | ความแปรผันของความหนาแน่นน้อยมาก |
| $0.3 < Ma < 0.8$ | Subsonic Compressible | มีผลกระทบของ compressibility เล็กน้อย |
| $Ma = 1$ | Sonic | สภาวะวิกฤต การไหลผ่านความเร็วเสียง |
| $0.8 < Ma < 1.2$ | Transonic | บริเวณ Subsonic/Supersonic ผสมกัน |
| $Ma > 1.2$ | Supersonic | การไหลเร็วกว่าเสียง Shock Wave ก่อตัว |

### OpenFOAM Solver Selection

OpenFOAM มี Solver เฉพาะทางสำหรับระบอบ Mach number ที่แตกต่างกัน:

```cpp
// Low Mach number (Ma < 0.3) - incompressible solvers
solver simpleFoam;        // Steady-state
solver pimpleFoam;        // Transient
solver icoFoam;          // Laminar transient

// Compressible flow solvers (Ma > 0.3)
solver rhoSimpleFoam;     // Steady compressible
solver rhoPimpleFoam;     // Transient compressible
solver sonicFoam;        // Transonic/supersonic flow
```

---

## 6. ไวยากรณ์ OpenFOAM: การแปลสัญลักษร์ทางคณิตศาสตร์

**ไวยากรณ์ของ OpenFOAM** ได้รับการออกแบบมาโดยเจตนาให้สะท้อนสัญลักษร์ vector ทางคณิตศาสตร์ที่ใช้ในสมการพลศาสตร์ของไหลอย่างใกล้ชิด

### การแม็ป Mathematical Operators กับ OpenFOAM Functions

ฟังก์ชัน finite volume method (FVM) ใน OpenFOAM สอดคล้องโดยตรงกับ mathematical operators:

| OpenFOAM Function | Mathematical Operator | ความหมาย |
|------------------|---------------------|-----------|
| `fvm::div(phi, U)` | $\nabla \cdot (\phi \mathbf{U})$ | Divergence operator |
| `fvm::laplacian(DT, T)` | $\nabla \cdot (DT \nabla T)$ | Laplacian operator |
| `fvm::ddt(rho, U)` | $\frac{\partial (\rho \mathbf{U})}{\partial t}$ | Temporal derivative |
| `fvc::grad(p)` | $\nabla p$ | Pressure gradient |

การสอดคล้องกันโดยตรงระหว่างสัญลักษร์ทางคณิตศาสตร์และการนำโค้ดไปใช้ช่วยลดภาระทางปัญญาได้อย่างมากเมื่อแปลสมการไปสู่แอปพลิเคชัน OpenFOAM

### ระบบ Field Type ใน OpenFOAM

OpenFOAM ใช้ระบบ template ที่ซับซ้อนสำหรับ field types ที่รักษาความสอดคล้องทางคณิตศาสตร์ตลอดทั้ง codebase:

#### Geometric Fields
- `volScalarField`
- `volVectorField`
- `volTensorField`

#### Surface Fields
- `surfaceScalarField`
- `surfaceVectorField`

#### Specialized Features
- **Dimensional Sets**: การวิเคราะห์มิติอัตโนมัติและการตรวจสอบหน่วย
- **Interpolation Schemes**: Linear, upwind, central differencing และ schemes ลำดับสูงกว่า

---

## 7. Boundary Conditions: สิ่งจำเป็นสำหรับ Physical Solutions

**Boundary conditions** มีความสำคัญอย่างยิ่งต่อการได้มาซึ่ง solution ที่ไม่ซ้ำกันและถูกต้องทางกายภาพสำหรับปัญหา CFD

เนื่องจาก governing equations เองยอมรับ solutions ที่ไม่มีที่สิ้นสุดหากไม่มีข้อจำกัดที่เหมาะสม ใน finite volume method, boundary conditions จะต้องถูกระบุสำหรับตัวแปรทั้งหมดที่ domain boundaries ทั้งหมด

### ประเภท Boundary Conditions ใน OpenFOAM

| ประเภท | ตัวอย่างใน OpenFOAM | การใช้งาน |
|---------|-------------------|-----------|
| **Dirichlet conditions** | `fixedValue` | ระบุค่าที่แน่นอนที่ boundaries |
| **Neumann conditions** | `fixedGradient` | ระบุค่า gradient (zero-gradient สำหรับ fully developed flow) |
| **Mixed conditions** | `mixed` | รวมการระบุค่าและ gradient |
| **Wall functions** | ต่างๆ | การจัดการเฉพาะทางสำหรับการจำลอง near-wall turbulence |
| **Open boundary conditions** | `inletOutlet`, `outletInlet` | อนุญาตให้ flow reversal และระบุเงื่อนไขตาม local flow direction |

### OpenFOAM Boundary Condition Examples

```cpp
// Example: Velocity inlet with turbulent profile
inlet
{
    type            fixedValue;
    value           uniform (10 0 0);  // m/s uniform velocity
}

// Example: Pressure outlet with backflow prevention
outlet
{
    type            zeroGradient;      // Natural development
}

// Example: No-slip wall
walls
{
    type            fixedValue;        // Fixed at zero for no-slip
    value           uniform (0 0 0);
}

// Example: Symmetry plane
symmetryPlane
{
    type            symmetry;
}
```

### Advanced Boundary Condition Capabilities

OpenFOAM มีความสามารถด้าน boundary condition ที่ซับซ้อนซึ่งขยายไปไกลกว่าการระบุค่าและ gradient พื้นฐาน:

- **Time-varying conditions**: `uniformFixedValue` พร้อมฟังก์ชันที่ขึ้นกับเวลา
- **Coupled boundaries**: `thermalBaffle` สำหรับ conjugate heat transfer
- **Cyclic conditions**: `cyclicAMI` สำหรับ rotating machinery interfaces
- **Atmospheric boundaries**: `atmBoundaryLayerInlet` สำหรับ atmospheric boundary layer modeling
- **Wave generation**: `waveAlpha` และ `waveSurfaceHeight` สำหรับ ocean engineering applications

---

## 8. Initial Conditions: รากฐานของความมั่นคงเชิงตัวเลข

การจำลองต้องเริ่มต้นจากจุดใดจุดหนึ่ง **Initial Conditions** (ในไดเรกทอรี `0/`) กำหนดสถานะที่ $t=0$ เงื่อนไขเหล่านี้มีความสำคัญอย่างยิ่งต่อ **Numerical Stability** และ **Convergence** ของการจำลอง CFD

### Velocity Field Initialization

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}

dimensions      [0 1 -1 0 0 0 0];  // m/s: ความยาว/เวลา
internalField   uniform (0 0 0);   // ฟิลด์ความเร็วเริ่มต้น

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (10 0 0); // ความเร็วขาเข้าแบบ Uniform 10 m/s
    }
    outlet
    {
        type            zeroGradient;     // การไหลที่พัฒนาเต็มที่
    }
    walls
    {
        type            noSlip;           // เงื่อนไข No-Slip
    }
}
```

### Pressure Field Initialization

```cpp
// Incompressible Flow
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}

dimensions      [0 2 -2 0 0 0 0];  // Pa: kg/(m·s²)
internalField   uniform 101325;    // ค่าอ้างอิงความดันบรรยากาศ

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    outlet
    {
        type            fixedValue;
        value           uniform 101325; // ความดันเกจ = 0
    }
    walls
    {
        type            zeroGradient;
    }
}
```

### Best Practices for Initial Conditions

1. **Physical Consistency**: ตรวจสอบให้แน่ใจว่า Initial Conditions เป็นไปตามกฎการอนุรักษ์พื้นฐาน
2. **Numerical Stability**: หลีกเลี่ยง **Discontinuities** ที่อาจทำให้เกิด Numerical Instability
3. **Convergence Acceleration**: สำหรับ **Steady-State Problems** ให้ใช้กลยุทธ์การเริ่มต้นที่ส่งเสริม Convergence อย่างรวดเร็ว
4. **Restart Capabilities**: จัดโครงสร้าง Initial Conditions เพื่ออำนวยความสะดวกในการ **Simulation Restarts**

---

## สรุปประเด็นสำคัญ

### หลักการพื้นฐานที่ต้องจำ

1. **กฎการอนุรักษ์** - รากฐานของ CFD ทั้งหมด:
   - การอนุรักษ์มวล → Continuity equation
   - การอนุรักษ์โมเมนตัม → Navier-Stokes equation
   - การอนุรักษ์พลังงาน → Energy equation

2. **สมการขนส่งทั่วไป**:
   $$\frac{\partial (\rho \phi)}{\partial t} + \nabla \cdot (\rho \phi \mathbf{u}) = \nabla \cdot (\Gamma \nabla \phi) + S_\phi$$

3. **Finite Volume Method** ใช้ Gauss's Divergence Theorem:
   $$\int_V \nabla \cdot \mathbf{F} \, \mathrm{d}V = \oint_S \mathbf{F} \cdot \mathbf{n} \, \mathrm{d}S$$

### เลขไร้มิติสำคัญ

| เลขไร้มิติ | สูตร | ความสำคัญ |
|--------------|-------|------------|
| Reynolds ($Re$) | $\frac{\rho U L}{\mu}$ | ทำนายระบอบการไหล (Laminar/Turbulent) |
| Mach ($Ma$) | $\frac{U}{c}$ | กำหนดผลกระทบของ compressibility |
| Froude ($Fr$) | $\frac{U}{\sqrt{gL}}$ | สำคัญสำหรับการไหลแบบ free surface |

### OpenFOAM Syntax Mapping

```cpp
fvm::ddt(rho, U)         // ∂(ρU)/∂t
fvm::div(phi, U)         // ∇·(ρUU)
fvm::laplacian(mu, U)     // ∇·(μ∇U)
fvc::grad(p)             // ∇p
```

### Pressure-Velocity Coupling Algorithms

- **SIMPLE**: Semi-Implicit Method for Pressure-Linked Equations (Steady-State)
- **PISO**: Pressure-Implicit with Splitting of Operators (Transient)
- **PIMPLE**: Combined SIMPLE-PISO (Hybrid)

### Boundary Conditions หลัก

- **Dirichlet**: `fixedValue` - ระบุค่าที่แน่นอน
- **Neumann**: `zeroGradient` - ระบุ gradient
- **Wall**: `noSlip` - ความเร็วศูนย์ที่ผนัง
- **Symmetry**: `symmetry` - ระนาบสมมาตร

---

> **[!TIP]** การเข้าใจประเด็นสำคัญเหล่านี้อย่างลึกซึ้งเป็นกุญแจสำคัญสู่ความสำเร็จในการจำลอง CFD ด้วย OpenFOAM ทั้งนี้เพราะทุกสิ่งใน CFD ตั้งแต่การสร้าง mesh ไปจนถึงการตีความผลลัพธ์ ล้วนอิงตามหลักการพื้นฐานเหล่านี้
