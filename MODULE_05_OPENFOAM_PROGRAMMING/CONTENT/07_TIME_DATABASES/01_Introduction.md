# Time & Databases - Practical Introduction

บทนำการใช้งาน Time และการเริ่มต้นจำลองใน OpenFOAM

---

## 🎯 Learning Objectives

- เขียน time loop ขั้นพื้นฐานและควบคุมการทำงานของการจำลอง
- ตั้งค่า controlDict และเข้าใจพารามิเตอร์ที่สำคัญ
- ใช้เมธอดหลักของ Time class ในการอ่านค่าและควบคุมการเขียนผลลัพธ์

---

## 📋 Prerequisites

- ความเข้าใจพื้นฐานเกี่ยวกับ C++ pointer และ references
- ความคุ้นเคยกับโครงสร้าง solver ของ OpenFOAM

---

## 1. Basic Time Loop Structure

โครงสร้าง time loop เป็นหัวใจของ solver ทุกตัวใน OpenFOAM:

```cpp
#include "createTime.H"  // สร้าง Time object (runTime)
#include "createMesh.H"  // สร้าง mesh object

while (runTime.loop())  // วนลูปจนกว่าจะถึง endTime
{
    Info << "Time = " << runTime.timeName() << nl;

    // แก้สมการ (Solve equations)
    solve(fvm::ddt(U) + fvm::div(phi, U) - fvm::laplacian(nu, U));

    // เขียนผลลัพธ์ถ้าถึงเวลาที่กำหนด
    runTime.write();
}

Info << "End\n" << endl;
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `createTime.H` | สร้าง `runTime` object สำหรับควบคุมเวลา |
| `createMesh.H` | สร้าง `mesh` object จากข้อมูลใน constant/polyMesh |
| `runTime.loop()` | เพิ่มค่าเวลาและตรวจสอบว่าควรทำต่อหรือไม่ |
| `runTime.write()` | เขียนผลลัพธ์ถ้าถึงช่วงเวลาที่กำหนด |

---

## 2. controlDict Parameters Detailed

ไฟล์ `system/controlDict` คุมการทำงานของ time loop:

### 2.1 Time Control Parameters

```cpp
application     simpleFoam;      // Solver ที่ใช้

startFrom       startTime;        // จุดเริ่มต้นการจำลอง
startTime       0;                // เวลาเริ่มต้น

stopAt          endTime;          // จุดสิ้นสุดการจำลอง
endTime         1000;             // เวลาสิ้นสุด

deltaT          1;                // ขนาด time step
```

**Parameter Options:**

| Parameter | Options | Description |
|-----------|---------|-------------|
| `startFrom` | `startTime`, `latestTime`, `firstTime` | จุดเริ่มต้นของการจำลอง |
| `stopAt` | `endTime`, `writeNow`, `nextWrite`, `noWriteNow` | เงื่อนไขการหยุด |
| `deltaT` | ค่าตัวเลข (สำหรับ steady state ใช้ 1) | ขนาด time step |

### 2.2 Write Control Parameters

```cpp
writeControl    timeStep;         // วิธีการควบคุมการเขียน
writeInterval   100;              // ช่วงเวลาการเขียน

purgeWrite      5;                // เก็บเฉพาะ 5 time folders ล่าสุด
writeFormat     ascii;            // รูปแบบไฟล์
writePrecision  6;                // ความแม่นยำของตัวเลข
writeCompression off;             // บีบอัดไฟล์หรือไม่
timeFormat      general;          // รูปแบบชื่อ time directory
timePrecision   6;                // จำนวนหลักในชื่อ directory
```

**Write Control Options:**

| `writeControl` | Meaning of `writeInterval` |
|----------------|---------------------------|
| `timeStep` | เขียนทุก N time steps |
| `runTime` | เขียนทุก N วินาทีของเวลาจำลอง |
| `adjustedRunTime` | เขียนทุก N วินาที (ปรับค่าเพื่อให้เขียนที่เวลาพอดี) |
| `cpuTime` | เขียนทุก N วินาทีของ CPU time |
| `clockTime` | เขียนทุก N วินาทีของเวลาจริง |

### 2.3 Adjustable Time Control (Transient)

สำหรับการจำลอง transient ที่ต้องการปรับ time step อัตโนมัติ:

```cpp
adjustTimeStep  yes;                    // เปิดการปรับ time step
maxCo           0.5;                    // ค่า Courant number สูงสุด
maxDeltaT       1;                      // ค่า time step สูงสุด

// หรือกำหนดจาก Courant number
maxAlphaCo      0.5;                    // สำหรับ VOF models
```

---

## 3. Key Time Methods

### 3.1 Time Query Methods

```cpp
// อ่านค่าเวลาปัจจุบัน (scalar)
scalar t = runTime.value();

// อ่านค่า time step (dimensionedScalar)
scalar dt = runTime.deltaT().value();

// อ่านชื่อเวลา (string) - ใช้ตั้งชื่อ directory
word tName = runTime.timeName();  // เช่น "0", "10.5", "100"
```

### 3.2 Loop Control Methods

```cpp
// วนลูปและเพิ่มเวลา - return false เมื่อถึง endTime
bool continue = runTime.loop();

// ตรวจสอบว่าควรทำต่อหรือไม่ (โดยไม่เพิ่มเวลา)
bool shouldContinue = runTime.run();

// เพิ่มเวลา 1 step
runTime++;
```

### 3.3 Write Control Methods

```cpp
// เขียนถ้าถึงเวลาที่กำหนด (ตาม writeInterval)
runTime.write();

// เขียนทันที (บังคับ)
runTime.writeNow();

// เขียนแล้วหยุดการจำลอง
runTime.writeAndEnd();
```

---

## 4. Common Usage Patterns

### 4.1 Steady-State Simulation

```cpp
// controlDict
deltaT          1;
writeControl    timeStep;
writeInterval   100;

// Solver
while (runTime.loop())
{
    // Initial residual สำหรับ convergence
    solve(UEqn == -fvc::grad(p));
    
    runTime.write();
}
```

### 4.2 Transient Simulation

```cpp
// controlDict
deltaT          0.001;
writeControl    adjustedRunTime;
writeInterval   0.1;  // เขียนทุก 0.1 วินาที

adjustTimeStep  yes;
maxCo           0.5;

// Solver
while (runTime.loop())
{
    #include "UEqn.H"
    
    // Time-accurate solution
    tmp<fvVectorMatrix> tUEqn
    (
        fvm::ddt(U) + fvm::div(phi, U) - fvm::laplacian(nu, U)
    );
    
    solve(tUEqn());
    runTime.write();
}
```

### 4.3 Multi-Region Simulation

```cpp
// Multiple time objects สำหรับแต่ละ region
Foam::Time runTime1(Foam::Time::controlDictName, rootPath, casePath, "region1");
Foam::Time runTime2(Foam::Time::controlDictName, rootPath, casePath, "region2");

while (runTime1.loop() && runTime2.loop())
{
    // Solve for region1
    // Solve for region2
}
```

---

## 5. Quick Reference Table

| Task | Code Snippet |
|------|--------------|
| Current time value | `runTime.value()` |
| Time step size | `runTime.deltaT().value()` |
| Time directory name | `runTime.timeName()` |
| Continue simulation | `runTime.loop()` |
| Manual time increment | `runTime++` |
| Write if scheduled | `runTime.write()` |
| Force immediate write | `runTime.writeNow()` |
| Write and terminate | `runTime.writeAndEnd()` |
| Check if running | `runTime.run()` |
| Time index (integer) | `runTime.timeIndex()` |

---

## 6. Troubleshooting Common Issues

### Issue 1: Time Loop Not Advancing

**Symptom:** `runTime.value()` ไม่เพิ่มขึ้น

```cpp
// ❌ WRONG - เรียก run() แทน loop()
while (runTime.run())  // ไม่เพิ่มเวลา
{
    // ... 
    runTime++;  // ต้องเพิ่มเวลาเอง
}

// ✅ CORRECT - loop() เพิ่มเวลาให้อัตโนมัติ
while (runTime.loop())
{
    // ...
}
```

### Issue 2: Output Files Not Written

**Symptom:** ไม่เห็น time directories ใน processor folders

**Solution:** ตรวจสอบ `writeControl` และ `writeInterval`:

```cpp
// ถ้า writeControl = timeStep
writeInterval   100;  // เขียนทุก 100 steps

// ถ้า writeControl = runTime
writeInterval   10;   // เขียนทุก 10 วินาทีของเวลาจำลอง
```

### Issue 3: Time Folder Names Wrong

**Symptom:** ชื่อ directory เป็น "0.100000" แทนที่จะเป็น "0.1"

**Solution:** ปรับ `timePrecision`:

```cpp
timeFormat      general;
timePrecision   6;  // ลดเหลือ 3 หรือใช้ fixed format
```

---

## 🧠 Concept Check

<details>
<summary><b>1. loop() ทำอะไรบ้าง?</b></summary>

`loop()` ทำ 2 อย่าง:
1. เพิ่มค่าเวลา (`runTime++`) ตาม `deltaT`
2. Return `true` ถ้ายังไม่ถึง endTime, return `false` ถ้าถึงแล้ว

</details>

<details>
<summary><b>2. timeName() ต่างจาก value() อย่างไร?</b></summary>

- **`timeName()`**: Return `word` (string) - ใช้สำหรับตั้งชื่อ directory เช่น "0", "10.5"
- **`value()`**: Return `scalar` (double) - ใช้สำหรับการคำนวณ

ตัวอย่าง:
```cpp
scalar t = runTime.value();        // t = 10.5
word name = runTime.timeName();    // name = "10.5"
```

</details>

<details>
<summary><b>3. writeControl ทำงานอย่างไร?</b></summary>

`writeControl` กำหนด **เงื่อนไขการเขียน** ผลลัพธ์:

- `timeStep`: เขียนเมื่อ `(timeIndex % writeInterval == 0)`
- `runTime`: เขียนเมื่อ `(value() / writeInterval)` เป็นจำนวนเต็ม
- `adjustedRunTime`: ปรับ deltaT เล็กน้อยเพื่อให้เขียนที่เวลาพอดี

ร่วมกับ `writeInterval` ซึ่งกำหนด **ความถี่** ของการเขียน

</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ writeNow()?</b></summary>

ใช้ `writeNow()` เมื่อต้องการ:
- เขียนผลลัพธ์ทันทีไม่ว่าจะถึงเวลาหรือไม่
- Capture state พิเศษเช่น ก่อน crash หรือ checkpoint
- Debug เพื่อดูค่าขณะนั้น

**⚠️ Warning:** อย่าใช้ใน loop หลักเพราะจะเขียนทุก step และใช้ดิสก์มาก

</details>

---

## 📚 Further Reading

- **ภาพรวม:** [00_Overview.md](00_Overview.md)
- **Architecture:** [02_Time_Architecture.md](02_Time_Architecture.md)
- **Runtime Issues:** [06_Runtime_Issues.md](06_Runtime_Issues.md)