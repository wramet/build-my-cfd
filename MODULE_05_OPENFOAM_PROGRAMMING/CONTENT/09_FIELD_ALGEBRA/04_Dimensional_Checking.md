# 4. Dimensional Checking

## "Hook": ป้องกันความไม่สอดคล้องทางฟิสิกส์ก่อนรันจำลอง

> [!TIP] **Dimensional Analysis as Type System**
>
> ระบบมิติของ OpenFOAM จับข้อผิดพลาดเช่นการบวกความดันเข้ากับความเร็ว **ก่อนที่คุณจะรันการจำลอง**
>
> เมื่อคุณเห็น `[M L⁻¹ T⁻²] + [L T⁻¹] → ERROR` คุณกำลังเห็นการวิเคราะห์มิติทำงานเป็นส่วนขยายของระบบ type ที่ทรงพลังที่ป้องกันการดำเนินการที่ไม่มีความหมายทางฟิสิกส์ในขั้นตอนที่เร็วที่สุด

สมการความผิดพลาดทางมิติ:
$$[\text{pressure}] + [\text{velocity}] \rightarrow \text{ERROR}$$
$$[M L^{-1} T^{-2}] + [L T^{-1}] \rightarrow \text{ไม่สอดคล้องกัน}$$

---

## แบบแผน: Dimension Sets และหน่วยฐาน

OpenFOAM แทนมิติทางกายภาพเป็นอาร์เรย์ 7 องค์ประกอบที่สอดคล้องกับหน่วยฐาน SI:

| มิติ | หน่วยฐาน SI | สัญลักษณ์ | ตำแหน่งในอาร์เรย์ |
|-------|---------------|-----------|-------------------|
| มวล | Mass | M | 1 |
| ความยาว | Length | L | 2 |
| เวลา | Time | T | 3 |
| อุณหภูมิ | Temperature | Θ | 4 |
| ปริมาณของสาร | Amount | N | 5 |
| กระแสไฟฟ้า | Electric Current | I | 6 |
| ความเข้มแสง | Luminous Intensity | J | 7 |

แต่ละมิติแทนด้วยเลขชี้กำลังจำนวนเต็ม ทำให้สามารถวิเคราะห์มิติได้อย่างครบถ้วน:

### การกำหนด DimensionSets ทั่วไป

```cpp
// Pressure: [M L⁻¹ T⁻²] = force per unit area
dimensionSet dimPressure(1, -1, -2, 0, 0, 0, 0);

// Velocity: [L T⁻¹] = distance per unit time
dimensionSet dimVelocity(0, 1, -1, 0, 0, 0, 0);

// Density: [M L⁻³] = mass per unit volume
dimensionSet dimDensity(1, -3, 0, 0, 0, 0, 0);

// Viscosity: [M L⁻¹ T⁻¹] = momentum diffusion
dimensionSet dimViscosity(1, -1, -1, 0, 0, 0, 0);

// Thermal conductivity: [M L T⁻³ Θ⁻¹] = heat flow rate per temperature gradient
dimensionSet dimConductivity(1, 1, -3, -1, 0, 0, 0);
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - `dimensionSet` constructor รับพารามิเตอร์ 7 ค่าสำหรับ (มวล, ความยาว, เวลา, อุณหภูมิ, ปริมาณสาร, กระแสไฟฟ้า, ความสว่าง)
> - แต่ละค่าคือเลขชี้กำลังของหน่วยฐาน SI นั้นๆ
> - ตัวอย่าง: `dimPressure(1, -1, -2, 0, 0, 0, 0)` แทน [M¹ L⁻¹ T⁻²]
>
> **หลักการสำคัญ:**
> - การวิเคราะห์มิติใน OpenFOAM ใช้ระบบเลขชี้กำลังของหน่วยฐาน SI
> - ทุกปริมาณทางกายภาพสามารถแสดงด้วยการคูณของหน่วยฐานทั้ง 7 นี้
> - ระบบนี้ช่วยตรวจสอบความสอดคล้องของมิติโดยอัตโนมัติ

### การใช้งาน Dimensioned Fields

ชนิดของสนามจะมีมิติเหล่านี้เป็นคุณสมบัติโดยธรรมชาติ:

```cpp
// Dimensioned scalar with pressure dimensions and value
dimensionedScalar p("p", dimPressure, 101325.0);

// Volume vector field with velocity dimensions
volVectorField U(
    IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimensionedVector("U", dimVelocity, vector(1.0, 0.0, 0.0))
);

// Surface scalar field with mass flow rate dimensions [M T⁻¹]
surfaceScalarField phi(
    IOobject("phi", runTime.timeName(), mesh, IOobject::NO_READ),
    fvc::interpolate(rho) * (U & mesh.Sf())
);
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - `dimensionedScalar`: ค่าสเกลาร์ที่มีมิติกำกับ
> - `volVectorField`: สนามเวกเตอร์บนเซลล์ควอนตัม (volume-centered)
> - `surfaceScalarField`: สนามสเกลาร์บนพื้นผิวเซลล์ (face-centered)
> - `IOobject` ใช้สำหรับจัดการ I/O และลงทะเบียนกับ object registry
>
> **หลักการสำคัญ:**
> - สนามทุกชนิดใน OpenFOAM ต้องมีมิติที่ชัดเจน
> - การดำเนินการระหว่างสนามจะตรวจสอบความเข้ากันของมิติโดยอัตโนมัติ
> - `phi` (mass flow rate) = ρ × U × Sf มีมิติ [M T⁻¹]

---

## กลไกภายใน: Template ของ DimensionedField

คลาส template `DimensionedField` ให้รากฐานสำหรับการตรวจสอบมิติโดยการรวมการจัดเก็บสนามกับข้อมูล metadata ของมิติ:

### โครงสร้าง DimensionedField

```cpp
template<class Type, class GeoMesh>
class DimensionedField
:
    public regIOobject,
    public Field<Type>
{
private:
    // Store dimensions for this field
    dimensionSet dimensions_;

    // Field name for identification
    word name_;

public:
    // Constructor with dimensions
    DimensionedField
    (
        const IOobject& io,
        const GeoMesh& mesh,
        const dimensionSet& dimensions
    )
    :
        regIOobject(io),
        Field<Type>(mesh.size()),
        dimensions_(dimensions),
        name_(io.name())
    {}

    // Access dimensions
    const dimensionSet& dimensions() const
    {
        return dimensions_;
    }
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/StationaryPhaseModel/StationaryPhaseModel.C`
>
> **คำอธิบาย:**
> - `DimensionedField` สืบทอดจาก `regIOobject` (สำหรับการจัดการ I/O) และ `Field<Type>` (สำหรับเก็บข้อมูล)
> - `dimensions_`: เก็บข้อมูลมิติของสนาม
> - Multiple inheritance: ให้ทั้งฟังก์ชันการจัดการไฟล์และการจัดเก็บข้อมูล
>
> **หลักการสำคัญ:**
> - การแยกข้อมูลมิติออกจากข้อมูลสนามทำให้ตรวจสอบได้อย่างมีประสิทธิภาพ
> - Template parameter `Type` อนุญาตให้ใช้กับ scalar, vector, tensor ฯลฯ
> - Template parameter `GeoMesh` อนุญาตให้ใช้กับ mesh ประเภทต่างๆ

### การตรวจสอบมิติใน Operators

```cpp
    // Addition operator with dimension checking
    DimensionedField<Type, GeoMesh> operator+
    (
        const DimensionedField<Type, GeoMesh>& df
    ) const
    {
        // Check dimension compatibility before operation
        if (dimensions_ != df.dimensions())
        {
            FatalErrorInFunction
                << "Incompatible dimensions for operation" << nl
                << "    LHS: " << name_ << " = " << dimensions_ << nl
                << "    RHS: " << df.name_ << " = " << df.dimensions() << nl
                << "    Operation: addition" << nl
                << abort(FatalError);
        }

        // Create result field with same dimensions
        DimensionedField<Type, GeoMesh> result(*this);
        result.Field<Type>::operator+=(df);
        return result;
    }
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - การบวกต้องการมิติที่ตรงกันทั้งหมด (homogeneous dimensions)
> - การตรวจสอบเกิดขึ้นก่อนการดำเนินการ เพื่อป้องกันการคำนวณที่ไม่มีความหมาย
> - ข้อความ error ให้ข้อมูลรายละเอียดเกี่ยวกับมิติทั้งสองฝั่ง
>
> **หลักการสำคัญ:**
> - Physical operations: การบวก/ลบ ต้องมีมิติเดียวกัน
> - การตรวจสอบเกิดที่ runtime ด้วยการเปรียบเทียบ `dimensionSet`
> - Fail-fast: หยุดการทำงานทันทีเมื่อพบความไม่สอดคล้อง

### การคูณและการหาร

```cpp
    // Multiplication: dimensions add
    DimensionedField<scalar, GeoMesh> operator*
    (
        const DimensionedField<Type, GeoMesh>& df
    ) const
    {
        // Result has sum of dimensions
        dimensionSet resultDims = dimensions_ + df.dimensions();

        DimensionedField<scalar, GeoMesh> result(
            IOobject(name_ + "*" + df.name_,
                    time().timeName(),
                    this->db(),
                    IOobject::NO_READ,
                    IOobject::NO_WRITE),
            this->mesh(),
            resultDims
        );

        // Perform element-wise multiplication
        forAll(result, i)
        {
            result[i] = this->operator[](i) * df[i];
        }

        return result;
    }

    // Division: dimensions subtract
    template<class Type2>
    DimensionedField<typename product<Type, Type2>::type, GeoMesh> operator/
    (
        const DimensionedField<Type2, GeoMesh>& df
    ) const
    {
        // Result has difference of dimensions
        dimensionSet resultDims = dimensions_ - df.dimensions();

        DimensionedField<typename product<Type, Type2>::type, GeoMesh> result(
            IOobject(name_ + "/" + df.name_,
                    time().timeName(),
                    this->db(),
                    IOobject::NO_READ,
                    IOobject::NO_WRITE),
            this->mesh(),
            resultDims
        );

        // Perform element-wise division with safety checks
        forAll(result, i)
        {
            if (mag(df[i]) < SMALL)
            {
                WarningInFunction
                    << "Division by very small number: " << df[i]
                    << " at index " << i;
            }
            result[i] = this->operator[](i) / df[i];
        }

        return result;
    }
};
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - การคูณ: มิติบวกกัน (exponents add) → [A] × [B] = [A+B]
> - การหาร: มิติลบกัน (exponents subtract) → [A] / [B] = [A-B]
> - `product<Type, Type2>::type`: กำหนด type ของผลลัพธ์ (เช่น scalar × vector = vector)
> - `SMALL`: ค่าต่ำสุดเพื่อป้องกันการหารด้วยศูนย์
>
> **หลักการสำคัญ:**
> - Dimensional propagation: มิติของผลลัพธ์คำนวณอัตโนมัติ
> - ตัวดำเนินการ算术อัตโนมัติจัดการทั้งค่าและมิติ
> - การป้องกัน numeric errors เช่น การหารด้วยค่าเล็กๆ

---

## กลไก: การตรวจสอบเวลาคอมไพล์และรันไทม์

### การตรวจสอบเวลาคอมไพล์

OpenFOAM ใช้ C++ template metaprogramming เพื่อจับข้อผิดพลาดของมิติในระหว่างการคอมไพล์:

```cpp
// Template specialization prevents incompatible operations
template<class Type, class GeoMesh>
class DimensionedField;

// Specialization for scalar multiplication allows different dimensions
template<class GeoMesh>
DimensionedField<scalar, GeoMesh> operator*
(
    const DimensionedField<scalar, GeoMesh>& df1,
    const DimensionedField<scalar, GeoMesh>& df2
)
{
    // Dimensions add: [A] * [B] = [A+B]
    return DimensionedField<scalar, GeoMesh>(
        df1.name() + "*" + df2.name(),
        df1.mesh(),
        df1.dimensions() + df2.dimensions()
    );
}

// Addition requires same dimensions - enforced at runtime
// But template system guarantees type safety
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - Template metaprogramming: ใช้ template parameters สำหรับ type checking
> - Compile-time safety: ตรวจสอบความถูกต้องของ type ก่อน runtime
> - Runtime enforcement: ตรวจสอบความเข้ากันของมิติเมื่อ execute
>
> **หลักการสำคัญ:**
> - Layered defense: ทั้ง compile-time และ runtime checking
> - Type safety vs Dimension safety: ต่างกันแต่เสริมกัน
> - การผสมผสานระหว่าง C++ type system และ dimensional analysis

### การตรวจสอบรันไทม์

การตรวจสอบมิติหลักเกิดขึ้นที่รันไทม์ผ่านการเปรียบเทียบมิติอย่างชัดเจน:

```cpp
// Example: dimension checking for gradient operation
template<class Type>
GeometricField<typename outerProduct<Type, vector>::type, fvPatchField, volMesh>
grad(const GeometricField<Type, fvPatchField, volMesh>& vf)
{
    typedef typename outerProduct<Type, vector>::type gradType;

    // Calculate gradient dimensions
    dimensionSet gradDims = vf.dimensions() / dimLength;

    return GeometricField<gradType, fvPatchField, volMesh>(
        IOobject("grad(" + vf.name() + ")", vf.time().timeName(), vf.db()),
        fvMesh(vf.mesh()),
        gradDims,
        fvPatchField<gradType>::calculatedType()
    );
}
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - Gradient operation: ∇Φ มีมิติเท่ากับ [Φ] / [L]
> - `outerProduct<Type, vector>::type`: กำหนด type ของ gradient (เช่น scalar → vector)
> - มิติของผลลัพธ์คำนวณอัตโนมัติจาก input field
>
> **หลักการสำคัญ:**
> - Automatic dimension propagation: มิติของผลลัพธ์คำนวณจาก input
> - Mathematical operations: แต่ละ operator มีกฎมิติที่ชัดเจน
> - Type inference: C++ templates อนุญาตให้ infer result type

### กฎการคำนวณมิติ

ระบบมิติทำตามกฎพีชคณิตพื้นฐาน:

#### การคูณ: มิติบวกกัน element-wise
$$[M^a L^b T^c \Theta^d N^e I^f J^g] \times [M^h L^i T^j \Theta^k N^l I^m J^n] = [M^{a+h} L^{b+i} T^{c+j} \Theta^{d+k} N^{e+l} I^{f+m} J^{g+n}]$$

#### การหาร: มิติลบกัน
$$[M^a L^b T^c \Theta^d N^e I^f J^g] / [M^h L^i T^j \Theta^k N^l I^m J^n] = [M^{a-h} L^{b-i} T^{c-j} \Theta^{d-k} N^{e-l} I^{f-m} J^{g-n}]$$

#### การบวก/ลบ: มิติต้องตรงกันพอดี
$$[M^a L^b T^c \Theta^d N^e I^f J^g] + [M^h L^i T^j \Theta^k N^l I^m J^n] \text{ requires } a=h, b=i, c=j, d=k, e=l, f=m, g=n$$

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - **Multiplication (การคูณ)**: เลขชี้กำลังของแต่ละหน่วยฐานบวกกัน
> - **Division (การหาร)**: เลขชี้กำลังของแต่ละหน่วยฐานลบกัน
> - **Addition/Subtraction (การบวก/ลบ)**: เลขชี้กำลังทุกตัวต้องเท่ากัน
>
> **หลักการสำคัญ:**
> - Exponent arithmetic: การดำเนินการกับเลขชี้กำลัง
> - Dimensional homogeneity: หลักมูลพื้นฐานของ physical equations
> - กฎเหล่านี้ใช้กับ operations ทั้งหมดใน OpenFOAM

---

## "ทำไม": ความสอดคล้องทางฟิสิกส์เป็นความกังวลระดับแรก

### ประโยชน์ด้านความปลอดภัย

> [!INFO] **Type Safety สำหรับฟิสิกส์**
>
> ระบบมิติขยายระบบ type ของ C++ เพื่อรวมหน่วยทางกายภาพ โดยให้การรับประกันเวลาคอมไพล์เกี่ยวกับความถูกต้องของมิติ:

```cpp
// This will fail to compile if dimensions don't match
template<class Field1, class Field2>
auto safeAdd(const Field1& f1, const Field2& f2) -> decltype(f1 + f2)
{
    static_assert(
        std::is_same_v<typename Field1::value_type, typename Field2::value_type>,
        "Field value types must match for addition"
    );
    return f1 + f2; // Dimension runtime check happens here
}
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseModel/StationaryPhaseModel/StationaryPhaseModel.C`
>
> **คำอธิบาย:**
> - `static_assert`: Compile-time assertion สำหรับ type checking
> - `decltype(f1 + f2)`: Infer return type จาก expression
> - Runtime check เกิดภายใน operator+ implementation
>
> **หลักการสำคัญ:**
> - Multi-layer safety: ทั้ง compile-time และ runtime
> - Type matching: ต้องมี type เดียวกันก่อน dimension matching
> - Modern C++ features: `static_assert`, `decltype`, `type_traits`

> [!WARNING] **การป้องกันข้อผิดพลาดที่มีค่าใช้จ่ายสูง**
>
> การตรวจสอบมิติป้องกันความล้มเหลวของการจำลองที่อาจปรากฏหลังจากการคำนวณเป็นชั่วโมง:

```cpp
// Common scenario: missing density in pressure gradient
// WRONG: returns force per volume instead of acceleration
volVectorField wrongAcceleration = -fvc::grad(p);

// CORRECT: returns proper acceleration
volVectorField correctAcceleration = -fvc::grad(p/rho);

// The dimension system catches:
// wrongAcceleration has [M L⁻² T⁻²] (force/volume)
// correctAcceleration has [L T⁻²] (acceleration)
// These are different physical quantities!
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - **Wrong**: ∇p มีมิติ [M L⁻² T⁻²] (force/volume) ≠ acceleration
> - **Correct**: ∇(p/ρ) มีมิติ [L T⁻²] (acceleration) ✓
> - การลืมหารด้วยความหนาแน่นเป็นข้อผิดพลาดที่พบบ่อย
>
> **หลักการสำคัญ:**
> - Pressure vs Pressure gradient: [M L⁻¹ T⁻²] vs [M L⁻² T⁻²]
> - Acceleration: [L T⁻²] คือความเร่ง
> - Cost of failure: การรันจำลองหลายชั่วโมงก่อนพบ error

### ประโยชน์ด้านประสิทธิภาพ

**ข้อความแสดงข้อผิดพลาดที่ชัดเจน**: ระบบให้ข้อมูลวินิจฉัยโดยละเอียด:

```cpp
/*
Example error:
--> FOAM FATAL ERROR:
Incompatible dimensions for operation
    LHS: dp = [M L⁻¹ T⁻²]      (pressure difference)
    RHS: U = [L T⁻¹]            (velocity magnitude)
    Operation: division
    Location: solver.C:145

    Physical interpretation: Cannot divide pressure by velocity
    Expected result: Either [M L⁻² T⁻¹] (viscosity) or [L⁰ T⁻¹] (1/velocity)
*/
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - Error messages ให้ข้อมูลทั้ง LHS, RHS, operation, และ location
> - Physical interpretation: อธิบายความหมายทางฟิสิกส์
> - Expected result: ชี้ให้เห็นสิ่งที่ควรจะเป็น
>
> **หลักการสำคัญ:**
> - Actionable error messages: ช่วยให้แก้ไขได้ทันที
> - Physical context: ไม่ได้แค่บอกว่าผิด แต่อธิบายว่าทำไม
> - Debugging efficiency: ลดเวลาในการหาสาเหตุ

**Code ที่บอกเอง**: มิติทำหน้าที่เป็นเอกสารแบบ inline:

```cpp
// Field declarations immediately state physical quantities
volScalarField T("T", dimTemperature, 293.0);           // Temperature field
volScalarField p("p", dimPressure, 101325.0);            // Pressure field
volVectorField U("U", dimVelocity, vector(0, 0, 0));    // Velocity field

// Readers instantly understand physical nature
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - Self-documenting code: มิติบอกคุณสมบัติทางฟิสิกส์
> - ไม่ต้อง comment อธิบายว่า T คืออุณหภูมิ, p คือความดัน
> - Improves readability และ maintainability
>
> **หลักการสำคัญ:**
> - Inline documentation: มิติเป็น metadata ของสนาม
> - Physical intent: สื่อสารความตั้งใจของ developer
> - Code understanding: ลดความจำเป็นในการอ่านเอกสาร

**ความปลอดภัยในการแปลงหน่วย**: การจัดการการแปลงหน่วยอัตโนมัติ:

```cpp
// Different units but same dimensions work seamlessly
dimensionedScalar p_atm("p_atm", dimPressure, 1.01325e5);    // Pa
dimensionedScalar p_bar("p_bar", dimPressure, 1.013);       // bar

// Operations work correctly with automatic conversion awareness
dimensionedScalar p_total = p_atm + p_bar;  // Both [M L⁻¹ T⁻²]
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - หน่วยต่างกันแต่มิติเดียวกัน: สามารถบวกกันได้
> - OpenFOAM ใช้ระบบหน่วย SI โดยค่าเริ่มต้น
> - การแปลงหน่วยเป็นความรับผิดชอบของ user
>
> **หลักการสำคัญ:**
> - Dimensional consistency: มิติตรงกัน = สามารถดำเนินการได้
> - Unit conversion: ค่าตัวเลขอาจต่างกันแต่มิติเดียวกัน
> - SI base units: OpenFOAM standardizes on SI

### ประโยชน์ด้านการตรวจสอบ

**การตรวจสอบแบบจำลองอัตโนมัติ**: แบบจำลองทางกายภาพใหม่สามารถตรวจสอบมิติได้:

```cpp
// Custom heat source term checking
volScalarField customHeatSource =
    k * fvc::laplacian(T) +  // [M L T⁻³ Θ⁻¹] * [Θ L⁻²] = [M L⁻¹ T⁻³]
    Q_vol;                    // [M L⁻¹ T⁻³]

// Both terms must have [M L⁻¹ T⁻³] (energy/volume/time)
if (customHeatSource.dimensions() != dimensionSet(1, -1, -3, 0, 0, 0, 0))
{
    FatalError << "Heat source has wrong dimensions!" << exit(FatalError);
}
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - Laplacian: ∇²T มีมิติ [Θ L⁻²]
> - k × ∇²T: [M L T⁻³ Θ⁻¹] × [Θ L⁻²] = [M L⁻¹ T⁻³] ✓
> - Q_vol: Heat source ต้องมีมิติเดียวกัน
>
> **หลักการสำคัญ:**
> - Equation consistency: ทุกเทอมในสมการต้องมีมิติเดียวกัน
> - Dimensional verification: ตรวจสอบก่อน runtime
> - Model validation: ช่วยรับรองความถูกต้องของ physical model

**การตรวจสอบความสอดคล้องของสมการ**: สมการที่ซับซ้อนสามารถตรวจสอบได้ทีละเทอม:

```cpp
// Energy equation: ρcp(∂T/∂t + U·∇T) = k∇²T + Q
// Each term should have dimensions [M L⁻¹ T⁻³]

dimensionSet energyFlux(1, -1, -3, 0, 0, 0, 0);  // Energy/volume/time

// Check each term
auto lhs1 = rho * cp * fvc::ddt(T);           // Should be energyFlux
auto lhs2 = rho * cp * (U & fvc::grad(T));    // Should be energyFlux
auto rhs1 = k * fvc::laplacian(T);            // Should be energyFlux
auto rhs2 = Q_vol;                             // Should be energyFlux

// All must match for dimensional consistency
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - **LHS1**: ρcp(∂T/∂t) → [M L⁻³][L² T⁻² Θ⁻¹][Θ T⁻¹] = [M L⁻¹ T⁻³] ✓
> - **LHS2**: ρcp(U·∇T) → [M L⁻³][L² T⁻² Θ⁻¹][L T⁻¹][Θ L⁻¹] = [M L⁻¹ T⁻³] ✓
> - **RHS1**: k∇²T → [M L T⁻³ Θ⁻¹][Θ L⁻²] = [M L⁻¹ T⁻³] ✓
> - **RHS2**: Q_vol → [M L⁻¹ T⁻³] (heat source) ✓
>
> **หลักการสำคัญ:**
> - Energy equation conservation: ทุกเทอมมีมิติเดียวกัน
> - Term-by-term verification: ตรวจสอบทีละเทอม
> - Physical consistency: รับประกันความถูกต้องทางฟิสิกส์

---

## การใช้งานและตัวอย่างข้อผิดพลาด: ข้อผิดพลาดมิติทั่วไป

### ตัวอย่างการใช้งานที่ถูกต้อง

#### การตรวจสอบสมการโมเมนตัม Navier-Stokes

สมการโมเมนตัมแบบสมบูรณ์:
$$\frac{\partial \mathbf{U}}{\partial t} + (\mathbf{U} \cdot \nabla) \mathbf{U} = -\nabla \frac{p}{\rho} + \nu \nabla^2 \mathbf{U} + \mathbf{f}$$

แต่ละเทอมต้องมีมิติ `[L T⁻²]` (ความเร่ง)

```cpp
dimensionSet acceleration(0, 1, -2, 0, 0, 0, 0);

// Local acceleration: ∂U/∂t
auto ddtTerm = fvc::ddt(U);
// Dimensions: [L T⁻¹] / [T] = [L T⁻²] ✓
assert(ddtTerm.dimensions() == acceleration);

// Convective acceleration: (U·∇)U
auto convTerm = (U & fvc::grad(U));
// Dimensions: [L T⁻¹] * [L T⁻¹] / [L] = [L T⁻²] ✓
assert(convTerm.dimensions() == acceleration);

// Pressure gradient acceleration: -∇p/ρ
auto pressureTerm = -fvc::grad(p/rho);
// Dimensions: [M L⁻¹ T⁻²] / [M L⁻³] / [L] = [L T⁻²] ✓
assert(pressureTerm.dimensions() == acceleration);

// Viscous diffusion: ν∇²U
auto viscousTerm = nu * fvc::laplacian(U);
// Dimensions: [L² T⁻¹] * [L T⁻¹] / [L²] = [L T⁻²] ✓
assert(viscousTerm.dimensions() == acceleration);

// Body force acceleration: f
auto bodyForce = g;  // Gravitational acceleration
// Dimensions: [L T⁻²] ✓
assert(bodyForce.dimensions() == acceleration);
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - **ddt(U)**: ∂U/∂t → [L T⁻¹]/[T] = [L T⁻²] (temporal acceleration)
> - **U & ∇U**: (U·∇)U → [L T⁻¹]×[T⁻¹] = [L T⁻²] (convective acceleration)
> - **∇(p/ρ)**: ∇p/ρ → [M L⁻² T⁻²]/[M L⁻³] = [L T⁻²] (pressure gradient)
> - **ν∇²U**: ν∇²U → [L² T⁻¹]×[L⁻² T⁻¹] = [L T⁻²] (viscous term)
> - **g**: gravitational acceleration → [L T⁻²] (body force)
>
> **หลักการสำคัญ:**
> - Navier-Stokes equation: ทุกเทอมเป็นความเร่ง
> - Dimensional homogeneity: สมการทางฟิสิกส์ต้องมีมิติเดียวกัน
> - Physical terms: แต่ละเทอมมีความหมายทางกายภาพชัดเจน

#### ความสอดคล้องของสมการพลังงาน

สมการพลังงาน:
$$\rho c_p \left(\frac{\partial T}{\partial t} + \mathbf{U} \cdot \nabla T\right) = k \nabla^2 T + \Phi + Q$$

แต่ละเทอม: `[M L⁻¹ T⁻³]` (พลังงานต่อหน่วยปริมาตรต่อหน่วยเวลา)

```cpp
dimensionSet energyRate(1, -1, -3, 0, 0, 0, 0);

// Time derivative: ρcp(∂T/∂t)
auto ddtEnergy = rho * cp * fvc::ddt(T);
// Dimensions: [M L⁻³][L² T⁻² Θ⁻¹][Θ]/[T] = [M L⁻¹ T⁻³] ✓

// Convection: ρcp(U·∇T)
auto convEnergy = rho * cp * (U & fvc::grad(T));
// Dimensions: [M L⁻³][L² T⁻² Θ⁻¹][L T⁻¹][Θ]/[L] = [M L⁻¹ T⁻³] ✓

// Conduction: k∇²T
auto condEnergy = k * fvc::laplacian(T);
// Dimensions: [M L T⁻³ Θ⁻¹][Θ]/[L²] = [M L⁻¹ T⁻³] ✓

// Viscous dissipation: Φ = 2μS:S
auto dissipation = 2 * mu * (symm(fvc::grad(U)) && symm(fvc::grad(U)));
// Dimensions: [M L⁻¹ T⁻¹][T⁻¹][T⁻¹] = [M L⁻¹ T⁻³] ✓
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - **LHS**: ρcp(∂T/∂t + U·∇T) → เทอม temporal และ convective
> - **RHS1**: k∇²T → เทอม conduction (diffusive heat transfer)
> - **RHS2**: Φ → viscous dissipation (แปลง kinetic energy → internal energy)
> - **RHS3**: Q → heat source/sink
>
> **หลักการสำคัญ:**
> - Energy conservation: ทุกเทอมมีมิติ [M L⁻¹ T⁻³]
> - Heat transfer: conduction, convection, dissipation, sources
> - Thermodynamic consistency: สมการพลังงานต้องสมดุล

### ข้อผิดพลาดมิติทั่วไป

| ข้อผิดพลาด | สาเหตุ | มิติที่ได้ | มิติที่ถูกต้อง | วิธีแก้ไข |
|-------------|---------|-------------|-----------------|-------------|
| 1: ลืมความหนาแน่นใน gradient ความดัน | ใช้ `-fvc::grad(p)` แทน `-fvc::grad(p/rho)` | `[M L⁻² T⁻²]` (แรง/ปริมาตร) | `[L T⁻²]` (ความเร่ง) | หารด้วยความหนาแน่น |
| 2: ความหนืดไดนามิก vs ความเร็ว | ใช้ `mu` แทน `nu` ใน `mu*fvc::laplacian(U)` | `[M L⁻² T⁻²]` (แรง/ปริมาตร) | `[L T⁻²]` (ความเร่ง) | ใช้ความหนืดคิเนมาติก `nu` |
| 3: อัตราการไหลของมวล vs ความเร็ว | ใช้ `U & mesh.Sf()` แทน `rho*(U & mesh.Sf())` | `[L³ T⁻¹]` (ปริมาตร/เวลา) | `[M T⁻¹]` (มวล/เวลา) | คูณด้วยความหนาแน่น |
| 4: การมองข้ามการแปลงหน่วย | กำหนด `p_inlet = 1.0` แทน `101325.0` | `1 Pa` | `1 atm = 101325 Pa` | ใช้หน่วยที่เหมาะสม |
| 5: เทอมแหล่งที่มีมิติผิด | แหล่งความร้อนไม่มีมิติ `[0,0,0,0,0,0,0]` | ไม่มีมิติ | `[M L⁻¹ T⁻³]` (พลังงาน/ปริมาตร/เวลา) | ระบุมิติที่ถูกต้อง |

#### ข้อผิดพลาด 1: ลืมความหนาแน่นใน gradient ความดัน

```cpp
// WRONG: missing density division
volVectorField momentumSource = -fvc::grad(p);
// Dimensions: [M L⁻¹ T⁻²] / [L] = [M L⁻² T⁻²] (force/volume)
// Error: should be [L T⁻²] (acceleration)

// CORRECT: include density
volVectorField momentumSource = -fvc::grad(p/rho);
// Dimensions: [M L⁻¹ T⁻²] / [M L⁻³] / [L] = [L T⁻²] ✓

// Alternative: divide by density afterwards
volVectorField momentumSource = -fvc::grad(p) / rho;
// Dimensions: [M L⁻² T⁻²] / [M L⁻³] = [L T⁻²] ✓
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - **Error**: สับสนระหว่าง pressure gradient [M L⁻² T⁻²] กับ acceleration [L T⁻²]
> - **Physics**: F = ma → a = F/m → ∇p/ρ ไม่ใช่ ∇p
> - **Common mistake**: ลืมว่า Navier-Stokes ใช้ acceleration ไม่ใช่ force
>
> **หลักการสำคัญ:**
> - Pressure gradient force: -∇p มีมิติ [M L⁻² T⁻²]
> - Acceleration: -∇p/ρ มีมิติ [L T⁻²]
> - F = ma → a = F/m ใช้กับ gradients เช่นกัน

#### ข้อผิดพลาด 2: ความหนื้นแบบไดนามิก vs ความเร็ว

```cpp
// WRONG: using dynamic viscosity instead of kinematic
volVectorField viscousTerm = mu * fvc::laplacian(U);
// mu dimensions: [M L⁻¹ T⁻¹]
// Result: [M L⁻¹ T⁻¹][L T⁻¹]/[L²] = [M L⁻² T⁻²] (force/volume)
// Error: should be [L T⁻²] (acceleration)

// CORRECT: use kinematic viscosity ν = μ/ρ
volVectorField viscousTerm = nu * fvc::laplacian(U);
// nu dimensions: [L² T⁻¹]
// Result: [L² T⁻¹][L T⁻¹]/[L²] = [L T⁻²] ✓

// Alternative: explicitly include density
volVectorField viscousTerm = (mu/rho) * fvc::laplacian(U);
// mu/rho dimensions: [L² T⁻¹] = kinematic viscosity ✓
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - **Dynamic viscosity (μ)**: [M L⁻¹ T⁻¹] - resistance to flow
> - **Kinematic viscosity (ν)**: [L² T⁻¹] = μ/ρ - diffusion coefficient
> - **Momentum diffusion**: ใช้ ν ไม่ใช่ μ ในสมการ velocity
>
> **หลักการสำคัญ:**
> - μ vs ν: dynamic vs kinematic viscosity
> - Dimensional difference: [M L⁻¹ T⁻¹] vs [L² T⁻¹]
> - Navier-Stokes ใช้ ν เพื่อให้ได้มิติความเร่ง

#### ข้อผิดพลาด 3: อัตราการไหลของมวล vs ความเร็วที่ขอบเขต

```cpp
// WRONG: using velocity where mass flow rate expected
surfaceScalarField phi = U & mesh.Sf();
// Dimensions: [L T⁻¹][L²] = [L³ T⁻¹] (volumetric flow rate)
// Error: for compressible flow, need mass flow rate [M T⁻¹]

// CORRECT: include density for mass flow rate
surfaceScalarField phi = fvc::interpolate(rho) * (U & mesh.Sf());
// Dimensions: [M L⁻³][L³ T⁻¹] = [M T⁻¹] (mass flow rate) ✓
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - **Volumetric flow rate**: U·Sf มีมิติ [L³ T⁻¹]
> - **Mass flow rate**: ρU·Sf มีมิติ [M T⁻¹]
> - **Compressible flow**: ต้องใช้ mass flow rate เพื่อ conservation
>
> **หลักการสำคัญ:**
> - Continuity equation: ∂ρ/∂t + ∇·(ρU) = 0
> - Mass conservation: ใช้ mass flow rate ไม่ใช่ volumetric
> - Incompressible: ρ = constant → สามารถใช้ volumetric

### การแก้ไขข้อผิดพลาดมิติ

#### กลยุทธ์ 1: แยกเทอมที่มีปัญหา

เมื่อเผชิญกับข้อผิดพลาดมิติ ให้ตรวจสอบแต่ละเทอมแยกกัน:

```cpp
Info << "U dimensions: " << U.dimensions() << endl;
Info << "grad(p) dimensions: " << fvc::grad(p).dimensions() << endl;
Info << "rho dimensions: " << rho.dimensions() << endl;
Info << "grad(p)/rho dimensions: " << (fvc::grad(p)/rho).dimensions() << endl;
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - Debugging technique: แสดงมิติของแต่ละ sub-expression
> - Isolate the problem: แยกส่วนประกอบเพื่อหาต้นตอ
> - Systematic debugging: ตรวจสอบทีละขั้นตอน
>
> **หลักการสำคัญ:**
> - Dimensional propagation: trace ตั้งแต่ input ถึง output
> - Incremental verification: ตรวจสอบทีละเทอม
> - Systematic approach: ใช้วิธีการแบบเป็นระบบ

#### กลยุทธ์ 2: ใช้ dimensionSet สำหรับการตรวจสอบ

```cpp
// Define expected dimensions for comparison
dimensionSet expectedAcceleration(0, 1, -2, 0, 0, 0, 0);

// Check complex expressions
auto complexTerm = someComplexOperation();
if (complexTerm.dimensions() != expectedAcceleration)
{
    Warning << "Complex term has unexpected dimensions: "
            << complexTerm.dimensions() << endl;
}
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - Baseline verification: เปรียบเทียบกับมิติที่คาดหวัง
> - Runtime assertions: ใช้ assert หรือ Warning สำหรับ debugging
> - Unit testing approach: ตรวจสอบ results ตามมาตรฐาน
>
> **หลักการสำคัญ:**
> - Expected dimensions: กำหนดมิติที่ถูกต้องล่วงหน้า
> - Assertions: ใช้ใน development/testing phase
> - Defensive programming: ตรวจสอบ assumptions

#### กลยุทธ์ 3: การทดสอบการแปลงหน่วย

```cpp
// Test conversion between different unit representations
dimensionedScalar p1("p1", dimPressure, 101325.0);      // Pa
dimensionedScalar p2("p2", dimPressure, 1.01325e5);     // Pa (scientific)
dimensionedScalar p3("p3", dimPressure, 1.01325);       // bar (if bar unit defined)

// All should represent same physical quantity
scalar ratio1 = p1.value()/p2.value();  // Should be 1.0
scalar ratio2 = p1.value()/p3.value();  // Should be 100000.0 (Pa/bar)
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - Unit conversion: ทดสอบการแปลงระหว่างหน่วยต่างๆ
> - Dimensional consistency: มิติเดียวกันแต่ค่าต่างกัน
> - Validation: ยืนยันว่าการแปลงถูกต้อง
>
> **หลักการสำคัญ:**
> - Same dimensions, different units: [M L⁻¹ T⁻²] สำหรับทั้ง Pa และ bar
> - Conversion factors: 1 bar = 10⁵ Pa
> - Physical equivalence: ค่าต่างกันแต่ quantity เดียวกัน

---

## การวิเคราะห์มิติขั้นสูง

### ชนิดมิติแบบกำหนดเอง

สำหรับการใช้งานเฉพาะทาง คุณสามารถกำหนดชนิดมิติแบบกำหนดเอง:

```cpp
// Create custom dimension for concentration
dimensionSet dimConcentration(0, -3, 0, 0, 1, 0, 0);  // [N L⁻³]

// Diffusion coefficient: [L² T⁻¹]
dimensionSet dimDiffusion(0, 2, -1, 0, 0, 0, 0);

// Chemical reaction rate: [N L⁻³ T⁻¹]
dimensionSet dimReactionRate(0, -3, -1, 0, 1, 0, 0);

// Concentration equation: ∂c/∂t = D∇²c + R
// Each term: [N L⁻³ T⁻¹]

volScalarField C("C", dimConcentration, 1.0);           // Concentration
dimensionedScalar D("D", dimDiffusion, 1e-9);           // Diffusion coefficient
volScalarField R("R", dimReactionRate, 0.0);            // Reaction rate

// Check equation dimensional consistency
auto dcdt = fvc::ddt(C);              // [N L⁻³ T⁻¹]
auto diffusion = D * fvc::laplacian(C); // [L² T⁻¹][N L⁻³]/[L²] = [N L⁻³ T⁻¹]

assert(dcdt.dimensions() == dimReactionRate);
assert(diffusion.dimensions() == dimReactionRate);
assert(R.dimensions() == dimReactionRate);
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/PhaseSystems/MomentumTransferPhaseSystem/MomentumTransferPhaseSystem.C`
>
> **คำอธิบาย:**
> - **Concentration (C)**: [N L⁻³] - amount of substance per volume
> - **Diffusion coefficient (D)**: [L² T⁻¹] - rate of spreading
> - **Reaction rate (R)**: [N L⁻³ T⁻¹] - creation/destruction rate
> - **Convection-diffusion-reaction equation**: ∂c/∂t + U·∇c = D∇²c + R
>
> **หลักการสำคัญ:**
> - Custom dimensions: ใช้ SI base units ทั้ง 7 แต่กำหนดเอง
> - Transport phenomena: ใช้กับ mass, heat, momentum, species transport
> - Dimensional consistency: ทุกเทอมต้องมีมิติเดียวกัน

### การวิเคราะห์ไร้มิติ

สำหรับการวิเคราะห์ความเหมือนและจำนวนไร้มิติ:

| จำนวนไร้มิติ | สมการ | ความหมายทางฟิสิกส์ | การใช้งานใน OpenFOAM |
|---------------|---------|-------------------|-------------------|
| Reynolds Number | $Re = \frac{\rho U L}{\mu} = \frac{U L}{\nu}$ | อัตราส่วนของแรงเฉื่อยต่อแรงเหนียว | `dimensionedScalar Re("Re", dimensionSet(0,0,0,0,0,0,0), rho.value() * U.value() * L.value() / mu.value())` |
| Nusselt Number | $Nu = \frac{h L}{k} = \frac{q"L}{k \Delta T}$ | อัตราส่วนของการถ่ายเทความร้อน | `dimensionedScalar Nu("Nu", dimensionSet(0,0,0,0,0,0,0), h.value() * L.value() / k.value())` |
| Prandtl Number | $Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$ | อัตราส่วนของ diffusion โมเมนตัมต่อความร้อน | `dimensionedScalar Pr("Pr", dimensionSet(0,0,0,0,0,0,0), nu.value() / alpha.value())` |

```cpp
// Reynolds number: Re = ρUL/μ = UL/ν
// Dimensionless: [M⁰ L⁰ T⁰]

dimensionedScalar Re
(
    "Re",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),  // Dimensionless
    rho.value() * U.value() * L.value() / mu.value()
);

// Nusselt number: Nu = hL/k = q"L/(kΔT)
dimensionedScalar Nu
(
    "Nu",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),
    h.value() * L.value() / k.value()
);

// Prandtl number: Pr = ν/α = μcp/k
dimensionedScalar Pr
(
    "Pr",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),
    nu.value() / alpha.value()
);
```

> 📂 **Source:** `.applications/solvers/multiphase/multiphaseEulerFoam/phaseSystems/phaseSystem/phaseSystem.H`
>
> **คำอธิบาย:**
> - **Reynolds number (Re)**: [M⁰ L⁰ T⁰] = inertia/viscosity forces ratio
> - **Nusselt number (Nu)**: [M⁰ L⁰ T⁰] = convective/conductive heat transfer ratio
> - **Prandtl number (Pr)**: [M⁰ L⁰ T⁰] = momentum/thermal diffusivity ratio
> - **Dimensionless numbers**: ทุกเลขชี้กำลัง = 0
>
> **หลักการสำคัญ:**
> - Dimensional analysis: ใช้กลับกันเพื่อ validate correlations
> - Similarity: dimensionless numbers ใช้สำหรับ scaling
> - Buckingham π theorem: จำนวน π groups = n - k (n=variables, k=dimensions)
> - OpenFOAM applications: ใช้สำหรับ validation, scaling, model comparison

---

## สรุป: ระบบตรวจสอบมิติ

การตรวจสอบมิติของ OpenFOAM ให้เฟรมเวิร์กที่แข็งแกร่งสำหรับการรับประกันความสอดคล้องทางฟิสิกส์ในการจำลอง CFD:

### ส่วนประกอบหลัก:

| คอมโพเนนต์ | หน้าที่ | คำอธิบาย |
|--------------|----------|------------|
| **ระบบปริมาณ 7 มิติ** | การแทนค่ามิติ | มวล, ความยาว, เวลา, อุณหภูมิ, ปริมาณ, กระแส, ความสว่าง |
| **Template `DimensionedField`** | การเก็บข้อมูล | รวมการจัดเก็บสนามกับ metadata มิติ |
| **คลาส `dimensionSet`** | การจัดการมิติ | แทนและจัดการข้อมูลมิติ |
| **การ propagation อัตโนมัติ** | การถ่ายทอดมิติ | มิติไหลผ่านการดำเนินการสนามทั้งหมด |

### กลไกการบังคับใช้:

| กลไก | ระดับ | วิธีการ |
|-------|--------|------------|
| **การตรวจสอบเวลาคอมไพล์** | Compile time | ความปลอดภ้ยของ type แบบ template |
| **การตรวจสอบรันไทม์** | Runtime | การเปรียบเทียบมิติอย่างชัดเจนในการดำเนินการ |
| **การรายงานข้อผิดพลาด** | Runtime | ข้อความโดยละเอียดที่แสดงความไม่ตรงกันของมิติ |
| **การจัดการการแปลง** | Runtime | การรับรู้อัตโนมัติของระบบหน่วยที่เข้ากันได้ |

### ประโยชน์:

| ประเภท | ประโยชน์ | คำอธิบาย |
|---------|------------|------------|
| **ความปลอดภ้ยทางฟิสิกส์** | การป้องกันข้อผิดพลาด | ป้องกันการดำเนินการที่ถูกต้องทางคณิตศาสตร์แต่ไม่มีความหมายทางฟิสิกส์ |
| **ความช่วยเหลือในการดีบัก** | การตรวจพบข้อผิดพลาด | การตรวจพบข้อผิดพลาดก่อนการคำนวณที่มีค่าใช้จ่ายสูง |
| **เอกสาร code** | การบอกคุณสมบัติ | มิติทำหน้าที่เป็นข้อกำหนดทางฟิสิกส์แบบ inline |
| **การตรวจสอบแบบจำลอง** | การทดสอบอัตโนมัติ | การตรวจสอบอัตโนมัติของแบบจำลองทางฟิสิกส์ใหม่ |
| **คุณค่าทางการศึกษา** | การเรียนรู้ | ยืนยันความเข้าใจความสัมพันธ์ทางฟิสิกส์ |

ระบบตรวจสอบมิติเป็นหนึ่งในคุณสมบัติเฉพาะที่สุดของ OpenFOAM โดยแปลงหลักการของการวิเคราะห์มิติจากนามธรรมเป็นตาข่ายความปลอดภัยอัตโนมัติที่เป็นรูปธรรมที่จับข้อผิดพลาดทางฟิสิกส์ในขั้นตอนที่เร็วที่สุดของการพัฒนา