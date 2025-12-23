# 📦 คอนเทนเนอร์ `List` ของ OpenFOAM: คู่มือครอบคลุมสำหรับการพัฒนา CFD

## 🔍 แนวคิดระดับสูง: ระบบจัดเก็บข้อมูลแบบยืดหยุ่น

ในพลศาสตร์ของไหลเชิงคำนวณ คอนเทนเนอร์ `List` ทำหน้าที่เป็นอาร์เรย์ขนาดไดนามิกพื้นฐานของ OpenFOAM—จินตนาการถึงระบบจัดเก็บข้อมูลแบบปรับตัวได้ที่มีช่องว่างสามารถขยายหรือหดตัวในขณะที่ยังคงรักษารูปแบบการเข้าถึงที่มีประสิทธิภาพสูง คอนเทนเนอร์นี้ให้โครงสร้างหลักสำหรับจัดเก็บข้อมูลฟิลด์, เวกเตอร์การแก้ปัญหา, และผลลัพธ์กลางคันตลอดการจำลอง CFD

คลาส `List` ใช้กลยุทธ์การจัดสรรหน่วยความจำต่อเนื่อง โดยที่องค์ประกอบทั้งหมดถูกจัดเก็บตามลำดับ ทำให้การดำเนินการที่เป็นมิตรกับแคชมีประสิทธิภาพสูงซึ่งเป็นสิ่งจำเป็นสำหรับการคำนวณเชิงตัวเลข ต่างจากอาร์เรย์ C++ มาตรฐาน, `List` จัดการการจัดสรรหน่วยความจำ, การปรับขนาด, และการตรวจสอบขอบเขตโดยอัตโนมัติในขณะที่ยังคงคุณสมบัติด้านประสิทธิภาพที่จำเป็นสำหรับแอปพลิเคชัน CFD ขนาดใหญ่

```mermaid
graph TD
    UList["UList<T><br/>(No Memory Ownership)"] --> List["List<T><br/>(Allocated Memory)"]
    List --> Field["Field<T><br/>(Algebraic Ops)"]
    Field --> GeometricField["GeometricField<T><br/>(Physical Field: p, U)"]
```
> **Figure 1:** ลำดับชั้นการสืบทอด (Inheritance Hierarchy) ของคลาสคอนเทนเนอร์ใน OpenFOAM เริ่มต้นจาก `UList` ที่ไม่มีความเป็นเจ้าของหน่วยความจำ ไปจนถึง `GeometricField` ซึ่งเป็นคลาสที่มีความซับซ้อนสูงสุดสำหรับการจัดการฟิลด์ทางฟิสิกส์ที่มีข้อมูลเมชประกอบอยู่

### สถาปัตยกรรมการจัดเก็บข้อมูลหลัก

`List` ทำงานบนหลักการของ **อาร์เรย์ไดนามิกที่ปลอดภัยต่อชนิดข้อมูล** พร้อมการจัดการหน่วยความจำอัตโนมัติ การออกแบบที่ใช้เทมเพลตทำให้มั่นใจได้ว่ามีการตรวจสอบชนิดข้อมูลในเวลาคอมไพล์ในขณะที่ให้ความยืดหยุ่นในการแก้ไขขนาดในรันไทม์ อินสแตนซ์ `List` แต่ละรายการรักษาองค์ประกอบสำคัญสามรายการ: พอยเตอร์ไปยังหน่วยความจำที่จัดสรร (`v_`), จำนวนองค์ประกอบปัจจุบัน (`size_`), และความจุทั้งหมดที่จัดสรร (`capacity_`)

กลยุทธ์การจัดเก็บทำตาม **รูปแบบการจัดสรรที่เน้นการเติบโต** โดยที่คอนเทนเนอร์จะขยายในชิ้นส่วนที่แยกจากกันเพื่อลดการจัดสรรหน่วยความจำซ้ำๆ เมื่อความจุปัจจุบันเกินขีดจำกัด ตัวจัดสรรโดยทั่วไปจะเพิ่มพื้นที่ที่จัดสรรเป็นสองเท่า, คัดลอกองค์ประกอบที่มีอยู่ไปยังตำแหน่งหน่วยความจำใหม่ และปล่อยการจัดสรรเก่า แนวทางนี้สมดุลระหว่างประสิทธิภาพหน่วยความจำกับการปรับให้เหมาะสมด้านประสิทธิภาพ

### ความสัมพันธ์กับระบบฟิลด์ของ OpenFOAM

`List` เป็นพื้นฐานสำหรับลำดับชั้นฟิลด์ทั้งหมดของ OpenFOAM คลาสฟิลด์ (`volScalarField`, `volVectorField`, ฯลฯ) สืบทอดจาก `List` และขยายความสามารถด้วยการรับรู้เมช, การจัดการเงื่อนไขขอบเขต, และการดำเนินการทางคณิตศาสตร์ การสืบทอดนี้ช่วยให้สามารถแปลงระหว่างการจัดเก็บข้อมูลดิบและการแสดงผลฟิลด์ที่มีความหมายทางฟิสิกส์ได้อย่างราบรื่น

เมื่อทำงานกับการจำลอง CFD, คุณจะพบกับอินสแตนซ์ `List` ทั่วทั้งโค้ดเบส—จากการกระจายความดันและความเร็วไปจนถึงพารามิเตอร์โมเดลความปั่นป่วนและความเข้มข้นของสารเคมี การออกแบบคอนเทนเนอร์มุ่งเน้นเฉพาะที่ความต้องการด้านประสิทธิภาพของวิธีการเชิงตัวเลข เช่น การวิธีปริมาตรจำกัด ซึ่งการเข้าถึงและการแก้ไของค์ประกอบอย่างรวดเร็วเป็นสิ่งจำเป็นสำหรับประสิทธิภาพของ solver

## ⚙️ การใช้งานทางเทคนิค

### สถาปัตยกรรมเทมเพลตและระบบชนิดข้อมูล

คลาสเทมเพลต `List` ใน OpenFOAM ให้รากฐานที่แข็งแกร่งสำหรับการดำเนินการคอนเทนเนอร์ที่ปลอดภัยต่อชนิดข้อมูล:

```cpp
template<class T>
class List : public UList<T>
{
private:
    T* __restrict__ v_;      // พอยเตอร์ไปยังหน่วยความจำที่จัดสรร
    label size_;             // จำนวนองค์ประกอบปัจจุบัน
    label capacity_;         // ความจุทั้งหมดที่จัดสรร

public:
    // Constructor กับรูปแบบการกำหนดค่าเริ่มต้นต่างๆ
    List();
    explicit List(const label n);
    List(const label n, const T& val);
    List(const List<T>& lst);

    // การดำเนินการจัดการหน่วยความจำ
    void resize(const label n);
    void reserve(const label n);
    void clear();
    void shrink();

    // การเข้าถึงองค์ประกอบพร้อมการตรวจสอบขอบเขต
    T& operator[](const label i);
    const T& operator[](const label i) const;

    // ตัวดำเนินการกำหนดค่าและการเปรียบเทียบ
    List<T>& operator=(const List<T>& lst);
    bool operator==(const List<T>& lst) const;
    bool operator!=(const List<T>& lst) const;
};
```

โครงสร้างเทมเพลตนี้ช่วยให้สามารถสร้างอินสแตนซ์ในเวลาคอมไพล์สำหรับชนิดข้อมูลต่างๆ ที่ใช้กันทั่วไปใน CFD:

```cpp
// ชนิดข้อมูล CFD ทั่วไปที่จัดเก็บใน Lists
List<scalar> pressureValues;           // ฟิลด์ความดัน
List<vector> velocityVectors;          // ส่วนประกอบความเร็ว
List<tensor> stressTensors;            // ฟิลด์เทนเซอร์ความเค้น
List<label> connectivityIndices;       // การเชื่อมต่อเมช
List<symmTensor> reynoldsStress;        // ปริมาณความปั่นป่วน
List<sphericalTensor> vorticity;        // ฟิลด์การหมุน
```

### กลยุทธ์การจัดการหน่วยความจำ

กลยุทธ์การจัดสรรใช้การเติบโตแบบเอกซ์โพเนนเชียลพร้อมการจัดการความจุ:

```cpp
template<class T>
void List<T>::reserve(const label nAlloc)
{
    if (nAlloc > capacity_)
    {
        T* newV = new T[nAlloc];           // จัดสรรหน่วยความจำใหม่

        // คัดลอกหน่วยความจำอย่างมีประสิทธิภาพโดยใช้ std::copy สำหรับ pod types
        if (std::is_trivially_copyable<T>::value)
        {
            std::memcpy(newV, v_, size_ * sizeof(T));
        }
        else
        {
            // คัดลอกแบบองค์ประกอบต่อองค์ประกอบสำหรับชนิดข้อมูลที่ซับซ้อนที่มี destructor
            for (label i = 0; i < size_; i++)
            {
                newV[i] = std::move(v_[i]);
            }
        }

        delete[] v_;                        // ปล่อยหน่วยความจำเก่า
        v_ = newV;                          // อัปเดตพอยเตอร์
        capacity_ = nAlloc;                 // อัปเดตความจุ
    }
}

template<class T>
void List<T>::resize(const label n)
{
    if (n != size_)
    {
        if (n > capacity_)
        {
            reserve(max(n, 2 * capacity_));  // การเติบโตแบบเอกซ์โพเนนเชียล
        }

        // สร้างองค์ประกอบใหม่ถ้าขยาย
        for (label i = size_; i < n; i++)
        {
            new (&v_[i]) T();                // Placement new สำหรับการสร้าง
        }

        // ทำลายองค์ประกอบที่ถูกลบถ้าหด
        for (label i = n; i < size_; i++)
        {
            v_[i].~T();                      // เรียก destructor อย่างชัดเจน
        }

        size_ = n;
    }
}
```

### การดำเนินการขั้นสูงและการสนับสนุนอัลกอริทึม

`List` ทำงานร่วมกับระบบอัลกอริทึมของ OpenFOAM ได้อย่างราบรื่น:

```cpp
// การดำเนินการแบบขนานโดยใช้เฟรมเวิร์กแบบขนานของ OpenFOAM
List<scalar> parallelReduce(const List<scalar>& field)
{
    scalar sumField = 0.0;
    forAll(field, i)
    {
        sumField += field[i];
    }
    reduce(sumField, sumOp<scalar>());      // MPI reduction ข้ามโปรเซสเซอร์
    return List<scalar>(1, sumField);
}

// การดำเนินการทางคณิตศาสตร์กับพีชคณิตฟิลด์
List<vector> computeGradients(const List<scalar>& phi, const fvMesh& mesh)
{
    List<vector> gradPhi(phi.size());

    forAll(gradPhi, cellI)
    {
        const labelList& cellFaces = mesh.cells()[cellI];
        vector grad = vector::zero;

        forAll(cellFaces, faceI)
        {
            label faceID = cellFaces[faceI];
            vector dSf = mesh.Sf()[faceID];  // เวกเตอร์พื้นที่ผิว
            scalar deltaPhi = phi[faceID] - phi[cellI];
            grad += deltaPhi * dSf / mesh.V()[cellI];
        }

        gradPhi[cellI] = grad;
    }

    return gradPhi;
}
```

### เทคนิคการปรับให้เหมาะสมด้านประสิทธิภาพ

การใช้งาน `List` ประกอบด้วยคุณสมบัติที่เพิ่มประสิทธิภาพหลายอย่าง:

```cpp
// รูปแบบการวนซ้ำที่เป็นมิตรกับแคช
template<class T>
class optimizedListOperations
{
public:
    // การวนซ้ำที่ตระหนักถึงการ prefetch สำหรับลิสต์ขนาดใหญ่
    static void elementwiseOperation(List<T>& result, const List<T>& op1, const List<T>& op2)
    {
        const label n = result.size();

        // ประมวลผลเป็นชิ้นที่เป็นมิตรกับแคช
        constexpr label chunkSize = 64;      // ปรับให้เหมาะสมสำหรับขนาด cache line

        for (label chunk = 0; chunk < n; chunk += chunkSize)
        {
            label end = min(chunk + chunkSize, n);

            // Prefetch ชิ้นถัดไปลงในแคช
            if (end + chunkSize <= n)
            {
                __builtin_prefetch(&op1[end + chunkSize], 0, 3);
                __builtin_prefetch(&op2[end + chunkSize], 0, 3);
                __builtin_prefetch(&result[end + chunkSize], 1, 3);
            }

            // ประมวลผลชิ้นปัจจุบัน
            for (label i = chunk; i < end; i++)
            {
                result[i] = op1[i] * op2[i];   // ตัวอย่าง: การคูณแบบองค์ประกอบต่อองค์ประกอบ
            }
        }
    }
};
```

## 🧠 สถาปัตยกรรมหน่วยความจำและการสืบทอด

### การออกแบบลำดับชั้นคอนเทนเนอร์

ระบบคอนเทนเนอร์ของ OpenFOAM ทำตามลำดับชั้นการสืบทอดที่มีโครงสร้างอย่างระมัดรัว:

```cpp
// อินเทอร์เฟซฐานโดยไม่มีความเป็นเจ้าของหน่วยความจำ
template<class T>
class UList
{
protected:
    T* __restrict__ v_;
    label size_;

public:
    // การดำเนินการอินเทอร์เฟซบริสุทธิ์
    virtual T& operator[](const label i) = 0;
    virtual const T& operator[](const label i) const = 0;
    virtual label size() const = 0;

    // Constructor แบบไม่มีความเป็นเจ้าของ
    UList(T* data, label size) : v_(data), size_(size) {}

    // Virtual destructor สำหรับพฤติกรรม polymorphic
    virtual ~UList() = default;
};

// คอนเทนเนอร์ที่เป็นเจ้าของพร้อมการจัดการหน่วยความจำ
template<class T>
class List : public UList<T>
{
private:
    label capacity_;     // การติดตามความจุเพิ่มเติม

public:
    // Constructor ที่เป็นเจ้าของหน่วยความจำ
    explicit List(label n = 0) : UList<T>(nullptr, n), capacity_(n)
    {
        if (n > 0)
        {
            this->v_ = new T[n];
        }
    }

    // การใช้งานกฎห้าม (Rule of five)
    List(const List<T>& other) : List(other.size())
    {
        for (label i = 0; i < this->size_; i++)
        {
            this->v_[i] = other.v_[i];
        }
    }

    List(List<T>&& other) noexcept
    {
        this->v_ = other.v_;
        this->size_ = other.size_;
        capacity_ = other.capacity_;

        other.v_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }

    List& operator=(const List<T>& other)
    {
        if (this != &other)
        {
            resize(other.size_);
            for (label i = 0; i < this->size; i++)
            {
                this->v_[i] = other.v_[i];
            }
        }
        return *this;
    }

    List& operator=(List<T>&& other) noexcept
    {
        if (this != &other)
        {
            delete[] this->v_;

            this->v_ = other.v_;
            this->size_ = other.size_;
            capacity_ = other.capacity_;

            other.v_ = nullptr;
            other.size_ = 0;
            other.capacity_ = 0;
        }
        return *this;
    }

    ~List()
    {
        delete[] this->v_;
    }
};
```

### การผสานรวมระบบฟิลด์

คลาสฟิลด์สร้างขึ้นบน `List` เพื่อให้ฟังก์ชันการทำงานที่รับรู้เมช:

```cpp
// คลาสฟิลด์ฐาน
template<class Type, class GeoMesh>
class GeometricField : public List<Type>
{
protected:
    const GeoMesh& mesh_;           // การอ้างอิงเมช
    word name_;                     // ตัวระบุฟิลด์
    Dimensioned<Type> dimensions_;  // มิติทางฟิสิกส์

public:
    // Constructor ที่รับรู้เมช
    GeometricField(const word& name, const GeoMesh& mesh, const dimensionSet& dims)
        : List<Type>(mesh.size()), mesh_(mesh), name_(name), dimensions_(dims)
    {}

    // วิธีการผสานรวมเมช
    const GeoMesh& mesh() const { return mesh_; }
    const word& name() const { return name_; }
    const dimensionSet& dimensions() const { return dimensions_.dimensions(); }

    // การจัดการเงื่อนไขขอบเขต
    template<class PatchField>
    void setBoundaryCondition(const word& patchName, const PatchField& condition)
    {
        label patchID = mesh_.boundaryMesh().findPatchID(patchName);
        if (patchID != -1)
        {
            // ใช้เงื่อนไขขอบเขตกับ patch ที่ระบุ
            applyPatchCondition(patchID, condition);
        }
    }
};

// ชนิดฟิลด์เฉพาะ
using volScalarField = GeometricField<scalar, fvMesh>;
using volVectorField = GeometricField<vector, fvMesh>;
using surfaceScalarField = GeometricField<scalar, surfaceMesh>;
```

## ⚠️ ข้อควรพิจารณาด้านประสิทธิภาพและข้อผิดพลาดทั่วไป

### ข้อผิดพลาดในการจัดการหน่วยความจำ

#### 1. การใช้ Iterator ไม่ได้ระหว่างการปรับขนาด

```cpp
// ปัญหาประสิทธิภาพร้ายแรง: การอ้างอิงที่ใช้ไม่ได้
void problematicResizing(List<scalar>& values)
{
    // รับพอยเตอร์ไปยังองค์ประกอบก่อนการจัดสรรหน่วยความจำใหม่ที่อาจเกิดขึ้น
    scalar& firstValue = values[0];  // การอ้างอิงถึงองค์ประกอบแรก

    // การจัดสรรหน่วยความจำใหม่อาจเกิดขึ้น, ย้ายตำแหน่งหน่วยความจำ
    values.resize(values.size() + 1000);  // หน่วยความจำอาจย้าย!

    // อันตราย: firstValue ตอนนี้ชี้ไปยังหน่วยความจำที่ถูกปล่อยแล้ว
    firstValue = 123.45;  // พฤติกรรมที่ไม่กำหนด - น่าจะขัดข้อง
}

// ทางเลือกที่ปลอดภัย
void safeResizing(List<scalar>& values)
{
    label originalSize = values.size();
    values.resize(originalSize + 1000);  // ปรับขนาดก่อน

    // รับการอ้างอิงใหม่หลังจากปรับขนาด
    scalar& firstValue = values[0];  // การอ้างอิงที่ถูกต้อง
    firstValue = 123.45;  // การดำเนินการที่ปลอดภัย
}
```

#### 2. ผลกระทบด้านประสิทธิภาพจากการจัดสรรหน่วยความจำซ้ำๆ

| แนวทาง | ความซับซ้อน | การจัดสรรหน่วยความจำ | ประสิทธิภาพ | คำอธิบาย |
|---------|-------------|------------------|---------|----------|
| `inefficientConstruction` | O(n²) | หลายครั้ง | ต่ำ | การใช้ `append()` ซ้ำๆ |
| `efficientConstruction` | O(n) | 1 ครั้ง | สูง | การจัดสรรครั้งเดียว |
| `dynamicGrowthWithReserve` | O(n) | 1-2 ครั้ง | สูง | การจองความจุล่วงหน้า |

```cpp
// รูปแบบตรงข้าม: ความซับซ้อน O(n²) จากการปรับขนาดซ้ำๆ
List<scalar> inefficientConstruction()
{
    List<scalar> data;

    // แต่ละการต่อท้ายอาจทำให้เกิดการจัดสรรและคัดลอกใหม่
    for (label i = 0; i < 100000; i++)
    {
        data.append(i * 0.001);  // การดำเนินการ O(n) ต่อการต่อท้ายที่เป็นไปได้
    }

    return data;  // ความซับซ้อนโดยรวม O(n²)
}

// แนวทางที่เหมาะสม: ความซับซ้อน O(n) พร้อมการจัดสรรล่วงหน้า
List<scalar> efficientConstruction()
{
    List<scalar> data(100000);  // จัดสรรครั้งเดียว

    // การกำหนดค่าโดยตรงโดยไม่มีการจัดสรรใหม่
    for (label i = 0; i < data.size(); i++)
    {
        data[i] = i * 0.001;  // การดำเนินการ O(1) ต่อองค์ประกอบ
    }

    return data;  // ความซับซ้อนโดยรวม O(n)
}

// ทางเลือก: การเติบโตแบบไดนามิกพร้อมการจองความจุ
List<scalar> dynamicGrowthWithReserve()
{
    List<scalar> data;
    data.reserve(100000);  // จองความจุล่วงหน้า

    // การดำเนินการต่อท้ายโดยไม่มีการจัดสรรใหม่
    for (label i = 0; i < 100000; i++)
    {
        data.append(i * 0.001);  // O(1) เฉลี่ยเฉลี่ยต่อการต่อท้าย
    }

    return data;
}
```

### การปรับให้เหมาะสมด้านประสิทธิภาพแคช

| รูปแบบการเข้าถึง | ประสิทธิภาพแคช | การใช้งาน | คำแนะนำ |
|---------------|--------------|----------|----------|
| `sequential` | สูง | การวนซ้ำปกติ | **แนะนำ** สำหรับลูปหลัก |
| `strided` | ปานกลาง | การเข้าถึงทุก n องค์ประกอบ | ใช้เมื่อจำเป็น |
| `random` | ต่ำ | การจัดทำดัชนี | หลีกเลี่ยงหากเป็นไปได้ |

```cpp
// รูปแบบการเข้าถึงตามลำดับที่เป็นมิตรกับแคช
void cacheFriendlyIteration(List<scalar>& field)
{
    // การเข้าถึงตามลำดับเพิ่มประสิทธิภาพการใช้แคช
    forAll(field, i)
    {
        field[i] *= 1.001;  // รูปแบบการเข้าถึงหน่วยความจำที่ทำนายได้
    }
}

// การประมวลผลแบบบล็อกสำหรับชุดข้อมูลขนาดใหญ่
void blockWiseProcessing(List<scalar>& field)
{
    constexpr label BLOCK_SIZE = 1024;  // ปรับให้เหมาะสมสำหรับขนาดแคช
    const label n = field.size();

    for (label block = 0; block < n; block += BLOCK_SIZE)
    {
        label blockEnd = min(block + BLOCK_SIZE, n);

        // ประมวลผลบล็อกเพื่อให้อยู่ภายในแคช
        for (label i = block; i < blockEnd; i++)
        {
            field[i] = sqrt(abs(field[i]));  // การดำเนินการที่ซับซ้อน
        }
    }
}
```

## 🎯 การประยุกต์ใช้ทางวิศวกรรมใน CFD

### การจัดเก็บและรูปแบบการเข้าถึงฟิลด์

ในการจำลอง CFD แบบปริมาตรจำกัด, คอนเทนเนอร์ `List` ทำหน้าที่เป็นกลไกการจัดเก็บข้อมูลหลักสำหรับค่าฟิลด์ที่แบ่งค่า:

```cpp
class CFDFieldStorage
{
private:
    const fvMesh& mesh_;

    // ตัวแปรฟิลด์หลัก
    List<scalar> pressure_;          // ฟิลด์ความดัน [Pa]
    List<vector> velocity_;          // ฟิลด์ความเร็ว [m/s]
    List<scalar> temperature_;       // ฟิลด์อุณหภูมิ [K]

    // ปริมาณที่ได้จากการคำนวณ
    List<scalar> turbulenceKE_;      // พลังงานจลน์ความปั่นป่วน [m²/s²]
    List<scalar> turbulenceEpsilon_; // การสลายตัวของความปั่นป่วน [m²/s³]

    // การเข้าถึงเรขาคณิตเมช
    List<vector> cellCenters_;       // พิกัดจุดศูนย์กลางเซลล์
    List<scalar> cellVolumes_;       // ปริมาตรเซลล์ [m³]
    List<tensor> cellGradients_;     // เทนเซอร์ไลเกรเดียนของเซลล์

public:
    CFDFieldStorage(const fvMesh& mesh) : mesh_(mesh)
    {
        // กำหนดค่าเริ่มต้นการจัดเก็บฟิลด์ด้วยมิติของเมช
        pressure_.setSize(mesh.nCells());
        velocity_.setSize(mesh.nCells());
        temperature_.setSize(mesh.nCells());
        turbulenceKE_.setSize(mesh.nCells());
        turbulenceEpsilon_.setSize(mesh.nCells());

        // คำนวณปริมาณทางเรขาคณิตล่วงหน้า
        computeGeometry();
    }

    // กำหนดค่าเริ่มต้นการกระจายความดันไฮโดรสแตติก
    void initializeHydrostaticPressure(scalar pRef, scalar rhoRef, scalar g)
    {
        forAll(pressure_, cellI)
        {
            scalar z = cellCenters_[cellI].z();  // ความสูงเหนือจุดอ้างอิง
            pressure_[cellI] = pRef - rhoRef * g * z;
        }
    }
};
```

### การผสานรวม Linear Solver

คอนเทนเนอร์ `List` เป็นพื้นฐานสำหรับการแก้ปัญหาระบบเชิงเส้นที่เกิดจากการวิธีปริมาตรจำกัด CFD

### การผสานรวมเวลาและการจำลองแบบข้าวเวลา

สำหรับการจำลองแบบ CFD แบบข้าวเวลา, คอนเทนเนอร์ `List` จัดเก็บประวัติฟิลด์และเปิดใช้งานอัลกอริทึมการขยับเวลา

## 🧮 พื้นฐานทางคณิตศาสตร์

คอนเทนเนอร์ `List` เป็นพื้นฐานสำหรับการดำเนินการทางคณิตศาสตร์ที่จำเป็นสำหรับพลศาสตร์ของไหลเชิงคำนวณ ในวิธีปริมาตรจำกัด, รูปแบบที่แบ่งค่าของสมการกำกับต้องการจัดเก็บและการจัดการค่าฟิลด์อย่างมีประสิทธิภาพข้ามเซลล์เมช, ผิวหน้า, และขอบเขต

### การวิธีปริมาตรจำกัด

วิธีปริมาตรจำกัดแบ่งสมการกำกับเป็นรูปแบบพีชคณิตที่สามารถแก้ปัญหาได้โดยใช้คอนเทนเนอร์ `List`:

$$\int_V \frac{\partial \phi}{\partial t} \, \mathrm{d}V + \oint_S \phi \mathbf{u} \cdot \mathbf{n} \, \mathrm{d}S = \int_V \nabla \cdot (\Gamma \nabla \phi) \, \mathrm{d}V + \int_V S_\phi \, \mathrm{d}V$$

รูปแบบอินทิกรัลนี้กลายเป็นระบบสมการพีชคณิต:

$$\sum_{f=1}^{n_f} \phi_f \mathbf{u}_f \cdot \mathbf{S}_f = \sum_{f=1}^{n_f} \Gamma_f \frac{\phi_{P} - \phi_{N}}{d_{PN}} |\mathbf{S}_f| + S_P V_P$$

โดยที่แต่ละเทอมถูกจัดเก็บและคำนวณโดยใช้คอนเทนเนอร์ `List`:

- $\phi$ ตัวแปรขนส่ง (เช่น ความเร็ว, อุณหภูมิ, ความเข้มข้นสาร)
- $\mathbf{u}$ เวกเตอร์ความเร็วของไหล
- $\mathbf{S}_f$ เวกเตอร์พื้นที่ผิวหน้า
- $\Gamma_f$ สัมประสิทธิ์การแพร่ตัวที่ผิวหน้า
- $d_{PN}$ ระยะห่างระหว่างเซลล์ข้างเคียง
- $S_P$ เทอมต้นทางต่อปริมาตร
- $V_P$ ปริมาตรเซลล์

```cpp
// การวิธีปริมาตรจำกัดโดยใช้คอนเทนเนอร์ List
class FiniteVolumeDiscretization
{
private:
    const fvMesh& mesh_;
    List<scalar> phi_;           // ฟิลด์ตัวแปรหลัก
    List<scalar> sourceTerm_;    // เทอมต้นทาง S_φ
    List<vector> velocity_;      // ฟิลด์ความเร็ว u
    List<scalar> diffusivity_;   // สัมประสิทธิ์การแพร่ Γ

    // สัมประสิทธิ์เมทริกซ์สำหรับระบบเชิงเส้น
    List<scalar> diagonal_;      // สัมประสิทธิ์ A_P
    List<scalar> lower_;         // สัมประสิทธิ์ A_N (สามเหลี่ยมล่าง)
    List<scalar> upper_;         // สัมประสิทธิ์ A_P (สามเหลี่ยมบน)
    List<label> lowerAddr_;      // การจัดที่อยู่เมทริกซ์ล่าง
    List<label> upperAddr_;      // การจัดที่อยู่เมทริกซ์บน

public:
    // สร้างเมทริกซ์การแบ่งค่าสำหรับสมการ convection-diffusion
    void buildConvectionDiffusionMatrix()
    {
        label nCells = mesh_.nCells();
        diagonal_.setSize(nCells, 0.0);
        sourceTerm_.setSize(nCells, 0.0);

        // ประมวลผลผิวหน้าทั้งหมดเพื่อสร้างเมทริกซ์
        forAll(mesh_.faces(), faceI)
        {
            if (!mesh_.isInternalFace(faceI)) continue;

            // รับข้อมูลคู่เซลล์
            label own = mesh_.owner()[faceI];
            label nei = mesh_.neighbour()[faceI];

            // เรขาคณิตผิวหน้า
            vector Sf = mesh_.Sf()[faceI];        // เวกเตอร์พื้นที่ผิวหน้า
            scalar d = mag(mesh_.C()[nei] - mesh_.C()[own]);  // ระยะห่างระหว่างเซลล์
            vector dVec = mesh_.C()[nei] - mesh_.C()[own];     // เวกเตอร์ระยะห่าง

            // แทรกค่าไปยังผิวหน้า
            scalar gamma_f = 0.5 * (diffusivity_[own] + diffusivity_[nei]);
            vector U_f = 0.5 * (velocity_[own] + velocity_[nei]);

            // เทอม convection
            scalar F = U_f & Sf;  // ปริมาณค่ามวลผ่านผิวหน้า

            // เทอม diffusion
            scalar D_f = gamma_f * mag(Sf) / d;  // คอนดักแตนซ์การแพร่

            // การแทรกค่า upwind สำหรับ convection
            scalar phi_face = (F > 0) ? phi_[own] : phi_[nei];

            // สัมประสิทธิ์เมทริกซ์
            scalar a_own = D_f - max(F, 0.0);
            scalar a_nei = D_f + max(F, 0.0);

            // อัปเดตสัมประสิทธิ์เมทริกซ์
            diagonal_[own] += D_f + max(F, 0.0);
            diagonal_[nei] += D_f - min(F, 0.0);

            // เพิ่มส่วนส่วนนอกเส้นแทยง
            addMatrixCoefficient(own, nei, -a_nei);
            addMatrixCoefficient(nei, own, -a_own);
        }

        // เพิ่มเทอมต้นทาง
        forAll(sourceTerm_, cellI)
        {
            sourceTerm_[cellI] *= mesh_.V()[cellI];  // คูณด้วยปริมาตรเซลล์
        }
    }
};
```

### อัลกอริทึมการผสานรวมความดัน-ความเร็ว

การผสานรวมความดัน-ความเร็วในการไหลแบบอัดไม่ได้ต้องการอัลกอริทึมที่ซับซ้อนซึ่งพึ่งพาการดำเนินการ `List` อย่างมาก

#### ขั้นตอนอัลกอริทึม PISO

1. **ทำนายความเร็ว**: $\mathbf{u}^* = \mathbf{u}^n + \Delta t \cdot \mathbf{H}(\mathbf{u}^n) - \Delta t \cdot \nabla p^n/\rho$
2. **แก้สมการการแก้ไขความดัน**: $\nabla^2 p' = \rho/\Delta t \cdot \nabla \cdot \mathbf{u}^*$
3. **แก้ไขความดัน**: $p^{n+1} = p^n + p'$
4. **แก้ไขความเร็ว**: $\mathbf{u}^{n+1} = \mathbf{u}^* - \Delta t \cdot \nabla p'/\rho$

## 📊 การวิเคราะห์และการปรับให้เหมาะสมด้านประสิทธิภาพ

### การวิเคราะห์ประสิทธิภาพแคช

ประสิทธิภาพของการดำเนินการ `List` ในการจำลองแบบ CFD ได้รับอิทธิพลอย่างมากจากการใช้แคช การใช้งาน `List` ของ OpenFOAM ได้รับการออกแบบมาเพื่อเพิ่มประสิทธิภาพแคชสูงสุดผ่านการจัดสรรหน่วยความจำต่อเนื่องและรูปแบบการเข้าถึงที่ปรับให้เหมาะสมสำหรับอัลกอริทึมเชิงตัวเลข

#### ความสัมพันธ์ขนาดบล็อกแคช

| ขนาดบล็อค | ความเหมาะสมสำหรับ | ประสิทธิภาพแคช | การใช้งาน |
|-------------|-------------------|----------------|----------|
| 16-32 องค์ประกอบ | เมชเล็ก | สูงมาก | การประมวลผลคู่ |
| 64-128 องค์ประกอบ | เมชขนาดกลาง | สูง | การใช้งานทั่วไป |
| 256+ องค์ประกอบ | เมชใหญ่ | ปานกลาง | การคำนวณเชิงซ้อน |

### การปรับให้เหมาะสมด้านการประมวลผลขนาน

คอนเทนเนอร์ `List` ของ OpenFOAM ผสานรวมกับเฟรมเวิร์กการประมวลผลขนานสำหรับระบบหน่วยความจำแบกระจายได้อย่างราบรื่น

#### ประสิทธิภาพการประมวลผลขนาน

| จำนวนโปรเซสเซอร์ | ประสิทธิภาพ | Overhead | การใช้งานที่เหมาะสม |
|-------------------|-----------|----------|----------------|
| 2-4 | 80-90% | ต่ำ | การจำลองขนาดเล็ก-กลาง |
| 8-16 | 70-85% | ปานกลาง | การจำลองขนาดกลาง |
| 32+ | 50-70% | สูง | การจำลองขนาดใหญ่ |

### การวิเคราะห์การใช้หน่วยความจำ

การทำความเข้าใจรูปแบบการใช้หน่วยความจำเป็นสิ่งจำเป็นสำหรับการปรับใหมาะสมการจำลองแบบ CFD ขนาดใหญ่

#### สถิติการใช้หน่วยความจำ

| การจำลองแบบ | เมช | ปริมาณฟิลด์ | หน่วยความจำ | ประสิทธิภาพ |
|--------------|------|-------------|-----------|-----------|
| Lid-driven cavity | 50×50 | 3-5 | < 100 MB | สูง |
| Backward-facing step | 200×100 | 5-8 | 500 MB - 1 GB | ปานกลาง |
| Turbulent pipe flow | 1000×200 | 8-12 | 2-5 GB | ต่ำ |
| DNS turbulence | 512³ | 10-15 | > 50 GB | ต่ำมาก |

## บทสรุป

คอนเทนเนอร์ `List` ของ OpenFOAM ให้คอนเทนเนอร์อาร์เรย์ไดนามิกที่มีประสิทธิภาพและปลอดภัยสำหรับการจัดเก็บข้อมูล CFD การออกแบบที่ใช้หน่วยความจำต่อเนื่องทำให้มั่นใจได้ว่าประสิทธิภาพสูงสุดในขณะที่ยังคงความง่ายในการใช้งาน ความสามารถที่มีให้อัลกอริทึมต่างๆ ของ OpenFOAM

**ประโยชน์หลัก:**
- **==การจัดการหน่วยความจำอัตโนมัติ==**
- **ประสิทธิภาพการเข้าถึงแบบต่อเนื่อง**
- **ความยืดหยุ่นในการขยายขนาด**
- **การผสานรวมที่ราบรื่นกับระบบฟิล์**

การเข้าใจคอนเทนเนอร์ `List` เป็นสิ่งจำเป็นสำหรับการพัฒนาการแอปพลิเคชัน CFD ที่มีประสิทธิภาพ ทั้งในด้านประสิทธิภาพและความถูกต้อง
