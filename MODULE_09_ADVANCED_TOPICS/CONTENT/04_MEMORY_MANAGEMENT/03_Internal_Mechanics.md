# Template Instantiation Mechanics
กลไกการ Instantiate แม่แบบ

---

## 🎯 Learning Objectives
เป้าหมายการเรียนรู้

After completing this section, you should be able to:
- **Explain** HOW C++ compilers instantiate templates (compilation model)
- **Identify** WHEN template instantiation occurs and WHERE object code lives
- **Apply** explicit instantiation techniques to reduce compilation time
- **Analyze** symbol visibility issues in template-heavy codebases
- **Debug** template instantiation errors effectively

หลังจากสิ้นสุดส่วนนี้ คุณควรจะสามารถ:
- **อธิบาย** วิธีการที่คอมไพเลอร์ C++ สร้างตัวแปรของแม่แบบ (โมเดลการคอมไพล์)
- **ระบุ** เมื่อใดที่การสร้างตัวแปรของแม่แบบเกิดขึ้นและ object code อยู่ที่ไหน
- **ประยุกต์** เทคนิคการสร้างตัวแปรแบบชัดเจนเพื่อลดเวลาคอมไพล์
- **วิเคราะห์** ปัญหาความมองเห็นสัญลักษณ์ในโค้ดเบสที่มีแม่แบบมาก
- **ดีบัก** ข้อผิดพลาดในการสร้างตัวแปรของแม่แบบได้อย่างมีประสิทธิภาพ

---

## Overview

ภาพรวม

> **Templates are not functions** — they are patterns for generating functions
> 
> **แม่แบบไม่ใช่ฟังก์ชัน** — แต่เป็นรูปแบบสำหรับสร้างฟังก์ชัน

### WHY: The Template Compilation Model
ทำไม: โมเดลการคอมไพล์ของแม่แบบ

Templates introduce a unique compilation model that differs from normal C++ code:

แม่แบบนำเสนอโมเดลการคอมไพล์ที่แตกต่างจากโค้ด C++ ปกติ:

- **Normal functions:** Compiled once, linked everywhere
- **Template functions:** Compiled separately for each type used
- **Header-only requirement:** Definition must be visible at compile-time
- **Code bloat:** Potential for duplicate object code

- **ฟังก์ชันปกติ:** คอมไพล์ครั้งเดียว ลิงก์ทุกที่
- **ฟังก์ชันแม่แบบ:** คอมไพล์แยกกันสำหรับแต่ละประเภทที่ใช้
- **ความต้องการ header-only:** คำนิยามต้องมองเห็นได้ในเวลาคอมไพล์
- **การบวมของโค้ด:** ความเป็นไปได้ของ object code ซ้ำซ้อน

Understanding internal mechanics is crucial for:
- Diagnosing obscure linker errors
- Optimizing compilation times in large projects
- Managing binary size in template-heavy libraries
- Debugging ODR (One Definition Rule) violations

การทำความเข้าใจกลไกภายในมีความสำคัญอย่างยิ่งสำหรับ:
- การวินิจฉัยข้อผิดพลาดของลิงก์เกอร์ที่คลุมเครือ
- การปรับปรุงเวลาคอมไพล์ในโปรเจ็กต์ขนาดใหญ่
- การจัดการขนาดไบนารีในไลบรารีที่มีแม่แบบมาก
- การดีบักการละเมิด ODR (One Definition Rule)

---

## 1. WHEN: Instantiation Points

เมื่อใด: จุด Instantiate

### 1.1 Implicit Instantiation
การ Instantiate โดยนัย

```cpp
// Template definition (in header)
template<typename T>
T square(T value) {
    return value * value;
}

// Usage point — THIS triggers instantiation
float f = square(3.14f);    // Instantiates square<float>
double d = square(2.71);    // Instantiates square<double>
```

**What happens:**

เกิดอะไรขึ้น:

1. Compiler sees `square<float>`
2. Substitutes `T` with `float`
3. Generates NEW function body
4. Compiles to machine code
5. Each translation unit gets its own copy

1. คอมไพเลอร์เห็น `square<float>`
2. แทนที่ `T` ด้วย `float`
3. สร้างตัวตนของฟังก์ชันใหม่
4. คอมไพล์เป็น machine code
5. แต่ละ translation unit ได้รับสำเนาของตัวเอง

### 1.2 Multiple Instantiation Problem
ปัญหาการ Instantiate หลายครั้ง

```cpp
// File1.cpp
#include "Square.h"  // Instantiates square<float>

// File2.cpp  
#include "Square.h"  // ALSO instantiates square<float>

// Result: TWO copies of square<float> in object files
//         Linker removes duplicates (ODR)
```

**Consequences:**

ผลที่ตามมา:

- Longer compile times (repeated work)
- Larger intermediate object files
- Linker must deduplicate (ODR merge)
- Potential ODR violations if definitions differ

- เวลาคอมไพล์ที่นานขึ้น (งานซ้ำ)
- ไฟล์อ็อบเจ็กต์ตัวกลางที่ใหญ่ขึ้น
- ลิงก์เกอร์ต้องลบค่าซ้ำ (การผสาน ODR)
- การละเมิด ODR ที่อาจเกิดขึ้นหากคำนิยามแตกต่างกัน

---

## 2. WHERE: Template Compilation Model

ที่ไหน: โมเดลการคอมไพล์ของแม่แบบ

### 2.1 Inclusion Model
โมเดลการรวม

**This is what OpenFOAM uses:**

นี่คือสิ่งที่ OpenFOAM ใช้:

```cpp
// SquareTemplate.H
#ifndef SquareTemplate_H
#define SquareTemplate_H

template<typename T>
T square(T value) {
    return value * value;
}

// ALWAYS inline template definitions in headers
#endif
```

**WHY this model:**

ทำไมโมเดลนี้:

✅ **Pros:** Simple, works everywhere
❌ **Cons:** Code bloat, longer compiles

✅ **ข้อดี:** ง่าย ใช้งานได้ทุกที่
❌ **ข้อเสีย:** โค้ดบวม คอมไพล์นานขึ้น

### 2.2 Instantiation Model (Alternative)
โมเดลการ Instantiate (ทางเลือก)

```cpp
// Square.H (declaration only)
template<typename T>
T square(T value);

// Square.C (implementation)
template<typename T>
T square(T value) {
    return value * value;
}

// Explicit instantiation
template float square(float);
template double square(double);
```

**OpenFOAM doesn't use this** because:
- Requires knowing all types upfront
- More complex build system
- Less flexible for user-defined types

**OpenFOAM ไม่ได้ใช้สิ่งนี้** เพราะ:
- ต้องการทราบประเภททั้งหมดล่วงหน้า
- ระบบบิลด์ที่ซับซ้อนมากขึ้น
- ยืดหยุ่นน้อยกว่าสำหรับประเภทที่ผู้ใช้กำหนด

---

## 3. HOW: Instantiation Process Details

อย่างไร: รายละเอียดกระบวนการ Instantiate

### 3.1 Two-Phase Lookup

การค้นหาสองเฟส

C++ compilers resolve templates in two phases:

คอมไพเลอร์ C++ แก้ไขแม่แบบในสองเฟส:

```cpp
template<typename T>
void process() {
    T x;              // Phase 1: Depends on T
    int y = 42;       // Phase 1: Non-dependent
    x.foo();          // Phase 2: Check if T::foo exists
    std::cout << y;   // Phase 2: Check std::cout visible
}
```

**Phase 1 (Definition time):**
- Check syntax independent of template parameters
- Verify names don't depend on `T`

**เฟส 1 (เวลานิยาม):**
- ตรวจสอบไวยากรณ์ที่ไม่ขึ้นกับพารามิเตอร์แม่แบบ
- ยืนยันชื่อที่ไม่ขึ้นกับ `T`

**Phase 2 (Instantiation time):**
- Verify dependent names actually exist
- Check all required symbols are visible

**เฟส 2 (เวลา Instantiate):**
- ยืนยันชื่อที่อ้างอิงมีอยู่จริง
- ตรวจสอบสัญลักษณ์ที่จำเป็นทั้งหมดมองเห็น

### 3.2 Name Lookup Strategies

กลยุทธ์การค้นหาชื่อ

```cpp
// GOOD: Explicit qualification
template<typename T>
void process() {
    std::cout << T::value;  // Clear dependency
}

// BAD: Hidden dependency
template<typename T>
void process() {
    using namespace std;
    cout << T::value;  // ADL issues, unclear
}
```

**Best Practice:**
- Always qualify dependent names with `typename`
- Use full namespaces for non-dependent names
- Avoid `using` directives in template headers

**แนวปฏิบัติที่ดี:**
- ระบุชื่อที่อ้างอิงด้วย `typename` เสมอ
- ใช้ namespaces แบบเต็มสำหรับชื่อที่ไม่ขึ้นกับ
- หลีกเลี่ยงคำสั่ง `using` ในส่วนหัวของแม่แบบ

---

## 4. Symbol Visibility and Linking

การมองเห็นสัญลักษณ์และการเชื่อมโยง

### 4.1 Weak Symbols

สัญลักษณ์อ่อน

```cpp
// Multiple definitions allowed (weak symbol)
template<typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}

// In object files:
// File1.o: WEAK SYMBOL max<int>
// File2.o: WEAK SYMBOL max<int>  
// Linker picks ONE, discards others
```

**OpenFOAM symbol table:**

```bash
# Check weak symbols
nm -C libOpenFOAM.so | grep " W " max

Output:
00000000 W max<int>
00000000 W max<double>
```

### 4.2 ODR Violation Detection

การตรวจจับการละเมิด ODR

```cpp
// Header1.H
template<typename T>
void func(T x) { /* version A */ }

// Header2.H  
template<typename T>
void func(T x) { /* version B */ }  // ODR violation!

// Both included → linker error OR undefined behavior
```

**Detection strategies:**

กลยุทธ์การตรวจจับ:

1. **Compiler warnings:** `-Wodr` (GCC)
2. **Linker errors:** Multiple definition errors
3. **Static analysis:** Tools like `clang-tidy`

1. **คำเตือนคอมไพเลอร์:** `-Wodr` (GCC)
2. **ข้อผิดพลาดลิงก์เกอร์:** ข้อผิดพลาดหลายนิยาม
3. **การวิเคราะห์แบบคงที่:** เครื่องมือเช่น `clang-tidy`

---

## 5. Explicit Instantiation

การ Instantiate อย่างชัดเจน

### 5.1 When to Use It

เมื่อไรต้องใช้

Use explicit instantiation when:
- You know all required types in advance
- Compilation time is critical
- Reducing code bloat is necessary

ใช้การ instantiate อย่างชัดเจนเมื่อ:
- คุณรู้ประเภทที่จำเป็นทั้งหมดล่วงหน้า
- เวลาคอมไพล์เป็นสิ่งสำคัญ
- การลดการบวมของโค้ดเป็นสิ่งจำเป็น

### 5.2 Syntax Pattern

รูปแบบไวยากรณ์

```cpp
// Geometry.H
template<typename T>
class Vector {
    // ... implementation ...
};

// Geometry.C
// Explicit instantiation for common types
template class Vector<float>;
template class Vector<double>;
template class Vector<int>;
```

**Benefits:**

ประโยชน์:

- Faster compiles (instantiation happens once)
- Smaller object files (no redundant copies)
- Better error messages (errors in .C file)

- คอมไพล์เร็วขึ้น (เกิด instantiation ครั้งเดียว)
- ไฟล์อ็อบเจ็กต์เล็กลง (ไม่มีสำเนาซ้ำ)
- ข้อความแสดงข้อผิดพลาดที่ดีกว่า (ข้อผิดพลาดในไฟล์ .C)

---

## 6. Debugging Template Errors

การดีบักข้อผิดพลาดของแม่แบบ

### 6.1 Common Error Patterns

รูปแบบข้อผิดพลาดทั่วไป

**Error Type 1: Missing Symbol**

```cpp
undefined reference to `Foam::max<Foam::Vector<double>>(...)'

Cause: Template not instantiated, definition not visible
Fix: Include header with definition
```

**Error Type 2: ODR Violation**

```cpp
multiple definition of `Foam::max<int>(...)'

Cause: Different definitions in different headers  
Fix: Ensure single definition, use include guards
```

**Error Type 3: Substitution Failure**

```cpp
error: no type named 'type' in 'struct std::enable_if<false>'

Cause: SFINAE failure (intentional or not)
Fix: Check template constraints, use `requires` (C++20)
```

### 6.2 Diagnostic Techniques

เทคนิคการวินิจฉัย

```cpp
// Technique 1: Static assertions for early detection
template<typename T>
void process(T x) {
    static_assert(std::is_arithmetic_v<T>, 
        "T must be arithmetic type");
}

// Technique 2: Concept-like checks (C++11)
template<typename T, 
    typename = std::enable_if_t<std::is_integral_v<T>>>
void integer_only(T x);

// Technique 3: Type traits inspection
template<typename T>
void debug_type(T) {
    std::cout << typeid(T).name() << std::endl;
}
```

---

## 7. Performance Considerations

ข้อควรพิจารณาด้านประสิทธิภาพ

### 7.1 Code Bloat

การบวมของโค้ด

```cpp
// Each instantiation = new function
template<typename T>
void process(T x) { /* 100 lines of code */ }

process(1);        // +100 bytes to binary
process(1.0);      // +100 bytes to binary  
process(1.0f);     // +100 bytes to binary
```

**Mitigation strategies:**

กลยุทธ์บรรเทา:

1. **Type erasure:** Use polymorphic base classes
2. **Shared implementation:** Non-template helper functions
3. **Explicit instantiation:** Control which types are generated

1. **Type erasure:** ใช้คลาสพื้นฐาน polymorphic
2. **การใช้งานร่วมกัน:** ฟังก์ชัน helper ที่ไม่ใช่แม่แบบ
3. **การ Instantiate อย่างชัดเจน:** ควบคุมประเภทที่สร้าง

### 7.2 Compile-Time vs. Runtime Trade-offs

การแลกเปลี่ยนเวลาคอมไพล์กับรันไทม์

| Factor | Template (Compile-time) | Virtual (Runtime) |
|--------|------------------------|-------------------|
| Performance | Inlined, optimized | Indirect call |
| Binary Size | Larger (copies) | Smaller (shared) |
| Compile Time | Slower | Faster |
| Flexibility | Type-safe, monomorphic | Dynamic, polymorphic |

| ปัจจัย | แม่แบบ (เวลาคอมไพล์) | เสมือน (รันไทม์) |
|--------|------------------------|-------------------|
| ประสิทธิภาพ | Inlined, ปรับแล้ว | การเรียกทางอ้อม |
| ขนาดไบนารี | ใหญ่กว่า (สำเนา) | เล็กกว่า (ใช้ร่วมกัน) |
| เวลาคอมไพล์ | ช้ากว่า | เร็วกว่า |
| ความยืดหยุ่น | ปลอดภัยประเภท, monomorphic | ไดนามิก, polymorphic |

---

## 8. Practical Template Instantiation

การ Instantiate แม่แบบในทางปฏิบัติ

### 8.1 OpenFOAM Field Instantiation

```cpp
// GeometricField.H - Common instantiation pattern
template<class Type>
class GeometricField {
    // Full template implementation
};

// Explicit instantiations for common types
template class GeometricField<scalar>;
template class GeometricField<vector>;
template class GeometricField<tensor>;
```

**Why this pattern:**

ทำไมรูปแบบนี้:

- Reduces compile time for users
- Ensures these types always available
- Controls binary size
- Provides well-tested specializations

- ลดเวลาคอมไพล์สำหรับผู้ใช้
- รับรองว่าประเภทเหล่านี้มีอยู่เสมอ
- ควบคุมขนาดไบนารี
- ให้การเชี่ยวชาญที่ทดสอบแล้ว

### 8.2 User-Defined Type Instantiation

```cpp
// User code
class MyCustomType {
    // ... user implementation ...
};

// Automatic instantiation when used
GeometricField<MyCustomType> myField(mesh);

// Generates: GeometricField<MyCustomType> code
// Compiler automatically handles instantiation
```

---

## Key Takeaways
สรุปสิ่งสำคัญ

### 🎯 Core Concepts
แนวคิดหลัก

**WHAT (What are templates):**
- **Templates are code generators**, not executable code
- Each type used = separate instantiation
- Requires header-only inclusion model

**แม่แบบคืออะไร:**
- **แม่แบบคือเครื่องกำเนิดโค้ด** ไม่ใช่โค้ดที่ปฏิบัติการได้
- แต่ละประเภทที่ใช้ = instantiation แยกกัน
- ต้องการโมเดลการรวม header-only

**WHY (Why understand mechanics):**
- Diagnose linker errors and ODR violations
- Optimize compilation times
- Manage binary size in template-heavy code
- Debug instantiation failures

**ทำไมต้องเข้าใจกลไก:**
- วินิจฉัยข้อผิดพลาดของลิงก์เกอร์และการละเมิด ODR
- ปรับปรุงเวลาคอมไพล์
- จัดการขนาดไบนารีในโค้ดที่มีแม่แบบมาก
- ดีบักความล้มเหลวในการ instantiate

**HOW (How to work with them):**
- **ALWAYS** include full template definitions in headers
- Use **explicit instantiation** for common types
- **QUALIFY** dependent names with `typename`
- **AVOID** `using` directives in template headers

**วิธีการทำงานกับพวกมัน:**
- **ต้อง** รวมคำนิยามแม่แบบทั้งหมดในส่วนหัว
- ใช้ **การ instantiate อย่างชัดเจน** สำหรับประเภททั่วไป
- **ระบุ** ชื่อที่อ้างอิงด้วย `typename`
- **หลีกเลี่ยง** คำสั่ง `using` ในส่วนหัวของแม่แบบ

### 📊 Decision Matrix

สมการตัดสินใจ

| Situation | Approach | Rationale |
|-----------|----------|-----------|
| Library code, known types | Explicit instantiation | Control bloat, faster compiles |
| User code, flexible types | Implicit instantiation | Maximum flexibility |
| Performance-critical | Template specialization | Optimize for hot types |
| Large compilation times | Precompiled headers | Cache template instantiations |

| สถานการณ์ | แนวทาง | เหตุผล |
|-----------|----------|-----------|
| โค้ดไลบรารี, ประเภทที่รู้จัก | Instantiate อย่างชัดเจน | ควบคุมการบวม, คอมไพล์เร็ว |
| โค้ดผู้ใช้, ประเภทยืดหยุ่น | Instantiate โดยนัย | ความยืดหยุ่นสูงสุด |
| ประสิทธิภาพสำคัญ | การเชี่ยวชาญของแม่แบบ | ปรับให้เหมาะกับประเภทที่ใช้บ่อย |
| เวลาคอมไพล์นาน | Precompiled headers | แคชการ instantiate ของแม่แบบ |

### 🔗 Connecting the Dots

เชื่อมโยงแนวคิด

```
Template Syntax (01) ← Instantiation Mechanics (03) ← Design Patterns (05)
        ↓                                  ↓                      ↓
   How to write                    How compiler          How to design
   template code                   generates code        template libraries
```

- **File 01 (Syntax)** shows you HOW to write template syntax
- **File 03 (This file)** explains HOW the compiler generates code
- **File 05 (Patterns)** applies mechanics to build reusable libraries

Understanding instantiation mechanics is the **bridge** between syntax and practical design.

- **ไฟล์ 01 (Syntax)** แสดงวิธีการเขียนไวยากรณ์แม่แบบ
- **ไฟล์ 03 (ไฟล์นี้)** อธิบายวิธีที่คอมไพเลอร์สร้างโค้ด
- **ไฟล์ 05 (Patterns)** ใช้กลไกเพื่อสร้างไลบรารีที่ใช้ซ้ำได้

การทำความเข้าใจกลไกของการ instantiate เป็น **สะพาน** ระหว่างไวยากรณ์และการออกแบบในทางปฏิบัติ

### ⚠️ Common Pitfalls
ข้อผิดพลาดทั่วไป

❌ **DON'T:** Put template definitions in .C files without explicit instantiation
✅ **DO:** Keep templates in headers OR use explicit instantiation

❌ **DON'T:** Forget `typename` keyword for dependent types
✅ **DO:** Always qualify: `typename T::iterator`

❌ **DON'T:** Use `using namespace` in template headers
✅ **DO:** Fully qualify names: `std::vector`, `Foam::List`

❌ **DON'T:** Ignore multiple definition warnings
✅ **DO:** Investigate ODR violations immediately

❌ **อย่า:** วางคำนิยามแม่แบบในไฟล์ .C โดยไม่มีการ instantiate อย่างชัดเจน
✅ **ทำ:** เก็บแม่แบบในส่วนหัวหรือใช้การ instantiate อย่างชัดเจน

❌ **อย่า:** ลืมคำหลัก `typename` สำหรับประเภทที่อ้างอิง
✅ **ทำ:** ระบุเสมอ: `typename T::iterator`

❌ **อย่า:** ใช้ `using namespace` ในส่วนหัวของแม่แบบ
✅ **ทำ:** ระบุชื่อแบบเต็ม: `std::vector`, `Foam::List`

❌ **อย่า:** ละเลยคำเตือนคำนิยามหลายครั้ง
✅ **ทำ:** สืบสวนการละเมิด ODR ทันที

---

## 🧠 Concept Check
ทดสอบความเข้าใจ

<details>
<summary><b>1. Why must template definitions be in headers?</b></summary>

**Answer:** Templates are instantiated at compile-time when used. The compiler needs the FULL definition to generate code. Unlike normal functions, templates cannot be compiled separately in .C files without explicit instantiation.

**คำตอบ:** แม่แบบถูกสร้างขึ้นในเวลาคอมไพล์เมื่อใช้ คอมไพเลอร์ต้องการคำนิยามทั้งหมดเพื่อสร้างโค้ด ต่างจากฟังก์ชันปกติ แม่แบบไม่สามารถคอมไพล์แยกในไฟล์ .C โดยไม่มีการ instantiate อย่างชัดเจน

**Key Point:** Inclusion model = definition visible to all translation units that use it

**จุดสำคัญ:** โมเดลการรวม = คำนิยามมองเห็นได้กับ translation units ทั้งหมดที่ใช้มัน
</details>

<details>
<summary><b>2. What happens when two translation units instantiate the same template?</b></summary>

**Answer:** Both generate object code for the template instantiation. The generated symbols are marked as **weak symbols**. During linking, the linker selects ONE copy and discards the others (ODR merge). This works IF definitions are identical, causes ODR violation if they differ.

**คำตอบ:** ทั้งคู่สร้าง object code สำหรับการ instantiate ของแม่แบบ สัญลักษณ์ที่สร้างขึ้นถูกทำเครื่องหมายเป็น **สัญลักษณ์อ่อน** ในระหว่างการเชื่อมโยง ลิงก์เกอร์เลือกสำเนาเดียวและทิ้งส่วนที่เหลือ (การผสาน ODR) นี่ใช้ได้ถ้าคำนิยามเหมือนกัน ก่อให้เกิดการละเมิด ODR หากแตกต่างกัน

**Key Point:** Weak symbols allow safe multiple instantiation with automatic deduplication

**จุดสำคัญ:** สัญลักษณ์อ่อนอนุญาตให้ instantiate หลายครั้งอย่างปลอดภัยพร้อมการลบค่าซ้ำอัตโนมัติ
</details>

<details>
<summary><b>3. When should you use explicit instantiation?</b></summary>

**Answer:** Use explicit instantiation when you:
1. Know all required types upfront (e.g., `float`, `double`, `vector` for fields)
2. Need to reduce compilation time (instantiate once, use everywhere)
3. Want to control binary size (avoid code bloat from unused types)
4. Are building a library with well-defined public API

**คำตอบ:** ใช้การ instantiate อย่างชัดเจนเมื่อคุณ:
1. รู้ประเภทที่จำเป็นทั้งหมดล่วงหน้า (เช่น `float`, `double`, `vector` สำหรับ fields)
2. ต้องการลดเวลาคอมไพล์ (instantiate ครั้งเดียว ใช้ทุกที่)
3. ต้องการควบคุมขนาดไบนารี (หลีกเลี่ยงการบวมของโค้ดจากประเภทที่ไม่ได้ใช้)
4. กำลังสร้างไลบรารีที่มี API สาธารณะที่กำหนดไว้อย่างดี

**Key Point:** Explicit instantiation trades flexibility for compilation efficiency and control

**จุดสำคัญ:** การ instantiate อย่างชัดเจนแลกเปลี่ยนความยืดหยุ่นเพื่อประสิทธิภาพการคอมไพล์และการควบคุม
</details>

<details>
<summary><b>4. What is two-phase lookup and why does it matter?</b></summary>

**Answer:** Two-phase lookup separates template checking into:
- **Phase 1:** Check non-dependent names at definition time
- **Phase 2:** Check dependent names at instantiation time

This matters because it allows earlier error detection for non-template issues and ensures that dependent names are properly resolved when concrete types are known.

**คำตอบ:** Two-phase lookup แยกการตรวจสอบแม่แบบเป็น:
- **เฟส 1:** ตรวจสอบชื่อที่ไม่ขึ้นกับในเวลานิยาม
- **เฟส 2:** ตรวจสอบชื่อที่อ้างอิงในเวลา instantiate

สิ่งนี้สำคัญเพราะช่วยให้ตรวจพบข้อผิดพลาดได้เร็วขึ้นสำหรับปัญหาที่ไม่ใช่แม่แบบและรับรองว่าชื่อที่อ้างอิงถูกแก้ไขอย่างเหมาะสมเมื่อรู้ประเภทที่เป็นรูปธรรม

**Key Point:** Two-phase lookup enables better error messages and catches bugs earlier

**จุดสำคัญ:** Two-phase lookup ช่วยให้ข้อความแสดงข้อผิดพลาดดีขึ้นและตรวจพบบั๊กได้เร็วขึ้น
</details>

---

## 📖 Further Reading
เอกสารอ้างอิงเพิ่มเติม

### Internal Dependencies
การพึ่งพาภายใน

- **Syntax:** [01_Introduction.md](01_Introduction.md) — How to write template syntax
- **Instantiation:** [02_Template_Syntax.md](02_Template_Syntax.md) — Template language rules
- **Patterns:** [05_Design_Patterns.md](05_Design_Patterns.md) — Applying mechanics to library design
- **Errors:** [06_Common_Errors_and_Debugging.md](06_Common_Errors_and_Debugging.md) — Debugging instantiation failures

### OpenFOAM Examples
ตัวอย่าง OpenFOAM

```bash
# View explicit instantiations in OpenFOAM
find $FOAM_SRC -name "*.C" -exec grep -l "template class" {} \;

# Common patterns:
# - GeometricField instantiations
# - tmp<T> explicit specializations
# - Field operations for scalar/vector/tensor
```

### External Resources
แหล่งข้อมูลภายนอก

- C++ Templates: The Complete Guide (Chapter 6: Instantiation)
- [cppreference.com: Template instantiation](https://en.cppreference.com/w/cpp/language/class_template)
- OpenFOAM source: `$FOAM_SRC/OpenFOAM/fields/`

---

**Next:** [04_Instantiation_and_Specialization.md](04_Instantiation_and_Specialization.md) — Deep dive into template specialization techniques