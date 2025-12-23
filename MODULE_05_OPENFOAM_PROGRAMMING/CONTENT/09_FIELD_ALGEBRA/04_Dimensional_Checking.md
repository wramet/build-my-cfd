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
// ความดัน: [M L⁻¹ T⁻²] = แรงต่อหน่วยพื้นที่
dimensionSet dimPressure(1, -1, -2, 0, 0, 0, 0);

// ความเร็ว: [L T⁻¹] = ระยะทางต่อหน่วยเวลา
dimensionSet dimVelocity(0, 1, -1, 0, 0, 0, 0);

// ความหนาแน่น: [M L⁻³] = มวลต่อหน่วยปริมาตร
dimensionSet dimDensity(1, -3, 0, 0, 0, 0, 0);

// ความหนืด: [M L⁻¹ T⁻¹] = diffusion ของโมเมนตัม
dimensionSet dimViscosity(1, -1, -1, 0, 0, 0, 0);

// ความนำความร้อน: [M L T⁻³ Θ⁻¹] = อัตราการไหลของความร้อนต่อ gradient ของอุณหภูมิ
dimensionSet dimConductivity(1, 1, -3, -1, 0, 0, 0);
```

### การใช้งาน Dimensioned Fields

ชนิดของสนามจะมีมิติเหล่านี้เป็นคุณสมบัติโดยธรรมชาติ:

```cpp
// สเกลาร์มิติที่มีหน่วยความดันและค่า
dimensionedScalar p("p", dimPressure, 101325.0);

// สนามเวกเตอร์ปริมาตรที่มีมิติความเร็ว
volVectorField U(
    IOobject("U", runTime.timeName(), mesh, IOobject::MUST_READ),
    mesh,
    dimensionedVector("U", dimVelocity, vector(1.0, 0.0, 0.0))
);

// สนามสเกลาร์พื้นผิวที่มีมิติอัตราการไหลของมวล [M T⁻¹]
surfaceScalarField phi(
    IOobject("phi", runTime.timeName(), mesh, IOobject::NO_READ),
    fvc::interpolate(rho) * (U & mesh.Sf())
);
```

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
    // เก็บมิติสำหรับสนามนี้
    dimensionSet dimensions_;

    // ชื่อสนามสำหรับการระบุ
    word name_;

public:
    // Constructor ที่มีมิติ
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

    // เข้าถึงมิติ
    const dimensionSet& dimensions() const
    {
        return dimensions_;
    }
```

### การตรวจสอบมิติใน Operators

```cpp
    // ตัวดำเนินการบวกที่มีการตรวจสอบมิติ
    DimensionedField<Type, GeoMesh> operator+
    (
        const DimensionedField<Type, GeoMesh>& df
    ) const
    {
        // ตรวจสอบความเข้ากันได้ของมิติก่อนการดำเนินการ
        if (dimensions_ != df.dimensions())
        {
            FatalErrorInFunction
                << "Incompatible dimensions for operation" << nl
                << "    LHS: " << name_ << " = " << dimensions_ << nl
                << "    RHS: " << df.name_ << " = " << df.dimensions() << nl
                << "    Operation: addition" << nl
                << abort(FatalError);
        }

        // สร้างสนามผลลัพธ์ที่มีมิติเดียวกัน
        DimensionedField<Type, GeoMesh> result(*this);
        result.Field<Type>::operator+=(df);
        return result;
    }
```

### การคูณและการหาร

```cpp
    // การคูณ: มิติบวกกัน
    DimensionedField<scalar, GeoMesh> operator*
    (
        const DimensionedField<Type, GeoMesh>& df
    ) const
    {
        // ผลลัพธ์มีผลรวมของมิติ
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

        // ดำเนินการคูณ element-wise
        forAll(result, i)
        {
            result[i] = this->operator[](i) * df[i];
        }

        return result;
    }

    // การหาร: มิติลบกัน
    template<class Type2>
    DimensionedField<typename product<Type, Type2>::type, GeoMesh> operator/
    (
        const DimensionedField<Type2, GeoMesh>& df
    ) const
    {
        // ผลลัพธ์มีผลต่างของมิติ
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

        // ดำเนินการหาร element-wise พร้อมการตรวจสอบความปลอดภัย
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

---

## กลไก: การตรวจสอบเวลาคอมไพล์และรันไทม์

### การตรวจสอบเวลาคอมไพล์

OpenFOAM ใช้ C++ template metaprogramming เพื่อจับข้อผิดพลาดของมิติในระหว่างการคอมไพล์:

```cpp
// Template specialization ป้องกันการดำเนินการที่ไม่เข้ากัน
template<class Type, class GeoMesh>
class DimensionedField;

// Specialization สำหรับการคูณสเกลาร์อนุญาตมิติที่แตกต่างกัน
template<class GeoMesh>
DimensionedField<scalar, GeoMesh> operator*
(
    const DimensionedField<scalar, GeoMesh>& df1,
    const DimensionedField<scalar, GeoMesh>& df2
)
{
    // มิติบวก: [A] * [B] = [A+B]
    return DimensionedField<scalar, GeoMesh>(
        df1.name() + "*" + df2.name(),
        df1.mesh(),
        df1.dimensions() + df2.dimensions()
    );
}

// การบวกต้องการมิติเดียวกัน - บังคับใช้ที่รันไทม์
// แต่ระบบ template รับประกันความปลอดภัยของ type
```

### การตรวจสอบรันไทม์

การตรวจสอบมิติหลักเกิดขึ้นที่รันไทม์ผ่านการเปรียบเทียบมิติอย่างชัดเจน:

```cpp
// ตัวอย่าง: การตรวจสอบมิติของการดำเนินการ gradient
template<class Type>
GeometricField<typename outerProduct<Type, vector>::type, fvPatchField, volMesh>
grad(const GeometricField<Type, fvPatchField, volMesh>& vf)
{
    typedef typename outerProduct<Type, vector>::type gradType;

    // คำนวณมิติของ gradient
    dimensionSet gradDims = vf.dimensions() / dimLength;

    return GeometricField<gradType, fvPatchField, volMesh>(
        IOobject("grad(" + vf.name() + ")", vf.time().timeName(), vf.db()),
        fvMesh(vf.mesh()),
        gradDims,
        fvPatchField<gradType>::calculatedType()
    );
}
```

### กฎการคำนวณมิติ

ระบบมิติทำตามกฎพีชคณิตพื้นฐาน:

#### การคูณ: มิติบวกกัน element-wise
$$[M^a L^b T^c \Theta^d N^e I^f J^g] \times [M^h L^i T^j \Theta^k N^l I^m J^n] = [M^{a+h} L^{b+i} T^{c+j} \Theta^{d+k} N^{e+l} I^{f+m} J^{g+n}]$$

#### การหาร: มิติลบกัน
$$[M^a L^b T^c \Theta^d N^e I^f J^g] / [M^h L^i T^j \Theta^k N^l I^m J^n] = [M^{a-h} L^{b-i} T^{c-j} \Theta^{d-k} N^{e-l} I^{f-m} J^{g-n}]$$

#### การบวก/ลบ: มิติต้องตรงกันพอดี
$$[M^a L^b T^c \Theta^d N^e I^f J^g] + [M^h L^i T^j \Theta^k N^l I^m J^n] \text{ requires } a=h, b=i, c=j, d=k, e=l, f=m, g=n$$

---

## "ทำไม": ความสอดคล้องทางฟิสิกส์เป็นความกังวลระดับแรก

### ประโยชน์ด้านความปลอดภัย

> [!INFO] **Type Safety สำหรับฟิสิกส์**
>
> ระบบมิติขยายระบบ type ของ C++ เพื่อรวมหน่วยทางกายภาพ โดยให้การรับประกันเวลาคอมไพล์เกี่ยวกับความถูกต้องของมิติ:

```cpp
// นี่จะล้มเหลวในการคอมไพล์หากมิติไม่ตรงกัน
template<class Field1, class Field2>
auto safeAdd(const Field1& f1, const Field2& f2) -> decltype(f1 + f2)
{
    static_assert(
        std::is_same_v<typename Field1::value_type, typename Field2::value_type>,
        "Field value types must match for addition"
    );
    return f1 + f2; // การตรวจสอบมิติรันไทม์เกิดขึ้นที่นี่
}
```

> [!WARNING] **การป้องกันข้อผิดพลาดที่มีค่าใช้จ่ายสูง**
>
> การตรวจสอบมิติป้องกันความล้มเหลวของการจำลองที่อาจปรากฏหลังจากการคำนวณเป็นชั่วโมง:

```cpp
// สถานการณ์ทั่วไป: ลืมความหนาแน่นใน gradient ของความดัน
// ผิด: ส่งคืนแรงต่อหน่วยปริมาตรแทนที่จะเป็นความเร่ง
volVectorField wrongAcceleration = -fvc::grad(p);

// ถูกต้อง: ส่งคืนความเร่งที่เหมาะสม
volVectorField correctAcceleration = -fvc::grad(p/rho);

// ระบบมิติจะจับ:
// wrongAcceleration มี [M L⁻² T⁻²] (แรงต่อปริมาตร)
// correctAcceleration มี [L T⁻²] (ความเร่ง)
// นี่คือปริมาณทางกายภพที่แตกต่างกัน!
```

### ประโยชน์ด้านประสิทธิภาพ

**ข้อความแสดงข้อผิดพลาดที่ชัดเจน**: ระบบให้ข้อมูลวินิจฉัยโดยละเอียด:

```cpp
/*
ตัวอย่างข้อผิดพลาด:
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

**Code ที่บอกเอง**: มิติทำหน้าที่เป็นเอกสารแบบ inline:

```cpp
// การประกาศสนามบอกปริมาณทางฟิสิกส์
volScalarField T("T", dimTemperature, 293.0);           // สนามอุณหภูมิ
volScalarField p("p", dimPressure, 101325.0);            // สนามความดัน
volVectorField U("U", dimVelocity, vector(0, 0, 0));    // สนามความเร็ว

// ผู้อ่านจะเข้าใจลักษณะทางกายภาพทันที
```

**ความปลอดภัยในการแปลงหน่วย**: การจัดการการแปลงหน่วยอัตโนมัติ:

```cpp
// หน่วยที่แตกต่างกันแต่มิติเดียวกันทำงานได้อย่างราบรื่น
dimensionedScalar p_atm("p_atm", dimPressure, 1.01325e5);    // Pa
dimensionedScalar p_bar("p_bar", dimPressure, 1.013);       // bar

// การดำเนินการทำงานถูกต้องด้วยความตระหนักถึงการแปลงอัตโนมัติ
dimensionedScalar p_total = p_atm + p_bar;  // ทั้งสอง [M L⁻¹ T⁻²]
```

### ประโยชน์ด้านการตรวจสอบ

**การตรวจสอบแบบจำลองอัตโนมัติ**: แบบจำลองทางกายภาพใหม่สามารถตรวจสอบมิติได้:

```cpp
// การตรวจสอบเทอมแหล่งความร้อนแบบกำหนดเอง
volScalarField customHeatSource =
    k * fvc::laplacian(T) +  // [M L T⁻³ Θ⁻¹] * [Θ L⁻²] = [M L⁻¹ T⁻³]
    Q_vol;                    // [M L⁻¹ T⁻³]

// เทอมทั้งสองต้องมี [M L⁻¹ T⁻³] (พลังงานต่อปริมาตรต่อเวลา)
if (customHeatSource.dimensions() != dimensionSet(1, -1, -3, 0, 0, 0, 0))
{
    FatalError << "Heat source has wrong dimensions!" << exit(FatalError);
}
```

**การตรวจสอบความสอดคล้องของสมการ**: สมการที่ซับซ้อนสามารถตรวจสอบได้ทีละเทอม:

```cpp
// สมการพลังงาน: ρcp(∂T/∂t + U·∇T) = k∇²T + Q
// แต่ละเทอมควรมีมิติ [M L⁻¹ T⁻³]

dimensionSet energyFlux(1, -1, -3, 0, 0, 0, 0);  // พลังงานต่อปริมาตรต่อเวลา

// ตรวจสอบแต่ละเทอม
auto lhs1 = rho * cp * fvc::ddt(T);           // ควรเป็น energyFlux
auto lhs2 = rho * cp * (U & fvc::grad(T));    // ควรเป็น energyFlux
auto rhs1 = k * fvc::laplacian(T);            // ควรเป็น energyFlux
auto rhs2 = Q_vol;                             // ควรเป็น energyFlux

// ทั้งหมดต้องตรงกันสำหรับความสอดคล้องของมิติ
```

---

## การใช้งานและตัวอย่างข้อผิดพลาด: ข้อผิดพลาดมิติทั่วไป

### ตัวอย่างการใช้งานที่ถูกต้อง

#### การตรวจสอบสมการโมเมนตัม Navier-Stokes

สมการโมเมนตัมแบบสมบูรณ์:
$$\frac{\partial \mathbf{U}}{\partial t} + (\mathbf{U} \cdot \nabla) \mathbf{U} = -\nabla \frac{p}{\rho} + \nu \nabla^2 \mathbf{U} + \mathbf{f}$$

แต่ละเทอมต้องมีมิติ `[L T⁻²]` (ความเร่ง)

```cpp
dimensionSet acceleration(0, 1, -2, 0, 0, 0, 0);

// ความเร่ง局部: ∂U/∂t
auto ddtTerm = fvc::ddt(U);
// มิติ: [L T⁻¹] / [T] = [L T⁻²] ✓
assert(ddtTerm.dimensions() == acceleration);

// ความเร่ง对流: (U·∇)U
auto convTerm = (U & fvc::grad(U));
// มิติ: [L T⁻¹] * [L T⁻¹] / [L] = [L T⁻²] ✓
assert(convTerm.dimensions() == acceleration);

// ความเร่ง gradient ความดัน: -∇p/ρ
auto pressureTerm = -fvc::grad(p/rho);
// มิติ: [M L⁻¹ T⁻²] / [M L⁻³] / [L] = [L T⁻²] ✓
assert(pressureTerm.dimensions() == acceleration);

// การ diffusion ความหนืด: ν∇²U
auto viscousTerm = nu * fvc::laplacian(U);
// มิติ: [L² T⁻¹] * [L T⁻¹] / [L²] = [L T⁻²] ✓
assert(viscousTerm.dimensions() == acceleration);

// ความเร่งแรงลำตัว: f
auto bodyForce = g;  // ความเร่งโน้มถ่วง
// มิติ: [L T⁻²] ✓
assert(bodyForce.dimensions() == acceleration);
```

#### ความสอดคล้องของสมการพลังงาน

สมการพลังงาน:
$$\rho c_p \left(\frac{\partial T}{\partial t} + \mathbf{U} \cdot \nabla T\right) = k \nabla^2 T + \Phi + Q$$

แต่ละเทอม: `[M L⁻¹ T⁻³]` (พลังงานต่อหน่วยปริมาตรต่อหน่วยเวลา)

```cpp
dimensionSet energyRate(1, -1, -3, 0, 0, 0, 0);

// อนุพันธ์ตามเวลา: ρcp(∂T/∂t)
auto ddtEnergy = rho * cp * fvc::ddt(T);
// มิติ: [M L⁻³][L² T⁻² Θ⁻¹][Θ]/[T] = [M L⁻¹ T⁻³] ✓

// การ convection: ρcp(U·∇T)
auto convEnergy = rho * cp * (U & fvc::grad(T));
// มิติ: [M L⁻³][L² T⁻² Θ⁻¹][L T⁻¹][Θ]/[L] = [M L⁻¹ T⁻³] ✓

// การ conduction: k∇²T
auto condEnergy = k * fvc::laplacian(T);
// มิติ: [M L T⁻³ Θ⁻¹][Θ]/[L²] = [M L⁻¹ T⁻³] ✓

// การ dissipation ความหนืด: Φ = 2μS:S
auto dissipation = 2 * mu * (symm(fvc::grad(U)) && symm(fvc::grad(U)));
// มิติ: [M L⁻¹ T⁻¹][T⁻¹][T⁻¹] = [M L⁻¹ T⁻³] ✓
```

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
// ผิด: ขาดการหารด้วยความหนาแน่น
volVectorField momentumSource = -fvc::grad(p);
// มิติ: [M L⁻¹ T⁻²] / [L] = [M L⁻² T⁻²] (แรงต่อปริมาตร)
// ข้อผิดพลาด: ควรเป็น [L T⁻²] (ความเร่ง)

// ถูกต้อง: รวมความหนาแน่น
volVectorField momentumSource = -fvc::grad(p/rho);
// มิติ: [M L⁻¹ T⁻²] / [M L⁻³] / [L] = [L T⁻²] ✓

// ทางเลือก: หารด้วยความหนาแน่นหลังจากนั้น
volVectorField momentumSource = -fvc::grad(p) / rho;
// มิติ: [M L⁻² T⁻²] / [M L⁻³] = [L T⁻²] ✓
```

#### ข้อผิดพลาด 2: ความหนื้นแบบไดนามิก vs ความเร็ว

```cpp
// ผิด: ใช้ความหนื้นแบบไดนามิกแทนความหนื้นแบบคิเนมาติก
volVectorField viscousTerm = mu * fvc::laplacian(U);
// mu มิติ: [M L⁻¹ T⁻¹]
// ผลลัพธ์: [M L⁻¹ T⁻¹][L T⁻¹]/[L²] = [M L⁻² T⁻²] (แรงต่อปริมาตร)
// ข้อผิดพลาด: ควรเป็น [L T⁻²] (ความเร่ง)

// ถูกต้อง: ใช้ความหนื้นแบบคิเนมาติก ν = μ/ρ
volVectorField viscousTerm = nu * fvc::laplacian(U);
// nu มิติ: [L² T⁻¹]
// ผลลัพธ์: [L² T⁻¹][L T⁻¹]/[L²] = [L T⁻²] ✓

// ทางเลือก: รวมความหนาแน่นอย่างชัดเจน
volVectorField viscousTerm = (mu/rho) * fvc::laplacian(U);
// mu/rho มิติ: [L² T⁻¹] = ความหนื้นแบบคิเนมาติก ✓
```

#### ข้อผิดพลาด 3: อัตราการไหลของมวล vs ความเร็วที่ขอบเขต

```cpp
// ผิด: ใช้ความเร็วที่ที่คาดหวังอัตราการไหลของมวล
surfaceScalarField phi = U & mesh.Sf();
// มิติ: [L T⁻¹][L²] = [L³ T⁻¹] (อัตราการไหลต่อปริมาตร)
// ข้อผิดพลาด: สำหรับการไหลบีบอัด ต้องการอัตราการไหลของมวล [M T⁻¹]

// ถูกต้อง: รวมความหนาแน่นสำหรับอัตราการไหลของมวล
surfaceScalarField phi = fvc::interpolate(rho) * (U & mesh.Sf());
// มิติ: [M L⁻³][L³ T⁻¹] = [M T⁻¹] (อัตราการไหลของมวล) ✓
```

### การแก้ไขข้อผิดพลาดมิติ

#### กลยุทธ์ 1: แยกเทอมที่มีปัญหา

เมื่อเผชิญกับข้อผิดพลาดมิติ ให้ตรวจสอบแต่ละเทอมแยกกัน:

```cpp
Info << "U dimensions: " << U.dimensions() << endl;
Info << "grad(p) dimensions: " << fvc::grad(p).dimensions() << endl;
Info << "rho dimensions: " << rho.dimensions() << endl;
Info << "grad(p)/rho dimensions: " << (fvc::grad(p)/rho).dimensions() << endl;
```

#### กลยุทธ์ 2: ใช้ dimensionSet สำหรับการตรวจสอบ

```cpp
// กำหนดมิติที่คาดหวังสำหรับการเปรียบเทียบ
dimensionSet expectedAcceleration(0, 1, -2, 0, 0, 0, 0);

// ตรวจสอบนิพจน์ที่ซับซ้อน
auto complexTerm = someComplexOperation();
if (complexTerm.dimensions() != expectedAcceleration)
{
    Warning << "Complex term has unexpected dimensions: "
            << complexTerm.dimensions() << endl;
}
```

#### กลยุทธ์ 3: การทดสอบการแปลงหน่วย

```cpp
// ทดสอบการแปลงระหว่างการแสดงหน่วยที่แตกต่างกัน
dimensionedScalar p1("p1", dimPressure, 101325.0);      // Pa
dimensionedScalar p2("p2", dimPressure, 1.01325e5);     // Pa (scientific)
dimensionedScalar p3("p3", dimPressure, 1.01325);       // bar (หากกำหนดหน่วย bar)

// ทั้งหมดควรแสดงปริมาณทางกายภาพเดียวกัน
scalar ratio1 = p1.value()/p2.value();  // ควรเป็น 1.0
scalar ratio2 = p1.value()/p3.value();  // ควรเป็น 100000.0 (Pa/bar)
```

---

## การวิเคราะห์มิติขั้นสูง

### ชนิดมิติแบบกำหนดเอง

สำหรับการใช้งานเฉพาะทาง คุณสามารถกำหนดชนิดมิติแบบกำหนดเอง:

```cpp
// สร้างมิติแบบกำหนดเองสำหรับความเข้มข้น
dimensionSet dimConcentration(0, -3, 0, 0, 1, 0, 0);  // [N L⁻³]

// สัมประสิทธิ์ diffusion: [L² T⁻¹]
dimensionSet dimDiffusion(0, 2, -1, 0, 0, 0, 0);

// อัตราปฏิกิริยาเคมี: [N L⁻³ T⁻¹]
dimensionSet dimReactionRate(0, -3, -1, 0, 1, 0, 0);

// สมการความเข้มข้น: ∂c/∂t = D∇²c + R
// แต่ละเทอม: [N L⁻³ T⁻¹]

volScalarField C("C", dimConcentration, 1.0);           // ความเข้มข้น
dimensionedScalar D("D", dimDiffusion, 1e-9);           // สัมประสิทธิ์ diffusion
volScalarField R("R", dimReactionRate, 0.0);            // อัตราปฏิกิริยา

// ตรวจสอบความสอดคล้องของมิติสมการ
auto dcdt = fvc::ddt(C);              // [N L⁻³ T⁻¹]
auto diffusion = D * fvc::laplacian(C); // [L² T⁻¹][N L⁻³]/[L²] = [N L⁻³ T⁻¹]

assert(dcdt.dimensions() == dimReactionRate);
assert(diffusion.dimensions() == dimReactionRate);
assert(R.dimensions() == dimReactionRate);
```

### การวิเคราะห์ไร้มิติ

สำหรับการวิเคราะห์ความเหมือนและจำนวนไร้มิติ:

| จำนวนไร้มิติ | สมการ | ความหมายทางฟิสิกส์ | การใช้งานใน OpenFOAM |
|---------------|---------|-------------------|-------------------|
| Reynolds Number | $Re = \frac{\rho U L}{\mu} = \frac{U L}{\nu}$ | อัตราส่วนของแรงเฉื่อยต่อแรงเหนียว | `dimensionedScalar Re("Re", dimensionSet(0,0,0,0,0,0,0), rho.value() * U.value() * L.value() / mu.value())` |
| Nusselt Number | $Nu = \frac{h L}{k} = \frac{q"L}{k \Delta T}$ | อัตราส่วนของการถ่ายเทความร้อน | `dimensionedScalar Nu("Nu", dimensionSet(0,0,0,0,0,0,0), h.value() * L.value() / k.value())` |
| Prandtl Number | $Pr = \frac{\nu}{\alpha} = \frac{\mu c_p}{k}$ | อัตราส่วนของ diffusion โมเมนตัมต่อความร้อน | `dimensionedScalar Pr("Pr", dimensionSet(0,0,0,0,0,0,0), nu.value() / alpha.value())` |

```cpp
// จำนวน Reynolds: Re = ρUL/μ = UL/ν
// ไร้มิติ: [M⁰ L⁰ T⁰]

dimensionedScalar Re
(
    "Re",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),  // ไร้มิติ
    rho.value() * U.value() * L.value() / mu.value()
);

// จำนวน Nusselt: Nu = hL/k = q"L/(kΔT)
dimensionedScalar Nu
(
    "Nu",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),
    h.value() * L.value() / k.value()
);

// จำนวน Prandtl: Pr = ν/α = μcp/k
dimensionedScalar Pr
(
    "Pr",
    dimensionSet(0, 0, 0, 0, 0, 0, 0),
    nu.value() / alpha.value()
);
```

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
| **การตรวจสอบเวลาคอมไพล์** | Compile time | ความปลอดภัยของ type แบบ template |
| **การตรวจสอบรันไทม์** | Runtime | การเปรียบเทียบมิติอย่างชัดเจนในการดำเนินการ |
| **การรายงานข้อผิดพลาด** | Runtime | ข้อความโดยละเอียดที่แสดงความไม่ตรงกันของมิติ |
| **การจัดการการแปลง** | Runtime | การรับรู้อัตโนมัติของระบบหน่วยที่เข้ากันได้ |

### ประโยชน์:

| ประเภท | ประโยชน์ | คำอธิบาย |
|---------|------------|------------|
| **ความปลอดภัยทางฟิสิกส์** | การป้องกันข้อผิดพลาด | ป้องกันการดำเนินการที่ถูกต้องทางคณิตศาสตร์แต่ไม่มีความหมายทางฟิสิกส์ |
| **ความช่วยเหลือในการดีบัก** | การตรวจพบข้อผิดพลาด | การตรวจพบข้อผิดพลาดก่อนการคำนวณที่มีค่าใช้จ่ายสูง |
| **เอกสาร code** | การบอกคุณสมบัติ | มิติทำหน้าที่เป็นข้อกำหนดทางฟิสิกส์แบบ inline |
| **การตรวจสอบแบบจำลอง** | การทดสอบอัตโนมัติ | การตรวจสอบอัตโนมัติของแบบจำลองทางฟิสิกส์ใหม่ |
| **คุณค่าทางการศึกษา** | การเรียนรู้ | ยืนยันความเข้าใจความสัมพันธ์ทางฟิสิกส์ |

ระบบตรวจสอบมิติเป็นหนึ่งในคุณสมบัติเฉพาะที่สุดของ OpenFOAM โดยแปลงหลักการของการวิเคราะห์มิติจากนามธรรมเป็นตาข่ายความปลอดภัยอัตโนมัติที่เป็นรูปธรรมที่จับข้อผิดพลาดทางฟิสิกส์ในขั้นตอนที่เร็วที่สุดของการพัฒนา
