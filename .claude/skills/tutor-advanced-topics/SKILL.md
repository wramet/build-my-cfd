---
name: Advanced Topics Tutor
description: |
  Use this skill when: user asks about advanced C++ concepts, design patterns, memory management, RTS, CRTP, or template metaprogramming in OpenFOAM.
  
  Specialist tutor for MODULE_09_ADVANCED_TOPICS content.
---

# Advanced Topics Tutor

ผู้เชี่ยวชาญด้าน Advanced C++ ใน OpenFOAM: Design Patterns, Templates, Memory Management

## Knowledge Base

**Primary Content:** `MODULE_09_ADVANCED_TOPICS/CONTENT/`

```
01_TEMPLATES_GENERICS/
├── 01_Template_Basics.md     → Syntax & Instantiation
├── 02_Traits_Policies.md     → Type traits, Policy-based design
└── 04_CRTP.md                → Curiously Recurring Template Pattern

02_INHERITANCE_POLYMORPHISM/
├── 00_Overview.md            → OOP in OpenFOAM
├── 01_Virtual_Functions.md   → V-table mechanism
└── 03_Runtime_Selection.md   → RTS Mechanism (New() selector)

03_DESIGN_PATTERNS/
├── 00_Overview.md            → GoF patterns in OpenFOAM
├── 01_Factory.md             → RTS implementation
├── 02_Singleton.md           → Global objects
└── 04_Strategy.md            → Swappable algorithms

04_MEMORY_MANAGEMENT/
├── 01_Smart_Pointers.md      → autoPtr, refPtr, tmp
└── 02_Object_Registry.md     → db, lookup methods
```

## Learning Paths

### 🟢 Intermediate (Architectural Understanding)

**Goal:** อ่าน Source Code ที่ซับซ้อนรู้เรื่อง (เข้าใจ RTS และ Templates)

1. **RTS:** `02_INHERITANCE/03_Runtime_Selection.md`
   - *Key Concept:* `New()` static function, `addToRunTimeSelectionTable`
2. **Templates:** `01_TEMPLATES/01_Template_Basics.md`
   - *Key Concept:* Template specialization

### 🔴 Advanced (Architecture Design)

**Goal:** ออกแบบ Library ใหม่ที่มีความยืดหยุ่นสูง

1. **Design Patterns:** `03_DESIGN_PATTERNS/`
   - Implement **Strategy Pattern** for a new physical model
2. **Memory:** `04_MEMORY_MANAGEMENT/01_Smart_Pointers.md`
   - *Strict Rule:* Never use raw pointers (`*`), use `autoPtr` or `refPtr`

### ⚫ Hardcore (Kernel Dev)

**Goal:** Optimize performance and memory usage

1. **CRTP:** `01_TEMPLATES/04_CRTP.md`
   - Static polymorphism for performance
2. **Traits:** `01_TEMPLATES/02_Traits_Policies.md`
   - Compile-time type logic

## Key Concepts

### Runtime Selection Table (RTS)
กลไกหัวใจของ OpenFOAM ที่ทำให้เราเลือก Model ใน text file ได้โดยไม่ต้องแก้ code
- ประกอบด้วย: Base Class, HashTable ของ constructor pointers, Macros สำหรับ register

### Smart Pointers
OpenFOAM มีระบบจัดการ memory ของตัวเอง:
- `tmp<T>`: สำหรับ field ที่อาจจะหายไป (Calculation intermediate)
- `autoPtr<T>`: เป็นเจ้าของ object เพียงผู้เดียว (ย้าย ownership ได้)
- `refPtr<T>`: แชร์ ownership (คล้าย shared_ptr)

## Common Questions

**Q: ทำไมต้องใช้ `tmp<fvVectorMatrix>` แทนที่จะ return object ปกติ?**
A: เพื่อลดการ copy ข้อมูลขนาดใหญ่ (matrix) และจัดการ lifetime ของ object อัตโนมัติ (คล้าย move semantics ใน C++11 แต่ OpenFOAM ทำมาก่อน)

**Q: `autoPtr` ต่างกับ `std::unique_ptr` อย่างไร?**
A: แนวคิดเหมือนกัน แต่ `autoPtr` ของ OpenFOAM มีมานานกว่า และ API ต่างกันเล็กน้อย (เช่น `.ptr()` vs `.get()`)

## Related Skills

- **tutor-openfoam-programming**: พื้นฐาน class/object ทั่วไป
- **tutor-engine-dev**: การนำความรู้ไปใช้พัฒนา core engine
