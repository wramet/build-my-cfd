# Dimension Arithmetic: เลขคณิตมิติใน OpenFOAM

> [!INFO] **ภาพรวม**
> OpenFOAM ใช้ระบบการวิเคราะห์มิติที่ซับซ้อนซึ่งทำการตรวจสอบความสม่ำเสมอของมิติโดยอัตโนมัติระหว่างการดำเนินการทางคณิตศาสตร์ ระบบนี้ป้องกันการคำนวณที่ไม่มีความหมายทางฟิสิกส์โดยบังคับให้มีความสม่ำเสมอของมิติในเวลาคอมไพล์และรันไทม์

---

## 1. พื้นฐานของการดำเนินการมิติ

### มิติพื้นฐาน SI ทั้งเจ็ด

คลาส `dimensionSet` ใน OpenFOAM เก็บมิติเป็นอาร์เรย์ของเลขชี้กำลังเจ็ดค่าสำหรับมิติพื้นฐาน SI:

| ดัชนี | มิติ | สัญลักษณ์ | หน่วย SI |
|:------:|-------|:----------:|:----------:|
| 0 | Mass (มวล) | $M$ | kg |
| 1 | Length (ความยาว) | $L$ | m |
| 2 | Time (เวลา) | $T$ | s |
| 3 | Temperature (อุณหภูมิ) | $\Theta$ | K |
| 4 | Moles (ปริมาณสาร) | $N$ | mol |
| 5 | Current (กระแสไฟฟ้า) | $I$ | A |
| 6 | Luminous Intensity (ความเข้มแสง) | $J$ | cd |

### การแสดงมิติทางคณิตศาสตร์

ปริมาณทางกายภาพแต่ละปริมาณสามารถแสดงเป็น:

$$[Q] = M^{e_0} L^{e_1} T^{e_2} \Theta^{e_3} N^{e_4} I^{e_5} J^{e_6}$$

โดยที่ $e_i$ แสดงถึงเลขชี้กำลังสำหรับมิติพื้นฐาน i-th

### ตัวอย่างชุดมิติทั่วไป

| ปริมาณ | dimensionSet | สมการมิติ | หน่วย SI |
|---------|-------------|-------------|-----------|
| **ความเร็ว** | `dimensionSet(0, 1, -1, 0, 0, 0, 0)` | $LT^{-1}$ | m/s |
| **ความดัน** | `dimensionSet(1, -1, -2, 0, 0, 0, 0)` | $ML^{-1}T^{-2}$ | Pa |
| **ความหนาแน่น** | `dimensionSet(1, -3, 0, 0, 0, 0, 0)` | $ML^{-3}$ | kg/m³ |
| **แรง** | `dimensionSet(1, 1, -2, 0, 0, 0, 0)` | $MLT^{-2}$ | N |
| **พลังงาน** | `dimensionSet(1, 2, -2, 0, 0, 0, 0)` | $ML^2T^{-2}$ | J |
| **ไร้มิติ** | `dimensionSet(0, 0, 0, 0, 0, 0, 0)` | $1$ | - |

---

## 2. การดำเนินการบวกและลบ

### หลักการพื้นฐาน

สำหรับการดำเนินการบวกและลบ OpenFOAM บังคับให้มีความสม่ำเสมอของมิติอย่างเคร่งครัด กล่าวคือ:

$$[A] + [B] \text{ ถูกต้อง เมื่อ } [A] = [B]$$

### ขั้นตอนการตรวจสอบ

1. เปรียบเทียบ `dimensionSet` ของปริมาณทั้งสอง
2. ตรวจสอบความเท่ากันของมิติทั้งเจ็ด
3. อนุญาตการดำเนินการเมื่อมิติตรงกันเท่านั้น

### การ Implement ใน OpenFOAM

```cpp
template<class Type, class GeoMesh>
void Foam::GeometricField<Type, GeoMesh>::operator+=
(
    const GeometricField<Type, GeoMesh>& gf
)
{
    if (dimensions() != gf.dimensions())
    {
        FatalErrorInFunction
            << "Dimensions of field and source are not equal" << nl
            << "    Field dimensions: " << dimensions() << nl
            << "    Source dimensions: " << gf.dimensions() << nl
            << abort(FatalError);
    }
    // ... perform addition
}
```

### ตัวอย่างการใช้งาน

```cpp
dimensionedScalar length("L", dimLength, 10.0);    // 10 m
dimensionedScalar time("t", dimTime, 2.0);         // 2 s
dimensionedScalar velocity("v", dimVelocity, 5.0);  // 5 m/s

// การดำเนินการที่ถูกต้อง
dimensionedScalar distance = length + velocity * time;  // 10 + 5×2 = 20 m

// ความไม่ตรงกันของมิติ - คอมไพล์ผิดพลาด
// dimensionedScalar invalid = length + time;  // ERROR: ไม่สามารถบวก L + T
```

### ข้อความแจ้งข้อผิดพลาด

หากมิติต่างกัน จะเกิด `Foam::error` พร้อมข้อความแสดงรายละเอียด:

```
--> FOAM FATAL ERROR:
    LHS and RHS of + have different dimensions
    dimensions : [0 1 0 0 0 0 0] != [0 0 1 0 0 0 0]
    From function operator+(const dimensioned<Type>&, const dimensioned<Type>&)
```

---

## 3. การดำเนินการคูณและหาร

### หลักการพื้นฐาน

การคูณและการหารเป็นไปตามกฎพื้นฐานของการวิเคราะห์มิติ:

- **การคูณ**: เลขชี้กำลังถูกบวกกัน
- **การหาร**: เลขชี้กำลังถูกลบกัน

### สมการมิติ

$$[A \times B] = [A] \cdot [B]$$
$$[A / B] = [A] / [B]$$

### การ Implement ใน OpenFOAM

```cpp
dimensionSet Foam::operator*(const dimensionSet& a, const dimensionSet& b)
{
    dimensionSet result(a);
    for (int i = 0; i < dimensionSet::nDimensions; ++i)
    {
        result.exponents_[i] += b.exponents_[i];
    }
    return result;
}

dimensionSet Foam::operator/(const dimensionSet& a, const dimensionSet& b)
{
    dimensionSet result(a);
    for (int i = 0; i < dimensionSet::nDimensions; ++i)
    {
        result.exponents_[i] -= b.exponents_[i];
    }
    return result;
}
```

### ตัวอย่างการใช้งาน

```cpp
// การคูณเพิ่มเลขชี้กำลัง
dimensionSet force(1, 1, -2, 0, 0, 0, 0);       // M¹L¹T⁻² (แรง)
dimensionSet distance(0, 1, 0, 0, 0, 0, 0);     // L¹ (ระยะทาง)
dimensionSet work = force * distance;           // M¹L²T⁻² (พลังงาน)

// การหารลดเลขชี้กำลัง
dimensionSet work(1, 2, -2, 0, 0, 0, 0);        // M¹L²T⁻² (พลังงาน)
dimensionSet time(0, 0, 1, 0, 0, 0, 0);         // T¹ (เวลา)
dimensionSet power = work / time;               // M¹L²T⁻³ (กำลัง)
```

### ตัวอย่างทางฟิสิกส์

กฎของแก๊สอุดมคติ: $p = \rho R T$

```cpp
volScalarField p = rho * R * T;
// [kg/m³] × [J/(kg·K)] × [K] = [Pa]
```

การตรวจสอบมิติ:
- $\rho$ (ความหนาแน่น): $ML^{-3}$
- $R$ (ค่าคงที่ก๊าซ): $L^{2}T^{-2}\Theta^{-1}$
- $T$ (อุณหภูมิ): $\Theta$
- $p$ (ความดัน): $ML^{-1}T^{-2}$ ✓

---

## 4. การดำเนินการยกกำลังและราก

### หลักการพื้นฐาน

การดำเนินการเลขชี้กำลังจะคูณแต่ละเลขชี้กำลังของมิติด้วยค่าสเกลาร์ของกำลัง:

$$[Q^s] = [Q]^s = (M^{e_0} L^{e_1} T^{e_2} \Theta^{e_3} N^{e_4} I^{e_5} J^{e_6})^s = M^{e_0 s} L^{e_1 s} T^{e_2 s} \Theta^{e_3 s} N^{e_4 s} I^{e_5 s} J^{e_6 s}$$

### การ Implement ใน OpenFOAM

```cpp
dimensionSet Foam::pow(const dimensionSet& ds, const scalar s)
{
    if (ds.dimensionless())
    {
        return dimensionSet(0, 0, 0, 0, 0, 0, 0);
    }

    dimensionSet result;
    for (int i = 0; i < dimensionSet::nDimensions; ++i)
    {
        result.exponents_[i] = ds.exponents_[i] * s;
    }
    return result;
}

dimensionSet Foam::sqrt(const dimensionSet& ds)
{
    return pow(ds, 0.5);
}

dimensionSet Foam::cbrt(const dimensionSet& ds)
{
    return pow(ds, 1.0/3.0);
}

// Square operation - equivalent to pow(ds, 2)
dimensionSet Foam::sqr(const dimensionSet& ds)
{
    return pow(ds, 2);
}
```

### ตัวอย่างการใช้งาน

```cpp
dimensionSet a(1, 2, -1, 0, 0, 0, 0);  // ML²T⁻¹

// Power operations
dimensionSet squared = pow(a, 2);     // M²L⁴T⁻²
dimensionSet root = pow(a, 0.5);      // M^0.5 L¹ T^-0.5
dimensionSet cubed = pow(a, 3);       // M³L⁶T⁻³

// Special functions
dimensionSet squareRoot = sqrt(a);    // M^0.5 L¹ T^-0.5
dimensionSet cubeRoot = cbrt(a);      // M^(1/3) L^(2/3) T^(-1/3)
```

### การประยุกต์ใช้กับ Bernoulli Equation

```cpp
// Bernoulli: p + ½ρU² = constant
volScalarField p(...);      // สนามความดัน
volVectorField U(...);      // สนามความเร็ว
dimensionedScalar rho("rho", dimDensity, 1.225);

// การดำเนินการที่สอดคล้องกับมิติ
volScalarField totalPressure = p + 0.5 * rho * magSqr(U);
// [Pa] + [kg/m³] × [m²/s²] = [Pa] + [kg/(m·s²)] = [Pa] ✓
```

---

## 5. ฟังก์ชันคณิตศาสตร์พิเศษ

### ฟังก์ชัน Transcendental

ฟังก์ชันเช่น `exp`, `log`, `sin`, `cos` ต้องการอาร์กิวเมนต์ที่ไร้มิติ เนื่องจากถูกกำหนดผ่านอนุกรมเทย์เลอร์:

$$e^x = 1 + x + \frac{x^{2}}{2!} + \frac{x^{3}}{3!} + \cdots$$

ถ้า $x$ มีมิติ แต่ละพจน์จะมีมิติที่แตกต่างกัน ทำให้อนุกรมไร้ความหมาย

### การ Implement ใน OpenFOAM

```cpp
dimensionSet Foam::trans(const dimensionSet& ds)
{
    if (!ds.dimensionless())
    {
        FatalErrorInFunction
            << "Transcendental functions require dimensionless argument" << nl
            << "    Argument dimensions: " << ds << nl
            << abort(FatalError);
    }
    return dimensionSet(0, 0, 0, 0, 0, 0, 0); // Returns dimensionless
}
```

### ตัวอย่างการใช้งานที่ผิด

```cpp
volScalarField theta(...);  // อุณหภูมิใน K
volScalarField expTheta = exp(theta);  // ERROR: exp requires dimensionless
```

### วิธีการแก้ไข

```cpp
dimensionedScalar Tref("Tref", dimTemperature, 300.0);  // อุณหภูมิอ้างอิง
volScalarField nondimTheta = theta / Tref;              // อุณหภูมิไร้มิติ
volScalarField expTheta = exp(nondimTheta);             // ตอนนี้ถูกต้อง
```

### ฟังก์ชัน Magnitude

```cpp
// Magnitude operation - preserves dimensions
dimensionSet Foam::mag(const dimensionSet& ds)
{
    // Magnitude doesn't change the fundamental dimensions
    return ds;
}
```

---

## 6. ความสม่ำเสมอของมิติในการดำเนินการ Field

### การดำเนินการกับ Field

เลขคณิตมิติขยายไปยังการดำเนินการ field ผ่าน template specialization:

```mermaid
flowchart TD
    A[Field Operation] --> B{Dimensional<br>Compatibility Check}
    B -->|Match| C[Create Result Field<br>with Combined Dimensions]
    B -->|Mismatch| D[Fatal Error]
    C --> E[Perform Element-wise<br>Computation]
    E --> F[Return Dimensionally<br>Consistent Result]
```

### กระบวนการดำเนินการกับ Field

1. ตรวจสอบความเข้ากันได้ของมิติ
2. สร้างผลลัพธ์ field พร้อมมิติที่รวมกัน
3. ดำเนินการ element-wise computation

### การ Implement ใน OpenFOAM

```cpp
template<class Type, class GeoMesh>
tmp<GeometricField<Type, GeoMesh>> Foam::operator*
(
    const GeometricField<Type, GeoMesh>& f1,
    const GeometricField<typename product<Type, Type>::type, GeoMesh>& f2
)
{
    // Check dimensional compatibility
    if (f1.dimensions() != f2.dimensions())
    {
        FatalErrorInFunction
            << "Incompatible dimensions for field multiplication" << nl
            << abort(FatalError);
    }

    // Create result field with combined dimensions
    tmp<GeometricField<typename product<Type, Type>::type, GeoMesh>> tResult
    (
        new GeometricField<typename product<Type, Type>::type, GeoMesh>
        (
            IOobject
            (
                f1.name() + "*" + f2.name(),
                f1.instance(),
                f1.db(),
                IOobject::NO_READ,
                IOobject::NO_WRITE
            ),
            f1.mesh(),
            f1.dimensions() * f2.dimensions()
        )
    );

    // Perform element-wise multiplication
    // ... implementation details

    return tResult;
}
```

### ตัวอย่างการใช้งาน

```cpp
volScalarField p(...);      // สนามความดัน
volVectorField U(...);      // สนามความเร็ว
dimensionedScalar rho("rho", dimDensity, 1.225);

// Bernoulli equation
volScalarField totalPressure = p + 0.5 * rho * magSqr(U);
// แต่ละพจน์มีมิติ: ML⁻¹T⁻² ✓
```

---

## 7. การตรวจสอบและการดีบัก

### ข้อความแจ้งข้อผิดพลาดทั่วไป

#### ข้อผิดพลาด 1: การบวกสนามที่ไม่เข้ากัน

```cpp
volScalarField p(...);  // ความดัน [Pa = kg/(m·s²)]
volScalarField T(...);  // อุณหภูมิ [K]
volScalarField wrong = p + T;  // FATAL ERROR: Dimension mismatch
```

**การแก้ไข**: ตรวจสอบความหมายทางฟิสิกส์ คุณหมายถึง `p/rho/T` หรือไม่ (กฎของแก๊สอุดมคติ)?

#### ข้อผิดพลาด 2: ลืมทำให้อาร์กิวเมนต์ไร้มิติ

```cpp
volScalarField theta(...);  // อุณหภูมิใน K
volScalarField expTheta = exp(theta);  // ERROR: exp requires dimensionless
```

**การแก้ไข**: ทำให้ไร้มิติ: `exp(theta/Tref)`

### การดีบักข้อผิดพลาดด้านมิติ

```cpp
// ตรวจสอบมิติฟิลด์
Info << "Pressure field dimensions: " << p.dimensions() << endl;
Info << "Velocity field dimensions: " << U.dimensions() << endl;

// ตรวจสอบว่าฟิลด์ไร้มิติหรือไม่
if (p.dimensions() == dimless)
{
    Info << "Pressure field is dimensionless" << endl;
}
```

### การตรวจสอบมิติในโค้ดที่กำหนดเอง

```cpp
template<class Type>
void validateDimensions(const GeometricField<Type, fvPatchField, volMesh>& field)
{
    // ตรวจสอบว่าฟิลด์มีมิติที่ถูกต้องหรือไม่
    if (field.dimensions() == dimensionSet::null)
    {
        WarningIn("validateDimensions")
            << "Field " << field.name() << " has null dimensions" << endl;
    }
}
```

---

## 8. แนวทางปฏิบัติที่ดีที่สุด

### การใช้มิติที่กำหนดไว้ล่วงหน้า

```cpp
// การใช้งานที่ถูกต้อง
dimensionedScalar rho("rho", dimDensity, 1.225);       // ความหนาแน่น
dimensionedScalar mu("mu", dimDynamicViscosity, 1.8e-5);  // ความหนืด

// การทำให้ไร้มิติ
dimensionedScalar Uref("Uref", dimVelocity, 10.0);
volScalarField Ustar = U / Uref;  // ความเร็วไร้มิติ
```

### การหลีกเลี่ยงหน่วยโดยนัย

```cpp
// การปฏิบัติที่ดี
pressure
{
    type        fixedValue;
    value       uniform 101325;    // Pa
}

// หลีกเลี่ยงหน่วยที่คลุมเครือ
pressure
{
    type        fixedValue;
    value       uniform 1.0;       // หน่วยที่ไม่ชัดเจน
}
```

### การใช้ระบบหน่วยที่สอดคล้องกัน

- แนะนำให้ใช้หน่วย SI (kg, m, s, K)
- บันทึกการแปลงหน่วยใดๆ
- ตรวจสอบหน่วยคุณสมบัติวัสดุ

---

## 9. สรุป

### หลักการสำคัญ

1. **ทุกปริมาณทางกายภาพต้องมีมิติที่ถูกต้อง** - OpenFOAM ติดตามมิติโดยอัตโนมัติ
2. **สมการต้องมีความเป็นเนื้อเดียวกันทางมิติ** - ทุกพจน์ในสมการต้องมีมิติเหมือนกัน
3. **ฟังก์ชัน transcendental ต้องการอาร์กิวเมนต์ไร้มิติ** - `exp`, `log`, `sin`, `cos` ฯลฯ
4. **การตรวจสอบมิติระหว่างรันไทม์ป้องกันข้อผิดพลาด** - OpenFOAM ให้การตรวจสอบความสอดคล้องของมิติในตัว

### ประโยชน์ของการวิเคราะห์มิติ

โดยการเข้าใจและใช้ความสามารถด้านการวิเคราะห์มิติของ OpenFOAM ผู้ปฏิบัติงาน CFD สามารถ:
- ตรวจจับข้อผิดพลาดได้ตั้งแต่เนิ่นๆ ในกระบวนการพัฒนา
- ทำให้มั่นใจได้ถึงความเป็นจริงทางฟิสิกส์ในการจำลอง
- ตรวจสอบการ implement เชิงตัวเลข
- ปรับปรุงความน่าเชื่อถือและการบำรุงรักษาโค้ด
- ดีบักปัญหาการจำลองได้ดียิ่งขึ้น

---

> [!TIP] **ข้อแนะนำ**
> ระบบการวิเคราะห์มิติของ OpenFOAM ไม่ใช่แค่คุณสมบัติด้านความปลอดภัย—แต่เป็นเครื่องมือพื้นฐานที่เชื่อมโยงระหว่างการกำหนดรูปแบบทางคณิตศาสตร์และความเป็นจริงทางกายภาพในพลศาสตร์ของไหลเชิงคำนวณ
