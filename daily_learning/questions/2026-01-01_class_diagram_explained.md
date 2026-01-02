---
source: daily_learning/2026-01-01.md
section: "2. OpenFOAM Class Hierarchy & Implementation"
date_asked: 2026-01-02
tags: [openfoam, oop, class-diagram, design-patterns]
---

# หลักการออกแบบ Class Hierarchy ใน OpenFOAM

> [!INFO] **แหล่งที่มา (Source)**
> เนื้อหานี้อธิบาย Class Diagram จาก Section 2.1 ของเอกสาร "Governing Equations - HARDCORE Level - 2026-01-01"

---

## ภาพรวม Class Hierarchy

Class Hierarchy ใน OpenFOAM ถูกออกแบบตามหลักการ OOP หลายประการ โดยมีเป้าหมายเพื่อ:

1. **Code Reusability** - การใช้โค้ดซ้ำผ่าน Inheritance
2. **Type Safety** - การรักษาความปลอดภัยของชนิดข้อมูลด้วย Templates
3. **Polymorphism** - การทำงานแบบ Polymorphic ผ่าน Virtual Functions
4. **Memory Efficiency** - การจัดการหน่วยความจำด้วย Smart Pointers

---

## 1. GeometricField<T, GeoMesh> - Base Class Template

### 1.1 Parent/Child Class

```
GeometricField<Type, GeoMesh>
├── volScalarField (Type=scalar, GeoMesh=fvMesh)
├── volVectorField (Type=vector, GeoMesh=fvMesh)
└── surfaceScalarField (Type=scalar, GeoMesh=pointMesh)
```

**หลักการ OOP:**

#### Template-based Design

Template = **"แบบพิมพ์"** ที่ยังไม่ระบุว่าจะใส่ข้อมูลชนิดใด:

```cpp
template<class Type>   // ← Type คือช่องว่างที่จะเติม
class GeometricField {
    Type internalField_;   // ← ยังไม่รู้ว่าเป็นอะไร (scalar? vector?)
};

// เมื่อใช้งานจริง:
GeometricField<scalar>   // ← เติม Type = scalar → เก็บตัวเลขเดียว
GeometricField<vector>   // ← เติม Type = vector → เก็บ (x, y, z)
```

#### Specialization

Specialization = **"ตั้งชื่อเล่น"** ให้กับ Template ที่เติมค่าแล้ว:

```cpp
// ไม่มี Specialization (ยาว):
GeometricField<scalar, fvPatchField, volMesh> p;

// มี Specialization (สั้น):
typedef GeometricField<scalar, fvPatchField, volMesh> volScalarField;

// ใช้งาน:
volScalarField p;  // เข้าใจง่าย!
```

| Template (แบบพิมพ์) | Specialization (ชื่อเล่น) | ใช้งานจริง |
|---------------------|--------------------------|------------|
| `GeometricField<scalar, ...>` | `volScalarField` | ความดัน p, อุณหภูมิ T |
| `GeometricField<vector, ...>` | `volVectorField` | ความเร็ว U |

### 1.2 Member Variables

```cpp
// Internal field values (cell-centered)
DimensionedField<Type, GeoMesh> internalField_;

// Boundary field values
FieldField<GeoMesh, Type> boundaryField_;

// Previous iteration (for under-relaxation)
DimensionedField<Type, GeoMesh> prevIter_;
```

**หลักการ OOP:**

#### Composition vs Inheritance

| หลักการ | ความหมาย | ตัวอย่าง |
|---------|----------|----------|
| **Inheritance** | A **เป็น** B (is-a) | `volScalarField` **เป็น** `GeometricField` |
| **Composition** | A **มี** B (has-a) | `GeometricField` **มี** `internalField_` |

```cpp
// ❌ Inheritance (ไม่เหมาะ): GeometricField "เป็น" DimensionedField?
class GeometricField : public DimensionedField { };

// ✅ Composition (เหมาะสม): GeometricField "มี" DimensionedField
class GeometricField {
    DimensionedField internalField_;   // มี internal data
    FieldField boundaryField_;         // มี boundary data
};
```

> 💡 **กฎง่าย:** ถ้า "A เป็น B" → Inheritance | ถ้า "A มี B" → Composition

#### Encapsulation

ข้อมูลถูกจัดเก็บเป็น private และเข้าถึงผ่าน Public Interface

### 1.3 Important Methods

```cpp
// Access dimensions
const dimensionSet& dimensions() const;

// Update boundary conditions
void correctBoundaryConditions();

// Field operations
tmp<GeometricField> operator+(const GeometricField&) const;
tmp<GeometricField> operator-(const GeometricField&) const;
```

**หลักการ OOP:**
- **Operator Overloading**: โหลด Operator ทางคณิตศาสตร์ให้ทำงานกับ Field Objects
- **Const Correctness**: แยก Methods ที่อ่านอย่างเดียว (const) จากที่แก้ไขข้อมูล

---

## 2. fvMatrix<T> - Matrix Assembly Class

### 2.1 Parent/Child Class

```
lduMatrix (Base sparse matrix)
    └── fvMatrix<Type>
            ├── fvScalarMatrix (Type=scalar)
            └── fvVectorMatrix (Type=vector)
```

**หลักการ OOP:**
- **Inheritance**: สืบทอดจาก `lduMatrix` ซึ่งเป็น Lower-Diagonal-Upper sparse matrix format
- **Template Specialization**: เพิ่ม Functionality เฉพาะสำหรับ Scalar และ Vector

### 2.2 Member Variables

```cpp
// Reference to field being solved
GeometricField<Type, fvPatchField, volMesh>& psi_;

// Source term vector
Field<Field<Type>> source_;

// Boundary coefficients
FieldField<fvPatchField, Type>& boundaryCoeffs_;
```

**หลักการ OOP:**
- **Reference Semantics**: เก็บ Reference แทน Copy เพื่อประหยัดหน่วยความจำ
- **Association**: มีความสัมพันธ์กับ GeometricField ผ่าน Reference

### 2.3 Important Methods

```cpp
// Solve the linear system
tmp<GeometricField<Type, fvPatchField, volMesh>> solve();

// Get residual
scalar residual() const;

// Matrix operations
fvMatrix& operator+=(const fvMatrix&);
fvMatrix& operator==(const fvMatrix&);
```

**หลักการ OOP:**
- **Fluent Interface**: ใช้ Operator Overloading (`==`) สำหรับสมการ
- **Return Type Optimization**: ใช้ `tmp<>` Smart Pointer สำหรับ Return Values

---

## 3. tmp<T> - Smart Pointer Pattern

### 3.1 Parent/Child Class

```
tmp<T> (Smart Pointer Wrapper)
    └── manages GeometricField, fvMatrix, etc.
```

**หลักการ OOP:**
- **RAII (Resource Acquisition Is Initialization)**: จัดการหน่วยความจำอัตโนมัติ
- **Reference Counting**: นับจำนวน References และลบ Object เมื่อเป็น 0

### 3.2 Member Variables

```cpp
T* ptr_;  // Raw pointer to managed object
```

### 3.3 Important Methods

```cpp
// Dereference operator
T& operator()();

// Clear pointer
void clear();

// Transfer ownership
tmp<T> operator=(const tmp<T>&);
```

**หลักการ OOP:**
- **Smart Pointer Pattern**: คล้าย `std::unique_ptr` แต่มี Reference Counting
- **Automatic Memory Management**: ป้องกัน Memory Leaks และ Dangling Pointers

---

## 4. fvMesh - Mesh Data Container

### 4.1 Parent/Child Class

```
polyMesh (Base topology)
    └── fvMesh (Finite Volume data)
```

**หลักการ OOP:**
- **Layered Architecture**: แยก Topology (polyMesh) จาก FV-specific Data (fvMesh)
- **Single Responsibility**: แต่ละคลาสมีหน้าที่ชัดเจน

### 4.2 Member Variables

```cpp
// Cell centers
volVectorField C_;

// Face area vectors
surfaceVectorField Sf_;

// Cell volumes
volScalarField V_;
```

**หลักการ OOP:**
- **Data Encapsulation**: ข้อมูลเมชถูกจัดเก็บเป็น Field Objects
- **Lazy Evaluation**: คำนวณค่าเมื่อจำเป็นและ Cache ไว้

### 4.3 Important Methods

```cpp
// Access cell centers
const volVectorField& C() const;

// Access face areas
const surfaceVectorField& Sf() const;

// Access cell volumes
const volScalarField& V() const;
```

---

## 5. Design Patterns ที่ใช้ใน OpenFOAM

### 5.1 Template Method Pattern

**ตำแหน่ง:** `GeometricField`, `fvMatrix`

**คำอธิบาย:**
- กำหนด Skeleton ของ Algorithm ใน Base Class
- ให้ Derived Classes  Implement เฉพาะส่วนที่ต่างกัน

**ตัวอย่าง:**
```cpp
// Base class defines interface
template<class Type>
class GeometricField {
    virtual void correctBoundaryConditions() = 0;
};

// Derived class implements specifics
class volScalarField : public GeometricField<scalar> {
    void correctBoundaryConditions() override {
        // Scalar-specific BC handling
    }
};
```

### 5.2 Smart Pointer Pattern (tmp<T>)

**ตำแหน่ง:** ทั่วทั้ง OpenFOAM

**คำอธิบาย:**
- ใช้ `tmp<T>` แทน Raw Pointers
- Automatic Reference Counting และ Memory Management

**ข้อดี:**
- ป้องกัน Memory Leaks
- ลด Overhead ของ Copying Large Objects
- Thread-safe (ในบางกรณี)

### 5.3 Factory Pattern

**ตำแหน่ง:** Boundary Conditions (`fvPatchField`)

**คำอธิบาย:**
- สร้าง Objects จาก Dictionary Data
- Runtime Selection ของ BC Types

**ตัวอย่าง:**
```cpp
// Factory creates BC from dictionary
auto* bc = fvPatchField<scalar>::New(patch, fieldDict).ptr();
```

### 5.4 Strategy Pattern

**ตำแหน่ง:** Discretization Schemes (`fvm::`, `fvc::`)

**คำอธิบาย:**
- แทนที่ Algorithm ด้วย Runtime Selection
- ใช้ Dictionary สำหรับเลือก Scheme

**ตัวอย่าง:**
```cpp
// Strategy selected at runtime
divSchemes {
    div(phi,U)  Gauss limitedLinear 1;  // Strategy 1
    div(phi,k)  Gauss upwind;           // Strategy 2
}
```

### 5.5 Composite Pattern

**ตำแหน่ง:** `GeometricField` = Internal + Boundary

**คำอธิบาย:**
- จัดการ Hierarchical Data Structures
- Internal Field + Boundary Fields = Complete Field

**ตัวอย่าง:**
```cpp
GeometricField = DimensionedField (internal) 
               + FieldField (boundary patches)
```

---

## 6. สรุปหลักการ OOP ใน OpenFOAM

| หลักการ (Principle) | การนำไปใช้ (Application) | ประโยชน์ (Benefit) |
|-------------------|---------------------|-----------------|
| **Encapsulation** | Private data, Public interface | ซ่อนความซับซ้อน, ลด Coupling |
| **Inheritance** | Base classes → Specialized classes | Code Reuse, Type Safety |
| **Polymorphism** | Virtual functions, Templates | Flexible Algorithms |
| **Composition** | Fields contain Fields, Mesh contains Fields | Modular Design |
| **RAII** | `tmp<>` Smart Pointer | Automatic Memory Management |
| **Operator Overloading** | Mathematical operators on Fields | Intuitive Syntax |

> [!TIP] **การอ่าน Class Hierarchy**
> เมื่ออ่าน OpenFOAM Source Code:
> 1. เริ่มจาก Base Classes (เช่น `GeometricField`, `fvMatrix`)
> 2. ดู Template Parameters เพื่อเข้าใจ Type System
> 3. ติดตาม Inheritance Chain ไปยัง Specialized Classes
> 4. สังเกต Design Patterns ที่ใช้ (Smart Pointer, Factory, Strategy)
> 5. ดู Member Variables เพื่อเข้าใจ Memory Layout

> [!WARNING] **ข้อควรระวัง**
> - **Template Bloat**: การใช้ Templates มากเกินไปทำให้ Compile Time นาน
> - **Reference Cycles**: `tmp<>` อาจเกิด Reference Cycles ถ้าใช้ผิดวิธี
> - **Virtual Function Overhead**: Polymorphism มี Cost ทาง Performance
> - (การออกแบบที่ดีต้อง Balance ระหว่าง Flexibility และ Performance)

---

## Recommended Reading

- OpenFOAM Programmer's Guide: https://doc.openfoam.com/
- Effective C++ by Scott Meyers (RAII, Smart Pointers)
- Design Patterns by Gang of Four (GoF Patterns)
