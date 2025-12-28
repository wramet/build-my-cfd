# Time Architecture

สถาปัตยกรรมการจัดการเวลาใน OpenFOAM

> [!TIP] ทำไม Time Architecture สำคัญ?
> **Time Architecture** คือหัวใจของการจำลองแบบที่ไม่คงที่ (unsteady/transient simulation) การเข้าใจการทำงานของ `Time` class และการจัดการ time step จะช่วยให้คุณ:
> - ควบคุม **ความเสถียร** ของการคำนวณ (โดยเฉพาะ Courant number)
> - ปรับแต่ง **ความแม่นยำ** ของ temporal discretization
> - บริหารจัดการ **disk space** ด้วยการเขียนผลลัพธ์อย่างมีประสิทธิภาพ
> - เข้าใจการทำงานของ **adjustable time step** สำหรับกรณีที่มีการเปลี่ยนแปลงเวลาจริง

---

## Overview

> [!NOTE] **📂 OpenFOAM Context**
> บทนี้เกี่ยวข้องกับ **Domain C: Simulation Control**
> - **ไฟล์หลัก:** `system/controlDict`
> - **Keywords:** `startFrom`, `startTime`, `stopAt`, `endTime`, `deltaT`, `writeControl`, `writeInterval`, `adjustTimeStep`
> - **Class:** `Time` ใน `src/OSspecific/POSIX/Time/Time.C`
>
> ในการจำลองแบบ (solver) คุณจะเห็นการใช้งานในรูปแบบ:
> ```cpp
> Time runTime(Time::controlDictName, args);
> while (runTime.loop()) { ... }
> ```

คลาส `Time` จัดการ:
- **Time stepping** — จาก startTime → endTime
- **Data I/O** — อ่าน/เขียน fields ตาม time folders
- **Field history** — เก็บ oldTime สำหรับ temporal schemes

---

## Core Time Class

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain E: Coding/Customization** — เข้าใจโครงสร้างภายในของ `Time` class
> - **Source Code:** `src/OpenFOAM/db/Time/Time.H` และ `Time.C`
> - **Usage:** ในทุก solver files (เช่น `applications/solvers/incompressible/simpleFoam/simpleFoam.C`)
> - **Constructor Pattern:** `Time runTime(Time::controlDictName, args);`
>
> ในโค้ด solver คุณจะเห็นการใช้งานจริงใน `while (runTime.loop())` loop

```cpp
class Time : public IOobject
{
    scalar startTime_;   // เริ่มต้น [s]
    scalar endTime_;     // สิ้นสุด [s]
    scalar deltaT_;      // Time step [s]
    scalar value_;       // Current time [s]
    label timeIndex_;    // Current step index
    
public:
    bool loop() {
        value_ += deltaT_;
        timeIndex_++;
        return value_ < endTime_;
    }
    
    const word& timeName() const;   // Folder name (e.g., "0.5")
    scalar value() const;           // Current time
    scalar deltaTValue() const;     // Time step size
};
```

**Usage in solver:**
```cpp
Time runTime(Time::controlDictName, args);

while (runTime.loop())
{
    #include "readTimeControls.H"
    solve(UEqn);
    runTime.write();
}
```

---

## controlDict Settings

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain C: Simulation Control** — ไฟล์ควบคุมการจำลองแบบที่สำคัญที่สุด
> - **ไฟล์:** `system/controlDict`
> - **Keywords:** `application`, `startFrom`, `startTime`, `stopAt`, `endTime`, `deltaT`, `writeControl`, `writeInterval`, `runTimeModifiable`
> - **การใช้งาน:** กำหนดระยะเวลา, ความละเอียดเวลา, และความถี่ในการบันทึกผลลัพธ์
>
> นี่เป็นไฟล์แรกที่คุณต้องตรวจสอบเมื่อเริ่มต้นหรือดีบักการจำลองแบบ

```cpp
// system/controlDict
application     simpleFoam;

startFrom       startTime;
startTime       0;

stopAt          endTime;
endTime         1000;

deltaT          1;

writeControl    timeStep;
writeInterval   100;

runTimeModifiable true;
```

| Keyword | Options | Description |
|---------|---------|-------------|
| `startFrom` | startTime, firstTime, latestTime | เริ่มจากเวลาไหน |
| `stopAt` | endTime, writeNow, noWriteNow, nextWrite | หยุดเมื่อไหร่ |
| `writeControl` | timeStep, runTime, adjustableRunTime | เงื่อนไขการเขียน |
| `writeInterval` | Number | ความถี่การเขียน |

---

## Field Time Management

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain A: Physics & Fields** + **Domain E: Coding**
> - **Field Storage:** Fields ถูกเก็บใน time directories (`0/`, `0.1/`, `0.2/`, ...)
> - **Code Structure:** `GeometricField` class ใน `src/OpenFOAM/fields/GeometricField/GeometricField.C`
> - **Temporal Schemes:** `system/fvSchemes` → `ddtSchemes`
> - **Usage:** `U.oldTime()`, `p.oldTime()` ใน solver code
>
> ระบบ oldTime ทำให้สามารถคำนวณ temporal derivatives (เช่น $\frac{\partial \phi}{\partial t}$) ได้

### Old Time Storage

```cpp
// เก็บค่าก่อนหน้าสำหรับ temporal schemes
void GeometricField::storeOldTime()
{
    if (!field0Ptr_)
    {
        field0Ptr_ = new GeometricField(*this);
    }
    *field0Ptr_ = *this;  // Copy current to old
}

// เข้าถึงค่าก่อนหน้า
const GeometricField& GeometricField::oldTime() const
{
    return *field0Ptr_;
}
```

### Temporal Schemes

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain B: Numerics & Linear Algebra** — Temporal Discretization
> - **ไฟล์:** `system/fvSchemes`
> - **Section:** `ddtSchemes`
> - **Keywords:** `default`, `Euler`, `backward`, `CrankNicolson`
> - **Code Implementation:** `src/finiteVolume/finiteVolume/ddtSchemes/`
>
> การเลือก scheme ส่งผลต่อ **ความแม่นยำ** (order of accuracy) และ **ความเสถียร** (stability limit)

| Scheme | Old Times Needed | Formula |
|--------|------------------|---------|
| Euler | 1 ($\phi^n$) | $\frac{\phi^{n+1} - \phi^n}{\Delta t}$ |
| backward | 2 ($\phi^n$, $\phi^{n-1}$) | $\frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}$ |
| CrankNicolson | 1 | $\frac{\phi^{n+1} - \phi^n}{\Delta t} + 0.5(f^{n+1} + f^n)$ |

```cpp
// system/fvSchemes
ddtSchemes
{
    default         Euler;        // 1st order
    // default      backward;     // 2nd order
    // default      CrankNicolson 0.5;
}
```

---

## GeometricField Template

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain E: Coding/Customization** — เข้าใจ Template Structure ของ Fields
> - **Source Code:** `src/OpenFOAM/fields/GeometricField/GeometricField.H`
> - **Type Definitions:** `src/OpenFOAM/fields/GeometricField/geometricFieldFwd.H`
> - **Usage:** สร้าง custom fields ใน solver หรือ boundary conditions
> - **Common Types:** `volScalarField`, `volVectorField`, `surfaceScalarField`
>
> Template นี้เป็นพื้นฐานของทุก field ที่คุณใช้ใน OpenFOAM

```cpp
template<class Type, template<class> class PatchField, class GeoMesh>
class GeometricField : public DimensionedField<Type, GeoMesh>
{
    // Time management
    mutable label timeIndex_;
    mutable GeometricField* field0Ptr_;      // n-1
    mutable GeometricField* fieldPrevIterPtr_; // Previous iteration
    
    // Boundary conditions
    FieldField<PatchField, Type> boundaryField_;
};
```

**Type aliases:**
```cpp
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;
typedef GeometricField<vector, fvPatchField, volMesh> volVectorField;
typedef GeometricField<scalar, fvsPatchField, surfaceMesh> surfaceScalarField;
```

---

## I/O Options

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain A: Physics & Fields** + **Domain E: Coding**
> - **Field Files:** `0/` (initial conditions), `0.1/`, `0.2/`, ... (time directories)
> - **I/O Control:** `IOobject` class ใน `src/OpenFOAM/db/IOobject/IOobject.H`
> - **Read Options:** `MUST_READ`, `READ_IF_PRESENT`, `NO_READ`
> - **Write Options:** `AUTO_WRITE`, `NO_WRITE`
>
> การตั้งค่าเหล่านี้กำหนดว่า field จะถูก **อ่าน** หรือ **เขียน** เมื่อไหร่ในระหว่าง simulation

```cpp
IOobject
(
    "p",                    // Field name
    runTime.timeName(),     // Time folder (e.g., "0")
    mesh,                   // Registry
    IOobject::MUST_READ,    // Read behavior
    IOobject::AUTO_WRITE    // Write behavior
)
```

| Read Option | Behavior |
|-------------|----------|
| `MUST_READ` | Error if not found |
| `READ_IF_PRESENT` | Use default if not found |
| `NO_READ` | Never read |

| Write Option | Behavior |
|--------------|----------|
| `AUTO_WRITE` | Write every writeInterval |
| `NO_WRITE` | Never write |

---

## Adjustable Time Step

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain C: Simulation Control** — Automatic Time Stepping
> - **ไฟล์:** `system/controlDict`
> - **Keywords:** `adjustTimeStep`, `maxCo`, `maxDeltaT`
> - **Solver Code:** `applications/solvers/incompressible/pimpleFoam/`
> - **Physics:** Courant-Friedrichs-Lewy (CFL) condition สำหรับความเสถียร
>
> ใช้สำหรับ transient solvers (เช่น `pimpleFoam`, `interFoam`) เพื่อปรับ deltaT อัตโนมัติตาม flow velocity

```cpp
// system/controlDict
adjustTimeStep  yes;
maxCo           1;      // Max Courant number
maxDeltaT       0.1;    // Max time step

// Implementation
scalar Co = max(mag(phi)/mesh.V()*runTime.deltaT()).value();
scalar newDeltaT = min(maxDeltaT, maxCo/Co * runTime.deltaT().value());
runTime.setDeltaT(newDeltaT);
```

---

## Function Objects

> [!NOTE] **📂 OpenFOAM Context**
> ส่วนนี้เป็น **Domain C: Simulation Control** — Runtime Post-processing
> - **ไฟล์:** `system/controlDict`
> - **Section:** `functions { ... }`
> - **Keywords:** `type`, `writeControl`, `writeInterval`, `fields`
> - **Code Implementation:** `src/OpenFOAM/db/functionObjects/`
> - **Common Types:** `fieldAverage`, `probes`, `sets`, `surfaces`, `forces`
>
> Function objects ช่วย **ประหยัดเวลา** และ **disk space** ด้วยการคำนวณ statistics ระหว่าง simulation แทนการ post-processing ภายหลัง

```cpp
functions
{
    fieldAverage1
    {
        type            fieldAverage;
        writeControl    writeTime;
        
        fields
        (
            U { mean on; prime2Mean on; }
            p { mean on; }
        );
    }
    
    probes1
    {
        type            probes;
        probeLocations  ((0.5 0 0) (1.0 0 0));
        fields          (p U);
    }
}
```

---

## Concept Check

<details>
<summary><b>1. oldTime() ใช้ทำอะไร?</b></summary>

เข้าถึงค่าของ field ที่ time step n-1 — ใช้สำหรับ temporal discretization schemes เช่น backward differencing ที่ต้องการค่าก่อนหน้า
</details>

<details>
<summary><b>2. writeControl vs writeInterval ต่างกันอย่างไร?</b></summary>

- **writeControl**: กำหนด *หน่วย* ของ interval (timeStep, runTime, etc.)
- **writeInterval**: กำหนด *จำนวน* ของหน่วยนั้น (เช่น ทุก 100 timeSteps หรือทุก 1 วินาที)
</details>

<details>
<summary><b>3. adjustTimeStep ทำงานอย่างไร?</b></summary>

ปรับ deltaT อัตโนมัติตาม Courant number — เมื่อ Co เกิน maxCo จะลด deltaT ลง เมื่อ Co ต่ำจะเพิ่ม deltaT (แต่ไม่เกิน maxDeltaT)
</details>

---

## เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md)
- **บทถัดไป:** [03_ObjectRegistry.md](03_ObjectRegistry.md)