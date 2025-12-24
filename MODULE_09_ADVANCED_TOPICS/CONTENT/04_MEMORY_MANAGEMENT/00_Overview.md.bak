# 03. คอนเทนเนอร์และการจัดการหน่วยความจำใน OpenFOAM

## 3.1 สถาปัตยกรรมการจัดการหน่วยความจำ

OpenFOAM ใช้ระบบการจัดการหน่วยความจำที่ซับซ้อนซึ่งสร้างขึ้นจาก smart pointer แบบ reference-counted และรูปแบบ object registry pattern การออกแบบนี้ช่วยให้การลบหน่วยความจำเกิดขึ้นโดยอัตโนมัติ ป้องกันการรั่วไหลของหน่วยความจำ และให้การจัดการวงจรชีวิตของออบเจกต์อย่างมีประสิทธิภาพในการจำลอง CFD ที่ซับซ้อน

### 3.1.1 ลำดับชั้นของ Smart Pointer

การจัดการหน่วยความจำของ OpenFOAM มีศูนย์กลางอยู่ที่ smart pointer 3 ประเภทหลัก:

#### `autoPtr<T>` - การถือครองเฉพาะ (Exclusive Ownership)
`autoPtr` ให้ semantic ของการถือครองเฉพาะเหมือนกับ `std::unique_ptr` ใน C++ สมัยใหม่:

```cpp
// การสร้างและการเริ่มต้น
autoPtr<fvMesh> meshPtr(new fvMesh(io));

// วิธีการเข้าถึง
fvMesh& mesh = meshPtr();           // ตัวดำเนินการ dereference
fvMesh* meshPtr = meshPtr.ptr();    // การเข้าถึง raw pointer

// การโอนกรรมสิทธิ์
autoPtr<fvMesh> transferredMesh = meshPtr.transfer();
```

**ลักษณะสำคัญ:**
- การถือครองเฉพาะ - มีเพียง `autoPtr` เดียวที่สามารถถือครองออบเจกต์ได้
- การทำลายโดยอัตโนมัติเมื่อ pointer ออกจาก scope
- การโอนกรรมสิทธิ์ผ่าน method `transfer()`
- ไม่สามารถคัดลอกได้ แต่สามารถย้ายได้เท่านั้น

#### `tmp<T>` - ออบเจกต์ชั่วคราวแบบ Reference-Counted
คลาส `tmp` ใช้การแชร์แบบ reference-counted สำหรับออบเจกต์ชั่วคราว:

```cpp
// การสร้างฟิลด์ชั่วคราว
tmp<volScalarField> tRho = rho;  // สร้างสำเนาแบบ reference-counted
tmp<volScalarField> tNewRho(new volScalarField(mesh));

// การเข้าถึงและการล้างข้อมูลโดยอัตโนมัติ
volScalarField& rhoField = tNewRho();  // การเข้าถึงแบบ reference
if (tNewRho.isTmp()) {               // ตรวจสอบว่าเป็นชั่วคราวหรือไม่
    // จะถูกลบโดยอัตโนมัติเมื่อ tNewRho ออกจาก scope
}
```

**กลไกการนับ reference:**
```cpp
// การนับ reference ภายใน
class tmp<T> {
private:
    T* ptr_;
    mutable bool refCount_;

public:
    tmp(const tmp<T>& t) : ptr_(t.ptr_), refCount_(true) {
        if (ptr_) ptr_->refCount++;
    }

    ~tmp() {
        if (ptr_ && refCount_ && --ptr_->refCount == 0) {
            delete ptr_;
        }
    }
};
```

#### `refPtr<T>` - การนับ Reference สมัยใหม่
เปิดตัวใน OpenFOAM-10, `refPtr` ให้การนับ reference ที่ดีขึ้น:

```cpp
// Modern reference-counted pointer
refPtr<dictionary> dictPtr(new dictionary);

// Copy semantics พร้อมการนับ reference
refPtr<dictionary> dictCopy = dictPtr;  // เพิ่ม reference count

// การล้างข้อมูลโดยอัตโนมัติ
// ออบเจกต์ถูกลบเมื่อ refPtr ตัวสุดท้ายออกจาก scope
```

### 3.1.2 ระบบ Object Registry

Object registry ให้การจัดการออบเจกต์แบบรวมศูนย์พร้อมการล้างข้อมูลโดยอัตโนมัติ:

```cpp
// ลำดับชั้นของ registry
class objectRegistry : public regIOobject {
private:
    HashTable<regIOobject*> objectRegistry_;

public:
    // การลงทะเบียนและการค้นหาออบเจกต์
    template<class Type>
    bool foundObject(const word& name) const;

    template<class Type>
    Type& lookupObject(const word& name) const;

    template<class Type>
    Type& lookupObjectRef(const word& name);

    void addObject(regIOobject* obj);
    void removeObject(const word& name);
};
```

**การใช้งานในบริบทของ solver:**
```cpp
// ใน constructor ของ solver
class mySolver : public fvMesh {
    objectRegistry& objectRegistry_;

public:
    mySolver(const IOobject& io)
    : fvMesh(io),
      objectRegistry_(this->objectRegistry()) {

        // ลงทะเบียนฟิลด์แบบกำหนดเอง
        volScalarField::New
        (
            "customField",
            *this,
            dimensionedScalar("zero", dimless, 0.0)
        );
    }
};
```

## 3.2 คลาสคอนเทนเนอร์และโครงสร้างข้อมูล

OpenFOAM ให้คอนเทนเนอร์เฉพาะที่ถูกปรับให้เหมาะสำหรับการดำเนินการ CFD และการคำนวณแบบ mesh-based

### 3.2.1 คอนเทนเนอร์ฟิลด์แบบไดนามิก

#### `Field<T>` - อาร์เรย์แบบไดนามิกทั่วไป
```cpp
// ฟิลด์แบบไดนามิกสำหรับข้อมูลประเภทต่างๆ
Field<scalar> pressureField(1000);           // 1000 ค่า scalar
Field<vector> velocityField(nCells);         // ฟิลด์เวกเตอร์ต่อเซลล์
Field<tensor> stressTensor(nInternalFaces);  // ฟิลด์เทนเซอร์ต่อหน้า

// การดำเนินการแบบไดนามิก
pressureField.resize(2000);           // ปรับขนาดพร้อมการรักษาข้อมูล
pressureField.append(101.325);        // เพิ่มค่า
pressureField.setSize(500);           // กำหนดขนาดใหม่

// การดำเนินการทางคณิตศาสตร์
Field<scalar> squared = pow(pressureField, 2.0);
scalar meanPressure = average(pressureField);
```

#### `List<T>` - อาร์เรย์ขนาดคงที่
```cpp
// รายการขนาดคงที่พร้อมการกำหนดขนาดเวลาคอมไพล์
List<label> cellNeighbours(6);           // เพื่อนบ้านของเซลล์หกเหลี่ยม
List<word> boundaryNames(nBoundaries);  // ชื่อของ patch ขอบเขต

// การเริ่มต้น
List<scalar> initialValues(10, 0.0);    // เริ่มต้นด้วยค่าเริ่มต้น
List<vector> zeroVectors(nCells, vector::zero);

// การเข้าถึงและการแก้ไข
forAll(cellNeighbours, i) {
    cellNeighbours[i] = mesh.cellCells()[cellI][i];
}
```

#### `DynamicList<T>` - คอนเทนเนอร์แบบไดนามิกที่มีประสิทธิภาพ
```cpp
// รายการแบบไดนามิกที่มีประสิทธิภาพพร้อมการจัดการความจุอัตโนมัติ
DynamicList<label> cellFaces;  // เริ่มว่าง ขยายตามความจำเป็น

// การสร้างคอลเลกชัน
forAll(cells, cellI) {
    const labelList& faces = mesh.cells()[cellI];
    cellFaces.append(faces);  // การเพิ่มแบบ bulk ที่มีประสิทธิภาพ
}

// การจัดการความจุ
cellFaces.setCapacity(cellFaces.size() * 2);  // การจัดสรรล่วงหน้า
cellFaces.shrink();                           // ปล่อยหน่วยความจำที่ไม่ได้ใช้
```

### 3.2.2 คอนเทนเนอร์เฉพาะสำหรับ Mesh

#### `faceList`, `cellList`, `pointField`
```cpp
// คอนเทนเนอร์โทโพโลยีของ mesh
faceList allFaces = mesh.faces();      // หน้าทั้งหมดของ mesh
cellList allCells = mesh.cells();      // เซลล์ทั้งหมดของ mesh
pointField allPoints = mesh.points();  // จุดทั้งหมดของ mesh

// การดำเนินการเข้าถึง
const face& f = allFaces[faceI];       // รับหน้าที่ระบุ
const labelList& cellFaces = allCells[cellI];  // รายการหน้าของเซลล์

// รูปแบบการวนซ้ำ
forAll(allFaces, faceI) {
    const face& f = allFaces[faceI];
    const pointField& facePoints = f.points(allPoints);
    vector faceNormal = f.normal(allPoints);
}
```

#### `UList<T>` - อินเตอร์เฟซรายการสากล
```cpp
// อินเตอร์เฟซสากลสำหรับคอนเทนเนอร์แบบอาร์เรย์
template<class T>
class UList {
protected:
    T* v_;
    label size_;

public:
    // การเข้าถึงโดยตรง
    T& operator[](const label i) { return v_[i]; }
    const T& operator[](const label i) const { return v_[i]; }

    // การเข้าถึงช่วง
    T* begin() { return v_; }
    T* end() { return v_ + size_; }

    // ข้อมูลขนาด
    label size() const { return size_; }
    bool empty() const { return size_ == 0; }
};
```

### 3.2.3 Hash Tables และ Dictionaries

#### `HashTable<Key, T>` - การจัดเก็บ Key-Value ที่มีประสิทธิภาพ
```cpp
// Hash table สำหรับการค้นหาแบบ key-based ที่รวดเร็ว
HashTable<word, label> patchTypeMap;
HashTable<scalar, word> propertyMap;

// การแทรกและการค้นหา
patchTypeMap.insert("wall", 0);
patchTypeMap.insert("inlet", 1);
patchTypeMap.insert("outlet", 2);

if (patchTypeMap.found("wall")) {
    label wallIndex = patchTypeMap["wall"];
}

// การวนซ้ำ
forAllConstIter(HashTable<word, label>, patchTypeMap, iter) {
    Info << "Patch: " << iter.key()
         << ", Index: " << iter.val() << endl;
}
```

#### `dictionary` - การจัดเก็บคอนฟิกูเรชันแบบลำดับชั้น
```cpp
// พจนานุกรมลำดับชั้นสำหรับคอนฟิกูเรชัน
dictionary transportProperties;

// การเพิ่มรายการ
transportProperties.add("nu", dimensionedScalar("nu", dimViscosity, 1e-6));
transportProperties.add("rho", dimensionedScalar("rho", dimDensity, 1000.0));

// Sub-dictionaries
dictionary turbulenceModel;
turbulenceModel.add("type", word("kEpsilon"));
turbulenceModel.add("Cmu", 0.09);
transportProperties.add("turbulence", turbulenceModel);

// การดำเนินการค้นหา
dimensionedScalar nu = transportProperties.lookup<dimensionedScalar>("nu");
word turbType = transportProperties.subDict("turbulence").lookup<word>("type");
```

## 3.3 เทคนิคการเพิ่มประสิทธิภาพหน่วยความจำ

### 3.3.1 Expression Templates และ Lazy Evaluation

OpenFOAM ใช้ expression templates เพื่อหลีกเลี่ยงการสร้างออบเจกต์ชั่วคราว:

```cpp
// ไม่มี expression templates (ไม่มีประสิทธิภาพ)
volScalarField temp1 = phi * rho;           // สร้างตัวชั่วคราว
volScalarField temp2 = temp1 * U.component(0);  // สร้างอีกตัวชั่วคราวหนึ่ง
divPhiRhoU = fvc::div(temp2);              // ใช้ผลลัพธ์

// มี expression templates (มีประสิทธิภาพ)
divPhiRhoU = fvc::div(phi * rho * U.component(0));  // ผ่านเดียว, ไม่มีตัวชั่วคราว
```

**การ implement expression template:**
```cpp
template<class Type1, class Type2>
class multiplyOp {
private:
    const Type1& f1_;
    const Type2& f2_;

public:
    multiplyOp(const Type1& f1, const Type2& f2)
    : f1_(f1), f2_(f2) {}

    // การเข้าถึงแบบ element-wise โดยไม่มีการจัดเก็บชั่วคราว
    typename Type1::value_type operator[](const label i) const {
        return f1_[i] * f2_[i];
    }
};
```

### 3.3.2 การจัดการ Reference ของฟิลด์

การเพิ่มประสิทธิภาพการอ้างอิงฟิลด์เพื่อลดการคัดลอก:

```cpp
// รูปแบบการเข้าถึงฟิลด์ที่มีประสิทธิภาพ
void calculateMomentumFlux
(
    const surfaceScalarField& phi,  // Reference เพื่อหลีกเลี่ยงการคัดลอก
    const volVectorField& U,        // Const reference สำหรับการเข้าถึงแบบอ่านอย่างเดียว
    surfaceVectorField& momentumFlux // Reference สำหรับ output
) {
    // การดำเนินการฟิลด์โดยตรง
    momentumFlux = phi * fvc::interpolate(U);
}
```

**กลยุทธ์การจัดการ reference:**
```cpp
// การเพิ่มประสิทธิภาพ tmp สำหรับการคำนวณชั่วคราว
tmp<volScalarField> calculateTKE
(
    const volVectorField& U
) {
    return tmp<volScalarField>
    (
        new volScalarField
        (
            0.5 * magSqr(U)  // การประเมิน expression template
        )
    );
}

// การใช้งานพร้อมการล้างข้อมูลอัตโนมัติ
tmp<volScalarField> tke = calculateTKE(U);
volScalarField& TKE = tke();  // การเข้าถึงแบบ reference
// tke ถูกล้างโดยอัตโนมัติเมื่อออกจาก scope
```

### 3.3.3 การจัดการ Memory Pool

OpenFOAM ใช้ memory pooling สำหรับออบเจกต์ที่จัดสรรบ่อย:

```cpp
// Memory pool สำหรับออบเจกต์ชั่วคราว
class memInfo {
private:
    static DynamicList<void*> memoryPool_;
    static label poolSize_;

public:
    static void* allocate(size_t size);
    static void deallocate(void* ptr);
    static void clearPool();

    static label poolSize() { return poolSize_; }
};
```

**รูปแบบการจัดสรร pool:**
```cpp
// การจัดสรรที่มีประสิทธิภาพสำหรับออบเจกต์เล็ก
template<class T>
class pooledObject {
private:
    static MemoryPool<T> pool_;

public:
    void* operator new(size_t size) {
        return pool_.allocate();
    }

    void operator delete(void* ptr) {
        pool_.deallocate(ptr);
    }
};
```

## 3.4 รูปแบบการจัดการหน่วยความจำขั้นสูง

### 3.4.1 การนับ Reference กับ `refCount`

คลาสฐานสำหรับออบเจกต์ที่มีการนับ reference:

```cpp
class refCount {
private:
    mutable int refCount_;

public:
    refCount() : refCount_(0) {}
    virtual ~refCount() {}

    void ref() const { refCount_++; }
    bool unref() const { return --refCount_ == 0; }
    int count() const { return refCount_; }

    bool unique() const { return refCount_ == 1; }
};
```

**การ implement ในคลาสฟิลด์:**
```cpp
template<class Type>
class GeometricField : public refCount {
private:
    // ข้อมูลฟิลด์และการอ้างอิง mesh
    Field<Type> internalField_;
    const fvMesh& mesh_;

public:
    // วิธีการนับ reference
    void operator=(const GeometricField& gf) {
        if (this != &gf) {
            internalField_ = gf.internalField_;
            mesh_ = gf.mesh_;
        }
    }

    // การคัดลอกอย่างปลอดภัยพร้อมการนับ reference
    tmp<GeometricField<Type>> clone() const {
        return tmp<GeometricField<Type>>
        (
            new GeometricField<Type>(*this)
        );
    }
};
```

### 3.4.2 การจัดการหน่วยความจำอัตโนมัติใน Solvers

สถาปัตยกรรม solver ที่แสดงการจัดการหน่วยความจำ:

```cpp
class simpleFoam : public fvMesh {
private:
    // สมาชิก smart pointer สำหรับการล้างข้อมูลอัตโนมัติ
    autoPtr<incompressible::turbulenceModel> turbulence_;
    autoPtr<volScalarField> p_;
    autoPtr<volVectorField> U_;
    autoPtr<surfaceScalarField> phi_;

    // ฟิลด์ชั่วคราวแบบ reference-counted
    tmp<surfaceScalarField> rAUf_;
    tmp<volScalarField> rAU_;

public:
    simpleFoam(const IOobject& io)
    : fvMesh(io) {

        // เริ่มต้นฟิลด์ด้วยการจัดการหน่วยความจำอัตโนมัติ
        p_.reset
        (
            new volScalarField
            (
                IOobject("p", *this, IOobject::MUST_READ),
                *this
            )
        );

        U_.reset
        (
            new volVectorField
            (
                IOobject("U", *this, IOobject::MUST_READ),
                *this
            )
        );

        // โมเดลความปั่นป่วนพร้อม smart pointer
        turbulence_ = incompressible::turbulenceModel::New("turbulence", *this, *U_, *p_);
    }

    ~simpleFoam() {
        // การล้างข้อมูลอัตโนมัติผ่าน smart pointers
        // ไม่จำเป็นต้องลบด้วยตนเอง
    }

    void solve() {
        // สร้างฟิลด์ชั่วคราวพร้อมการล้างข้อมูลอัตโนมัติ
        tmp<volScalarField> rAU = 1.0 / UEqn().A();
        tmp<volVectorField> UHbyA = U_*rAU();

        // ใช้ตัวชั่วคราว - ถูกล้างโดยอัตโนมัติ
        adjustPhi(phiHbyA(), U_, p_);

        // สมการความดัน
        fvScalarMatrix pEqn
        (
            fvm::laplacian(rAU(), p_) == fvc::div(phiHbyA)
        );

        pEqn.solve();

        // การแก้ไขความเร็ว
        U_ -= rAU()*fvc::grad(p_);
    }
};
```

### 3.4.3 การประมวลผลแบบขนานที่ประหยัดหน่วยความจำ

การจัดการหน่วยความจำแบบกระจายสำหรับการประมวลผลแบบขนาน:

```cpp
// การกระจายฟิลด์แบบขนาน
template<class Type>
class distributedField {
private:
    Field<Type> localField_;
    List<List<Type>> processorFields_;

public:
    // การดำเนินการ gather
    void gather(const labelList& procIDs) {
        processorFields_.setSize(procIDs.size());

        forAll(procIDs, i) {
            if (procIDs[i] == Pstream::myProcNo()) {
                processorFields_[i] = localField_;
            } else {
                // รับจาก processor อื่น
                IPstream fromProc(procIDs[i]);
                fromProc >> processorFields_[i];
            }
        }
    }

    // การดำเนินการ scatter
    void scatter(const labelList& procIDs) {
        forAll(procIDs, i) {
            if (procIDs[i] != Pstream::myProcNo()) {
                // ส่งไปยัง processor อื่น
                OPstream toProc(procIDs[i]);
                toProc << processorFields_[i];
            } else {
                localField_ = processorFields_[i];
            }
        }
    }
};
```

## 3.5 การพิจารณาด้านประสิทธิภาพและแนวทางปฏิบัติที่ดีที่สุด

### 3.5.1 รูปแบบการเข้าถึงหน่วยความจำ

**โครงสร้างข้อมูลที่เป็นมิตรกับแคช:**
```cpp
// Structure of Arrays (SoA) สำหรับการใช้แคชที่ดีขึ้น
class particleContainer {
private:
    DynamicList<scalar> x_, y_, z_;        // ส่วนประกอบตำแหน่ง
    DynamicList<vector> U_;                // เวกเตอร์ความเร็ว
    DynamicList<scalar> diameter_;         // เส้นผ่านศูนย์กลางของอนุภาค
    DynamicList<label> cellID_;            // ID ของเซลล์

public:
    // รูปแบบการเข้าถึงหน่วยความจำแบบต่อเนื่อง
    void updatePositions(const scalar deltaT) {
        forAll(x_, i) {
            x_[i] += U_[i].x() * deltaT;
            y_[i] += U_[i].y() * deltaT;
            z_[i] += U_[i].z() * deltaT;
        }
    }
};
```

**กลยุทธ์การ prefetch หน่วยความจำ:**
```cpp
// Prefetch บรรทัดแคชถัดไป
void computeGradients
(
    const volScalarField& field,
    volVectorField& gradField
) {
    const scalarField& fieldInternal = field.internalField();
    vectorField& gradInternal = gradField.internalField();

    for (label cellI = 0; cellI < fieldInternal.size(); cellI++) {
        // Prefetch ข้อมูลเซลล์ถัดไป
        if (cellI + 1 < fieldInternal.size()) {
            __builtin_prefetch(&fieldInternal[cellI + 1], 0, 3);
        }

        // การคำนวณ
        gradInternal[cellI] = fvc::grad(field)[cellI];
    }
};
```

### 3.5.2 การเพิ่มประสิทธิภาพการใช้หน่วยความจำ

**การนำกลับและการรีไซเคิลฟิลด์:**
```cpp
class fieldManager {
private:
    // ฟิลด์ชั่วคราวที่ใช้ซ้ำได้
    mutable tmp<volScalarField> tempScalarField_;
    mutable tmp<volVectorField> tempVectorField_;

public:
    tmp<volScalarField> getTempScalarField(const fvMesh& mesh) {
        if (!tempScalarField_.valid()) {
            tempScalarField_ = tmp<volScalarField>
            (
                new volScalarField
                (
                    IOobject("tempScalar", mesh),
                    mesh,
                    dimensionedScalar("zero", dimless, 0.0)
                )
            );
        }
        return tempScalarField_;
    }

    // การล้างฟิลด์ชั่วคราว
    void clearTempFields() {
        tempScalarField_.clear();
        tempVectorField_.clear();
    }
};
```

**การจัดการเงื่อนไขขอบเขตที่ประหยัดหน่วยความจำ:**
```cpp
// Lazy evaluation สำหรับเงื่อนไขขอบเขต
class lazyBoundaryField {
private:
    mutable List<scalar> cachedValues_;
    mutable bool upToDate_;

public:
    const scalarField& values() const {
        if (!upToDate_) {
            calculateValues();
            upToDate_ = true;
        }
        return cachedValues_;
    }

    void updateCoeffs() {
        upToDate_ = false;  // Invalidate cache
    }

private:
    void calculateValues() const {
        cachedValues_.setSize(patch().size());
        // คำนวณค่าเมื่อจำเป็นเท่านั้น
        forAll(cachedValues_, faceI) {
            cachedValues_[faceI] = calculateValue(faceI);
        }
    }
};
```

## 3.6 การดีบักและการวิเคราะห์หน่วยความจำ

### 3.6.1 การตรวจจับการรั่วไหลของหน่วยความจำ

OpenFOAM ให้การติดตามหน่วยความจำในตัว:

```cpp
// Macros สำหรับการติดตามหน่วยความจำ
#define DeclareMemStack(name) \
    static label memStack_##name = 0

#define IncMemStack(name, size) \
    memStack_##name += size

#define DecMemStack(name, size) \
    memStack_##name -= size

#define PrintMemStack(name) \
    Info << "Memory stack " << #name << ": " << memStack_##name << endl
```

**การใช้งานในการดำเนินการฟิลด์:**
```cpp
class memoryTrackedField {
private:
    DeclareMemStack(fieldData);

public:
    memoryTrackedField(label size) {
        IncMemStack(fieldData, size * sizeof(scalar));
        fieldData_.setSize(size);
    }

    ~memoryTrackedField() {
        DecMemStack(fieldData, fieldData_.size() * sizeof(scalar));
    }

    void resize(label newSize) {
        DecMemStack(fieldData, fieldData_.size() * sizeof(scalar));
        fieldData_.setSize(newSize);
        IncMemStack(fieldData, newSize * sizeof(scalar));
    }
};
```

### 3.6.2 การวิเคราะห์ประสิทธิภาพ

เครื่องมือวิเคราะห์ประสิทธิภาพหน่วยความจำ:

```cpp
// คลาส memory profiler
class memoryProfiler {
private:
    clock_t startTime_;
    label allocatedBytes_;
    label deallocatedBytes_;

public:
    void startProfiling() {
        startTime_ = clock();
        allocatedBytes_ = 0;
        deallocatedBytes_ = 0;
    }

    void recordAllocation(label bytes) {
        allocatedBytes_ += bytes;
    }

    void recordDeallocation(label bytes) {
        deallocatedBytes_ += bytes;
    }

    void report() const {
        clock_t endTime = clock();
        scalar cpuTime = scalar(endTime - startTime_) / CLOCKS_PER_SEC;

        Info << "Memory Profile:" << nl
             << "  CPU Time: " << cpuTime << " s" << nl
             << "  Allocated: " << allocatedBytes_ << " bytes" << nl
             << "  Deallocated: " << deallocatedBytes_ << " bytes" << nl
             << "  Net Memory: " << (allocatedBytes_ - deallocatedBytes_) << " bytes" << nl
             << "  Allocation Rate: " << allocatedBytes_/cpuTime << " bytes/s" << endl;
    }
};
```

### 3.6.3 ปัญหาหน่วยความจำทั่วไปและวิธีแก้ไข

**ปัญหา 1: การอ้างอิงแบบวงจร (Cyclic References)**
```cpp
// ปัญหา: การอ้างอิงแบบวงจรที่ป้องกันการลบ
class fieldA;
class fieldB;

class fieldA {
    refPtr<fieldB> bField_;  // สร้างวงจร
};

class fieldB {
    refPtr<fieldA> aField_;  // สร้างวงจร
};

// วิธีแก้ไข: ใช้ weak references หรือการหยุดแบบแมนนวล
class fieldA {
    refPtr<fieldB> bField_;

    ~fieldA() {
        if (bField_.valid()) {
            bField_->breakReference();  // หยุดวงจร
        }
    }
};
```

**ปัญหา 2: การสร้างตัวชั่วคราวมากเกินไป**
```cpp
// ปัญหา: หลายออบเจกต์ชั่วคราว
volScalarField temp1 = mag(U);
volScalarField temp2 = pow(temp1, 2.0);
volScalarField TKE = 0.5 * temp2;

// วิธีแก้ไข: Expression templates
volScalarField TKE = 0.5 * magSqr(U);  // ไม่มีตัวชั่วคราว
```

**ปัญหา 3: การแบ่งส่วนหน่วยความจำ (Memory Fragmentation)**
```cpp
// ปัญหา: การจัดสรรที่แตกส่วน
List<autoPtr<particle>> particles;
for (label i = 0; i < 10000; i++) {
    particles.append(new particle());  // หน่วยความจำแตกส่วน
}

// วิธีแก้ไข: Memory pool หรือการจัดสรรแบบ bulk
particlePool pool(10000);
List<particle*> particles = pool.allocateAll();
```

เอกสารฉบับสมบูรณ์นี้ครอบคลุมคลาสคอนเทนเนอร์และระบบการจัดการหน่วยความจำของ OpenFOAM โดยให้ตัวอย่างที่ใช้งานได้จริงและแนวทางปฏิบัติที่ดีที่สุดสำหรับการใช้หน่วยความจำอย่างมีประสิทธิภาพในแอปพลิเคชัน CFD
