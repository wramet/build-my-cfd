# Strategy Pattern (รูปแบบกลยุทธ์)

> **Strategy Pattern** = Define family of algorithms, encapsulate each one, and make them interchangeable

---

## Learning Objectives (วัตถุประสงค์การเรียนรู้)

หลังจากศึกษาบทนี้ คุณจะสามารถ:
- เข้าใจหลักการของ Strategy Pattern และการนำไปใช้ใน OpenFOAM
- ระบุตำแหน่งที่ Strategy Pattern ถูกใช้งานใน OpenFOAM (fvSchemes, turbulence models)
- เปรียบเทียบข้อดีข้อเสียระหว่าง Strategy Pattern กับการใช้ inheritance แบบดั้งเดิม
- นำไปประยุกต์ใช้กับการเลือก discretization schemes และ numerical methods
- แยกแยะได้ว่าเมื่อใดควรใช้ Strategy Pattern เมื่อใดควรใช้รูปแบบอื่น

---

## Prerequisites (ความรู้พื้นฐานที่ต้องมี)

- **Basic C++**: Class inheritance, virtual functions, abstract base classes
- **OpenFOAM Basics**: การอ่านและเขียน dictionary files (`fvSchemes`, `fvSolution`)
- **Discretization Concepts**: ความเข้าใจเกี่ยวกับ upwind, linear, QUICK schemes
- **Design Patterns Fundamentals**: ความเข้าใจพื้นฐานเกี่ยวกับ polymorphism

---

## 1. Introduction (3W Framework)

### WHAT: Strategy Pattern คืออะไร?

**Strategy Pattern** เป็น behavioral design pattern ที่:
- กำหนด family of algorithms ที่เกี่ยวข้องกัน
- Encapsulate แต่ละ algorithm ไว้ใน class แยกกัน
- ทำให้ algorithms สามารถสลับทดแทนกันได้ (interchangeable)

**ใน OpenFOAM**: Strategy Pattern ถูกใช้อย่างแพร่หลายสำหรับ:
- Discretization schemes (upwind, linear, cubic, etc.)
- Turbulence models (k-ε, k-ω, LES, etc.)
- Riemann solvers
- Gradient schemes

### WHY: ทำไมต้องใช้ Strategy Pattern?

**ปัญหาที่แก้ไขได้**:
```cpp
// ❌ BAD: Hardcoded algorithm
scalar calculateFlux(surfaceScalarField& phi)
{
    // Only linear interpolation!
    return linearInterpolate(phi);
}

// Problem: 
// - Cannot change without recompiling
// - Hard to test different schemes
// - Violates Open-Closed Principle
```

**ข้อดีของ Strategy Pattern**:
| Benefit | Description | OpenFOAM Example |
|---------|-------------|------------------|
| **Flexibility** | เปลี่ยน algorithm ได้โดยไม่ต้องแก้ code | เปลี่ยน upwind → linear ใน fvSchemes |
| **Runtime Selection** | เลือก strategy ตอน runtime ผ่าน dictionary | `divSchemes { div(phi,U) Gauss upwind; }` |
| **Testing** | ทดสอบแต่ละ scheme ได้อิสระ | Compare upwind vs linear accuracy |
| **Extensibility** | เพิ่ม scheme ใหม่ได้โดยไม่กระทบเดิม | Add new QUICK scheme |
| **Configuration-Driven** | User กำหนดผ่าน dictionary files | No recompile needed |

### HOW: ใช้งานใน OpenFOAM อย่างไร?

**สถาปัตยกรรมพื้นฐาน**:
```
Abstract Strategy (interface)
    ↓
Concrete Strategies (specific algorithms)
    ↓
Context (uses strategy)
    ↓
Dictionary (selects strategy at runtime)
```

---

## 2. Strategy Pattern Fundamentals

### 2.1 Pattern Structure

```cpp
// ===== ABSTRACT STRATEGY =====
class interpolationScheme
{
public:
    virtual ~interpolationScheme() = default;
    
    // Strategy interface - algorithm to be implemented
    virtual tmp<surfaceScalarField> interpolate
    (
        const volScalarField& vf
    ) const = 0;
    
    // Runtime type information
    virtual const word& type() const = 0;
};

// ===== CONCRETE STRATEGY 1: Linear =====
class linearInterpolation
:
    public interpolationScheme
{
public:
    // Constructor from dictionary
    linearInterpolation(const dictionary& dict)
    {}
    
    // Implement algorithm
    tmp<surfaceScalarField> interpolate
    (
        const volScalarField& vf
    ) const override
    {
        // Linear interpolation formula
        return surfaceScalarField::New
        (
            "interpolate(" + vf.name() + ')',
            vf.mesh(),
            dimensionedScalar(vf.dimensions(), 0)
        );
    }
    
    const word& type() const override
    {
        return word::null;
    }
};

// ===== CONCRETE STRATEGY 2: Upwind =====
class upwindInterpolation
:
    public interpolationScheme
{
    const surfaceScalarField& faceFlux_;
    
public:
    upwindInterpolation
    (
        const dictionary& dict,
        const surfaceScalarField& faceFlux
    )
    :
        faceFlux_(faceFlux)
    {}
    
    tmp<surfaceScalarField> interpolate
    (
        const volScalarField& vf
    ) const override
    {
        // Upwind interpolation based on flux direction
        return surfaceScalarField::New
        (
            "interpolate(" + vf.name() + ')',
            vf.mesh(),
            dimensionedScalar(vf.dimensions(), 0)
        );
    }
    
    const word& type() const override
    {
        return word::null;
    }
};
```

### 2.2 Context Usage

```cpp
// ===== CONTEXT CLASS =====
class convectionScheme
{
    // Strategy reference
    autoPtr<interpolationScheme> interpolator_;
    
public:
    // Constructor with strategy selection
    convectionScheme
    (
        const fvMesh& mesh,
        const dictionary& dict
    )
    :
        interpolator_
        (
            interpolationScheme::New(mesh, dict)
        )
    {}
    
    // Use strategy (algorithm hidden from user)
    tmp<surfaceScalarField> interpolate
    (
        const volScalarField& vf
    ) const
    {
        // Delegate to strategy
        return interpolator_->interpolate(vf);
    }
};
```

### 2.3 Factory Method (Pattern Combination)

```cpp
// ===== FACTORY METHOD =====
autoPtr<interpolationScheme> interpolationScheme::New
(
    const fvMesh& mesh,
    const dictionary& dict
)
{
    const word schemeType(dict.lookup("scheme"));
    
    Info << "Selecting interpolation scheme: " << schemeType << endl;
    
    typename dictionaryConstructorTable::iterator cstrIter =
        dictionaryConstructorTablePtr_->find(schemeType);
    
    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown interpolation scheme " << schemeType
            << endl << endl
            << "Valid schemes:" << endl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalError);
    }
    
    return cstrIter()(mesh, dict);
}
```

---

## 3. Strategy Pattern in OpenFOAM

### 3.1 fvSchemes Dictionary (Primary Example)

```cpp
// ===== SYSTEM/fvSchemes =====
ddtSchemes
{
    default         Euler;              // Strategy 1: First-order
}

gradSchemes
{
    default         Gauss linear;       // Strategy 2: Linear gradient
    grad(p)         Gauss linear;       // Strategy 3: Same
    grad(U)         cellLimited Gauss linear 1;  // Strategy 4: Limited
}

divSchemes
{
    div(phi,U)      Gauss upwind;       // Strategy 5: Upwind (stable)
    div(phi,T)      Gauss linearUpwind grad(T);  // Strategy 6: Higher-order
    div(phi,k)      Gauss limitedLinearV 1;      // Strategy 7: Bounded
}

laplacianSchemes
{
    laplacian(nu,U) Gauss linear corrected;      // Strategy 8: Non-orthogonal correction
    laplacian((1|A(U)),p) Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

**Interpretation**:
- **Gauss**: Base integration strategy
- **upwind/linear/linearUpwind**: Conflux strategies
- **corrected**: Strategy handling non-orthogonal meshes

### 3.2 Turbulence Models (Strategy + RTSTable)

```cpp
// ===== constant/turbulenceProperties =====
simulationType  RAS;        // Strategy selection: RAS, LES, or DNS

RAS
{
    RASModel        kEpsilon;           // Concrete strategy: k-ε model
    turbulence      on;
    
    printCoeffs     on;
}

// ===== Runtime selection =====
// User can change to:
RAS
{
    RASModel        kOmegaSST;          // Different strategy!
    turbulence      on;
}

// Or switch to LES:
simulationType  LES;
LES
{
    LESModel        Smagorinsky;        // Different strategy family!
}
```

**Code Implementation**:
```cpp
// Abstract strategy
class RASModel
:
    public turbulenceModel
{
public:
    virtual tmp<volSymmTensorField> R() const = 0;
    virtual tmp<volScalarField> k() const = 0;
    virtual tmp<volScalarField> epsilon() const = 0;
};

// Concrete strategy 1
class kEpsilon
:
    public RASModel
{
    // k-ε model implementation
};

// Concrete strategy 2
class kOmegaSST
:
    public RASModel
{
    // k-ω SST model implementation
};
```

### 3.3 Discretization Schemes Deep Dive

```cpp
// ===== GAUSS INTEGRATION (Base Strategy) =====
// File: src/finiteVolume/interpolation/surfaceInterpolationScheme/

// Abstract base class
template<class Type>
class surfaceInterpolationScheme
{
public:
    virtual tmp<GeometricField<Type, fvsPatchField, surfaceMesh>>
    interpolate(const GeometricField<Type, fvPatchField, volMesh>&) const = 0;
};

// ===== CONCRETE STRATEGIES =====

// 1. Linear interpolation
template<class Type>
class linear
:
    public surfaceInterpolationScheme<Type>
{
    // Central differencing: ψ_f = (ψ_P + ψ_N) / 2
};

// 2. Upwind interpolation
template<class Type>
class upwind
:
    public surfaceInterpolationScheme<Type>
{
    const surfaceScalarField& faceFlux_;
    
    // ψ_f = ψ_upwind (based on flux direction)
};

// 3. Linear upwind
template<class Type>
class linearUpwind
:
    public surfaceInterpolationScheme<Type>
{
    // Higher-order upwind using gradient
    // ψ_f = ψ_upwind + ∇ψ · Δr
};

// 4. QUICK scheme
template<class Type>
class QUICK
:
    public surfaceInterpolationScheme<Type>
{
    // Quadratic Upstream Interpolation for Convective Kinematics
};

// 5. Limited schemes (TVD)
template<class Type>
class limitedLinearV
:
    public surfaceInterpolationScheme<Type>
{
    // Van Leer limiter for boundedness
    // ψ_f = ψ_upwind + limiter(r) × (ψ_downwind - ψ_upwind)
};
```

### 3.4 Practical Usage Example

```cpp
// ===== SOLVER CODE (User doesn't know which scheme) =====
// File: applications/solvers/incompressible/simpleFoam/simpleFoam.C

// Create convection scheme (strategy selected from dictionary)
tmp<fv::convectionScheme<scalar>> mvConvection
(
    fv::convectionScheme<scalar>::New
    (
        mesh,
        schemes,
        phi,
        mesh.divScheme("div(phi,nuTilda)")
    )
);

// Use scheme (algorithm hidden!)
// User code doesn't know if it's upwind, linear, or QUICK
fvScalarMatrix nuTildaEqn
(
    fvm::ddt(phase, nuTilda)
  + fvm::div(phi, nuTilda, divScheme)  // ← Strategy used here
  - fvm::laplacian(DnuTildaEff, nuTilda)
 ==
    fvOptions(source, nuTilda)
);

// Change scheme by editing dictionary only:
// No need to recompile solver!
```

---

## 4. Strategy vs Other Patterns

### 4.1 Strategy vs Inheritance

```cpp
// ===== TRADITIONAL INHERITANCE =====
class Field
{
public:
    virtual scalar interpolate(scalar a, scalar b, scalar t) = 0;
};

class LinearField : public Field
{
    scalar interpolate(scalar a, scalar b, scalar t) override
    {
        return a + t * (b - a);
    }
};

class CubicField : public Field
{
    scalar interpolate(scalar a, scalar b, scalar t) override
    {
        scalar t2 = sqr(t);
        return a + t2 * (3 - 2*t) * (b - a);
    }
};

// ❌ PROBLEM: Field IS-A LinearField or CubicField
// - Cannot change interpolation at runtime
// - Must create new subclass for each combination

// ===== STRATEGY PATTERN =====
class InterpolationStrategy
{
public:
    virtual scalar interpolate(scalar a, scalar b, scalar t) = 0;
};

class Field
{
    InterpolationStrategy* strategy_;  // HAS-A strategy
    
public:
    void setStrategy(InterpolationStrategy* s) { strategy_ = s; }
    
    scalar interpolate(scalar a, scalar b, scalar t)
    {
        return strategy_->interpolate(a, b, t);  // Delegate
    }
};

// ✅ BENEFIT: Field HAS-A InterpolationStrategy
// - Change strategy at runtime!
// - Mix and match strategies
```

| Aspect | Inheritance | Strategy Pattern |
|--------|-------------|------------------|
| **Relationship** | IS-A (static) | HAS-A (dynamic) |
| **Changeability** | Compile-time only | Runtime |
| **Flexibility** | Low (fixed hierarchy) | High (plug-and-play) |
| **Use Case** | Fundamental type differences | Algorithm variations |

### 4.2 Strategy vs State Pattern

```cpp
// ===== STRATEGY PATTERN =====
// Algorithm variation
class interpolationScheme
{
    virtual scalar interpolate(scalar a, scalar b, scalar t) = 0;
};

// Different algorithms for interpolation
class LinearScheme : public interpolationScheme { /* ... */ };
class CubicScheme : public interpolationScheme { /* ... */ };

// ===== STATE PATTERN =====
// State variation (internal state changes behavior)
class turbulenceModel
{
    virtual void correct() = 0;
};

// Different states of turbulence
class LaminarModel : public turbulenceModel { /* ... */ };
class TurbulentModel : public turbulenceModel { /* ... */ };
```

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Strategy** | Algorithm interchangeable | upwind vs linear |
| **State** | State-dependent behavior | laminar vs turbulent |

### 4.3 Strategy + Factory Pattern

```cpp
// ===== COMBINATION: STRATEGY + FACTORY =====
// OpenFOAM uses both patterns together

// 1. STRATEGY: Different discretization algorithms
class divScheme
{
public:
    virtual tmp<surfaceScalarField> fvmDiv
    (
        const surfaceScalarField&,
        const volScalarField&
    ) const = 0;
};

// 2. FACTORY: Create strategy from dictionary
autoPtr<divScheme> divScheme::New
(
    const fvMesh& mesh,
    const dictionary& dict
)
{
    const word schemeType(dict.lookup("divScheme"));
    
    // Factory method creates appropriate strategy
    if (schemeType == "upwind")
    {
        return autoPtr<divScheme>(new upwindDivScheme(mesh, dict));
    }
    else if (schemeType == "linear")
    {
        return autoPtr<divScheme>(new linearDivScheme(mesh, dict));
    }
    // ... more strategies
    
    FatalError << "Unknown scheme" << exit(FatalError);
}

// 3. USAGE: User selects in dictionary
// system/fvSchemes:
divSchemes
{
    div(phi,U)      Gauss upwind;  // ← Factory creates upwindDivScheme
}
```

---

## 5. When to Use Strategy Pattern

### ✅ USE Strategy Pattern When:

1. **Multiple Algorithms for Same Task**
   ```cpp
   // Different convection schemes: upwind, linear, QUICK
   divSchemes { div(phi,U) Gauss upwind; }
   ```

2. **Runtime Selection Needed**
   ```cpp
   // User changes scheme without recompiling
   simulationType LES;  // vs RAS or DNS
   ```

3. **Algorithm Complexity Isolated**
   ```cpp
   // Each turbulence model in separate class
   RASModel kEpsilon;  // vs kOmegaSST, SpalartAllmaras
   ```

4. **Testing Different Variants**
   ```cpp
   // Compare scheme accuracy/performance
   linearScheme vs upwindScheme
   ```

5. **Configuration-Driven Design**
   ```cpp
   // Dictionary-driven algorithm selection
   gradSchemes { default Gauss linear; }
   ```

### ❌ DON'T USE Strategy Pattern When:

1. **Single Algorithm Only**
   ```cpp
   // No need for strategy if only one way to do it
   scalar calculateMagnitude(vector v) { return mag(v); }
   ```

2. **Algorithm Never Changes**
   ```cpp
   // Fixed formula not worth abstracting
   scalar pi() { return constant::mathematical::pi; }
   ```

3. **Performance Critical** (virtual function overhead)
   ```cpp
   // Tight loops might need direct calls
   // (but OpenFOAM accepts this for flexibility)
   ```

---

## 6. Key Takeaways (สรุปสาระสำคัญ)

### Core Concepts

1. **Strategy = Interchangeable Algorithm**
   - Encapsulate แต่ละ algorithm ใน class แยก
   - สลับ algorithm ได้โดยไม่แก้ client code
   - OpenFOAM ใช้ทุกหนทุกแห่ง (schemes, models, solvers)

2. **OpenFOAM Implementation**
   - Abstract base class = strategy interface
   - Concrete classes = specific algorithms
   - Dictionary files = runtime selection
   - RTS (Runtime Selection) = factory creation

3. **Benefits**
   - **Flexibility**: เปลี่ยน algorithm ใน dictionary ไม่ต้อง recompile
   - **Testing**: ทดสอบเปรียบเทียบ schemes ได้ง่าย
   - **Extensibility**: เพิ่ม scheme ใหม่โดยไม่กระทบเดิม
   - **User Control**: User กำหนด algorithm ผ่าน dictionary

### Strategy vs Other Patterns

| Pattern | Focus | Change | Example |
|---------|-------|--------|---------|
| **Strategy** | Algorithm | Runtime | upwind vs linear |
| **Inheritance** | Type | Compile-time | Field vs VectorField |
| **State** | Internal state | Automatic | laminar vs turbulent |
| **Factory** | Creation | Object creation | New scheme from dict |

### Practical Guidelines

- ✅ Use Strategy: เมื่อมีหลาย algorithms และต้องเปลี่ยนบ่อย
- ✅ Use +Factory: เมื่อต้องสร้าง strategy จาก dictionary
- ✅ Use +RTS: เมื่อต้องการ runtime type selection
- ❌ Avoid: เมื่อมี algorithm เดียวหรือไม่เคยเปลี่ยน

---

## Quick Reference

### Strategy Pattern Structure

| Component | OpenFOAM Example | Role |
|-----------|------------------|------|
| **Strategy Interface** | `surfaceInterpolationScheme<Type>` | Abstract algorithm |
| **Concrete Strategy** | `linear<Type>`, `upwind<Type>` | Specific algorithm |
| **Context** | `convectionScheme` | Uses strategy |
| **Factory** | `New(mesh, dict)` | Creates strategy |
| **Dictionary** | `system/fvSchemes` | Selects strategy |

### Common OpenFOAM Strategies

| Category | Strategies | Dictionary Location |
|----------|------------|---------------------|
| **Time** | Euler, backward, CrankNicolson | `fvSchemes:ddtSchemes` |
| **Gradient** | Gauss linear, leastSquares | `fvSchemes:gradSchemes` |
| **Divergence** | upwind, linear, QUICK, limitedLinearV | `fvSchemes:divSchemes` |
| **Laplacian** | linear corrected, uncorrected | `fvSchemes:laplacianSchemes` |
| **Interpolation** | linear, cellPoint, cellPointFaceWallModified | `fvSchemes:interpolationSchemes` |
| **SnGrad** | corrected, uncorrected | `fvSchemes:snGradSchemes` |
| **Turbulence** | kEpsilon, kOmegaSST, SpalartAllmaras | `constant/turbulenceProperties` |
| **Riemann** | HLL, HLLC, Roe | `constant/schemeProperties` |

### Template Code Pattern

```cpp
// ABSTRACT STRATEGY
class MyScheme
{
public:
    virtual tmp<volScalarField> calculate() = 0;
    virtual ~MyScheme() = default;
};

// CONCRETE STRATEGIES
class SchemeA : public MyScheme
{
    tmp<volScalarField> calculate() override { /* ... */ }
};

class SchemeB : public MyScheme
{
    tmp<volScalarField> calculate() override { /* ... */ }
};

// FACTORY
autoPtr<MyScheme> MyScheme::New(const dictionary& dict)
{
    const word type(dict.lookup("scheme"));
    
    if (type == "A") return autoPtr<MyScheme>(new SchemeA(dict));
    if (type == "B") return autoPtr<MyScheme>(new SchemeB(dict));
    
    FatalError << "Unknown scheme: " << type << exit(FatalError);
}

// USAGE
autoPtr<MyScheme> scheme = MyScheme::New(mesh.schemesDict());
tmp<volScalarField> result = scheme->calculate();
```

---

## 🧠 Concept Check

<details>
<summary><b>1. Strategy Pattern และ Inheritance ต่างกันอย่างไร?</b></summary>

**Strategy Pattern**: 
- HAS-A relationship (composition)
- เปลี่ยน algorithm ได้ runtime
- ใช้เมื่อมีหลายวิธีทำงานเดียวกัน

**Traditional Inheritance**:
- IS-A relationship
- กำหนด algorithm ที่ compile-time
- ใช้เมื่อ type มีความแตกต่างพื้นฐาน

ตัวอย่าง:
```cpp
// Inheritance: Field IS-A LinearField
class LinearField : public Field { };

// Strategy: Field HAS-A InterpolationStrategy
class Field {
    InterpolationStrategy* strategy_;
};
```
</details>

<details>
<summary><b>2. fvSchemes เป็น Strategy Pattern หรือไม่?</b></summary>

**ใช่** — fvSchemes เป็นตัวอย่างคลาสสิกของ Strategy Pattern:

```cpp
// User กำหนด strategy ใน dictionary
divSchemes
{
    div(phi,U)      Gauss upwind;     // ← Strategy 1
    div(phi,T)      Gauss linear;     // ← Strategy 2
}

// Solver ใช้ strategy โดยไม่รู้ว่าคืออะไร
fvm::div(phi, U)  // ← ใช้ upwind หรือ linear?
// ขึ้นอยู่กับ dictionary!
```

**ข้อดี**: เปลี่ยน scheme โดยไม่ต้อง recompile solver
</details>

<details>
<summary><b>3. ข้อดีของการเลือก strategy ผ่าน dictionary คืออะไร?</b></summary>

**Configuration-Driven Selection**:

| Benefit | Explanation |
|---------|-------------|
| **No Recompile** | เปลี่ยน scheme ใน dict ไม่ต้อง compile ใหม่ |
| **User Control** | User กำหนด algorithm เอง |
| **Rapid Testing** | เปรียบเทียบ schemes ได้เร็ว |
| **Portability** | ย้าย case ไปเครื่องอื่นได้เลย |
| **Documentation** | Dictionary เป็น spec ของ case |

ตัวอย่าง:
```bash
# เปลี่ยนจาก upwind → linear
vim system/fvSchemes
# แก้: div(phi,U) Gauss linear;

# Run immediately - no recompile!
simpleFoam
```
</details>

<details>
<summary><b>4. เมื่อไหร่ควรใช้ Strategy Pattern?</b></summary>

**✅ ใช้เมื่อ**:
1. มี multiple algorithms ทำ task เดียวกัน
2. ต้องการเปลี่ยน algorithm ที่ runtime
3. ต้องการ configuration-driven selection
4. ต้องการเปรียบเทียบ algorithms

**❌ ไม่ใช้เมื่อ**:
1. มี algorithm เดียวเท่านั้น
2. Algorithm ไม่เคยเปลี่ยน
3. Performance critical มาก (virtual function overhead)

**OpenFOAM Guidelines**:
- Discretization schemes: ✅ ใช้ Strategy
- Turbulence models: ✅ ใช้ Strategy + RTS
- Boundary conditions: ✅ ใช้ Strategy + Factory
- Core vector math: ❌ ไม่ใช้ (direct calls)
</details>

<details>
<summary><b>5. Strategy Pattern ทำงานร่วมกับ Factory Pattern อย่างไร?</b></summary>

**Combination** (OpenFOAM ใช้บ่อยมาก):

```cpp
// 1. STRATEGY: Algorithm interfaces
class divScheme { virtual tmp<surfaceScalarField> fvmDiv() = 0; };

// 2. CONCRETE STRATEGIES: Specific algorithms
class upwindDivScheme : public divScheme { /* ... */ };
class linearDivScheme : public divScheme { /* ... */ };

// 3. FACTORY: Create from dictionary
autoPtr<divScheme> divScheme::New(const fvMesh&, const dictionary&)
{
    word schemeType(dict.lookup("scheme"));
    
    if (schemeType == "upwind") 
        return autoPtr<divScheme>(new upwindDivScheme(...));
    if (schemeType == "linear") 
        return autoPtr<divScheme>(new linearDivScheme(...));
}

// 4. DICTIONARY: User selection
divSchemes { div(phi,U) Gauss upwind; }

// Flow: Dictionary → Factory → Strategy → Usage
```

**ข้อดีของการรวม**:
- Factory สร้าง strategy จาก dictionary
- Strategy ให้ flexibility
- Dictionary ให้ user control
</details>

<details>
<summary><b>6. สรุปขั้นตอนการสร้าง Strategy Pattern ใน OpenFOAM?</b></summary>

**Step-by-Step**:

1. **Define Abstract Strategy**
```cpp
class myAlgorithm
{
public:
    virtual tmp<volScalarField> calculate() = 0;
    virtual ~myAlgorithm() = default;
};
```

2. **Implement Concrete Strategies**
```cpp
class algorithmA : public myAlgorithm
{
    tmp<volScalarField> calculate() override { /* implementation */ }
};

class algorithmB : public myAlgorithm
{
    tmp<volScalarField> calculate() override { /* implementation */ }
};
```

3. **Add Factory Method**
```cpp
autoPtr<myAlgorithm> myAlgorithm::New(const dictionary& dict)
{
    word type(dict.lookup("algorithm"));
    
    if (type == "A") return autoPtr<myAlgorithm>(new algorithmA(dict));
    if (type == "B") return autoPtr<myAlgorithm>(new algorithmB(dict));
    
    FatalError << "Unknown: " << type << exit(FatalError);
}
```

4. **Add to Dictionary**
```cpp
// system/fvSchemes or custom dict
myAlgorithms
{
    default         A;  // Select algorithm
}
```

5. **Use in Code**
```cpp
autoPtr<myAlgorithm> algo = myAlgorithm::New(mesh.schemesDict());
tmp<volScalarField> result = algo->calculate();
```
</details>

---

## 📖 Related Documents

### ใน Module เดียวกัน
- **Overview**: [00_Overview.md](00_Overview.md) - ภาพรวม Design Patterns ใน OpenFOAM
- **Factory Pattern**: [02_Factory_Pattern.md](02_Factory_Pattern.md) - การสร้าง Objects จาก Dictionary
- **Template Method**: [04_Template_Method_Pattern.md](04_Template_Method_Pattern.md) - Algorithm skeleton
- **Pattern Synergy**: [06_Pattern_Synergy.md](06_Pattern_Synergy.md) - การรวมหลาย patterns

### ใน Modules อื่น
- **Discretization**: [MODULE_04](../MODULE_04_NUMERICAL_METHODS/) - รายละเอียด discretization schemes
- **Turbulence**: [MODULE_05](../MODULE_05_TURBULENCE_MODELING/) - Turbulence model selection
- **Solver Development**: [MODULE_06](../MODULE_06_SOLVER_DEVELOPMENT/) - การเขียน solver ใช้ schemes

### External Resources
- **Gamma et al.**: Design Patterns: Elements of Reusable Object-Oriented Software (Strategy Pattern chapter)
- **OpenFOAM Programmer's Guide**: Runtime selection mechanisms
- **Source Code**: `src/finiteVolume/` - Scheme implementations