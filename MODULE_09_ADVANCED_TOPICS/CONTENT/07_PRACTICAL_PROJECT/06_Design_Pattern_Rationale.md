# Design Pattern Rationale

หลักการเลือกและใช้ Design Patterns ใน OpenFOAM

---

## Overview

> **Design Pattern Rationale** — ประเมินและเลือก Design Pattern ที่เหมาะสมกับการพัฒนา OpenFOAM โดยพิจารณาจากความต้องการของระบบ ข้อดีข้อเสย และสถานการณ์การใช้งานที่เหมาะสม

---

## Learning Objectives 🎯

หลังจากศึกษาบทนี้ คุณจะสามารถ:
- **เลือก Design Pattern ที่เหมาะสม** กับปัญหาที่ต้องการแก้ไขใน OpenFOAM
- **เข้าใจ Pattern Selection Guide** — เมื่อไรใช้ Pattern ไหน และทำไม
- **หลีกเลี่ยง Anti-Patterns** ที่พบบ่อยในการพัฒนา OpenFOAM
- **ประยุกต์ใช้ Pattern ร่วมกัน** เพื่อแก้ปัญหาที่ซับซ้อน
- **เปรียบเทียบ Trade-offs** ระหว่าง Pattern ที่แตกต่างกัน

---

## Prerequisites 📚

ความรู้พื้นฐานที่ควรมีก่อน:
- **Inheritance และ Polymorphism** — ความเข้าใจเกี่ยวกับ Virtual Functions
- **Basic Design Patterns** — Factory, Strategy, Template Method
- **OpenFOAM Runtime Selection** — ระบบการเลือก Model จาก Dictionary
- **Memory Management** — RAII และ Smart Pointers

---

## 1. Factory Pattern — Pattern Selection Guide

### What?

**Factory Pattern** ใน OpenFOAM ใช้สำหรับสร้าง Objects จาก Dictionary โดยไม่ต้องระบุประเภทที่แน่นอนใน Compile Time

```cpp
// Runtime selection from dictionary
autoPtr<turbulenceModel> turb = turbulenceModel::New(
    mesh,
    transportProperties,
    rho,
    U,
    phi
);

// Different models via dictionary
// turbulenceModel: kEpsilon | kOmegaSST | SpalartAllmaras
```

### Why?

| Reason | Description |
|--------|-------------|
| **User Flexibility** | User เลือก Model ผ่าน Dictionary โดยไม่ต้อง Recompile |
| **Decoupling** | Solver Code ไม่ต้องรู้จัก Concrete Model Types |
| **Extensibility** | เพิ่ม Model ใหม่โดยไม่ต้องแก้ Solver Code |
| **Runtime Selection** | เลือก Model ตาม Case โดย Automatic |

### When to Use?

✅ **Use Factory when:**
- มีหลาย Model/Algorithm ที่ทำหน้าที่คล้ายกัน
- User ต้องการเลือก Model ผ่าน Dictionary
- ต้องการเพิ่ม Model ใหม่โดยไม่แก้ Code เดิม
- Model Type ขึ้นกับ Input Data

❌ **Avoid Factory when:**
- มี Class เดียวที่ใช้เสมอ
- Object Creation ซับซ้อนเกินไป (Over-engineering)
- Performance Critical ที่ Direct Construction เร็วกว่า

### Anti-Patterns ⚠️

**Anti-Pattern 1: Factory Overkill**
```cpp
// ❌ BAD: Factory for simple single class
autoPtr<simpleCalculator> calc = simpleCalculator::New();
// Better: simpleCalculator calc;

// ✅ GOOD: Factory for multiple models
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
```

**Anti-Pattern 2: Tight Coupling**
```cpp
// ❌ BAD: Factory with hardcoded types
if (dict.lookup("model") == "typeA") return new TypeA();
else if (dict.lookup("model") == "typeB") return new TypeB();

// ✅ GOOD: Runtime selection table
New* selectorFunction(Istream&);  // Automatic registration
```

---

## 2. Strategy Pattern — Pattern Selection Guide

### What?

**Strategy Pattern** ทำให้ Algorithm สามารถเปลี่ยนแปลงได้โดยไม่ต้อง Recompile

```cpp
// Dictionary-based strategy selection
fvSchemes
{
    divSchemes
    {
        div(phi,U) Gauss upwind;        // Strategy 1
        div(phi,k) Gauss limitedLinear 1;  // Strategy 2
    }
}

fvSolution
{
    solvers
    {
        p
        {
            solver          GAMG;      // Strategy 1
            tolerance       1e-06;
            relTol          0.01;
        }
    }
}
```

### Why?

| Reason | Description |
|--------|-------------|
| **Runtime Configurability** | เปลี่ยน Discretization โดยไม่ Recompile |
| **Easy Comparison** | เปรียบเทียบ Schemes ได้ทันที |
| **Case-Specific Tuning** | ปรับแต่ง per Case ได้ง่าย |
| **Separation of Concerns** | Solver Logic แยกจาก Numerical Scheme |

### When to Use?

✅ **Use Strategy when:**
- มีหลาย Algorithm แก้ปัญหาเดียวกัน
- ต้องการเปรียบเทียบ Performance
- Algorithm ต้อง Tunable ตาม Case
- ต้องการ Switch โดยไม่ Recompile

❌ **Avoid Strategy when:**
- Algorithm คงที่และไม่เปลี่ยน
- Performance ของ Indirection สำคัญมาก
- มี Strategy เดียวที่ใช้เสมอ

### Anti-Patterns ⚠️

**Anti-Pattern 1: Strategy Explosion**
```cpp
// ❌ BAD: Too many similar strategies
divSchemes
{
    div(phi,U) Gauss upwind;
    div(phi,U) Gauss linear;
    div(phi,U) Gauss linearUpwind;
    div(phi,U) Gauss limitedLinear;
    div(phi,U) Gauss QUICK;
    div(phi,U) Gauss SFCD;
    // ... 20 more options
}

// ✅ GOOD: Well-documented strategies with use cases
divSchemes
{
    // First-order: stable but diffusive
    div(phi,U) Gauss upwind;
    
    // Second-order: accurate but may need limiters
    div(phi,U) Gauss limitedLinear 1;
}
```

**Anti-Pattern 2: Hardcoded Strategy**
```cpp
// ❌ BAD: Hardcoded strategy in code
tmp<fv::convectionScheme<double>> convection(
    fv::convectionScheme<double>::New(
        mesh, schemes, phi, "Gauss", "upwind"  // Hardcoded
    )
);

// ✅ GOOD: Read from dictionary
tmp<fv::convectionScheme<double>> convection(
    fv::convectionScheme<double>::New(
        mesh, schemes, phi  // Dictionary driven
    )
);
```

---

## 3. Template Method Pattern — Pattern Selection Guide

### What?

**Template Method** กำหนด Structure ของ Algorithm แต่ให้ Override Steps ที่ต้องการ

```cpp
class Foam::solver
{
    // Template method
    void solve()
    {
        setValues();          // Hook 1
        while (!loop())
        {
            solveEquations();  // Hook 2 (must override)
            postProcess();     // Hook 3
        }
    }
    
    // Override in derived classes
    virtual void solveEquations() = 0;
};

// Derived classes implement specific algorithms
class simpleSolver : public solver
{
    virtual void solveEquations()
    {
        solveUEqn();
        solvePEqn();
    }
};
```

### Why?

| Reason | Description |
|--------|-------------|
| **Fixed Structure** | รักษา Workflow หลัก ให้คงที่ |
| **Customizable Steps** | Override เฉพาะส่วนที่ต้องการ |
| **Code Reuse** | Common Logic ใช้ร่วมกัน |
| **Consistent Behavior** | รับประกันว่า Basic Flow ถูกต้อง |

### When to Use?

✅ **Use Template Method when:**
- Algorithm มี Structure คงที่ แต่ Details ต่างกัน
- ต้องการรักษา Basic Workflow
- มี Common Code ที่ควร Reuse
- ต้องการ Guarantee Flow Control

❌ **Avoid Template Method when:**
- Structure แตกต่างกันมาก
- ไม่มี Common Workflow
- Flexibility สำคัญกว่า Consistency

### Anti-Patterns ⚠️

**Anti-Pattern 1: Overridden Template Method**
```cpp
// ❌ BAD: Derived class changes the structure
class badSolver : public solver
{
    void solve()
    {
        // Completely different flow
        preProcess();
        solveSpecial();
        if (condition) postProcess();
    }
};

// ✅ GOOD: Only override specific steps
class goodSolver : public solver
{
    virtual void solveEquations()
    {
        // Custom implementation
    }
};
```

**Anti-Pattern 2: Too Many Hooks**
```cpp
// ❌ BAD: Too many customization points
class solver
{
    void solve()
    {
        prePreProcess();       // Hook 1
        prePrePreProcess();    // Hook 2
        setValues();           // Hook 3
        // ... 15 more hooks
    }
};

// ✅ GOOD: Essential hooks only
class solver
{
    void solve()
    {
        setValues();        // Before main loop
        solveEquations();   // Must override
        postProcess();      // After main loop
    }
};
```

---

## 4. RAII — Pattern Selection Guide

### What?

**RAII (Resource Acquisition Is Initialization)** คือ Resource Lifetime เท่ากับ Object Lifetime

```cpp
// Automatic resource management
{
    autoPtr<volScalarField> pField
    (
        new volScalarField
        (
            IOobject("p", runTime.timeName(), mesh),
            mesh,
            dimensionedScalar("p", dimPressure, 0)
        )
    );
    
    // Use pField
    pField->correctBoundaryConditions();
    
} // <-- Automatic cleanup here
```

### Why?

| Reason | Description |
|--------|-------------|
| **No Memory Leaks** | Automatic Cleanup ใน Destructor |
| **Exception Safety** | Resource ถูก Release แม้มี Exception |
| **Clear Ownership** | รู้ว่าใครควร Delete |
| **Simplified Code** | ไม่ต้อง Manual Memory Management |

### When to Use?

✅ **Use RAII for:**
- Dynamic Memory Allocation (new/delete)
- File Handles
- Database Connections
- GPU Resources
- Temporary Objects

❌ **Avoid RAII when:**
- Stack Objects (Automatic RAII อยู่แล้ว)
- Simple Value Types
- Performance Critical ที่ Manual Control จำเป็น

### Anti-Patterns ⚠️

**Anti-Pattern 1: Manual Memory Management**
```cpp
// ❌ BAD: Manual delete (leak-prone)
volScalarField* p = new volScalarField(...);
// ... use p
delete p;  // Easy to forget or skip

// ✅ GOOD: RAII
autoPtr<volScalarField> p(new volScalarField(...));
// Automatic cleanup
```

**Anti-Pattern 2: Raw Pointers in Containers**
```cpp
// ❌ BAD: Raw pointers leak
PtrList<volScalarField*> fields;  // Who deletes?
for (int i = 0; i < 10; i++)
{
    fields.append(new volScalarField(...));
}  // Memory leak!

// ✅ GOOD: Smart pointers
PtrList<autoPtr<volScalarField>> fields;
for (int i = 0; i < 10; i++)
{
    fields.append(autoPtr<volScalarField>(
        new volScalarField(...)
    ));
}  // Automatic cleanup
```

---

## 5. Pattern Combination — When Patterns Work Together

### Pattern Selection Flowchart

```
┌─────────────────────────────────────┐
│    What is your requirement?       │
└──────────────────┬──────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     ▼             ▼             ▼
┌─────────┐  ┌─────────┐  ┌──────────────┐
│ Create  │  │ Change  │  │ Fixed        │
│ Object  │  │ Algo    │  │ Structure?   │
└────┬────┘  └────┬────┘  └──────┬───────┘
     │            │              │
     ▼            ▼              ▼
┌─────────┐  ┌─────────┐  ┌──────────────┐
│ Factory │  │Strategy │  │ Template     │
│ Pattern │  │ Pattern │  │ Method       │
└────┬────┘  └─────────┘  └──────┬───────┘
     │                            │
     └──────────┬─────────────────┘
                │
                ▼
         ┌──────────────┐
         │  Need RAII?  │
         └──────┬───────┘
                │
          ┌─────┴─────┐
          │           │
         Yes         No
          │           │
          ▼           ▼
    ┌──────────┐  ┌──────────┐
    │  Use     │  │  Skip    │
    │  RAII    │  │  RAII    │
    └──────────┘  └──────────┘
```

### Real-World Example: Pattern Combination

```cpp
// Factory + Template Method + RAII
class mySolver : public fvMesh
{
    // Factory creates this
    mySolver(const IOdictionary& dict)
    :
        fvMesh(IOobject(dict)),
        // RAII - automatic cleanup
        turbulence_(turbulenceModel::New(*this, dict)),
        transport_(singlePhaseTransportModel::New(*this, dict))
    {}
    
    // Template Method
    void solve()
    {
        while (runTime_.loop())
        {
            // Strategy: can change schemes via dict
            solveUEqn();       // Override point 1
            solvePEqn();       // Override point 2
            turbulence_->correct();  // Strategy usage
        }
    }
    
    // RAII cleanup automatic
    ~mySolver() = default;
    
private:
    // RAII managed resources
    autoPtr<turbulenceModel> turbulence_;
    autoPtr<singlePhaseTransportModel> transport_;
};
```

---

## 6. Comprehensive Pattern Selection Guide

### Decision Matrix

| Requirement | Recommended Pattern | Alternative | Trade-offs |
|-------------|---------------------|-------------|------------|
| **Create from Dictionary** | Factory | Builder | Factory: Simple, Builder: Complex |
| **Change Algorithm at Runtime** | Strategy | State | Strategy: User choice, State: Internal |
| **Fixed Workflow Structure** | Template Method | Chain of Responsibility | Template: Structured, Chain: Flexible |
| **Automatic Resource Management** | RAII | Shared Pointer | RAII: Single owner, Shared: Multiple |
| **Multiple Similar Operations** | Strategy | Command | Strategy: Interchangeable, Command: Queued |
| **Extensible Object Creation** | Factory | Prototype | Factory: New objects, Prototype: Cloned |

### Pattern Comparison Table

| Pattern | Flexibility | Complexity | Performance | Use Case |
|---------|-------------|------------|-------------|----------|
| **Factory** | High | Low | Medium | Model selection |
| **Strategy** | Very High | Low | Low-Medium | Discretization schemes |
| **Template Method** | Medium | Low | Low | Solver frameworks |
| **RAII** | Low | Very Low | High | Resource management |
| **Observer** | High | Medium | Medium | Event handling |
| **Decorator** | High | Medium | Low | Adding features |

---

## 7. Anti-Patterns Summary

### Common OpenFOAM Anti-Patterns

#### Anti-Pattern 1: **Golden Hammer** — ใช้ Pattern เดียวทุกปัญหา

```cpp
// ❌ Using Factory for everything
autoPtr<simpleCalc> calc = simpleCalc::New();  // Overkill
autoPtr<myHelper> helper = myHelper::New();    // Unnecessary

// ✅ Use appropriate tools
simpleCalc calc;  // Direct construction
myHelper helper;  // Stack allocation
```

#### Anti-Pattern 2: **Reinventing the Wheel** — ไม่ใช้ Built-in Patterns

```cpp
// ❌ Custom runtime selection
if (modelType == "A") return new ModelA();
else if (modelType == "B") return new ModelB();

// ✅ Use OpenFOAM runtime selection
defineTypeNameAndDebug(ModelA, 0);
addToRunTimeSelectionTable(turbulenceModel, ModelA, dictionary);
```

#### Anti-Pattern 3: **God Object** — ใช้ Pattern ผิดจังหวะ

```cpp
// ❌ One class does everything
class SuperSolver : public Factory, public Strategy, 
                    public TemplateMethod, public Observer
{
    // 1000+ lines doing everything
};

// ✅ Separate concerns
class TurbulenceModelFactory { /* Factory logic */ };
class ConvectionScheme { /* Strategy logic */ };
class Solver { /* Template method logic */ };
```

---

## Key Takeaways 🔑

### Pattern Selection Principles

1. **Know Your Requirements**
   - ต้องการ Flexibility หรือ Performance?
   - Runtime Configuration หรือ Compile-time?
   - มีกี่ Variant ที่ต้องรองรับ?

2. **Keep It Simple**
   - อย่า Over-engineer
   - Pattern คือ Solution ไม่ใช่ Goal
   - Direct Construction ถ้าเป็นไปได้

3. **Consider Trade-offs**
   - Flexibility ↔ Complexity
   - Performance ↔ Indirection
   - Control ↔ Automation

4. **Use OpenFOAM Conventions**
   - Runtime Selection Tables
   - Dictionary-driven Design
   - RAII for Resources

5. **Avoid Anti-Patterns**
   - Golden Hammer (ใช้ Pattern เดียวทุกอย่าง)
   - Reinventing Wheel (ไม่ใช้ Built-in)
   - God Object (ทำอะไรหมดในที่เดียว)

### Quick Decision Guide

- **Need to Create from Dictionary?** → Factory Pattern
- **Need to Change Algorithm?** → Strategy Pattern
- **Fixed Structure, Custom Steps?** → Template Method
- **Managing Resources?** → RAII
- **Multiple Patterns Together?** → Combine Wisely

---

## 🧠 Concept Check

<details>
<summary><b>1. เมื่อไรควรใช้ Factory Pattern แทน Direct Construction?</b></summary>

**Factory Pattern** เหมาะเมื่อ:
- มีหลาย Model Types ที่ User เลือกได้
- ต้อง Runtime Selection จาก Dictionary
- ต้องการเพิ่ม Model ใหม่โดยไม่แก้ Solver Code

**Direct Construction** เหมาะเมื่อ:
- มี Class เดียวที่ใช้เสมอ
- Performance สำคัญมาก
- Construction ง่ายๆ ไม่ซับซ้อน
</details>

<details>
<summary><b>2. Strategy Pattern ต่างจาก Simple If-Else อย่างไร?</b></summary>

**Strategy Pattern:**
- Dictionary-driven (ไม่ต้อง recompile)
- แก้ไขได้โดย User
- Extensible ง่าย (เพิ่ม Strategy ใหม่)

**If-Else Hardcoded:**
- Compile-time (ต้อง recompile เพื่อเปลี่ยน)
- Developer ต้องแก้ Code
- ยากต่อการ Extensibility

```cpp
// ❌ Hardcoded
if (scheme == "upwind") useUpwind();
else if (scheme == "linear") useLinear();

// ✅ Strategy (dictionary-driven)
div(phi,U) Gauss upwind;  // Change in dict
```
</details>

<details>
<summary><b>3. Template Method Pattern vs. Strategy Pattern?</b></summary>

**Template Method:**
- Fixed Structure, Custom Steps
- Inheritance-based
- Base Class กำหนด Flow
- ใช้ใน: `solver::solve()` Frameworks

**Strategy:**
- Interchangeable Algorithms
- Composition-based
- Runtime Selection
- ใช้ใน: `fvSchemes` Discretization
</details>

<details>
<summary><b>4. RAII ช่วยอะไรใน OpenFOAM?</b></summary>

**Automatic Cleanup** — ไม่ต้อง `delete` 手动:
- ป้องกัน Memory Leaks
- Exception Safe
- Clear Ownership

**ใช้เมื่อ:**
- Dynamic Allocation: `autoPtr<T>`, `refPtr<T>`
- Temporary Objects
- Resource Management

**หลีกเลี่ยง:**
- Raw Pointers ใน Containers
- Manual `new`/`delete`
</details>

<details>
<summary><b>5. Anti-Pattern ที่พัญช่วยใน OpenFOAM?</b></summary>

1. **Golden Hammer** — ใช้ Pattern เดียวทุกปัญหา
2. **Reinventing Wheel** — ไม่ใช้ Built-in Runtime Selection
3. **Manual Memory Management** — ไม่ใช้ RAII
4. **God Object** — Class หนึ่งทำทุกอย่าง
5. **Hardcoded Strategies** — ไม่ Dictionary-driven

**Solution:**
- เลือก Pattern ตาม Requirement
- ใช้ OpenFOAM Conventions
- RAII for Resources
- Separation of Concerns
</details>

<details>
<summary><b>6. การเลือก Pattern หลายๆ ตัวมาใช้ร่วมกัน?</b></summary>

**Pattern Combinations:**

**Factory + RAII:**
```cpp
autoPtr<turbulenceModel> turb = turbulenceModel::New(dict);
```

**Template Method + Strategy:**
```cpp
void solver::solve() {
    while (loop()) {
        solveEquations();  // Template hook
        turbulence_->correct();  // Strategy usage
    }
}
```

**Guideline:**
- Pattern ควร Complement กัน
- อย่าซ้อนทับกัน
- แต่ละ Pattern มีหน้าที่ชัดเจน
</details>

---

## 📖 เอกสารที่เกี่ยวข้อง

### ใน Module เดียวกัน
- **Overview:** [00_Overview.md](00_Overview.md) — ภาพรวม Design Patterns
- **Factory Pattern:** [02_Factory_Pattern.md](02_Factory_Pattern.md) — รายละเอียด Factory
- **Strategy Pattern:** [03_Strategy_Pattern.md](03_Strategy_Pattern.md) — รายละเอียด Strategy
- **Pattern Synergy:** [04_Pattern_Synergy.md](04_Pattern_Synergy.md) — การรวม Pattern หลายตัว

### ข้าม Module
- **Inheritance:** [02_Inheritance_and_Polymorphism.md](../02_INHERITANCE_POLYMORPHISM/02_Inheritance_and_Polymorphism.md) — พื้นฐาน Virtual Functions
- **Runtime Selection:** [02_INHERITANCE_POLYMORPHISM/04_Run_Time_Selection_System.md](../02_INHERITANCE_POLYMORPHISM/04_Run_Time_Selection_System.md) — ระบบ Runtime Selection
- **Memory Management:** [04_Memory_Management.md](../04_MEMORY_MANAGEMENTMENT/00_Overview.md) — RAII และ Smart Pointers
- **Practical Project:** [07_PRACTICAL_PROJECT](../07_PRACTICAL_PROJECT/00_Overview.md) — ประยุกต์ใช้ Patterns จริง

---

## 🎯 Next Steps

### Apply These Patterns
1. **Analyze Your Code** — หา Pattern ที่เหมาะสม
2. **Check Anti-Patterns** — หลีกเลี่ยง Common Pitfalls
3. **Start Simple** — ใช้ Pattern ตาม Requirement
4. **Combine Wisely** — ผสม Pattern เมื่อจำเป็น

### Practice Exercises
- Refactor Existing Code เพื่อใช้ Pattern ที่เหมาะสม
- Implement Simple Factory สำหรับ Model Selection
- Add Strategy Pattern สำหรับ Discretization Schemes
- Replace Manual Memory Management ด้วย RAII

---

**Version:** 1.0 | **Last Updated:** 2025-12-31 | **Module:** Design Patterns in OpenFOAM