# Unit Testing

การทดสอบระดับหน่วย (Unit Testing)

---

## Learning Objectives

หลังจากศึกษาบทนี้ คุณจะสามารถ:
- **อธิบาย (WHAT)** ความหมายและบทบาทของ Unit Testing ในการพัฒนา OpenFOAM
- **เข้าใจ (WHY)** ประโยชน์และแรงจูงใจในการใช้ Unit Testing ที่มีต่อคุณภาพซอฟต์แวร์
- **นำไปใช้ (HOW)** เขียน Unit Test สำหรับฟังก์ชัน คลาส และ Field ด้วย assertion ที่เหมาะสม
- **จัดระเบียบ** โครงสร้างไฟล์และไดเรกทอรีสำหรับการทดสอบอย่างเป็นระบบ
- **หลีกเลี่ยง** ข้อผิดพลาดทั่วไปในการเขียน Unit Test

---

## Overview

> **Unit test** = Test individual functions/classes in isolation

### WHAT: Unit Testing คืออะไร?

Unit Testing คือการทดสอบเชิงหน่วย (เชิงส่วนประกอบ) ที่เน้นทดสอบฟังก์ชัน คลาส หรือเมธอดแต่ละอย่างแยกจากกัน (isolated) โดยไม่พึ่งพาส่วนประกอบอื่นๆ ภายนอก ในบริบทของ OpenFOAM หมายถึง:

- **Function-level test:** ทดสอบฟังก์ชันคณิตศาสตร์ (`mag`, `sqr`, `pow`)
- **Class-level test:** ทดสอบคลาสพื้นฐาน (`vector`, `tensor`, `Field`)
- **Method-level test:** ทดสอบเมธอดของคลาส (`solve()`, `correct()`)
- **NOT:** ทดสอบทั้ง case หรือทั้ง solver (นั่นคือ System Test)

### WHY: ทำไมต้อง Unit Testing?

#### 🎯 **เพิ่มความมั่นใจในคุณภาพโค้ด**

**ปัญหา:** การแก้ไขโค้ดเก่าอาจทำให้ฟังก์ชันที่เคยทำงานได้พังลงโดยไม่รู้ตัว (regression)

**วิธีแก้:** Unit Test ทำหน้าที่เป็น "safety net" ที่จับความผิดพลาดทันทีที่เกิดขึ้น:

```
แก้โค้ด → Run Test → Fail ทันที → รู้ว่าพังตรงไหน → แก้ไขได้ทันที
```

#### ⚡ **ลดเวลา Debug**

- **ไม่มี Test:** พบปัญหาตอน run case → ใช้เวลาหลายชั่วโมงหาสาเหตุ
- **มี Test:** พบปัญหาตอน run test → รู้ทันทีว่าฟังก์ชันไหนผิด → แก้ในไม่กี่นาที

#### 📈 **ช่วย Refactor อย่างมั่นใจ**

เมื่อต้องการปรับปรุงประสิทธิภาพโค้ด (refactor):
1. เขียน Test ครอบคลุมฟังก์ชันที่จะแก้
2. Run Test ให้ผ่านก่อน (baseline)
3. Refactor โค้ด
4. Run Test อีกครั้ง → ถ้าผ่าน แปลว่าไม่ทำลายฟังก์ชันเดิม

#### 💰 **ลดค่าใช้จ่ายระยะยาว**

| Stage | Find Bug Cost | Fix Time |
|-------|--------------|----------|
| Unit Testing | $1 | 5 นาที |
| Integration Testing | $10 | 1 ชั่วโมง |
| System Testing | $100 | 1 วัน |
| Production | $1000+ | สัปดาห์/เดือน |

#### 🚀 **เอกสารที่เป็น "Living Documentation"**

Test ที่ดีคือ "ตัวอย่างการใช้งาน" (usage example) ที่สามารถ:
- อธิบายว่าฟังก์ชันทำอะไร (พร้อมตัวอย่าง input/output)
- แสดง behavior ที่คาดหวัง (edge case, error case)
- อัปเดตตามโค้ดเสมอ (ไม่ตกยุคเหมือน README)

### HOW: Unit Test ใน OpenFOAM ทำงานอย่างไร?

```
┌─────────────────────────────────────────────────────┐
│              OpenFOAM Test Framework                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐      ┌─────────────┐              │
│  │   Test .C   │ ───→ │   wmake     │              │
│  │   (Source)  │      │  (Compile)  │              │
│  └─────────────┘      └──────┬──────┘              │
│                              ↓                      │
│                      ┌─────────────┐               │
│                      │   Test-XXX  │               │
│                      │  (Executable)│               │
│                      └──────┬──────┘               │
│                             ↓                      │
│                      ┌─────────────┐               │
│                      │   Run Test  │               │
│                      │  (Execution) │               │
│                      └──────┬──────┘               │
│                             ↓                      │
│                      ┌─────────────┐               │
│                      │  PASS/FAIL  │               │
│                      │  (Report)   │               │
│                      └─────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Testing Pyramid: มองภาพรวมแนวทางการทดสอบ

<!-- IMAGE: IMG_08_003 -->
<!-- 
Purpose: เพื่อแสดง "Pyramid of Testing" ให้เห็นสัดส่วนของการทดสอบ. ฐานรากคือ Unit Test (เยอะ, เร็ว, ราคาถูก). ตรงกลางคือ Integration Test (เทสการเชื่อมต่อ). ยอดคือ System Test (เทสทั้งระบบ). OpenFOAM ควรเน้นฐานรากให้แน่น
Prompt: "Software Testing Pyramid for CFD Development. **Base Layer (70%):** 'Unit Tests' (Class check, Math routines). Color: Green. Features: Fast, Isolated. **Middle Layer (20%):** 'Integration Tests' (Physics Models, BCs). Color: Blue. Features: Modules connecting. **Top Layer (10%):** 'System/Validation Tests' (Full Case Run). Color: Red. Features: Slow, Expensive. **Constraint:** Arrows on the side showing 'Execution Speed (Fast $\rightarrow$ Slow)' and 'Cost (Low $\rightarrow$ High)'. STYLE: Infographic pyramid, clean flat layers."
-->
![IMG_08_003: Testing Pyramid](IMG_08_003.jpg)

**สัดส่วนที่เหมาะสมสำหรับ OpenFOAM Development:**
- **Unit Tests (70%):** Test ฟังก์ชันคณิตศาสตร์, คลาสพื้นฐาน → รันไว (ms), รันได้บนเครื่องใดก็ได้
- **Integration Tests (20%):** Test การเชื่อมต่อ physics models → รันช้ากว่า (นาที), ต้องการ mesh
- **Validation Tests (10%):** Test ทั้ง case เทียบกับ experimental/data → ช้าที่สุด (ชั่วโมง/วัน)

---

## 1. OpenFOAM Test Structure

### WHAT: โครงสร้างพื้นฐานของ Unit Test

OpenFOAM ใช้ Test Framework แบบ Lightweight ที่ออกแบบมาเพื่อ:
- **Minimal overhead:** เขียน test ง่าย ไม่ต้อง setup ซับซ้อน
- **Fast execution:** แต่ละ test รันเสร็จภายในมิลลิวินาที
- **Clear output:** บอกได้ทันทีว่า test ไหน fail และทำไม

### WHY: ทำไมต้อง inherit จาก `Test::TestCase`

การสืบทอดจาก `Test::TestCase` ช่วยให้:
- เรียกใช้ assertion macros ได้ (`ASSERT_EQ`, `ASSERT_NEAR`)
- Framework รู้จักและจัดการ test นี้โดยอัตโนมัติ
- สามารถรวมเข้าเป็น test suite ได้

### HOW: เขียน Test Case แรกของคุณ

**ตัวอย่างที่ 1: ทดสอบ Vector Operations**

```cpp
#include "TestCase.H"
#include "fvCFD.H"

// สร้าง test class โดยสืบทอดจาก Test::TestCase
class vectorTest : public Test::TestCase
{
public:
    // รัน test ทั้งหมดใน method นี้
    void runTest()
    {
        // สร้าง vectors สำหรับทดสอบ
        vector a(1, 0, 0);  // Unit vector in x-direction
        vector b(0, 1, 0);  // Unit vector in y-direction
        
        // Test cross product: a × b ควรเท่ากับ (0, 0, 1)
        vector c = a ^ b;
        
        // Assert ว่าผลลัพธ์ตรงกับที่คาดหวัง
        ASSERT_EQ(c, vector(0, 0, 1));
        
        // Test magnitude
        scalar magA = mag(a);
        ASSERT_NEAR(magA, 1.0, 1e-10);
        
        // Test dot product
        scalar dotAB = a & b;
        ASSERT_EQ(dotAB, 0.0);  // Perpendicular vectors
    }
};
```

**คำอธิบาย:**
1. `#include "TestCase.H"`: รวม framework สำหรับ testing
2. `class vectorTest : public Test::TestCase`: สร้าง test class
3. `void runTest()`: method หลักที่มี test cases ทั้งหมด
4. `ASSERT_EQ`: เช็คความเท่ากันทุติยภูมิ (exact equality)
5. `ASSERT_NEAR`: เช็คความใกล้เคียงสำหรับ floating-point

**ตัวอย่างที่ 2: ทดสอบ Tensor Operations**

```cpp
class tensorTest : public Test::TestCase
{
public:
    void runTest()
    {
        // สร้าง identity tensor
        tensor I(1, 0, 0, 0, 1, 0, 0, 0, 1);
        
        // Test ว่า I × v = v (identity property)
        vector v(2, 3, 4);
        vector result = I & v;
        
        ASSERT_EQ(result, v);
        
        // Test trace
        scalar tr = tr(I);
        ASSERT_NEAR(tr, 3.0, 1e-10);  // 1 + 1 + 1 = 3
    }
};
```

---

## 2. Basic Assertions

### WHAT: Assertion Macros ที่มีให้ใช้

Assertion คือ "คำสั่งตรวจสอบ" ที่จะบอกว่าผลลัพธ์ที่ได้ตรงกับที่คาดหวังหรือไม่ ถ้าไม่ตรง → Test Fail

### WHY: ทำไมต้องหลายประเภท?

แต่ละประเภทออกแบบมาเพื่อการตรวจสอบที่เฉพาะเจาะจง:
- `ASSERT_EQ`: เช็คค่าที่แน่นอน (integer, string, exact values)
- `ASSERT_NEAR`: เช็คค่าที่มีความคลาดเคลื่อน (floating-point, physical quantities)
- `ASSERT_TRUE/FALSE`: เช็คเงื่อนไข (logic, state)
- `ASSERT_THROW`: เช็คว่า throw exception ตามที่คาดหวัง

### HOW: เลือกใช้ Assertion ที่เหมาะสม

#### 2.1 Exact Equality: `ASSERT_EQ`

ใช้เมื่อ: ต้องการเช็คความเท่ากันทุติยภูมิ 100%

```cpp
void testIntegerMath()
{
    int a = 5;
    int b = 3;
    int result = a + b;
    
    // เช็คว่า 5 + 3 = 8
    ASSERT_EQ(result, 8);
    
    // เช็ค vector equality
    vector v1(1, 2, 3);
    vector v2(1, 2, 3);
    ASSERT_EQ(v1, v2);
    
    // เช็ค string equality
    word name("turbulenceModel");
    ASSERT_EQ(name, word("turbulenceModel"));
}
```

**เมื่อไหร่ใช้:**
- Integer arithmetic
- Vector/tensor equality (ทุก component ตรง)
- String comparison
- Enum comparison

#### 2.2 Floating-Point Comparison: `ASSERT_NEAR`

ใช้เมื่อ: เช็คค่า floating-point ที่มีความคลาดเคลื่อนจาก rounding errors

**ปัญหา:**
```cpp
double a = 0.1 + 0.2;  // ผลลัพธ์คือ 0.30000000000000004
ASSERT_EQ(a, 0.3);     // ❌ FAIL! (ไม่เท่ากันทุติยภูมิ)
```

**วิธีแก้:**
```cpp
void testFloatingPoint()
{
    double a = 0.1 + 0.2;
    
    // เช็คว่า a อยู่ในช่วง ±tolerance จาก 0.3
    ASSERT_NEAR(a, 0.3, 1e-10);  // ✓ PASS
    
    // Test การคำนวณทางกายภาพ
    scalar rho = 1.225;  // kg/m³ (air density)
    scalar p = 101325;   // Pa (pressure)
    scalar T = 288.15;   // K (temperature)
    
    // Ideal gas law: R = p / (rho * T)
    scalar R_calc = p / (rho * T);
    scalar R_expected = 287.05;  // J/(kg·K) for air
    
    // ยอมรับความคลาดเคลื่อน 0.01%
    ASSERT_NEAR(R_calc, R_expected, 0.01);
}
```

**การเลือก Tolerance:**

| Type | Tolerance | ตัวอย่าง |
|------|-----------|-----------|
| Machine precision | `1e-15` | Double arithmetic แม่นยำ |
| Math functions | `1e-10` | `sin()`, `exp()`, `log()` |
| Physical quantities | `1e-6` | Pressure, Temperature |
| Engineering approximations | `1e-3` | Turbulence models |

**เมื่อไหร่ใช้:**
- Floating-point arithmetic
- Physical quantities (p, T, U)
- Math functions (`sin`, `exp`, `sqrt`)
- Numerical methods (iterative solvers)

#### 2.3 Boolean Checks: `ASSERT_TRUE` / `ASSERT_FALSE`

ใช้เมื่อ: เช็คเงื่อนไขหรือสถานะ

```cpp
void testLogicalConditions()
{
    vector v(0, 0, 0);
    
    // เช็คว่า vector เป็น zero vector
    ASSERT_TRUE(mag(v) < SMALL);  // SMALL คือค่าน้อยๆ ใน OpenFOAM
    
    // เช็คว่าไม่ใช่ null pointer
    autoPtr<fvMesh> meshPtr = createMesh();
    ASSERT_TRUE(meshPtr.valid());
    
    // เช็ค boundary condition type
    word patchType = mesh.boundary()[0].type();
    ASSERT_TRUE(patchType == "fixedValue" || patchType == "zeroGradient");
    
    // เช็คว่าไม่มี NaN หรือ Inf
    scalarField values(10, 1.0);
    ASSERT_FALSE(values.hasNaN());
    ASSERT_FALSE(values.hasInf());
}
```

**เมื่อไหร่ใช้:**
- Condition checks (`<`, `>`, `==`, `!=`)
- Pointer validity
- State flags (`converged`, `initialized`)
- Field validity (`hasNaN`, `hasInf`)

#### 2.4 Exception Checking: `ASSERT_THROW`

ใช้เมื่อ: ต้องการ verify ว่าฟังก์ชัน throw exception ตามที่คาดหวัง

```cpp
void testErrorHandling()
{
    // Test ว่า division by zero throw error
    ASSERT_THROW(1.0 / 0.0, std::overflow_error);
    
    // Test ว่า access นอก bounds throw error
    List<scalar> list(5);
    ASSERT_THROW(list[10], std::out_of_range);
    
    // Test ว่า invalid mesh construction throw error
    ASSERT_THROW(createInvalidMesh(), std::runtime_error);
}
```

**เมื่อไหร่ใช้:**
- Error handling validation
- Input validation
- Edge case handling

---

## 3. Testing Fields

### WHAT: Field Testing คืออะไร?

Field Testing คือการทดสอบ operations บน OpenFOAM fields ได้แก่:
- **volScalarField:** ค่าสเกลาร์บน cell centers
- **volVectorField:** เวกเตอร์บน cell centers
- **surfaceScalarField:** ค่าสเกลาร์บน faces (flux)

### WHY: ทำไมต้องทดสอบ Fields?

Fields คือ "heart" ของ OpenFOAM simulations:
- **Complex operations:** Field algebra มีความซับซ้อน (`div`, `grad`, `laplacian`)
- **Performance critical:** Operations ทำงานบนข้อมูลจำนวนมหาศาล
- **Easy to introduce bugs:** Dimension inconsistency, boundary condition errors

### HOW: เขียน Test สำหรับ Fields

#### 3.1 Test 1: Basic Field Operations

**เป้าหมาย:** ทดสอบการสร้างและ operations พื้นฐานบน scalar field

```cpp
void testBasicFieldOperations()
{
    // Setup: สร้าง mesh ง่ายๆ สำหรับ testing
    fvMesh mesh = createSimpleMesh(10, 10, 10);  // 10×10×10 cells
    
    // Test 1: สร้าง field ด้วย constant value
    volScalarField T
    (
        IOobject("T", mesh.time().constant(), mesh),
        mesh,
        dimensionedScalar("T", dimTemperature, 300.0)  // 300 K everywhere
    );
    
    // Verify: ทุก cell ควรมีค่า 300
    forAll(T, cellI)
    {
        ASSERT_NEAR(T[cellI], 300.0, 1e-10);
    }
    
    // Test 2: Field algebra - square operation
    volScalarField T2 = sqr(T);  // T² = 300² = 90000
    
    // Verify: ผลลัพธ์ต้องถูกต้อง
    ASSERT_NEAR(T2[0], 90000.0, 1e-6);
    ASSERT_NEAR(max(T2), 90000.0, 1e-6);
    ASSERT_NEAR(min(T2), 90000.0, 1e-6);
    
    // Test 3: Field arithmetic
    volScalarField T_sum = T + T2;  // 300 + 90000 = 90300
    ASSERT_NEAR(T_sum[100], 90300.0, 1e-6);
    
    // Test 4: Field with dimensions
    dimensionSet tempDims(dimTemperature);
    ASSERT_TRUE(T.dimensions() == tempDims);
    ASSERT_TRUE(T2.dimensions() == dimTemperature*dimTemperature);  // K²
}
```

**สิ่งที่ test นี้ตรวจสอบ:**
- ✓ Field initialization ถูกต้อง
- ✓ Element-wise operations (`sqr`, `+`)
- ✓ Field functions (`max`, `min`)
- ✓ Dimension consistency

#### 3.2 Test 2: Field with Spatial Variation

**เป้าหมาย:** ทดสอบ field ที่มีค่าแตกต่างกันในแต่ละตำแหน่ง

```cpp
void testSpatiallyVaryingField()
{
    fvMesh mesh = createSimpleMesh(20, 20, 20);
    
    // สร้าง coordinate field
    const volVectorField& C = mesh.C();  // Cell centers
    
    // สร้าง temperature field ที่เป็น linear gradient: T = 300 + 10*x
    volScalarField T
    (
        IOobject("T", mesh.time().constant(), mesh),
        mesh,
        dimensionedScalar("T", dimTemperature, 0.0)
    );
    
    // Set T ในแต่ละ cell ตามตำแหน่ง x
    forAll(T, cellI)
    {
        T[cellI] = 300.0 + 10.0 * C[cellI].x();
    }
    
    // Verify: เช็คค่าที่ cell แรก (x ≈ 0)
    ASSERT_NEAR(T[0], 300.0, 1.0);
    
    // Verify: เช็็คค่าที่ cell สุดท้าย (x ≈ L)
    scalar L = mesh.bounds().max().x();
    scalar T_max_expected = 300.0 + 10.0 * L;
    ASSERT_NEAR(max(T), T_max_expected, 1.0);
    
    // Test gradient operation: grad(T) ควร ≈ (10, 0, 0)
    volVectorField gradT = fvc::grad(T);
    
    // เช็คว่า gradT.x() ≈ 10 ทุก cell
    forAll(gradT, cellI)
    {
        ASSERT_NEAR(gradT[cellI].x(), 10.0, 0.5);  // ยอมรับ error จาก discretization
    }
}
```

**สิ่งที่ test นี้ตรวจสอบ:**
- ✓ Field assignment ทีละ cell
- ✓ Spatial variation
- ✓ Gradient calculation (`fvc::grad`)
- ✓ Numerical accuracy ของ discretization

#### 3.3 Test 3: Boundary Conditions

**เป้าหมาย:** ทดสอบว่า boundary conditions ทำงานถูกต้อง

```cpp
void testBoundaryConditions()
{
    fvMesh mesh = createMeshWithBCs();
    
    // สร้าง pressure field
    volScalarField p
    (
        IOobject("p", mesh.time().constant(), mesh),
        mesh,
        dimensionedScalar("p", dimPressure, 0.0),
        calculatedFvPatchScalarField::typeName
    );
    
    // Set fixed value ที่ patch ชื่อ "inlet"
    word inletPatchName = "inlet";
    label inletPatchID = mesh.boundaryMesh().findPatchID(inletPatchName);
    
    ASSERT_TRUE(inletPatchID != -1);  // Verify ว่ามี patch นี้จริง
    
    fvPatchScalarField& p_inlet = p.boundaryFieldRef()[inletPatchID];
    
    // Set ค่าที่ inlet = 101325 Pa
    p_inlet == 101325.0;
    
    // Verify: เช็คว่า BC ถูก set ถูกต้อง
    forAll(p_inlet, faceI)
    {
        ASSERT_NEAR(p_inlet[faceI], 101325.0, 1e-10);
    }
    
    // Test zeroGradient ที่ "outlet"
    word outletPatchName = "outlet";
    label outletPatchID = mesh.boundaryMesh().findPatchID(outletPatchName);
    
    fvPatchScalarField& p_outlet = p.boundaryFieldRef()[outletPatchID];
    ASSERT_TRUE(p_outlet.type() == zeroGradientFvPatchScalarField::typeName);
}
```

**สิ่งที่ test นี้ตรวจสอบ:**
- ✓ Boundary condition assignment (`==` operator)
- ✓ Patch identification
- ✓ BC type verification (`fixedValue`, `zeroGradient`)

#### 3.4 Test 4: Field Statistics and Reductions

**เป้าหมาย:** ทดสอบฟังก์ชันสรุปค่าทางสถิติ

```cpp
void testFieldStatistics()
{
    fvMesh mesh = createSimpleMesh(10, 10, 10);
    
    // สร้าง field ที่รู้ค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐาน
    volScalarField field
    (
        IOobject("field", mesh.time().constant(), mesh),
        mesh,
        dimensionedScalar("field", dimless, 0.0)
    );
    
    // Set ค่า: ครึ่งหนึ่งเป็น 1, อีกครึ่งเป็น -1
    for (label i = 0; i < mesh.nCells(); ++i)
    {
        field[i] = (i % 2 == 0) ? 1.0 : -1.0;
    }
    
    // Test 1: Mean value ควร ≈ 0
    scalar meanField = sum(field) / mesh.nCells();
    ASSERT_NEAR(meanField, 0.0, 1e-10);
    
    // Test 2: Min and Max
    ASSERT_NEAR(min(field), -1.0, 1e-10);
    ASSERT_NEAR(max(field), 1.0, 1e-10);
    
    // Test 3: gAverage (geometric average - weighted by volume)
    scalar gAvg = gAverage(field);
    ASSERT_NEAR(gAvg, 0.0, 1e-10);
    
    // Test 4: RMS (Root Mean Square)
    scalar rms = sqrt(sum(sqr(field)) / mesh.nCells());
    ASSERT_NEAR(rms, 1.0, 1e-10);
}
```

**สิ่งที่ test นี้ตรวจสอบ:**
- ✓ Reduction operations (`sum`, `max`, `min`)
- ✓ Weighted averages (`gAverage`)
- ✓ Statistical measures (`RMS`)

#### 3.5 Test 5: Field-Vector Interactions

**เป้าหมาย:** ทดสอบ operations ระหว่าง scalar และ vector fields

```cpp
void testFieldVectorInteractions()
{
    fvMesh mesh = createSimpleMesh(10, 10, 10);
    
    // สร้าง velocity field
    volVectorField U
    (
        IOobject("U", mesh.time().constant(), mesh),
        mesh,
        dimensionedVector("U", dimVelocity, vector::zero)
    );
    
    // Set U = (1, 2, 3) ทุก cell
    U == vector(1, 2, 3);
    
    // Test 1: Magnitude field
    volScalarField magU = mag(U);  // sqrt(1² + 2² + 3²) = sqrt(8) ≈ 3.742
    ASSERT_NEAR(magU[0], 3.74165738677, 1e-6);
    
    // Test 2: Component access
    volScalarField Ux = U.component(0);  // x-component
    volScalarField Uy = U.component(1);  // y-component
    volScalarField Uz = U.component(2);  // z-component
    
    ASSERT_NEAR(Ux[5], 1.0, 1e-10);
    ASSERT_NEAR(Uy[5], 2.0, 1e-10);
    ASSERT_NEAR(Uz[5], 3.0, 1e-10);
    
    // Test 3: Vector-scalar multiplication
    volScalarField alpha(mesh, dimensionedScalar("alpha", dimless, 2.0));
    volVectorField U_scaled = alpha * U;  // (2, 4, 6)
    
    ASSERT_NEAR(U_scaled[0].x(), 2.0, 1e-10);
    ASSERT_NEAR(U_scaled[0].y(), 4.0, 1e-10);
    ASSERT_NEAR(U_scaled[0].z(), 6.0, 1e-10);
    
    // Test 4: Dot product
    volVectorField V(mesh, dimensionedVector("V", dimVelocity, vector(4, 5, 6)));
    volScalarField dotProduct = U & V;  // 1*4 + 2*5 + 3*6 = 32
    
    ASSERT_NEAR(dotProduct[0], 32.0, 1e-10);
}
```

**สิ่งที่ test นี้ตรวจสอบ:**
- ✓ Vector magnitude calculation
- ✓ Component extraction
- ✓ Scalar-vector multiplication
- ✓ Dot product operations

---

## 4. Test Script

### WHAT: Automation Script สำหรับรัน Test ทุกตัว

Test script คือ shell script ที่:
- Compile test ทุกตัวใน project
- รัน test ตามลำดับ
- รวบรวมผลลัพธ์ (PASS/FAIL)
- แจ้งเตือนเมื่อมี test ล้มเหลว

### WHY: ทำไมต้อง automate?

**Manual testing:**
```bash
cd Test1
wmake
./Test-Test1
cd ../Test2
wmake
./Test-Test2
...  (ทำซ้ำทุกครั้งที่แก้โค้ด)
```
**Problems:**
- ใช้เวลานาน เบื่อ และเสี่ยงลืม
- ไม่สะดวกเมื่อ test มีหลายสิบตัว
- ยากต่อการ integrate กับ CI/CD

**Automated testing:**
```bash
./runAllTests.sh  →  รันทุก test อัตโนมัติ แล้วสรุปผล
```
**Benefits:**
- รันได้ด้วยคำสั่งเดียว
- รันได้ทุกครั้งที่แก้โค้ด (pre-commit hook)
- สามารถ integrate กับ Jenkins/GitHub Actions

### HOW: เขียน Test Script ที่ครอบคลุม

#### 4.1 Basic Test Runner

**ไฟล์: `runUnitTests.sh`**

```bash
#!/bin/bash
# runUnitTests.sh - รัน Unit Tests ทั้งหมดใน OpenFOAM project
# Usage: ./runUnitTests.sh [test_directory]

set -e  # หยุดทันทีถ้ามี command ล้มเหลว

# Configuration
TEST_DIR="${1:-$FOAM_RUN/../test}"  # Default: $FOAM_RUN/../test
LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo "========================================" | tee -a "$LOG_FILE"
echo "OpenFOAM Unit Test Runner" | tee -a "$LOG_FILE"
echo "Start time: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo ""

# ตรวจสอบว่า test directory มีอยู่จริง
if [ ! -d "$TEST_DIR" ]; then
    echo "❌ Error: Test directory not found: $TEST_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

echo "📂 Test directory: $TEST_DIR" | tee -a "$LOG_FILE"
echo ""

# Loop ผ่านทุก test subdirectory
for test_dir in "$TEST_DIR"/*/; do
    # ถ้าไม่มี subdirectory ใดๆ
    if [ ! -d "$test_dir" ]; then
        echo "⚠️  No test directories found in $TEST_DIR" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # ดึงชื่อ test (เอา path สุดท้าย)
    test_name=$(basename "$test_dir")
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "🧪 Test: $test_name" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Step 1: Compile
    echo "  🔨 Compiling..." | tee -a "$LOG_FILE"
    cd "$test_dir"
    
    if wmake > /dev/null 2>&1; then
        echo "  ✅ Compilation successful" | tee -a "$LOG_FILE"
    else
        echo "  ❌ Compilation FAILED" | tee -a "$LOG_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        continue  # ข้าม test นี้ ไป test ตัวถัดไป
    fi
    
    # Step 2: Run test
    echo "  🏃 Running test..." | tee -a "$LOG_FILE"
    
    # หา executable file
    test_executable=$(find . -maxdepth 1 -type f -name "Test-*" -executable | head -n 1)
    
    if [ -z "$test_executable" ]; then
        echo "  ⚠️  No executable found (expected: Test-*)" | tee -a "$LOG_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        continue
    fi
    
    # รัน test และ capture output
    if ./"$test_executable" >> "$LOG_FILE" 2>&1; then
        echo "  ✅ PASSED" | tee -a "$LOG_FILE"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "  ❌ FAILED (exit code: $?)" | tee -a "$LOG_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo ""
done

# Summary
echo "========================================" | tee -a "$LOG_FILE"
echo "📊 Test Summary" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Total tests:  $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "✅ Passed:     $PASSED_TESTS" | tee -a "$LOG_FILE"
echo "❌ Failed:     $FAILED_TESTS" | tee -a "$LOG_FILE"
echo "End time: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Exit code: 0 ถ้าทุก test ผ่าน, 1 ถ้ามีอย่างน้อย 1 test ล้มเหลว
if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 All tests passed!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "💥 Some tests failed. Check $LOG_FILE for details." | tee -a "$LOG_FILE"
    exit 1
fi
```

**คำอธิบาย:**
1. `set -e`: Stop immediately on error
2. `tee -a "$LOG_FILE"`: Write to both stdout and log file
3. Loop: ผ่านทุก test directory
4. Compile: Run `wmake` ในแต่ละ directory
5. Execute: หาและรัน executable file
6. Summary: รายงานผลรวม

**การใช้งาน:**
```bash
# รัน test ทั้งหมด
./runUnitTests.sh

# รัน test ใน directory ที่ระบุ
./runUnitTests.sh /path/to/custom/tests

# ดู log file
cat test_results_20231215_143022.log
```

#### 4.2 Parallel Test Runner (Advanced)

**ไฟล์: `runUnitTestsParallel.sh`**

```bash
#!/bin/bash
# runUnitTestsParallel.sh - รัน Unit Tests แบบ parallel (เร็วขึ้น)
# ใช้ GNU Parallel เพื่อรัน test หลายตัวพร้อมกัน

TEST_DIR="${1:-$FOAM_RUN/../test}"
MAX_PARALLEL=${2:-4}  # รันสูงสุด 4 tests พร้อมกัน

echo "Running tests in parallel (max $MAX_PARALLEL concurrent)..."

# ใช้ GNU parallel ในการรัน test
find "$TEST_DIR" -mindepth 1 -maxdepth 1 -type d | \
    parallel -j "$MAX_PARALLEL" \
    --joblog "test_parallel.log" \
    --tag \
    "
    cd {}
    test_name=\$(basename {})
    echo \"🧪 Test: \$test_name\"
    if wmake > /dev/null 2>&1; then
        test_exec=\$(find . -maxdepth 1 -type f -name 'Test-*' -executable | head -n 1)
        if [ -n \"\$test_exec\" ]; then
            if ./\$test_exec > /tmp/\${test_name}.log 2>&1; then
                echo \"✅ PASSED\"
                exit 0
            else
                echo \"❌ FAILED\"
                cat /tmp/\${test_name}.log
                exit 1
            fi
        else
            echo \"⚠️  No executable\"
            exit 1
        fi
    else
        echo \"❌ Compilation failed\"
        exit 1
    fi
    "

echo ""
echo "Check test_parallel.log for detailed results."
```

**ประโยชน์:**
- รัน test หลายตัวพร้อมกัน (ใช้ประโยชน์จาก multi-core CPU)
- เหมาะสำหรับ test ที่เป็น independent (ไม่ depend on กัน)

---

## 5. Make Structure

### WHAT: Build Configuration สำหรับ Test

แต่ละ test ต้องมีไฟล์ Make สองไฟล์:
- `Make/files`: ระบุ source files และ executable name
- `Make/options`: ระบุ include paths และ libraries

### WHY: ทำไมต้องแยก Make files?

OpenFOAM ใช้ wmake system ซึ่ง:
- **Modular:** แต่ละ test มี dependencies ของตัวเอง
- **Incremental:** compile เฉพาะที่เปลี่ยน
- **Reproducible:** บันทึก build configuration ใน version control

### HOW: ตั้งค่า Make Files สำหรับ Test

#### 5.1 โครงสร้าง Directory ที่ควรมี

```
test/
├── vectorTest/
│   ├── vectorTest.C          # Source code
│   └── Make/
│       ├── files
│       └── options
├── fieldTest/
│   ├── fieldTest.C
│   └── Make/
│       ├── files
│       └── options
└── runUnitTests.sh
```

#### 5.2 ไฟล์ `Make/files`

**ระบุ source file และ executable name:**

```make
# Source file(s)
vectorTest.C

# Executable name (จะถูกสร้างใน $FOAM_USER_APPBIN)
EXE = $(FOAM_USER_APPBIN)/Test-vectorTest
```

**หลาย source files:**

```make
# Multiple source files
mainTest.C
testUtils.C
vectorMathTest.C

EXE = $(FOAM_USER_APPBIN)/Test-comprehensive
```

**Naming Convention:**
- Test executables ควรขึ้นต้นด้วย `Test-` เพื่อให้ script หาได้ง่าย
- ใช้ชื่อที่สื่อความหมาย: `Test-vector`, `Test-turbulenceModel`

#### 5.3 ไฟล์ `Make/options`

**ระบุ include paths และ libraries:**

```make
# Include paths (ค้นหา header files)
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/meshTools/lnInclude \
    -I$(LIB_SRC)/sampling/lnInclude

# Libraries to link against
EXE_LIBS = \
    -lfiniteVolume \
    -lmeshTools \
    -lsampling
```

**คำอธิบาย:**
- `EXE_INC`: Include paths สำหรับ header files
  - `$(LIB_SRC)/finiteVolume/lnInclude` → Path ไปยัง finiteVolume headers
  - `lnInclude` คือ symbolic links ไปยัง actual include files
- `EXE_LIBS`: Libraries ที่ต้อง link
  - `-lfiniteVolume` → Link กับ libfiniteVolume.so

**ตัวอย่างเพิ่มเติม (Test ที่ซับซ้อน):**

```make
EXE_INC = \
    -I$(LIB_SRC)/finiteVolume/lnInclude \
    -I$(LIB_SRC)/turbulenceModels \
    -I$(LIB_SRC)/transportModels \
    -I$(LIB_SRC)/thermophysicalModels/basic/lnInclude \
    -I$(LIB_SRC)/ODE/lnInclude

EXE_LIBS = \
    -lfiniteVolume \
    -lturbulenceModels \
    -ltransportModels \
    -lthermophysicalFunctions \
    -lODE
```

#### 5.4 ตัวอย่าง Complete Test Structure

**Directory: `test/vectorMathTest/`**

**ไฟล์: `vectorMathTest.C`**
```cpp
#include "TestCase.H"
#include "fvCFD.H"

class vectorMathTest : public Test::TestCase
{
public:
    void runTest()
    {
        // Test vector operations
        vector a(1, 2, 3);
        vector b(4, 5, 6);
        
        vector sum = a + b;
        ASSERT_EQ(sum, vector(5, 7, 9));
        
        scalar dot = a & b;
        ASSERT_EQ(dot, 32.0);  // 1*4 + 2*5 + 3*6
        
        vector cross = a ^ b;
        ASSERT_EQ(cross, vector(-3, 6, -3));
    }
};
```

**ไฟล์: `Make/files`**
```make
vectorMathTest.C

EXE = $(FOAM_USER_APPBIN)/Test-vectorMath
```

**ไฟล์: `Make/options`**
```make
EXE_INC = -I$(LIB_SRC)/finiteVolume/lnInclude

EXE_LIBS = -lfiniteVolume
```

**การ Build:**
```bash
cd test/vectorMathTest
wmake
# Output: wmake ... (compilation messages)
# Executable created: $FOAM_USER_APPBIN/Test-vectorMath

# Run test
$FOAM_USER_APPBIN/Test-vectorMath
# Output: All tests passed!
```

---

## 6. Best Practices

### WHAT: แนวทางปฏิบัติที่ดีในการเขียน Unit Tests

| Practice | Why | Example |
|----------|-----|---------|
| **Test one thing** | Clear failure reason | ✅ `testVectorAddition()` <br>❌ `testEverything()` |
| **Meaningful names** | Self-documenting | ✅ `testCrossProductPerpendicularity()` <br>❌ `test1()` |
| **Independent tests** | Order doesn't matter | Each test creates its own data |
| **Fast execution** | Run often | Avoid heavy I/O, large meshes |
| **Arrange-Act-Assert** | Clear structure | 1. Setup data <br>2. Call function <br>3. Check result |
| **Test edge cases** | Catch hidden bugs | Zero, empty, NaN, Inf |
| **Use fixtures** | Avoid code duplication | Shared setup code |

### WHY: แต่ละ Practice มีผลต่ออะไร?

#### 1. Test One Thing

**Problem:** Test ที่ทดสอบหลายอย่างพร้อมกัน
```cpp
void testBadExample()  // ❌
{
    // Test vector addition
    vector a(1, 2, 3);
    vector b(4, 5, 6);
    ASSERT_EQ(a + b, vector(5, 7, 9));
    
    // Test field operations (ไม่เกี่ยวกับ vector!)
    volScalarField T(...);
    ASSERT_NEAR(max(T), 300, 1e-6);
    
    // Test boundary conditions (ไม่เกี่ยวอีก!)
    p.boundaryFieldRef()[0] == 101325;
}
```

**ถ้า fail:** ไม่รู้ว่าส่วนไหนพัง (vector? field? BC?)

**Solution:** แยก test ออกเป็นหลาย test
```cpp
void testVectorAddition()  // ✅
{
    vector a(1, 2, 3);
    vector b(4, 5, 6);
    ASSERT_EQ(a + b, vector(5, 7, 9));
}

void testFieldMax()  // ✅
{
    volScalarField T(...);
    ASSERT_NEAR(max(T), 300, 1e-6);
}

void testBoundaryConditionSet()  // ✅
{
    volScalarField p(...);
    p.boundaryFieldRef()[0] == 101325;
    ASSERT_EQ(p.boundaryField()[0][0], 101325);
}
```

#### 2. Meaningful Names

**Bad:** ไม่บอกว่า test อะไร
```cpp
void test1();  // ❌ Test อะไร?
void testVector();  // ❌ Test อะไรเกี่ยวกับ vector?
void testOK();  // ❌ ไม่มีความหมาย
```

**Good:** บอกว่า test อะไร, ภายใต้เงื่อนไขอะไร
```cpp
void testVectorAddition_CommutativeProperty();  // ✅ a + b = b + a
void testVectorCrossProduct_PerpendicularToOperands();  // ✅ a × b ⟂ a, b
void testFieldGradient_LinearField_GradEqualsSlope();  // ✅ [scenario]_[expected]
void testBoundaryCondition_fixedValue_PrescribedCorrectly();  // ✅ [feature]_[behavior]
```

**Naming Pattern:**
```
test[Feature]_[Scenario]_[ExpectedBehavior]
```

**ตัวอย่าง:**
- `testVectorAddition_TwoVectors_ReturnsCorrectSum`
- `testTurbulenceModel_WallBC_CalculatesYPlus`
- `testFieldInterpolation_CellToPoint_PreservesConservation`

#### 3. Independent Tests

**Problem:** Test ที่ depend on กัน
```cpp
static volScalarField sharedField;  // ❌ Global state

void testA()
{
    sharedField = ...;  // Modify shared state
    ASSERT_TRUE(...);
}

void testB()
{
    // ถ้า testA รันก่อน → ผ่าน
    // ถ้า testB รันก่อน → ล้มเหลว!
    ASSERT_EQ(sharedField[0], 123);
}
```

**Solution:** แต่ละ test สร้าง data เอง
```cpp
void testA()  // ✅
{
    volScalarField fieldA = createTestField();
    // ... test ...
}

void testB()  // ✅
{
    volScalarField fieldB = createTestField();  // Fresh data
    // ... test ...
}
```

#### 4. Fast Execution

**Guidelines:**
- **Target:** แต่ละ test ควรใช้เวลา < 1 ms
- **Avoid:** Large meshes (>1000 cells), heavy I/O, complex solvers

**Slow:**
```cpp
void testSlow()  // ❌ ใช้เวลา 10 วินาที
{
    fvMesh mesh = createLargeMesh(1000000);  // 1M cells
    simpleControl control(mesh);
    
    while (control.loop())
    {
        solve(fvm::ddt(U) + fvm::div(phi, U));  // Run solver!
    }
}
```

**Fast:**
```cpp
void testFast()  // ✅ ใช้เวลา < 1 ms
{
    fvMesh mesh = createSmallMesh(10);  // 10 cells
    volScalarField T(mesh, dimensionedScalar("T", dimTemperature, 300));
    
    T[0] = 350;
    ASSERT_NEAR(T[0], 350, 1e-10);  // Simple check
}
```

**Tip:** แยก "Unit Tests" (รวดเร็ว) กับ "Integration Tests" (ช้ากว่า) ออกจากกัน

#### 5. Arrange-Act-Assert (AAA) Pattern

**Structure:**
```cpp
void testAAA()
{
    // ─────────────────────────────────────
    // 1. ARRANGE (Setup) - เตรียมข้อมูล
    // ─────────────────────────────────────
    vector a(1, 2, 3);
    vector b(4, 5, 6);
    scalar expected = 32.0;  // 1*4 + 2*5 + 3*6
    
    // ─────────────────────────────────────
    // 2. ACT (Execute) - เรียกฟังก์ชันที่ test
    // ─────────────────────────────────────
    scalar result = a & b;  // Dot product
    
    // ─────────────────────────────────────
    // 3. ASSERT (Verify) - ตรวจสอบผลลัพธ์
    // ─────────────────────────────────────
    ASSERT_EQ(result, expected);
}
```

**Benefits:**
- อ่านง่าย: เห็น flow ของ test ชัดเจน
- แก้ไขง่าย: รู้ว่าแต่ละส่วนทำอะไร
- Consistent: ทุก test ใช้ pattern เดียวกัน

#### 6. Test Edge Cases

**Common edge cases:**
- **Zero:** Empty vector, zero scalar, empty field
- **Negative:** Negative values, opposite directions
- **Large:** Very large numbers, overflow
- **Small:** Very small numbers, underflow
- **NaN/Inf:** Result of invalid operations
- **Boundary:** At array bounds, at patch boundaries

**ตัวอย่าง:**
```cpp
void testVectorEdgeCases()
{
    // Test 1: Zero vector
    vector zero(0, 0, 0);
    ASSERT_EQ(mag(zero), 0.0);
    
    // Test 2: Negative components
    vector neg(-1, -2, -3);
    ASSERT_NEAR(mag(neg), 3.74165738677, 1e-6);
    
    // Test 3: Very large values
    vector large(1e10, 2e10, 3e10);
    scalar magLarge = mag(large);
    ASSERT_TRUE(magLarge > 0 && !std::isinf(magLarge));
    
    // Test 4: NaN propagation
    vector nan(1, 2, 3);
    nan.x() = NAN;
    scalar magNan = mag(nan);
    ASSERT_TRUE(std::isnan(magNan));
}
```

#### 7. Use Fixtures (Shared Setup)

**Problem:** โค้ด setup ซ้ำๆ
```cpp
void testA()  // ❌ Duplicate code
{
    fvMesh mesh = createMesh(10, 10, 10);
    volScalarField T(mesh, dimensionedScalar("T", dimTemperature, 300));
    // ... test A ...
}

void testB()  // ❌ Duplicate code
{
    fvMesh mesh = createMesh(10, 10, 10);
    volScalarField T(mesh, dimensionedScalar("T", dimTemperature, 300));
    // ... test B ...
}
```

**Solution:** ใช้ fixture class
```cpp
class FieldTestFixture : public Test::TestCase
{
protected:
    // Shared data members
    autoPtr<fvMesh> mesh;
    autoPtr<volScalarField> T;
    
    // Setup: Run before each test
    void setUp()
    {
        mesh.set(new fvMesh(createMesh(10, 10, 10)));
        T.set(new volScalarField(
            IOobject("T", mesh().time().constant(), mesh()),
            mesh(),
            dimensionedScalar("T", dimTemperature, 300.0)
        ));
    }
    
    // Teardown: Run after each test
    void tearDown()
    {
        T.clear();
        mesh.clear();
    }
};

class temperatureTest : public FieldTestFixture
{
public:
    void runTest()
    {
        // Test 1: Average value
        scalar meanT = average(T().internalField());
        ASSERT_NEAR(meanT, 300.0, 1e-10);
        
        // Test 2: Set value
        T()[0] = 350;
        ASSERT_NEAR(T()[0], 350.0, 1e-10);
    }
};
```

### HOW: นำ Best Practices ไปใช้

**ตัวอย่าง Complete Test (ทำตาม Best Practices ทั้งหมด):**

```cpp
#include "TestCase.H"
#include "fvCFD.H"

class vectorDotProductTest : public Test::TestCase
{
public:
    void runTest()
    {
        // ─────────────────────────────────
        // ARRANGE: เตรียมข้อมูล
        // ─────────────────────────────────
        const vector a(1, 2, 3);
        const vector b(4, 5, 6);
        const scalar expected = 32.0;  // 1*4 + 2*5 + 3*6
        
        // ─────────────────────────────────
        // ACT: เรียกฟังก์ชัน
        // ─────────────────────────────────
        const scalar result = a & b;  // Dot product
        
        // ─────────────────────────────────
        // ASSERT: ตรวจสอบผลลัพธ์
        // ─────────────────────────────────
        ASSERT_EQ(result, expected);
        
        // Additional check: Commutative property (a·b = b·a)
        const scalar result_reverse = b & a;
        ASSERT_EQ(result, result_reverse);
    }
};
```

---

## 7. Common Pitfalls

### WHAT: ข้อผิดพลาดที่พบบ่อยในการเขียน Unit Tests

| Pitfall | Why It's Wrong | Solution |
|---------|----------------|----------|
| **Testing framework instead of code** | Waste time testing library code | Focus on YOUR code |
| **Fragile tests** | Tests fail when code changes (not broken) | Test behavior, not implementation |
| **No tolerance for floats** | Floating-point never exactly equal | Use `ASSERT_NEAR` |
| **Tests depend on order** | Pass in one order, fail in another | Make each test independent |
| **Too complex setup** | Hard to understand/maintain | Use fixtures, helper functions |
| **No tests for error cases** | Only happy path tested | Add tests for invalid inputs |
| **Slow tests** | Developers stop running them | Keep tests < 1ms each |

### WHY: เข้าใจข้อผิดพลาดเพื่อหลีกเลี่ยง

#### 1. Testing Framework Instead of Your Code

**Problem:**
```cpp
void testOpenFOAMVectorAddition()  // ❌
{
    // Test ว่า OpenFOAM รู้จักบวก vector
    vector a(1, 2, 3);
    vector b(4, 5, 6);
    ASSERT_EQ(a + b, vector(5, 7, 9));
}
```

**Why:** นี่เป็นการ test OpenFOAM library, ไม่ใช่ test โค้ดของคุณ! OpenFOAM ได้ test นี้ไปแล้ว

**Solution:** Test โค้ดที่คุณเขียนเอง
```cpp
// Test ฟังก์ชันที่คุณเขียน
scalar calculateVelocityMagnitude(const volVectorField& U)
{
    // Custom calculation logic
    return sum(mag(U)) / U.size();
}

void testCalculateVelocityMagnitude()  // ✅
{
    // Setup mock data
    fvMesh mesh = createSimpleMesh(10);
    volVectorField U(mesh, dimensionedVector("U", dimVelocity, vector(1, 2, 3)));
    
    // Test
    scalar expectedMag = sqrt(14.0);  // sqrt(1² + 2² + 3²)
    scalar result = calculateVelocityMagnitude(U);
    
    ASSERT_NEAR(result, expectedMag, 1e-6);
}
```

#### 2. Fragile Tests (Testing Implementation, Not Behavior)

**Problem:**
```cpp
void testTemperatureFieldIteration()  // ❌
{
    volScalarField T(...);
    
    // ระบุ exact loop count - แก้ implementation แล้ว test พัง!
    for (int i = 0; i < 5; ++i)  // Hard-coded!
    {
        T = 2 * T;
    }
    
    ASSERT_EQ(T[0], 3200.0);  // 100 * 2^5 = 3200
}
```

**Why:** Test fail เมื่อเปลี่ยน implementation (แม้ behavior ยังเหมือนเดิม)

**Solution:** Test behavior, ไม่ใช่ implementation
```cpp
void testTemperatureFieldDoubles()  // ✅
{
    volScalarField T(...);
    T[0] = 100.0;
    
    // Call function (ไม่สนใจว่าทำยังไง)
    doubleTemperature(T);
    
    // Assert behavior (ไม่สนใจว่าใช้ loop กี่ครั้ง)
    ASSERT_NEAR(T[0], 200.0, 1e-10);
}
```

#### 3. No Tolerance for Floating-Point

**Problem:**
```cpp
void testFloatingPointMath()  // ❌
{
    double result = 0.1 + 0.2;  // = 0.30000000000000004
    ASSERT_EQ(result, 0.3);  // FAIL!
}
```

**Why:** Floating-point มี rounding errors เสมอ

**Solution:** เสมอใช้ `ASSERT_NEAR`
```cpp
void testFloatingPointMath()  // ✅
{
    double result = 0.1 + 0.2;
    ASSERT_NEAR(result, 0.3, 1e-10);  // PASS
}
```

**Guideline:**
```cpp
// ❌ อย่าใช้ ASSERT_EQ กับ floating-point
ASSERT_EQ(mag(U), 10.0);

// ✅ ใช้ ASSERT_NEAR แทน
ASSERT_NEAR(mag(U), 10.0, 1e-6);
```

#### 4. Tests Depend on Order

**Problem:**
```cpp
static volScalarField globalT;  // ❌ Global state!

void testA()
{
    globalT = ...;  // Modify global
    ASSERT_TRUE(globalT[0] > 0);
}

void testB()
{
    // ถ้า testA รันก่อน → globalT มีค่า
    // ถ้า testB รันก่อน → globalT ว่าง → CRASH!
    ASSERT_NEAR(globalT[0], 123, 1e-10);
}
```

**Why:** Test ผ่าน/ไม่ผ่าน ขึ้นกับลำดับการรัน

**Solution:** แต่ละ test สร้าง data เอง
```cpp
void testA()  // ✅
{
    volScalarField T = createTestField();
    // ... test ...
}

void testB()  // ✅
{
    volScalarField T = createTestField();  // Fresh instance
    // ... test ...
}
```

#### 5. Too Complex Setup

**Problem:**
```cpp
void testComplexThing()  // ❌
{
    // 50 lines of setup code!
    fvMesh mesh(...);
    volScalarField p(...);
    volVectorField U(...);
    volScalarField T(...);
    surfaceScalarField phi(...);
    // ... อีก 40 lines ...
    
    // แค่ 1 line ของ actual test
    ASSERT_TRUE(someCondition(p, U, T, phi));
}
```

**Why:** ยากต่อการอ่าน/แก้ไข และไม่รู้ว่า test อะไรจริงๆ

**Solution:** แยก setup ออกเป็น helper functions
```cpp
// Helper function
TestSetup createStandardSetup()
{
    TestSetup setup;
    setup.mesh = createSimpleMesh();
    setup.p = createPressureField(setup.mesh);
    setup.U = createVelocityField(setup.mesh);
    return setup;
}

void testComplexThing()  // ✅
{
    // Clear setup in 1 line
    auto setup = createStandardSetup();
    
    // Clear test
    ASSERT_TRUE(someCondition(setup.p, setup.U));
}
```

#### 6. No Tests for Error Cases

**Problem:** ทดสอบเฉพาะ "happy path" (input ปกติ)
```cpp
void testDivision()  // ❌
{
    ASSERT_EQ(divide(10, 2), 5.0);  // แค่กรณีปกติ
}
```

**Why:** Bug มักเกิดใน edge cases, ไม่ใช่ normal cases

**Solution:** Test error cases ด้วย
```cpp
void testDivision()  // ✅
{
    // Normal case
    ASSERT_EQ(divide(10, 2), 5.0);
    
    // Edge case: division by zero
    ASSERT_THROW(divide(10, 0), std::invalid_argument);
    
    // Edge case: negative numbers
    ASSERT_EQ(divide(-10, 2), -5.0);
    
    // Edge case: very small numbers
    ASSERT_NEAR(divide(0.001, 0.002), 0.5, 1e-10);
}
```

#### 7. Slow Tests

**Problem:** Test แต่ละตัวใช้เวลานาน
```cpp
void testSolver()  // ❌ ใช้เวลา 5 นาที
{
    // Run full CFD simulation
    runSolver("case", 1000);  // 1000 iterations
}
```

**Why:** Developers จะไม่อยากรัน test บ่อยๆ (รบกวน workflow)

**Solution:** แยก Unit Tests (รวดเร็ว) กับ Integration Tests (ช้ากว่า)
```cpp
// Unit test: รวดเร็ว (< 1 ms)
void testDiscretizationCoefficients()  // ✅
{
    scalar coeff = calculateUpwindCoeff(1.5);
    ASSERT_NEAR(coeff, 1.0, 1e-10);
}

// Integration test: ช้ากว่า (ในไฟล์/directory แยก)
void testSolverConvergence()  // ✅
{
    runSolver("test_case", 10);  // แค่ 10 iterations
    // ... verify convergence ...
}
```

### HOW: Detect และ Avoid Pitfalls

**Checklist ก่อน commit Test:**

- [ ] Test โค้ดของฉันเอง ไม่ใช่ library code
- [ ] Test behavior ไม่ใช่ implementation details
- [ ] ใช้ `ASSERT_NEAR` กับ floating-point
- [ ] แต่ละ test independent (ไม่มี global state)
- [ ] Setup code ง่ายและชัดเจน
- [ ] Test error cases และ edge cases
- [ ] Test แต่ละตัวใช้เวลา < 1 ms

---

## Quick Reference

### Assertions

| Assert | Use Case | Example |
|--------|----------|---------|
| `ASSERT_EQ(actual, expected)` | Exact equality | `ASSERT_EQ(result, 42)` |
| `ASSERT_NEAR(actual, expected, tol)` | Floating-point | `ASSERT_NEAR(p, 101325, 1e-6)` |
| `ASSERT_TRUE(condition)` | Boolean true | `ASSERT_TRUE(mesh.nCells() > 0)` |
| `ASSERT_FALSE(condition)` | Boolean false | `ASSERT_FALSE(field.hasNaN())` |
| `ASSERT_THROW(expr, exception)` | Exception thrown | `ASSERT_THROW(1.0/0, overflow_error)` |

### Common Field Operations

| Operation | Syntax | Notes |
|-----------|--------|-------|
| Create field | `volScalarField T(mesh, dimScalar("T", dimTemperature, 300))` | Constant value |
| Access cell value | `T[cellI]` | Internal field |
| Access boundary | `T.boundaryField()[patchI][faceI]` | Patch data |
| Max value | `max(T)` | Global maximum |
| Min value | `min(T)` | Global minimum |
| Sum | `sum(T)` | Sum of all cells |
| Average | `average(T)` | Arithmetic mean |
| Magnitude | `mag(U)` | Vector magnitude |
| Gradient | `fvc::grad(T)` | Field gradient |
| Divergence | `fvc::div(phi)` | Field divergence |

### Test Structure

```
test/
├── vectorTest/
│   ├── vectorTest.C
│   └── Make/
│       ├── files          (Source files, EXE name)
│       └── options        (Include paths, libraries)
├── fieldTest/
│   ├── fieldTest.C
│   └── Make/
│       ├── files
│       └── options
└── runUnitTests.sh        (Test runner script)
```

---

## Key Takeaways

✅ **Unit Testing คือการทดสอบฟังก์ชัน/คลาสแต่ละอย่างแยกจากกัน** เพื่อค้นหา bug ตั้งแต่ early stage และลดเวลา debug

✅ **มี 3 ประเภทหลักของ assertions:** `ASSERT_EQ` (exact equality), `ASSERT_NEAR` (floating-point ที่มี tolerance), และ `ASSERT_TRUE/FALSE` (boolean conditions)

✅ **Field Testing ต้องการ mesh และ field objects** แต่ควรใช้ small meshes เพื่อให้ test รวดเร็ว - เน้นทดสอบ operations พื้นฐาน, boundary conditions, และ field statistics

✅ **Automation ผ่าน test scripts ช่วยรัน test ทุกตัวอัตโนมัติ** สามารถ integrate กับ CI/CD pipeline ได้

✅ **Best Practices:** Test one thing per test, ใช้ชื่อที่สื่อความหมาย, ทำให้ tests independent, รักษาความรวดเร็ว (< 1ms ต่อ test)

✅ **หลีกเลี่ยง Common Pitfalls:** อย่า test framework code, ใช้ tolerance กับ floating-point, หลีกเลี่ยง global state, อย่าทำให้ tests ช้าเกินไป

---

## Concept Check

<details>
<summary><b>1. Unit test คืออะไร? และต่างจาก System Test อย่างไร?</b></summary>

**Unit test:** Test ฟังก์ชัน/คลาสแต่ละอย่างแยกจากกัน (isolated), รวดเร็ว (ms), ไม่ต้องการ mesh ซับซ้อน

**System test:** Test ทั้ง case หรือ solver, ช้า (ชั่วโมง/วัน), ต้องการ full mesh และ boundary conditions

**ตัวอย่าง:**
- Unit: Test `mag(vector(1,2,3)) = 3.74...`
- System: Run `simpleFoam` ทั้ง case แล้วเช็คความถูกต้องของผลลัพธ์
</details>

<details>
<summary><b>2. ทำไมต้องใช้ ASSERT_NEAR แทน ASSERT_EQ กับ floating-point?</b></summary>

**Floating-point arithmetic มี rounding errors เสมอ** เนื่องจาก:
- คอมพิวเตอร์เก็บทศนิยมแบบ binary (ฐาน 2) ไม่ใช่ decimal (ฐาน 10)
- บางตัวเลขไม่สามารถแทนได้อย่างแม่นยำ (เช่น 0.1 = 0.10000000000000001)

**ตัวอย่าง:**
```cpp
double a = 0.1 + 0.2;  // = 0.30000000000000004
ASSERT_EQ(a, 0.3);      // ❌ FAIL!
ASSERT_NEAR(a, 0.3, 1e-10);  // ✅ PASS
```
</details>

<details>
<summary><b>3. Independent tests ดีอย่างไร?</b></summary>

**Independent tests:**
- **Run ได้ในทุกลำดับ** —ไม่มีการพึ่งพาระหว่าง tests
- **Debug ง่าย** —ถ้า fail รู้ทันทีว่า test ไหนพัง (ไม่ใช่ cascade failure)
- **Parallel execution** —สามารถรันหลาย tests พร้อมกันได้

**ตรงข้าม:** Dependent tests อาจผ่าน/ล้มเหลวขึ้นกับลำดับการรัน → unreliable
</details>

<details>
<summary><b>4. Arrange-Act-Assert (AAA) pattern คืออะไร? ทำไมต้องใช้?</b></summary>

**AAA Pattern** คือโครงสร้างมาตรฐานของ test:
1. **Arrange:** เตรียมข้อมูล (create objects, set values)
2. **Act:** เรียกฟังก์ชันที่ต้องการ test
3. **Assert:** ตรวจสอบผลลัพธ์

**ประโยชน์:**
- **อ่านง่าย:** เห็น flow ของ test ชัดเจน
- **Consistent:** ทุก test ใช้รูปแบบเดียวกัน
- **แก้ไขง่าย:** รู้ว่าแต่ละส่วนทำอะไร

**ตัวอย่าง:**
```cpp
void testAAA()
{
    // Arrange: เตรียมข้อมูล
    vector a(1, 2, 3);
    
    // Act: เรียกฟังก์ชัน
    scalar m = mag(a);
    
    // Assert: ตรวจสอบ
    ASSERT_NEAR(m, 3.7416, 1e-4);
}
```
</details>

<details>
<summary><b>5. Field testing ควรใช้ mesh ขนาดเท่าไหร่? ทำไม?</b></summary>

**ควรใช้ small mesh (~10-100 cells)**

**เหตุผล:**
- **Speed:** Test ควรใช้เวลา < 1 ms แต่ละตัว
- **Focus:** Test operations, ไม่ใช่ physical accuracy
- **Reproducibility:** Small mesh ทำให้ผลลัพธ์ predictable

**Large mesh (1000+ cells):**
- ใช้เวลานาน → developers ไม่อยากรัน test
- เหมาะสำหรับ **integration tests** (อยู่ใน directory แยก)

**ตัวอย่าง:**
```cpp
// ✅ Good for unit test
fvMesh mesh = createSimpleMesh(10, 10, 10);  // 1000 cells

// ❌ Too big for unit test (move to integration test)
fvMesh mesh = createRealMesh(100000);  // 100k cells
```
</details>

<details>
<summary><b>6. ทำไมต้องเขียน test สำหรับ edge cases?</b></summary>

**Edge cases** (กรณีขอบ) คือสถานการณ์พิเศษที่มักทำให้โค้ดพัง:
- **Zero:** หารด้วยศูนย์, empty vector
- **Negative:** ค่าลบ, ทิศทางตรงข้าม
- **Very large/very small:** Overflow, underflow
- **NaN/Inf:** ผลลัพธ์ของ operations ที่ไม่ถูกต้อง

**เหตุผล:**
- **Bugs ซ่อนอยู่ที่ edge cases:** Normal cases มักทำงานได้ดี
- **Real-world usage:** Users อาจ input ค่าผิดปกติ
- **Robustness:** Code ที่ดีต้อง handle ทุกกรณี

**ตัวอย่าง:**
```cpp
void testDivision()
{
    // Normal case
    ASSERT_EQ(divide(10, 2), 5);
    
    // Edge case: division by zero
    ASSERT_THROW(divide(10, 0), std::invalid_argument);
    
    // Edge case: negative
    ASSERT_EQ(divide(-10, 2), -5);
}
```
</details>

---

## Related Documents

### ภาพรวม
- **Testing Overview:** [00_Overview.md](00_Overview.md) — ภาพรวมการทดสอบใน OpenFOAM

### เนื้อหาที่เกี่ยวข้อง
- **Verification:** [02_Verification_Fundamentals/01_Introduction.md](../02_VERIFICATION_FUNDAMENTALS/01_Introduction.md) — หลักการ Verification ที่ใช้ Unit Test
- **Test Framework Coding:** [03_Test_Framework_Coding/00_Overview.md](../03_TEST_FRAMEWORK_CODING/00_Overview.md) — รายละเอียดการเขียน Test Framework

### ถัดไปในเส้นทางการเรียนรู้
1. **Validation:** [02_Validation_Coding.md](02_Validation_Coding.md) — ทดสอบความถูกต้องของผลลัพธ์ CFD
2. **Automation:** [04_Test_Automation.md](04_Test_Automation.md) — Script และ CI/CD สำหรับ testing
3. **Best Practices:** [05_Testing_Best_Practices.md](05_Testing_Best_Practices.md) — แนวทางปฏิบัติที่ดีในการทดสอบ