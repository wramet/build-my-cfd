# Instantiation and Specialization

Template Instantiation และ Specialization ใน OpenFOAM

---

## Learning Objectives

หลังจากอ่านบทนี้ คุณควรจะสามารถ:

- อธิบายความแตกต่างระหว่าง **implicit** และ **explicit instantiation** และทราบว่าควรใช้เมื่อใด
- เขียน **full specialization** และ **partial specialization** สำหรับ template ทั้งแบบ function และ class
- ใช้ **member specialization** เพื่อ override พฤติกรรมของสมาชิกบางตัวใน template class
- อธิบายวิธีการที่ OpenFOAM ใช้ explicit instantiation เพื่อลดเวลา compile
- เลือกวิธีการ instantiation ที่เหมาะสมกับ use case ของคุณ

---

## Overview

> **Instantiation** = กระบวนการสร้าง concrete code จาก template definition  
> **Specialization** = การกำหนด custom implementation สำหรับ specific types หรือ combinations

ใน OpenFOAM แนวคิดเหล่านี้มีความสำคัญอย่างยิ่งต่อ:
- **Performance**: Explicit instantiation ลดเวลา compilation
- **Flexibility**: Specialization อนุญาต optimization สำหรับ types เฉพาะ
- **Type Safety**: Compile-time checking สำหรับ generic code

---

## 1. Implicit Instantiation

**What**: Compiler สร้าง instance โดยอัตโนมัติเมื่อ template ถูกใช้กับ concrete type

**Why**: ความสะดวกในการใช้งาน - ไม่ต้องระบุ types ล่วงหน้า

**How**: การใช้งานทั่วไปของ template

```cpp
template<class Type>
Type maximum(const Type& a, const Type& b)
{
    return (a > b) ? a : b;
}

// Implicit instantiation - compiler generates maximum<scalar> automatically
scalar m = maximum(3.0, 5.0);

// Also generates maximum<vector>
vector v1(1, 2, 3), v2(4, 5, 6);
vector maxV = maximum(v1, v2);
```

**ข้อดี:**
- ง่ายและตรงไปตรงมา
- ใช้งานได้กับทุก type ที่รองรับ operations

**ข้อเสีย:**
- Compile-time เพิ่มขึ้นเมื่อมีการใช้หลาย types
- ไม่สามารถควบคุมได้ว่า types ใดจะถูก instantiate

---

## 2. Explicit Instantiation

**What**: บังคับให้ compiler สร้าง template instance สำหรับ types ที่ระบุ

**Why**: 
- ลดเวลา compilation โดยแยก instantiation ไปไว้ใน .C files
- ควบคุมได้ว่าอยากให้ types ใดถูกสร้างเท่านั้น
- ลด code bloat ใน header files

**How**: ใส่ declaration ใน .C file หรือที่ท้าย template definition

```cpp
// In a .C file (OpenFOAM style)
template class List<scalar>;
template class List<vector>;
template class List<tensor>;

// For functions
template scalar maximum(const scalar&, const scalar&);
template vector maximum(const vector&, const vector&);

// Prevent implicit instantiation in other translation units
extern template class List<label>;
```

**ตัวอย่าง OpenFOAM:**

```cpp
// In GeometricField.C
template
void GeometricField<scalar, fvPatchField, volMesh>::
correctBoundaryConditions();

template
void GeometricField<vector, fvPatchField, volMesh>::
correctBoundaryConditions();
```

**Best Practice:**
- ใช้ explicit instantiation สำหรับ types ที่รู้ว่าจะใช้แน่นอน
- ใช้ `extern template` เพื่อป้องกัน instantiation ใน translation units อื่น
- วาง explicit instantiations ใน .C files แยกต่างหาก

---

## 3. Full Specialization

**What**: กำหนด implementation ที่แตกต่างสำหรับ template เมื่อทุก template parameters ถูกระบุ

**Why**: 
- จัดการกับ types ที่ต้องการพฤติกรรมพิเศษ
- Optimize performance สำหรับ types ที่รู้จัก
- Handle edge cases ที่ generic implementation ทำงานไม่ได้

**How**: ใช้ `template<>` prefix พร้อมระบุ types ทั้งหมด

```cpp
// General template
template<class Type>
void print(const Type& val)
{
    Info << "Value: " << val << endl;
}

// Full specialization for vector
template<>
void print<vector>(const vector& val)
{
    Info << "Vector: (" << val.x() << ", " 
         << val.y() << ", " << val.z() << ")" << endl;
}

// Full specialization for symmTensor
template<>
void print<symmTensor>(const symmTensor& val)
{
    Info << "Tensor: " << val << endl;
}
```

**ตัวอย่าง Class Template:**

```cpp
// General template
template<class T>
class MathOps
{
public:
    static T identity()
    {
        return T(0);
    }
};

// Full specialization for scalar
template<>
class MathOps<scalar>
{
public:
    static scalar identity()
    {
        return 1.0;  // Multiplicative identity for scalars
    }
};

// Full specialization for vector
template<>
class MathOps<vector>
{
public:
    static vector identity()
    {
        return vector::zero;  // Additive identity
    }
};
```

---

## 4. Partial Specialization

**What**: Specialization สำหรับ template classes ที่มี parameters บางส่วนระบุและบางส่วนยังเป็น generic

**Why**: 
- จัดการกับกลุ่มของ types ที่มีคุณสมบัติคล้ายกัน
- Optimize สำหรับ categories ของ types
- Special behavior สำหรับ type relationships เฉพาะ

**How**: ระบุบาง parameters เป็น concrete types และคงบาง parameters เป็น generic

**Important**: Partial specialization ใช้ได้กับ **class templates เท่านั้น** (ไม่รองรับ function templates)

```cpp
// Primary template
template<class T1, class T2>
class Pair
{
public:
    T1 first_;
    T2 second_;
    
    void print()
    {
        Info << "Pair<" << typeid(T1).name() 
             << ", " << typeid(T2).name() << ">" << endl;
    }
};

// Partial specialization: both same type
template<class T>
class Pair<T, T>
{
public:
    T first_;
    T second_;
    
    void print()
    {
        Info << "Homogeneous Pair<" << typeid(T).name() << ">" << endl;
    }
    
    // Additional methods for homogeneous pairs
    T sum() const { return first_ + second_; }
};

// Partial specialization: second is pointer
template<class T>
class Pair<T, T*>
{
public:
    T first_;
    T* second_;
    
    void print()
    {
        Info << "Pair with pointer" << endl;
    }
};
```

**ตัวอย่าง OpenFOAM-style:**

```cpp
// General field template
template<class Type, class GeoMesh>
class Field
{
    // Generic implementation
};

// Specialization for volMesh
template<class Type>
class Field<Type, volMesh>
{
    // volMesh-specific optimizations
    void syncPar();  // Parallel synchronization for volume fields
};

// Specialization for surfaceMesh
template<class Type>
class Field<Type, surfaceMesh>
{
    // surfaceMesh-specific implementation
    void syncPar();  // Different sync for surface fields
};
```

---

## 5. Class Member Specialization

**What**: Specialize เฉพาะ member functions หรือ data members โดยไม่ต้อง specialize ทั้ง class

**Why**: 
- Custom behavior สำหรับ members โดยไม่กระทบ structure ของ class
- ลด code duplication
- แก้ปัญหาเฉพาะจุดใน generic class

**How**: ใช้ `template<>` กับ member definition และระบุ class template parameters

```cpp
template<class Type>
class Container
{
public:
    void process();       // General declaration
    Type getDefaultValue();
};

// General member definitions
template<class Type>
void Container<Type>::process()
{
    Info << "Processing generic type" << endl;
}

template<class Type>
Type Container<Type>::getDefaultValue()
{
    return Type();
}

// Member specialization for scalar
template<>
void Container<scalar>::process()
{
    Info << "Processing scalar with special algorithm" << endl;
}

template<>
scalar Container<scalar>::getDefaultValue()
{
    return 0.0;
}

// Member specialization for vector
template<>
void Container<vector>::process()
{
    Info << "Processing vector component-wise" << endl;
}
```

**Limitations:**
- ไม่สามารถ specialize เฉพาะ data member (ต้อง specialize ทั้ง class)
- Member specialization ต้องเป็น explicit (ไม่มี partial member specialization)

---

## 6. OpenFOAM Examples

### 6.1 GeometricField Explicit Instantiation

```cpp
// In src/finiteVolume/fields/geometricFields/geometricField/geometricField.C

// Explicit instantiations for common types
template class GeometricField<scalar, fvPatchField, volMesh>;
template class GeometricField<vector, fvPatchField, volMesh>;
template class GeometricField<tensor, fvPatchField, volMesh>;
template class GeometricField<symmTensor, fvPatchField, volMesh>;
template class GeometricField<sphericalTensor, fvPatchField, volMesh>;
```

**Why**: ลดเวลา compilation ของ solvers ที่ใช้ fields หลายประเภท

### 6.2 List Template Instantiation

```cpp
// In src/OpenFOAM/containers/Lists/List/List.C

template class List<label>;
template class List<scalar>;
template class List<vector>;
template class List<tensor>;
```

### 6.3 Specialized Field Operations

```cpp
// Special handling for scalar fields in boundary conditions
template<>
void fixedValueFvPatchField<scalar>::updateCoeffs()
{
    // Scalar-specific optimization
    if (this->updated())
    {
        return;
    }
    // ... scalar implementation
}

// Vector version might handle components separately
template<>
void fixedValueFvPatchField<vector>::updateCoeffs()
{
    if (this->updated())
    {
        return;
    }
    // ... vector-specific implementation
}
```

---

## Comparison Table

| Aspect | Implicit Instantiation | Explicit Instantiation | Full Specialization | Partial Specialization |
|--------|----------------------|----------------------|-------------------|----------------------|
| **Syntax** | Automatic from usage | `template class C<T>;` | `template<> class C<T>` | `template<T> class C<T, T>` |
| **Purpose** | Convenience | Reduce compile time | Custom implementation | Category-specific behavior |
| **When to Use** | Generic code | Known types, headers | Type-specific logic | Type pattern matching |
| **Function/Class** | Both | Both | Both | Classes only |
| **Compile Cost** | Per translation unit | Once | Replaces generic | Adds to generic |

---

## Best Practices

1. **Prefer Explicit Instantiation for Library Code**
   - ลด compile time สำหรับ users
   - ควบคุม ABI compatibility

2. **Use Specialization Judiciously**
   - Specialization เพิ่มความซับซ้อนของ codebase
   - พิจารณา overloading หรือ inheritance ก่อน

3. **Document Specializations**
   - อธิบายว่าทำไมจำเป็นต้อง specialize
   - ระบุ behavior ที่ต่างจาก generic version

4. **Test Generic and Specialized Versions**
   - ตรวจสอบว่า specializations ยังคงความหมายเดิมของ interface

5. **Consider SFINAE for Modern C++**
   - ใช้ `std::enable_if` หรือ concepts แทน specialization ในบางกรณี

---

## 🧠 Concept Check

<details>
<summary><b>1. Template instantiation เกิดขึ้นเมื่อไหร่?</b></summary>

**Compile-time** เมื่อ:
- **Implicit instantiation**: เมื่อ template ถูกใช้กับ concrete type ใน translation unit
- **Explicit instantiation**: เมื่อ compiler เจอ `template class` declaration

Instantiation ไม่เกิดขึ้นที่ runtime
</details>

<details>
<summary><b>2. Full vs Partial specialization - ความแตกต่างคืออะไร?</b></summary>

- **Full Specialization**: ระบุ **ทุก** template parameters เป็น concrete types
  ```cpp
  template<> void print<vector>(const vector&);
  ```
  
- **Partial Specialization**: ระบุ **บาง** parameters ยังคง generic
  ```cpp
  template<class T> class Pair<T, T*>;
  ```

**Note**: Function templates รองรับเฉพาะ full specialization เท่านั้น
</details>

<details>
<summary><b>3. ทำไม OpenFOAM ต้องใช้ explicit instantiation?</b></summary>

**สามเหตุผลหลัก:**

1. **Reduce Compile Time**: Instantiate ครั้งเดียวใน .C file ไม่ใช่ทุก translation unit
2. **Control ABI**: ระบุชัดเจนว่า types ใดถูกรองรับ
3. **Code Organization**: แยก template definitions จาก instantiations

ตัวอย่าง:
```cpp
// In .C file - compile once
template class GeometricField<scalar, fvPatchField, volMesh>;

// In solver headers - no recompilation
extern template class GeometricField<scalar, fvPatchField, volMesh>;
```
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ specialization vs function overloading?</b></summary>

**ใช้ Specialization เมื่อ:**
- ต้องการ customize behavior ของ **existing template**
- Interface เหมือนกัน แต่ implementation ต่างกัน
- ทำงานกับ template classes

**ใช้ Overloading เมื่อ:**
- Functions มี signatures ที่แตกต่างกัน
- ไม่ต้องการ maintain template interface
- ต้องการ type conversions แบบ specific
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

- **ภาพรวม Templates:** [00_Overview.md](00_Overview.md)
- **Template Syntax:** [02_Template_Syntax.md](02_Template_Syntax.md)
- **กลไกภายใน:** [03_Internal_Mechanics.md](03_Internal_Mechanics.md)
- **Design Patterns:** [05_Template_Patterns.md](05_Template_Patterns.md)