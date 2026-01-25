# Deep Dive: fvSchemes และ fvSolution ใน OpenFOAM

**ตำแหน่งใน Roadmap:** Day 01 - Phase 1 Foundation Theory (Extended Coverage)  
**ไฟล์ที่เกี่ยวข้อง:** 
- [`daily_learning/Phase_01_Foundation_Theory/2026-01-03.md:1060-1310`](daily_learning/Phase_01_Foundation_Theory/2026-01-03.md:1060-1310) - fvSchemes Implementation
- [`daily_learning/Phase_01_Foundation_Theory/2026-01-08.md:735-930`](daily_learning/Phase_01_Foundation_Theory/2026-01-08.md:735-930) - fvSolution และ Linear Solvers
- [`daily_learning/Phase_01_Foundation_Theory/2026-01-12.md:269-322`](daily_learning/Phase_01_Foundation_Theory/2026-01-12.md:269-322) - fvSolution Integration

---

## 🔗 Prerequisites
- ความเข้าใจ Numerical Methods สำหรับ PDEs
- ความรู้เรื่อง Discretization Schemes (Upwind, Central, TVD)
- ความเข้าใจ Linear Algebra และ Iterative Solvers
- ความรู้เกี่ยวกับ Runtime Configuration Systems

---

## 📝 Step-by-step Explanation

### 1. Overview: Runtime Configuration System

OpenFOAM ใช้ระบบ Runtime Configuration ที่ทรงพลังซึ่งประกอบด้วยสองส่วนหลัก:

1. **`fvSchemes`**: ควบคุม **Numerical Discretization Schemes**
2. **`fvSolution`**: ควบคุม **Linear Solvers และ Solution Algorithms**

ระบบนี้ใช้ **Factory Pattern** และ **Runtime Selection** ทำให้ผู้ใช้สามารถเปลี่ยน numerical methods ได้โดยไม่ต้อง recompile code

### 2. fvSchemes: Discretization Scheme Management

#### 2.1 Class Structure

```cpp
// src/finiteVolume/fvSchemes/fvSchemes.H
class fvSchemes
:
    public regIOobject  // สำหรับ IO operations
{
private:
    // Sub-dictionaries สำหรับแต่ละประเภทของ scheme
    dictionary ddtSchemes_;
    dictionary gradSchemes_;
    dictionary divSchemes_;
    dictionary laplacianSchemes_;
    dictionary interpolationSchemes_;
    dictionary snGradSchemes_;
    
public:
    // Constructor
    fvSchemes(const objectRegistry& obr, const fileName& instance);
    
    // Read/write methods
    virtual bool read();
    virtual bool writeData(Ostream&) const;
    
    // Access methods
    const dictionary& ddtSchemes() const { return ddtSchemes_; }
    const dictionary& divSchemes() const { return divSchemes_; }
    // ... อื่นๆ
};
```

#### 2.2 Dictionary Structure

ไฟล์ `system/fvSchemes` มีโครงสร้างแบบ nested dictionaries:

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss linear;
    grad(U)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss upwind;
    div(phi,alpha)  Gauss vanLeer;
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

fluxRequired
{
    default         no;
    p               ;
}

// ************************************************************************* //
```

#### 2.3 Scheme Selection Mechanism

ระบบใช้ **Runtime Selection Table** สำหรับเลือก scheme:

```cpp
// ตัวอย่าง: divScheme selection
template<class Type>
tmp<fvMatrix<Type>> divScheme<Type>::New
(
    const surfaceScalarField& phi,
    const GeometricField<Type, fvPatchField, volMesh>& vf,
    const word& name
)
{
    // อ่าน scheme name จาก fvSchemes dictionary
    word schemeName = mesh().schemesDict().divScheme(name);
    
    // ค้นหาใน runtime selection table
    typename IstreamConstructorTable::iterator cstrIter =
        IstreamConstructorTablePtr_->find(schemeName);
    
    if (cstrIter == IstreamConstructorTablePtr_->end())
    {
        FatalErrorInFunction
            << "Unknown divScheme " << schemeName
            << abort(FatalError);
    }
    
    // สร้าง scheme object
    return cstrIter()(phi, vf, schemeName);
}
```

#### 2.4 Scheme Types สำหรับ Phase Change Problems

สำหรับ evaporator simulation เราต้องเลือก schemes ที่เหมาะสม:

```cpp
// Recommended schemes for phase change simulations
ddtSchemes
{
    default         CrankNicolson 0.9;  // Blended สำหรับ stability และ accuracy
}

divSchemes  
{
    default         none;
    
    // Momentum equation - ใช้ upwind สำหรับ stability
    div(phi,U)      Gauss limitedLinearV 1;  // TVD scheme
    
    // Volume fraction - ใช้ compressive scheme สำหรับ sharp interface
    div(phi,alpha)  Gauss vanLeer;
    div(phir,alpha) Gauss interfaceCompression;
    
    // Scalar equations - ใช้ upwind หรือ TVD
    div(phi,T)      Gauss limitedLinear 1;
    div(phi,k)      Gauss upwind;
    div(phi,omega)  Gauss upwind;
}

gradSchemes
{
    default         Gauss linear;
    
    // สำหรับ interface normal calculation
    grad(alpha)     Gauss cellLimited linear 1;  // Limited เพื่อป้องกัน oscillations
}

interpolationSchemes
{
    default         linear;
    interpolate(alpha) vanLeer;  // TVD interpolation สำหรับ alpha
}
```

### 3. fvSolution: Linear Solver Configuration

#### 3.1 Class Structure

`fvSolution` เป็น `dictionary` object ที่ไม่ใช่ class แบบดั้งเดิม แต่ถูกจัดการผ่าน `IOdictionary`:

```cpp
// การอ่าน fvSolution dictionary
IOdictionary fvSolution
(
    IOobject
    (
        "fvSolution",
        runTime.system(),
        runTime,
        IOobject::MUST_READ,
        IOobject::NO_WRITE
    )
);

// การเข้าถึง solver settings
const dictionary& solversDict = fvSolution.subDict("solvers");
const dictionary& pDict = solversDict.subDict("p");
const dictionary& UDict = solversDict.subDict("U");
```

#### 3.2 Dictionary Structure

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-6;
        relTol          0;
        maxIter         1000;
    }
    
    pFinal
    {
        $p;
        tolerance       1e-7;
        relTol          0;
    }
    
    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-5;
        relTol          0.1;
        maxIter         1000;
    }
    
    "(U|k|epsilon|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-5;
        relTol          0.1;
        maxIter         1000;
    }
    
    T
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0;
        maxIter         1000;
    }
    
    alpha
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;
        relTol          0;
        maxIter         100;
        nSweeps         2;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    
    residualControl
    {
        p               1e-5;
        U               1e-5;
        "(k|epsilon|omega)" 1e-5;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
        "(k|epsilon|omega)" 0.7;
    }
}

// ************************************************************************* //
```

#### 3.3 Solver Selection Logic

ระบบเลือก solver ตาม matrix properties:

```cpp
void selectSolver
(
    const lduMatrix& A,
    const dictionary& solverDict,
    autoPtr<lduMatrix::solver>& solverPtr
)
{
    word solverName = solverDict.lookup("solver");
    word preconditionerName = solverDict.lookup("preconditioner");
    
    // ตรวจสอบ symmetry สำหรับเลือกระหว่าง PCG และ PBiCGStab
    bool isSymmetric = checkSymmetry(A);
    
    if (solverName == "PCG" && !isSymmetric)
    {
        WarningInFunction
            << "Matrix is not symmetric, switching to PBiCGStab"
            << endl;
        solverName = "PBiCGStab";
    }
    
    // สร้าง solver ผ่าน factory
    solverPtr = lduMatrix::solver::New
    (
        solverName,
        A,
        solverDict
    );
}
```

#### 3.4 Recommended Settings สำหรับ Phase Change

```cpp
solvers
{
    // Pressure - ใช้ PCG กับ DIC สำหรับ symmetric matrix
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-6;
        relTol          0.05;      // Allow 5% relative tolerance
        maxIter         2000;      // เพิ่ม iterations สำหรับ stiff problems
    }
    
    // Velocity - ใช้ PBiCGStab กับ DILU สำหรับ asymmetric matrix
    U
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-5;
        relTol          0.1;       // Higher relTol สำหรับ faster convergence
        maxIter         1000;
    }
    
    // Temperature - คล้ายกับ velocity
    T
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0;
        maxIter         1000;
    }
    
    // Volume fraction - ใช้ smoothSolver สำหรับ stability
    alpha
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-8;       // Tight tolerance สำหรับ mass conservation
        relTol          0;
        maxIter         50;
        nSweeps         2;
    }
}

PIMPLE
{
    nOuterCorrectors  3;           // เพิ่ม outer correctors สำหรับ coupling
    nCorrectors       2;
    nNonOrthogonalCorrectors 1;
    
    residualControl
    {
        p               1e-5;
        U               1e-5;
        alpha           1e-7;       // Tight control สำหรับ interface
        T               1e-6;
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;        // Conservative relaxation สำหรับ pressure
        alpha           0.5;        // Moderate relaxation สำหรับ alpha
    }
    equations
    {
        U               0.7;
        T               0.8;
        "(k|omega)"     0.8;
    }
}
```

### 4. Integration กับ Core Classes

#### 4.1 Integration กับ fvMatrix

```cpp
template<class Type>
SolverPerformance<Type> fvMatrix<Type>::solve(const dictionary& solverControls)
{
    // อ่าน solver settings
    word solverName = solverControls.lookup("solver");
    scalar tolerance = solverControls.lookup<scalar>("tolerance");
    scalar relTol = solverControls.lookupOrDefault<scalar>("relTol", 0);
    
    // สร้าง solver object
    autoPtr<lduMatrix::solver> solver = 
        lduMatrix::solver::New(solverName, *this, solverControls);
    
    // Apply boundary conditions
    this->addBoundaryDiag(diag(), 0);
    this->addBoundarySource(source(), false);
    
    // Solve
    solver->solve(psi_.internalField(), source());
    
    // Update boundary values
    psi_.correctBoundaryConditions();
}
```

#### 4.2 Integration กับ Time Loop

```cpp
while (runTime.loop())
{
    // อ่าน fvSolution สำหรับ time step นี้ (อาจ adaptive)
    const dictionary& fvSolution = runTime.solutionDict();
    
    // PISO/PIMPLE loop
    for (int corr = 0; corr < nCorr; corr++)
    {
        // Solve momentum
        UEqn.solve(fvSolution.subDict("solvers").subDict("U"));
        
        // Solve pressure
        pEqn.solve(fvSolution.subDict("solvers").subDict("p"));
        
        // Correct velocity และ flux
        U = HbyA - fvc::grad(p)/UEqn.A();
        phi = fvc::flux(U);
    }
    
    // Solve scalar equations
    TEqn.solve(fvSolution.subDict("solvers").subDict("T"));
    alphaEqn.solve(fvSolution.subDict("solvers").subDict("alpha"));
    
    // Apply relaxation
    p.relax(fvSolution.subDict("relaxationFactors").lookup<scalar>("p"));
    U.relax(fvSolution.subDict("relaxationFactors").lookup<scalar>("U"));
}
```

### 5. Adaptive Control สำหรับ Phase Change

#### 5.1 Dynamic Solver Selection

```cpp
class AdaptiveSolverController
{
private:
    // Track convergence history
    List<scalar> pResiduals_;
    List<scalar> UResiduals_;
    List<scalar> alphaResiduals_;
    
public:
    void adjustSolverSettings
    (
        dictionary& fvSolution,
        const scalar time,
        const scalar Co,
        const scalar maxAlphaChange
    )
    {
        // Adjust based on Courant number
        if (Co > 5.0)
        {
            // ใช้ more robust settings สำหรับ high Co
            fvSolution.subDict("solvers").subDict("p").set("solver", "GAMG");
            fvSolution.subDict("solvers").subDict("p").set("tolerance", 1e-4);
        }
        
        // Adjust based on interface movement
        if (maxAlphaChange > 0.1)
        {
            // Tighten alpha solver สำหรับ rapid interface movement
            fvSolution.subDict("solvers").subDict("alpha")
                .set("tolerance", 1e-9);
            fvSolution.subDict("solvers").subDict("alpha")
                .set("maxIter", 100);
        }
        
        // Adjust relaxation factors
        scalar pRelax = 0.3;
        if (pResiduals_.size() > 10)
        {
            // Reduce relaxation ถ้า residuals oscillate
            scalar residualRatio = pResiduals_.last() / pResiduals_[pResiduals_.size()-2];
            if (residualRatio > 1.5)
            {
                pRelax *= 0.8;
            }
        }
        fvSolution.subDict("relaxationFactors").subDict("fields").set("p", pRelax);
    }
};
```

#### 5.2 Interface-Aware Settings

```cpp
void setInterfaceAwareSchemes
(
    dictionary& fvSchemes,
    const volScalarField& alpha,
    scalar interfaceThreshold = 0.01
)
{
    // Detect interface cells
    labelList interfaceCells = findInterfaceCells(alpha, interfaceThreshold);
    
    if (!interfaceCells.empty())
    {
        // ใช้ compressive schemes เฉพาะใกล้ interface
        fvSchemes.subDict("divSchemes").set("div(phi,alpha)", "Gauss interfaceCompression");
        
        // ใช้ limited gradient schemes สำหรับ interface normal
        fvSchemes.subDict("gradSchemes").set("grad(alpha)", "Gauss cell
        // ใช้ limited gradient schemes สำหรับ interface normal
        fvSchemes.subDict("gradSchemes").set("grad(alpha)", "Gauss cellLimited linear 1");
        
        // ใช้ implicit Euler ใกล้ interface สำหรับ stability
        fvSchemes.subDict("ddtSchemes").set("default", "Euler");
    }
    else
    {
        // ใช้ higher-order schemes ใน bulk regions
        fvSchemes.subDict("ddtSchemes").set("default", "CrankNicolson 0.9");
        fvSchemes.subDict("divSchemes").set("div(phi,alpha)", "Gauss vanLeer");
    }
}
```

---

## 💡 Key Insights

1. **Runtime Flexibility**: fvSchemes/fvSolution ให้ความยืดหยุ่นสูงสุดโดยไม่ต้อง recompile code
2. **Physics-Aware Configuration**: สามารถปรับ settings ตาม physical characteristics ของแต่ละ field
3. **Performance vs Accuracy Trade-offs**: การเลือก schemes และ solvers ต้อง balance ระหว่าง computational cost และ solution accuracy
4. **Adaptive Control**: สามารถ implement dynamic adjustment ของ settings ตาม simulation state

---

## 🧪 Quick Check

**คำถาม:** ทำไมต้องใช้ different schemes สำหรับ `div(phi,U)` และ `div(phi,alpha)` ใน phase change simulations?

**คำตอบ:** เพราะ physical characteristics ของ fields ต่างกัน:
1. **`U` (Velocity)**: มีทั้ง convective และ diffusive characteristics ต้องการ schemes ที่รักษา momentum conservation และ stability
2. **`alpha` (Volume Fraction)**: ต้อง bounded ระหว่าง 0 ถึง 1 ต้องการ compressive schemes ที่รักษา interface sharpness
3. **Different Numerical Requirements**: 
   - `U`: ใช้ TVD schemes (`limitedLinearV`) เพื่อป้องกัน oscillations ใน high gradient regions
   - `alpha`: ใช้ compressive schemes (`vanLeer`, `interfaceCompression`) เพื่อรักษา interface thickness

---

## 📚 Related Topics

- **Day 03:** Spatial Discretization Schemes และ fvSchemes Implementation
- **Day 08:** Linear Solvers และ fvSolution Configuration  
- **Day 09:** Pressure-Velocity Coupling Algorithms (PISO/SIMPLE)
- **Day 10:** VOF Method และ Interface Capturing Schemes
- **Day 12:** Integrated Solver Architecture และ Configuration Management

---

## ⚠️ Common Pitfalls และ Solutions

### Pitfall 1: Incorrect Scheme Selection
```cpp
// ❌ ผิด: ใช้ central differencing สำหรับ convective terms
divSchemes
{
    div(phi,U)      Gauss linear;  // อาจเกิด oscillations
    div(phi,alpha)  Gauss linear;  // interface จะ diffuse
}

// ✅ ถูก: ใช้ appropriate schemes
divSchemes
{
    div(phi,U)      Gauss limitedLinearV 1;  // TVD สำหรับ momentum
    div(phi,alpha)  Gauss vanLeer;           // Compressive สำหรับ interface
}
```

### Pitfall 2: Overly Tight Tolerances
```cpp
// ❌ ผิด: tolerances ที่ tight เกินไป
solvers
{
    p { tolerance 1e-12; maxIter 10000; }  // ใช้เวลาคำนวณนาน
    U { tolerance 1e-12; maxIter 10000; }
}

// ✅ ถูก: ใช้ practical tolerances
solvers
{
    p { tolerance 1e-6; relTol 0.05; maxIter 2000; }
    U { tolerance 1e-5; relTol 0.1; maxIter 1000; }
}
```

### Pitfall 3: Missing Relaxation Factors
```cpp
// ❌ ผิด: ไม่ใช้ relaxation สำหรับ stiff problems
relaxationFactors {}  // อาจทำให้ diverge

// ✅ ถูก: ใช้ appropriate relaxation
relaxationFactors
{
    fields { p 0.3; alpha 0.5; }
    equations { U 0.7; T 0.8; }
}
```

### Pitfall 4: Inconsistent Settings
```cpp
// ❌ ผิด: settings ที่ขัดแย้งกัน
solvers
{
    p { solver PCG; }  // สำหรับ symmetric matrix
}
// แต่ matrix ไม่ symmetric เพราะมี convective terms

// ✅ ถูก: ใช้ solver ที่เหมาะสม
solvers
{
    p { solver PCG; }        // OK ถ้า matrix symmetric
    U { solver PBiCGStab; }  // สำหรับ asymmetric matrix
}
```

---

## 🎯 Engineering Impact

การเข้าใจ fvSchemes/fvSolution อย่างลึกซึ้งช่วยให้:
1. **Optimize Simulation Performance**: เลือก schemes และ solvers ที่เหมาะสมกับปัญหา
2. **Ensure Numerical Stability**: ป้องกัน divergence จาก incorrect settings
3. **Maintain Physical Accuracy**: รักษา conservation laws และ physical bounds
4. **Debug Convergence Issues**: วินิจฉัยและแก้ปัญหา convergence ได้อย่างมีประสิทธิภาพ
5. **Implement Advanced Features**: สร้าง adaptive control systems สำหรับ complex physics

---

## 🔬 Advanced Topics

### 1. Dynamic Scheme Switching
```cpp
// Adaptive scheme selection based on local flow conditions
void AdaptiveSchemeManager::updateSchemes(
    const volScalarField& alpha,
    const volVectorField& U
) {
    // Calculate local Peclet number
    volScalarField Pe = mag(U)*mesh_.deltaCoeffs()/nu_;
    
    // Switch schemes based on Pe
    forAll(Pe, cellI) {
        if (Pe[cellI] > 2.0) {
            // ใช้ upwind ใน high Pe regions
            setCellScheme(cellI, UPWIND);
        } else {
            // ใช้ central ใน low Pe regions  
            setCellScheme(cellI, CENTRAL);
        }
    }
}
```

### 2. Machine Learning-Based Tuning
```cpp
// Use ML to predict optimal solver settings
class MLSolverTuner {
public:
    dictionary predictOptimalSettings(
        const meshQualityMetrics& metrics,
        const flowCondition& condition,
        const phaseChangeIntensity& intensity
    ) {
        // Extract features
        vector features = extractFeatures(metrics, condition, intensity);
        
        // Predict using trained model
        solverSettings settings = mlModel_.predict(features);
        
        // Convert to dictionary
        return settings.toDictionary();
    }
};
```

### 3. Multi-Objective Optimization
```cpp
// Optimize for both accuracy และ performance
class MultiObjectiveOptimizer {
public:
    paretoFront optimizeSettings(
        const simulationObjectives& objectives,
        const constraints& constraints
    ) {
        // Explore parameter space
        for (auto& settings : parameterSpace) {
            scalar accuracy = evaluateAccuracy(settings);
            scalar speed = evaluateSpeed(settings);
            scalar robustness = evaluateRobustness(settings);
            
            // Add to Pareto front
            updateParetoFront(settings, {accuracy, speed, robustness});
        }
        
        return paretoFront_;
    }
};
```

---

**สรุป:** fvSchemes และ fvSolution เป็นหัวใจของ numerical configuration ใน OpenFOAM การเข้าใจระบบนี้อย่างลึกซึ้งช่วยให้สามารถควบคุมและ optimize numerical simulations ได้อย่างมีประสิทธิภาพ โดยเฉพาะสำหรับ complex problems เช่น phase change simulations
