# Time Architecture

สถาปัตยกรรมการจัดการเวลาใน OpenFOAM

---

## Learning Objectives

เมื่ออ่านจบบทนี้ คุณจะสามารถ:
- **อธิบาย** บทบาทและหน้าที่ของ `Time` class ใน OpenFOAM
- **กำหนดค่า** controlDict เพื่อควบคุม time stepping และ data output
- **เลือกใช้** temporal discretization schemes ที่เหมาะสมกับปัญหา
- **ประยุกต์ใช้** adjustable time step สำหรับการจำลองแบบ transient
- **จัดการ** field I/O และ oldTime storage สำหรับการคำนวณ time-dependent

> [!TIP] ทำไม Time Architecture สำคัญ?
> **Time Architecture** คือหัวใจของการจำลองแบบที่ไม่คงที่ (unsteady/transient simulation) การเข้าใจการทำงานของ `Time` class และการจัดการ time step จะช่วยให้คุณ:
> - ควบคุม **ความเสถียร** ของการคำนวณ (โดยเฉพาะ Courant number)
> - ปรับแต่ง **ความแม่นยำ** ของ temporal discretization
> - บริหารจัดการ **disk space** ด้วยการเขียนผลลัพธ์อย่างมีประสิทธิภาพ
> - เข้าใจการทำงานของ **adjustable time step** สำหรับกรณีที่มีการเปลี่ยนแปลงเวลาจริง

---

## Overview

**Domain Context:** บทนี้เกี่ยวข้องกับ **Domain C: Simulation Control** และ **Domain E: Coding/Customization**

- **ไฟล์หลัก:** `system/controlDict`, `system/fvSchemes`
- **Keywords:** `startFrom`, `startTime`, `stopAt`, `endTime`, `deltaT`, `writeControl`, `writeInterval`, `adjustTimeStep`, `ddtSchemes`
- **Class:** `Time` ใน `src/OpenFOAM/db/Time/Time.C`
- **Solver Pattern:** `while (runTime.loop()) { ... }`

คลาส `Time` จัดการ:
- **Time stepping** — จาก startTime → endTime
- **Data I/O** — อ่าน/เขียน fields ตาม time directories
- **Field history** — เก็บ oldTime สำหรับ temporal schemes

---

## Core Time Class

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

## controlDict Configuration

**Domain Context:** **Domain C: Simulation Control** — ไฟล์ควบคุมการจำลองแบบที่สำคัญที่สุด

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

### Time Control Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| `startFrom` | `startTime`, `firstTime`, `latestTime` | เริ่มจากเวลาไหน |
| `startTime` | Number | เวลาเริ่มต้น (เมื่อใช้ startTime) |
| `stopAt` | `endTime`, `writeNow`, `noWriteNow`, `nextWrite` | หยุดเมื่อไหร่ |
| `endTime` | Number | เวลาสิ้นสุด |
| `deltaT` | Number | Time step size |
| `writeControl` | `timeStep`, `runTime`, `adjustableRunTime`, `cpuTime` | เงื่อนไขการเขียน |
| `writeInterval` | Number | ความถี่การเขียน |

### Write Control Strategies

- **timeStep:** เขียนทุก N time steps
- **runTime:** เขียนทุก N วินาทีของเวลาจำลองแบบ
- **adjustableRunTime:** เขียนทุก N วินาที แต่ปรับจังหวะเพื่อให้ตรงกับ time step ที่เป็นจริง

---

## Field Time Management

**Domain Context:** **Domain A: Physics & Fields** + **Domain B: Numerics**

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

### Temporal Discretization Schemes

**Configuration:** `system/fvSchemes` → `ddtSchemes`

```cpp
ddtSchemes
{
    default         Euler;           // 1st order implicit
    // default      backward;        // 2nd order implicit
    // default      CrankNicolson 0.5;  // 2nd order blended
}
```

| Scheme | Order | Old Times Needed | Stability | Use Case |
|--------|-------|------------------|-----------|----------|
| **Euler** | 1st | 1 ($\phi^n$) | Unconditionally stable | Quick simulations, debugging |
| **backward** | 2nd | 2 ($\phi^n$,1$\phi^{n-1}$) | Conditionally stable | Higher accuracy transient |
| **CrankNicolson** | 2nd | 1 | Conditionally stable | Balanced accuracy/stability |

**Mathematical formulations:**

- **Euler:**1$\frac{\phi^{n+1} - \phi^n}{\Delta t}$
- **backward:**1$\frac{3\phi^{n+1} - 4\phi^n + \phi^{n-1}}{2\Delta t}$
- **CrankNicolson:**1$\frac{\phi^{n+1} - \phi^n}{\Delta t} + 0.5(f^{n+1} + f^n)$

---

## Adjustable Time Stepping

**Domain Context:** **Domain C: Simulation Control** — Automatic Time Stepping

**Configuration:** `system/controlDict`

```cpp
adjustTimeStep  yes;
maxCo           1;      // Max Courant number
maxDeltaT       0.1;    // Max time step [s]
```

**Mechanism:** ปรับ deltaT อัตโนมัติตาม Courant-Friedrichs-Lewy (CFL) condition

```cpp
// Pseudo-code จาก solver implementation
scalar Co = max(mag(phi)/mesh.V()*runTime.deltaT()).value();
scalar newDeltaT = min(maxDeltaT, maxCo/Co * runTime.deltaT().value());
runTime.setDeltaT(newDeltaT);
```

**Guidelines:**
- **maxCo = 1:** เหมาะสำหรับ PISO/PIMPLE solvers
- **maxCo = 0.3-0.5:** เหมาะสำหรับ multiphase flows
- **maxDeltaT:** จำกัดไม่ให้ time step ใหญ่เกินไปเมื่อ flow ช้า

---

## Function Objects for Time Monitoring

**Domain Context:** **Domain C: Simulation Control** — Runtime Post-processing

**Configuration:** `system/controlDict` → `functions`

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
    
    timeExecution
    {
        type            executionTime;
        writeControl    timeStep;
        writeInterval   1;
    }
}
```

**Common function objects:**
- **fieldAverage:** Compute time-averaged fields
- **probes:** Monitor fields at specific locations
- **sets:** Sample along lines/surfaces
- **forces:** Compute forces on patches
- **executionTime:** Track computational cost

---

## I/O Options

**Domain Context:** **Domain E: Coding** — Field I/O Configuration

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

### Read Options

| Option | Behavior | Use Case |
|--------|----------|----------|
| `MUST_READ` | Error if not found | Initial conditions (0/ folder) |
| `READ_IF_PRESENT` | Use default if not found | Optional fields |
| `NO_READ` | Never read | Calculated fields |

### Write Options

| Option | Behavior | Use Case |
|--------|----------|----------|
| `AUTO_WRITE` | Write every writeInterval | Solution fields |
| `NO_WRITE` | Never write | Intermediate/temporary fields |

---

## Common Issues and Solutions

### Issue 1: Time Step Too Large

**Symptoms:** Solver diverges, Courant number exceeds limit

**Solution:**
```cpp
// ลด deltaT เบื้องต้น
deltaT 0.001;

// หรือใช้ adjustable time step
adjustTimeStep yes;
maxCo 0.5;
```

### Issue 2: Excessive Disk Usage

**Symptoms:** Too many time directories written

**Solution:**
```cpp
// ลดความถี่การเขียน
writeControl    adjustableRunTime;
writeInterval   10;  // เขียนทุก 10 วินาที simulation time

// หรือใช้ purgeWrite
purgeWrite      5;   // เก็บเฉพาะ 5 time directories ล่าสุด
```

### Issue 3: Old Time Field Missing

**Symptoms:** Error accessing `oldTime()` when using backward scheme

**Solution:** Ensure solver calls `storeOldTime()` before first iteration
```cpp
if (!mesh.solutionDict().found("noOldTime"))
{
    U.storeOldTime();
}
```

---

## 🧠 Concept Check

<details>
<summary><b>1. oldTime() ใช้ทำอะไร?</b></summary>

เข้าถึงค่าของ field ที่ time step n-1 — ใช้สำหรับ temporal discretization schemes เช่น backward differencing ที่ต้องการค่าก่อนหน้า
</details>

<details>
<summary><b>2. writeControl vs writeInterval ต่างกันอย่างไร?</b></summary>

- **writeControl**: กำหนด *หน่วย* ของ interval (timeStep, runTime, adjustableRunTime)
- **writeInterval**: กำหนด *จำนวน* ของหน่วยนั้น (เช่น ทุก 100 timeSteps หรือทุก 1 วินาที)
</details>

<details>
<summary><b>3. adjustTimeStep ทำงานอย่างไร?</b></summary>

ปรับ deltaT อัตโนมัติตาม Courant number — เมื่อ Co เกิน maxCo จะลด deltaT ลง เมื่อ Co ต่ำจะเพิ่ม deltaT (แต่ไม่เกิน maxDeltaT)
</details>

<details>
<summary><b>4. Euler vs backward scheme: เลือกอะไรเมื่อไหร่?</b></summary>

- **Euler:** เริ่มต้น simulation, debugging, หรือเมื่อความแม่นยำ temporal ไม่สำคัญ
- **backward:** เมื่อต้องการความแม่นยำระดับสอง (2nd order) สำหรับ transient cases
</details>

---

## Key Takeaways

- **Time class** เป็นหัวใจของการจำลองแบบ transient — ควบคุม loop, I/O, และ field history
- **controlDict** คือศูนย์รวมการตั้งค่าเวลา — startFrom, stopAt, deltaT, writeControl
- **Temporal schemes** เชื่อมโยงกับ oldTime storage — backward ต้องการ 2 old time levels
- **Adjustable time step** ช่วยรักษาเสถียรภาพ — ปรับ deltaT ตาม Courant number อัตโนมัติ
- **Function objects** ให้ runtime monitoring — ลดเวลา post-processing และ disk space
- **I/O options** ควบคุม field storage — MUST_READ/AUTO_WRITE สำหรับ solution fields

---

## 📖 เอกสารที่เกี่ยวข้อง

- **บทก่อนหน้า:** [01_Introduction.md](01_Introduction.md)
- **บทถัดไป:** [03_ObjectRegistry.md](03_ObjectRegistry.md)
- **GeometricFields:** [Module 05 - Fields and GeometricFields](../05_FIELDS_GEOMETRICFIELDS/00_Overview.md)
- **Numerical Methods:** [Module 02 - Pressure-Velocity Coupling](../../03_SINGLE_PHASE_FLOW/CONTENT/02_PRESSURE_VELOCITY_COUPLING/00_Overview.md)