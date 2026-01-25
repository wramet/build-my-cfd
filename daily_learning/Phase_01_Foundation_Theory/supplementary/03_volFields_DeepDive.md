# Deep Dive: volScalarField และ volVectorField ใน OpenFOAM

**ตำแหน่งใน Roadmap:** Day 01 - Phase 1 Foundation Theory  
**ไฟล์ต้นฉบับ:** [`daily_learning/Phase_01_Foundation_Theory/2026-01-01.md:186-321`](daily_learning/Phase_01_Foundation_Theory/2026-01-01.md:186-321)

---

## 🔗 Prerequisites
- ความเข้าใจพื้นฐานเกี่ยวกับ C++ Template Programming
- ความรู้เรื่อง Inheritance และ Polymorphism
- ความเข้าใจ Finite Volume Method (FVM) เบื้องต้น

---

## 📝 Step-by-step Explanation

### 1. Inheritance Hierarchy ที่ซับซ้อน

โครงสร้างของ `volScalarField` และ `volVectorField` ใน OpenFOAM ถูกออกแบบด้วย Template Metaprogramming และ Inheritance ที่ซับซ้อน:

```cpp
// Simplified Inheritance Hierarchy
volScalarField → volField<scalar> → GeometricField<scalar, fvPatchField, volMesh>
volVectorField → volField<vector> → GeometricField<vector, fvPatchField, volMesh>
```

**แต่ละชั้นมีหน้าที่เฉพาะ:**
1. **`GeometricField<Type, PatchField, GeoMesh>`**: Base template class ที่จัดการ:
   - Memory allocation สำหรับ internal field และ boundary field
   - IO operations (อ่าน/เขียนไฟล์)
   - Dimension checking ผ่าน `dimensionSet`

2. **`volField<Type>`**: Intermediate class ที่เพิ่มฟังก์ชันเฉพาะสำหรับ volume fields:
   - การคำนวณ gradient, divergence (ผ่าน virtual functions)
   - การจัดการ boundary conditions

3. **`volScalarField`/`volVectorField`**: Concrete classes ที่ผู้ใช้ใช้งานจริง

### 2. Internal Data Structure

ภายใน `volScalarField` เก็บข้อมูล 3 ส่วนหลัก:

```cpp
class volScalarField {
private:
    // 1. Internal Field: ข้อมูลที่ cell centers
    Field<scalar> internalField_;
    
    // 2. Boundary Field: เงื่อนไขขอบสำหรับแต่ละ patch
    PtrList<fvPatchField<scalar>> boundaryField_;
    
    // 3. Geometric Information: Reference ไปยัง mesh
    const fvMesh& mesh_;
    
    // 4. Dimensions: ตรวจสอบหน่วยทางฟิสิกส์
    dimensionSet dimensions_;
};
```

**การทำงานของแต่ละส่วน:**
- **`internalField_`**: เก็บค่าของ field ที่ศูนย์กลางของทุก internal cell
- **`boundaryField_`**: เป็น list ของ `fvPatchField` objects แต่ละตัวจัดการ boundary condition ของ patch นั้นๆ
- **`mesh_`**: Reference ไปยัง mesh object สำหรับการคำนวณ geometric quantities

### 3. Boundary Conditions Management

ระบบ Boundary Conditions ของ OpenFOAM ออกแบบมาอย่างยืดหยุ่น:

```cpp
// ตัวอย่างการกำหนด Boundary Conditions
volScalarField p
(
    IOobject("p", runTime.timeName(), mesh),
    mesh,
    dimensionedScalar("p", dimPressure, 1e5),
    // Boundary Conditions
    {
        {"inlet", fixedValue(1.2e5)},      // Fixed pressure at inlet
        {"outlet", zeroGradient()},        // Zero gradient at outlet
        {"walls", fixedGradient(0.0)}      // Fixed gradient at walls
    }
);
```

**ประเภทของ Boundary Conditions หลัก:**
1. **`fixedValue`**: กำหนดค่าคงที่ที่ boundary
2. **`zeroGradient`**: Gradient เป็นศูนย์ (Neumann condition)
3. **`fixedGradient`**: กำหนด gradient คงที่
4. **`mixed`**: ผสมระหว่าง fixedValue และ fixedGradient

### 4. Dimension Checking System

หนึ่งในฟีเจอร์ที่สำคัญที่สุดของ OpenFOAM คือ **Compile-time Dimension Checking**:

```cpp
// ตัวอย่าง dimension checking
volScalarField p(dimPressure);          // [kg/(m·s²)]
volScalarField rho(dimDensity);         // [kg/m³]
volScalarField U(dimVelocity);          // [m/s]

// การคำนวณ kinetic energy: 0.5*rho*U²
volScalarField k = 0.5 * rho * magSqr(U);  // ✅ ถูกต้อง: [kg/m³] * [m²/s²] = [kg/(m·s²)]

// ข้อผิดพลาดจะถูกจับที่ compile-time
// volScalarField wrong = p + U;  // ❌ Compile error: dimensions ไม่ match
```

**`dimensionSet` class ทำงานอย่างไร:**
- เก็บ exponents ของ 7 base dimensions: [Mass, Length, Time, Temperature, Quantity, Current, Luminous Intensity]
- ตรวจสอบ dimensional consistency ใน operations ทุกชนิด (+, -, *, /, ==, etc.)

### 5. Memory Management และ Performance

OpenFOAM ใช้ระบบ memory management ที่ซับซ้อนเพื่อประสิทธิภาพสูง:

```cpp
// 1. Field Data Storage
Field<scalar> data_;          // Contiguous memory allocation

// 2. Reference Counting
tmp<volScalarField> tempField = fvc::grad(p);  // tmp ใช้ reference counting

// 3. Expression Templates
// เพื่อหลีกเลี่ยง temporary objects ใน complex expressions
volScalarField result = a + b * c - d / e;  // ประเมินใน single pass
```

**Optimization Techniques:**
- **Contiguous Memory**: `Field<T>` ใช้ contiguous memory สำหรับ cache efficiency
- **Expression Templates**: ลดจำนวน temporary objects ใน complex expressions
- **Reference Counting**: `tmp<T>` และ `autoPtr<T>` จัดการ memory อัตโนมัติ

### 6. Extended Implementation สำหรับ Phase Change

ตามที่ระบุใน Day 01 Section 2.1.3 เราต้องการ extended version ของ `volScalarField`:

```cpp
class ExtendedVolScalarField : public volScalarField {
private:
    // Additional data for phase change
    const volScalarField& alpha_;          // Volume fraction field
    const dimensionedScalar& rho_l_;       // Liquid density
    const dimensionedScalar& rho_v_;       // Vapor density
    
public:
    // Critical method for expansion term
    tmp<fvScalarMatrix> addExpansionSource(
        const volScalarField& mDot,        // Mass transfer rate
        const word& fieldName = "p"        // Field being solved
    ) const {
        // Calculate expansion source: mDot * (1/rho_v - 1/rho_l)
        volScalarField expansion = mDot * (1.0/rho_v_ - 1.0/rho_l_);
        
        // Create and return matrix contribution
        return fvm::SuSp(expansion, *this);
    }
};
```

**เหตุผลในการออกแบบ Extended Class:**
1. **Domain-Specific Logic**: มี method เฉพาะสำหรับ phase change physics
2. **Performance Optimization**: คำนวณ expansion term ได้อย่างมีประสิทธิภาพ
3. **Type Safety**: ตรวจสอบว่า field นี้ใช้กับ phase change problem เท่านั้น

### 7. การใช้งานใน Solver

ตัวอย่างการใช้งาน `volScalarField` ใน pressure equation:

```cpp
void EvaporatorSolver::solvePressure() {
    // สร้าง pressure field
    volScalarField p
    (
        IOobject("p", runTime.timeName(), mesh),
        mesh,
        dimensionedScalar("p", dimPressure, 1e5)
    );
    
    // Assemble pressure equation
    fvScalarMatrix pEqn(fvm::laplacian(p) == fvc::div(U));
    
    // เพิ่ม expansion term ถ้าใช้ extended version
    if (usePhaseChange_) {
        ExtendedVolScalarField& pExtended = dynamic_cast<ExtendedVolScalarField&>(p);
        pEqn += pExtended.addExpansionSource(mDot_);
    }
    
    // Solve pressure equation
    pEqn.solve();
}
```

---

## 💡 Key Insights

1. **Template Design Pattern**: OpenFOAM ใช้ template metaprogramming อย่างหนักเพื่อ code reuse ระหว่าง scalar, vector, tensor fields
2. **Dimension Safety**: Compile-time dimension checking ป้องกันข้อผิดพลาดทางฟิสิกส์
3. **Memory Efficiency**: Contiguous memory storage และ expression templates เพิ่ม performance
4. **Extensibility**: สามารถสร้าง derived classes สำหรับ domain-specific requirements ได้

---

## 🧪 Quick Check

**คำถาม:** ทำไม `volScalarField` ต้องเก็บ reference ไปยัง `fvMesh` object?

**คำตอบ:** เพราะการคำนวณ geometric quantities (เช่น gradient, divergence) ต้องการข้อมูลเกี่ยวกับ mesh geometry (cell volumes, face areas, cell centers) `volScalarField` ใช้ mesh reference เพื่อ:
1. คำนวณ spatial derivatives อย่างถูกต้อง
2. Interpolate values จาก cell centers ไปยัง faces
3. Integrate ฟิลด์เหนือ domain
4. จัดการ boundary conditions ที่ขึ้นกับ geometry

---

## 📚 Related Topics

- **Day 05:** Mesh Topology และการเชื่อมโยงกับ Field Classes
- **Day 06:** Boundary Conditions Management
- **Day 07:** Linear Algebra (LDU Format) สำหรับ Field Operations
- **Day 09:** Pressure-Velocity Coupling ที่ใช้ volScalarField สำหรับ pressure
- **Day 10:** VOF Method ที่ใช้ volScalarField สำหรับ volume fraction

---

## ⚠️ Common Pitfalls และ Solutions

### Pitfall 1: Memory Leak จาก Temporary Objects
```cpp
// ❌ ผิด: สร้าง temporary objects หลายตัว
volScalarField result = a + b + c + d;

// ✅ ถูก: ใช้ expression templates
volScalarField result = a;
result += b;
result += c;
result += d;
```

### Pitfall 2: Dimension Mismatch
```cpp
// ❌ ผิด: dimensions ไม่ match
volScalarField p(dimPressure);
volScalarField U(dimVelocity);
volScalarField wrong = p + U;  // Compile error

// ✅ ถูก: ตรวจสอบ dimensions
volScalarField dynamicPressure = 0.5 * rho * magSqr(U);  // [kg/(m·s²)]
```

### Pitfall 3: Boundary Conditions Not Updated
```cpp
// ❌ ผิด: ลืม update boundary conditions
pEqn.solve();
// p.boundaryField() ยังไม่ถูก update

// ✅ ถูก: เรียก correctBoundaryConditions()
pEqn.solve();
p.correctBoundaryConditions();
```

### Pitfall 4: Shallow Copy vs Deep Copy
```cpp
// ❌ ผิด: shallow copy
volScalarField p1 = ...;
volScalarField p2 = p1;  // Shallow copy, แชร์ data

// ✅ ถูก: ใช้ clone() สำหรับ deep copy
volScalarField p2 = p1.clone();
```

---

## 🎯 Engineering Impact

การเข้าใจ `volScalarField` และ `volVectorField` อย่างลึกซึ้งช่วยให้:
1. **เขียนโค้ดที่มีประสิทธิภาพสูง**: ใช้ memory อย่างมีประสิทธิภาพ
2. **ป้องกันข้อผิดพลาดทางฟิสิกส์**: Dimension checking จับข้อผิดพลาดตั้งแต่ compile-time
3. **ออกแบบ extensions ได้ถูกต้อง**: สร้าง derived classes สำหรับ specific physics
4. **ดีบักได้ง่ายขึ้น**: เข้าใจ internal structure ช่วย diagnose problems

---

**สรุป:** `volScalarField` และ `volVectorField` เป็นหัวใจของ data representation ใน OpenFOAM การออกแบบที่ซับซ้อนแต่มีประสิทธิภาพนี้ทำให้ OpenFOAM สามารถจัดการปัญหาทางฟิสิกส์ที่ซับซ้อนได้อย่างมีประสิทธิภาพ

---

## Phase Properties Management (การจัดการคุณสมบัติของเฟส)

สำหรับปัญหาการเปลี่ยนสถานะ (phase change) การจัดการคุณสมบัติของแต่ละเฟสเป็นสิ่งสำคัญอย่างยิ่ง ใน ExtendedVolScalarField ของเรา เราต้องเก็บข้อมูล phase-specific properties:

### 1. Phase Property Storage

```cpp
class ExtendedVolScalarField : public volScalarField {
private:
    // Phase-specific properties
    const dimensionedScalar& rho_l_;       // Liquid density [kg/m³]
    const dimensionedScalar& rho_v_;       // Vapor density [kg/m³]
    const dimensionedScalar& mu_l_;        // Liquid dynamic viscosity [Pa·s]
    const dimensionedScalar& mu_v_;        // Vapor dynamic viscosity [Pa·s]
    const dimensionedScalar& cp_l_;        // Liquid specific heat [J/(kg·K)]
    const dimensionedScalar& cp_v_;        // Vapor specific heat [J/(kg·K)]
    const dimensionedScalar& k_l_;         // Liquid thermal conductivity [W/(m·K)]
    const dimensionedScalar& k_v_;         // Vapor thermal conductivity [W/(m·K)]
    
    // Reference to volume fraction field
    const volScalarField& alpha_;          // α = 1 (liquid), α = 0 (vapor)
    
public:
    // Method to calculate mixture properties
    volScalarField mixtureProperty(
        const dimensionedScalar& phi_l,
        const dimensionedScalar& phi_v
    ) const {
        return alpha_ * phi_l + (1.0 - alpha_) * phi_v;
    }
    
    // Calculate mixture density
    volScalarField rho_m() const {
        return mixtureProperty(rho_l_, rho_v_);
    }
    
    // Calculate mixture viscosity
    volScalarField mu_m() const {
        return mixtureProperty(mu_l_, mu_v_);
    }
};
```

### 2. Property Interpolation at Interface

ที่บริเวณ interface (0 < α < 1) การคำนวณคุณสมบัติต้องใช้วิธีที่เหมาะสม:

```cpp
// Harmonic mean สำหรับ thermal conductivity ที่ interface
scalar kHarmonic(scalar alpha, scalar k_l, scalar k_v) {
    if (alpha > 0.99) return k_l;
    if (alpha < 0.01) return k_v;
    
    // Harmonic mean: 1/k_m = α/k_l + (1-α)/k_v
    return 1.0 / (alpha/k_l + (1.0 - alpha)/k_v);
}

// Linear interpolation สำหรับ properties อื่นๆ
scalar linearInterp(scalar alpha, scalar phi_l, scalar phi_v) {
    return alpha * phi_l + (1.0 - alpha) * phi_v;
}
```

### 3. Property Update Strategy

ในแต่ละ time step ของ simulation:

1. **ก่อน solve equations**: อัพเดท mixture properties จาก α ปัจจุบัน
2. **ระหว่าง iteration**: Recalculate properties ถ้า α เปลี่ยนแปลงมาก
3. **หลัง convergence**: อัพเดท properties สำหรับ output

```cpp
void EvaporatorSolver::updateMixtureProperties() {
    // Update all mixture properties based on current alpha
    rho_ = alpha_ * rho_l_ + (1.0 - alpha_) * rho_v_;
    mu_ = alpha_ * mu_l_ + (1.0 - alpha_) * mu_v_;
    cp_ = alpha_ * cp_l_ + (1.0 - alpha_) * cp_v_;
    
    // Use harmonic mean for thermal conductivity at interface
    forAll(alpha_, cellI) {
        scalar alphaVal = alpha_[cellI];
        if (alphaVal > 0.01 && alphaVal < 0.99) {
            k_[cellI] = kHarmonic(alphaVal, k_l_.value(), k_v_.value());
        } else {
            k_[cellI] = linearInterp(alphaVal, k_l_.value(), k_v_.value());
        }
    }
}
```

### 4. Temperature-Dependent Properties

สำหรับสารทำความเย็น R410A คุณสมบัติเปลี่ยนตามอุณหภูมิ:

```cpp
// Property correlations for R410A
dimensionedScalar rhoLiquidR410A(scalar T) {
    // Simplified correlation: ρ_l = A - B*T
    return dimensionedScalar("rho_l", dimDensity, 1200.0 - 0.5*(T - 273.15));
}

dimensionedScalar rhoVaporR410A(scalar T) {
    // Ideal gas law approximation: ρ_v = P/(R*T)
    const scalar R = 287.0;  // Specific gas constant [J/(kg·K)]
    const scalar P = 1e5;    // Pressure [Pa]
    return dimensionedScalar("rho_v", dimDensity, P/(R*T));
}
```

### 5. Implementation Considerations

**ความท้าทาย:**
1. **Property Discontinuity**: ที่ interface คุณสมบัติเปลี่ยนอย่างรวดเร็ว
2. **Numerical Stability**: การ interpolate properties ที่ไม่เหมาะสมทำให้ solver diverge
3. **Conservation Laws**: ต้องรักษา mass และ energy conservation

**แนวทางแก้ไข:**
1. ใช้ **smoothed interpolation** สำหรับ properties ที่ interface
2. **Under-relaxation** สำหรับ property updates
3. **Consistency check** ระหว่าง properties และ governing equations

---

## Interface Tracking (การติดตามอินเทอร์เฟซ)

การติดตามตำแหน่ง interface ระหว่างของเหลวและไอเป็นหัวใจของ VOF method:

### 1. Interface Detection Methods

```cpp
class InterfaceDetector {
public:
    // Method 1: Alpha-based detection
    labelList findInterfaceCells(
        const volScalarField& alpha,
        scalar threshold = 0.01
    ) const {
        DynamicList<label> interfaceCells(alpha.size()/10);
        
        forAll(alpha, cellI) {
            scalar alphaVal = alpha[cellI];
            if (alphaVal > threshold && alphaVal < (1.0 - threshold)) {
                interfaceCells.append(cellI);
            }
        }
        
        return interfaceCells;
    }
    
    // Method 2: Gradient-based detection
    volScalarField interfaceIndicator(
        const volScalarField& alpha
    ) const {
        // |∇α| จะมีค่าสูงที่ interface
        return mag(fvc::grad(alpha));
    }
    
    // Method 3: Curvature calculation
    volScalarField interfaceCurvature(
        const volScalarField& alpha
    ) const {
        // κ = -∇·(∇α/|∇α|)
        volVectorField n = fvc::grad(alpha);
        volScalarField magN = mag(n) + dimensionedScalar("small", dimless, 1e-12);
        n /= magN;
        
        return -fvc::div(n);
    }
};
```

### 2. Interface Reconstruction

```cpp
class InterfaceReconstructor {
public:
    // PLIC (Piecewise Linear Interface Calculation)
    void reconstructPLIC(
        const volScalarField& alpha,
        volVectorField& normal,
        volScalarField& distance
    ) const {
        // 1. Calculate interface normal from alpha gradient
        normal = fvc::grad(alpha);
        volScalarField magN = mag(normal) + dimensionedScalar("small", dimless, 1e-12);
        normal /= magN;
        
        // 2. Calculate distance to interface
        // ใช้ iterative method เพื่อหา distance ที่ให้ volume fraction ถูกต้อง
        forAll(alpha, cellI) {
            distance[cellI] = calculateDistance(alpha[cellI], normal[cellI], cellVolumes_[cellI]);
        }
    }
    
private:
    scalar calculateDistance(
        scalar alpha,
        vector normal,
        scalar cellVolume
    ) const {
        // Simplified calculation
        // ในความเป็นจริงต้องคำนวณจาก geometry ของ cell
        return (alpha - 0.5) * pow(cellVolume, 1.0/3.0);
    }
};
```

### 3. Interface Compression

เพื่อรักษา interface ให้ sharp ต้องใช้ interface compression term:

```cpp
// Interface compression term ในสมการ VOF
surfaceScalarField phic =
    fvc::flux
    (
        phir,
        alpha,
        alphaScheme
    )
  + fvc::flux
    (
        -fvc::flux(-phir, beta, alpharScheme),
        alpha,
        alpharScheme
    );

// เพิ่ม compression term
phic +=
    fvc::flux
    (
        -fvc::flux
        (
            phir*(1.0 - alpha),
            fvc::interpolate(beta),
            alpharScheme
        ),
        alpha,
        alpharScheme
    );
```

### 4. Mass Transfer at Interface

```cpp
// Mass transfer rate calculation at interface cells
volScalarField calculateMassTransfer(
    const volScalarField& T,
    const volScalarField& alpha,
    const dimensionedScalar& T_sat,
    const dimensionedScalar& coeff
) const {
    volScalarField mDot = volScalarField::New("mDot", mesh_, dimensionedScalar(dimMass/dimVolume/dimTime, 0.0));
    
    // Lee model: mDot = C * α * ρ * (T - T_sat)/T_sat
    // สำหรับ evaporation (T > T_sat): mDot > 0
    // สำหรับ condensation (T < T_sat): mDot < 0
    
    // คำนวณเฉพาะที่ interface cells
    labelList interfaceCells = findInterfaceCells(alpha, 0.01);
    
    forAll(interfaceCells, i) {
        label cellI = interfaceCells[i];
        scalar alphaVal = alpha[cellI];
        scalar TVal = T[cellI];
        
        // คำนวณ mixture density ที่ cell นี้
        scalar rho_m = alphaVal * rho_l_.value() + (1.0 - alphaVal) * rho_v_.value();
        
        // Lee model
        mDot[cellI] = coeff.value() * alphaVal * rho_m * (TVal - T_sat.value()) / T_sat.value();
    }
    
    return mDot;
}
```

### 5. Interface Visualization และ Diagnostics

```cpp
void writeInterfaceDiagnostics(
    const volScalarField& alpha,
    const volScalarField& mDot,
    const word& timeName
) const {
    // Calculate interface statistics
    scalar interfaceArea = 0.0;
    scalar totalMassTransfer = 0.0;
    
    labelList interfaceCells = findInterfaceCells(alpha, 0.01);
    
    forAll(interfaceCells, i) {
        label cellI = interfaceCells[i];
        interfaceArea += mesh_.V()[cellI];
        totalMassTransfer += mDot[cellI] * mesh_.V()[cellI];
    }
    
    // Write to log file
    Info << "Time = " << timeName << nl
         << "  Interface cells = " << interfaceCells.size() << nl
         << "  Interface area = " << interfaceArea << " m²" << nl
         << "  Total mass transfer = " << totalMassTransfer << " kg/s" << nl
         << endl;
}
```

---

## Phase-Specific Implementation (การนำไปใช้เฉพาะเฟส)

การ implement logic เฉพาะสำหรับแต่ละเฟสใน ExtendedVolScalarField:

### 1. Phase Identification

```cpp
enum PhaseType {
    LIQUID_PHASE,
    VAPOR_PHASE,
    INTERFACE_PHASE
};

PhaseType identifyPhase(scalar alpha, scalar threshold = 0.01) {
    if (alpha > (1.0 - threshold)) {
        return LIQUID_PHASE;
    } else if (alpha < threshold) {
        return VAPOR_PHASE;
    } else {
        return INTERFACE_PHASE;
    }
}
```

### 2. Phase-Specific Calculations

```cpp
class PhaseSpecificCalculator {
public:
    // Liquid-phase specific calculations
    volScalarField liquidFraction(const volScalarField& alpha) const {
        return max(min(alpha, 1.0), 0.0);
    }
    
    volScalarField vaporFraction(const volScalarField& alpha) const {
        return max(min(1.0 - alpha, 1.0), 0.0);
    }
    
    // Phase-specific source terms
    volScalarField liquidSourceTerm(
        const volScalarField& field,
        const volScalarField& alpha
    ) const {
        return liquidFraction(alpha) * field;
    }
    
    volScalarField vaporSourceTerm(
        const volScalarField& field,
        const volScalarField& alpha
    ) const {
        return vaporFraction(alpha) * field;
    }
    
    // Phase-aware expansion term calculation
    volScalarField expansionTermPhaseAware(
        const volScalarField& mDot,
        const volScalarField& alpha,
        const dimensionedScalar& rho_l,
        const dimensionedScalar& rho_v
    ) const {
        volScalarField expansion(mDot.mesh(), dimensionedScalar(dimless/dimTime, 0.0));
        
        forAll(mDot, cellI) {
            scalar mDotVal = mDot[cellI];
            scalar alphaVal = alpha[cellI];
            
            if (mDotVal > 0.0) {
                // Evaporation: liquid → vapor
                // ใช้ vapor density สำหรับ volume expansion
                expansion[cellI] = mDotVal * (1.0/rho_v.value());
            } else if (mDotVal < 0.0) {
                // Condensation: vapor → liquid
                // ใช้ liquid density สำหรับ volume contraction
                expansion[cellI] = mDotVal * (1.0/rho_l.value());
            }
            
            // Subtract the phase being consumed
            if (mDotVal > 0.0) {
                // Evaporation consumes liquid
                expansion[cellI] -= mDotVal * (1.0/rho_l.value());
            } else if (mDotVal < 0.0) {
                // Condensation consumes vapor
                expansion[cellI] -= mDotVal * (1.0/rho_v.value());
            }
        }
        
        return expansion;
    }
};
```

### 3. Phase-Dependent Boundary Conditions

```cpp
void applyPhaseSpecificBC(
    volScalarField& field,
    const volScalarField& alpha,
    const word& patchName,
    const PhaseType phase
) {
    fvPatchScalarField& patchField = field.boundaryFieldRef()[patchName];
    
    switch (phase) {
        case LIQUID_PHASE:
            // Liquid-phase specific BC
            if (isType<fixedValueFvPatchScalarField>(patchField)) {
                // Adjust for liquid properties
                fixedValueFvPatchScalarField& fixedPatch =
                    refCast<fixedValueFvPatchScalarField>(patchField);
                // ... liquid-specific adjustments
            }
            break;
            
        case VAPOR_PHASE:
            // Vapor-phase specific BC
            if (isType<fixedValueFvPatchScalarField>(patchField)) {
                // Adjust for vapor properties
                fixedValueFvPatchScalarField& fixedPatch =
                    refCast<fixedValueFvPatchScalarField>(patchField);
                // ... vapor-specific adjustments
            }
            break;
            
        case INTERFACE_PHASE:
            // Interface-specific BC (mixed condition)
            if (isType<mixedFvPatchScalarField>(patchField)) {
                mixedFvPatchScalarField& mixedPatch =
                    refCast<mixedFvPatchScalarField>(patchField);
                // ... interface-specific adjustments
            }
            break;
    }
}
```

### 4. Phase-Specific Linearization

```cpp
class PhaseSpecificLinearizer {
public:
    // Linearization coefficients ที่ขึ้นกับ phase
    void linearizeSourceTerm(
        const volScalarField& field,
        const volScalarField& alpha,
        scalarField& Sp,
        scalarField& Su
    ) const {
        forAll(field, cellI) {
            scalar alphaVal = alpha[cellI];
            PhaseType phase = identifyPhase(alphaVal);
            
            switch (phase) {
                case LIQUID_PHASE:
                    // Strong implicit treatment for liquid
                    Sp[cellI] = 1.0;  // Strong diagonal contribution
                    Su[cellI] = 0.0;
                    break;
                    
                case VAPOR_PHASE:
                    // Weaker implicit treatment for vapor
                    Sp[cellI] = 0.5;  // Moderate diagonal contribution
                    Su[cellI] = 0.0;
                    break;
                    
                case INTERFACE_PHASE:
                    // Mixed treatment at interface
                    Sp[cellI] = 0.8;  // Strong implicit to stabilize interface
                    Su[cellI] = 0.2 * field[cellI];  // Small explicit part
                    break;
            }
        }
    }
};
```

### 5. Implementation Benefits

**ประโยชน์ของ Phase-Specific Implementation:**
1. **Improved Accuracy**: การคำนวณที่แม่นยำสำหรับแต่ละเฟส
2. **Enhanced Stability**: Linearization ที่เหมาะสมสำหรับแต่ละเฟส
3. **Better Convergence**: Phase-aware numerical treatment
4. **Physical Consistency**: รักษาคุณสมบัติทางฟิสิกส์ของแต่ละเฟส

**Use Cases:**
- **Evaporation Simulation**: ใช้ liquid-phase logic สำหรับ bulk liquid, interface logic สำหรับ evaporation zone
- **Condensation Simulation**: ใช้ vapor-phase logic สำหรับ bulk vapor, interface logic สำหรับ condensation zone
- **Boiling Simulation**: ใช้ทั้ง liquid, vapor, และ interface logic สำหรับ complex boiling phenomena
